"""Full RAG pipeline orchestrator — retrieval, generation, and response assembly.

Implements the complete 10-step query pipeline with 3-tier fallback:
  Tier 1 (Fast DB): Search database, return if confidence > 70%
  Tier 2 (Web Crawl): If confidence low, try web crawl
  Tier 3 (LLM Fallback): If nothing found, use GPT-4o to answer directly

Ensures users ALWAYS get a response, even for unknown queries.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
import uuid
from typing import Optional, Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_factory
from app.services import embed_service, cache_service, translate_service
from app.services.generate_service import generate_query_response, general_legal_answer, get_openai_client
from app.schemas.query import QueryResponse, LawResult

logger = logging.getLogger("lexindia.services.rag")


NORMALISE_PROMPT = """
You are a legal query parser for Indian law.
Given a citizen's complaint in plain language, extract:
1. The core legal issues (max 3, in plain legal terms)
2. A normalised search query combining all issues

Examples:
Input:  "bus conductor did not give me change and spoke rudely"
Output: {
  "issues": ["overcharging by transport conductor",
             "verbal abuse by public servant",
             "consumer service deficiency"],
  "normalised_query": "transport conductor overcharging passenger verbal abuse deficiency of service"
}

Input:  "my landlord won't return deposit"
Output: {
  "issues": ["wrongful retention of security deposit"],
  "normalised_query": "landlord refusing to return security deposit breach of contract criminal breach of trust"
}

Return ONLY valid JSON. No extra text.
"""


def _heuristic_normalise_query(issue_en: str) -> dict[str, Any]:
    """Fallback normaliser when GPT normalization is unavailable."""
    q = issue_en.lower().strip()
    issues: list[str] = []
    tokens: list[str] = []

    if re.search(r"bus|conductor|ticket|change|balance|overcharg", q):
        issues.append("overcharging by transport conductor")
        tokens.extend(["transport conductor", "passenger overcharging", "ticket fare", "balance amount not returned"])

    if re.search(r"rude|abuse|ill[- ]?manner|insult|obscene|spoke", q):
        issues.append("verbal abuse in public service")
        tokens.extend(["verbal abuse", "intentional insult", "obscene words public place"])

    if re.search(r"landlord|owner|deposit|security", q):
        issues.append("wrongful retention of security deposit")
        tokens.extend(["landlord refusing security deposit", "breach of contract", "criminal breach of trust"])

    if re.search(r"salary|wage|employer|not paid|unpaid|months", q):
        issues.append("non payment of wages by employer")
        tokens.extend(["employer non payment salary", "delayed wages", "labour law wage dues"])

    if re.search(r"service|deficien|consumer", q):
        issues.append("consumer service deficiency")
        tokens.extend(["deficiency of service", "consumer protection"])

    if not issues:
        issues = ["general legal grievance"]
        tokens = [issue_en]

    # Preserve original meaning while adding legal anchors
    normalised_query = " ".join(dict.fromkeys([issue_en] + tokens))
    return {"issues": issues[:3], "normalised_query": normalised_query}


async def _normalise_query_for_embedding(issue_en: str, query_id: str) -> dict[str, Any]:
    """Normalize conversational complaint to legal search terms before embedding."""
    try:
        client = get_openai_client()
        normalised = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": NORMALISE_PROMPT},
                {"role": "user", "content": issue_en},
            ],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0,
        )
        raw = normalised.choices[0].message.content or "{}"
        parsed = json.loads(raw)
        search_query = (parsed.get("normalised_query") or issue_en).strip()
        if not search_query:
            search_query = issue_en
        issues = parsed.get("issues") or []
        logger.info(f"[{query_id}] Query normalised via GPT: {issues}")
        return {"issues": issues, "normalised_query": search_query}
    except Exception as e:
        logger.warning(f"[{query_id}] Query normalisation via GPT failed: {e}")
        fallback = _heuristic_normalise_query(issue_en)
        logger.info(f"[{query_id}] Query normalised via heuristic: {fallback.get('issues', [])}")
        return fallback


async def _calculate_result_confidence(laws: list) -> float:
    """Calculate confidence score for database results.
    
    Returns:
        Confidence between 0.0 and 1.0
        > 0.70 = High confidence (use DB result)
        0.50-0.70 = Medium confidence (consider web crawl)
        < 0.50 = Low confidence (use LLM fallback)
    """
    if not laws:
        return 0.0
    
    # Average relevance score of top 3 results
    top_scores = [law.get("relevance_score", 0) for law in laws[:3]]
    avg_score = sum(top_scores) / len(top_scores) if top_scores else 0
    
    # Boost confidence if high severity match
    high_severity_count = len([l for l in laws[:3] if l.get("severity") == "high"])
    severity_boost = 0.1 * high_severity_count
    
    confidence = min(1.0, avg_score + severity_boost)
    logger.info(f"Result confidence: {confidence:.2f} (avg_score: {avg_score:.2f}, high_severity: {high_severity_count})")
    
    return confidence


async def query_laws(
    issue: str,
    language: str,
    db: AsyncSession,
    mode: str = "citizen",
) -> dict:
    """Execute the hybrid 3-tier RAG pipeline for a user's legal query.

    TIER 1 (Fast DB): Search database, return if confidence > 70%
    TIER 2 (Web): If confidence 50-70%, try web crawl for better results
    TIER 3 (LLM): If confidence < 50%, use GPT-4o to generate legal answer

    Args:
        issue: The user's plain-language legal problem description.
        language: Desired response language ('en', 'ta', or 'hi').
        db: Async database session.

    Returns:
        Complete query response dict matching QueryResponse schema.
        ALWAYS returns a response (never "no results" error).
    """
    start_time = time.perf_counter()
    query_id = str(uuid.uuid4())

    # ── Step 1: Detect input language ────────────────────────────────
    detected_lang = await translate_service.detect(issue)
    logger.info(f"[{query_id}] Detected language: {detected_lang}")

    # ── Step 2: Translate to English if needed ───────────────────────
    if detected_lang != "en":
        issue_en = await translate_service.translate_to_english(issue, detected_lang)
        logger.info(f"[{query_id}] Translated to English: '{issue_en[:80]}...'")
    else:
        issue_en = issue

    # ── Step 3: Check Redis cache ────────────────────────────────────
    cache_key = f"lexindia:query:{hashlib.md5(issue.encode()).hexdigest()}:{language}:{mode}"
    try:
        cached = await cache_service.get(cache_key)
    except Exception:
        cached = None
    if cached:
        logger.info(f"[{query_id}] Cache hit — returning cached response")
        cached["query_id"] = query_id
        cached["response_ms"] = int((time.perf_counter() - start_time) * 1000)
        return cached

    # ▰▰▰ TIER 1: Fast Database Search ▰▰▰
    logger.info(f"[{query_id}] ═══ TIER 1: Fast Database Search ═══")
    
    # ── Step 4: Embed the English query ──────────────────────────────
    normalised = await _normalise_query_for_embedding(issue_en, query_id)
    search_query = normalised.get("normalised_query", issue_en)

    try:
        query_vector = embed_service.embed(search_query)
    except Exception as e:
        logger.error(f"EMBEDDING FAILED — this must be fixed: {e}")
        raise HTTPException(
            status_code=503,
            detail=(
                f"Embedding service unavailable: {str(e)}. "
                "Run setup/generate_embeddings.py first."
            ),
        )
    logger.info(
        f"[{query_id}] Query embedded ({len(query_vector)} dimensions) "
        f"using normalised query: '{search_query[:140]}'"
    )

    try:
        results = await db.execute(
            text("""
                SELECT
                    section_id, act_name, act_code, section_number, section_title,
                    section_text, simplified_en, simplified_ta, simplified_hi,
                    severity, filing_link, punishment,
                                        1 - (embedding <=> CAST(:qvec AS vector)) AS score
                FROM laws
                WHERE embedding IS NOT NULL
                                    AND 1 - (embedding <=> CAST(:qvec AS vector)) > :threshold
                                ORDER BY embedding <=> CAST(:qvec AS vector)
                LIMIT :max_results
            """),
            {
                "qvec": str(query_vector),
                "threshold": settings.SIMILARITY_THRESHOLD,
                "max_results": settings.MAX_RESULTS,
            },
        )
        rows = results.fetchall()
        logger.info(f"[{query_id}] Vector search returned {len(rows)} results")
    except Exception as e:
        logger.error(f"[{query_id}] Vector search failed: {e}")
        # Explicitly rollback to avoid tainting the session for subsequent calls
        await db.rollback()
        raise e

    # Calculate confidence from DB results
    db_laws = [
        {
            "section_id": row.section_id,
            "act_name": row.act_name,
            "section_number": row.section_number,
            "section_title": row.section_title,
            "section_text": row.section_text,
            "simplified_en": row.simplified_en,
            "severity": row.severity,
            "punishment": row.punishment,
            "filing_link": row.filing_link,
            "relevance_score": float(row.score),
        }
        for row in rows
    ]
    
    db_confidence = await _calculate_result_confidence(db_laws)
    logger.info(f"[{query_id}] DB confidence: {db_confidence:.2f}")

    # ▰▰▰ TIER 1 DECISION ▰▰▰
    if db_laws:
        logger.info(
            f"[{query_id}] ✅ TIER 1 SUCCESS: Returning {len(db_laws)} database results "
            f"(confidence: {db_confidence:.2f})"
        )
        response = await _process_tier1_results(
            db_laws, rows, query_id, issue_en, detected_lang, language, start_time, cache_key
        )
        return response

    # ▰▰▰ TIER 2: Web Crawl Fallback ▰▰▰
    # Trigger web crawl when DB has no results OR low confidence.
    # This ensures unknown queries are actually escalated to external sources.
    if (not db_laws) or (db_confidence < settings.MIN_RESULT_CONFIDENCE):
        logger.info(f"[{query_id}] ═══ TIER 2: Web Crawl Fallback ═══")
        logger.warning(
            f"[{query_id}] No/low DB confidence ({db_confidence:.2f}) — attempting web crawl"
        )
        
        # Try to crawl indiacode.nic.in for better results
        web_laws = await _crawl_indiacode(search_query, query_id)
        
        if web_laws and len(web_laws) > 0:
            logger.info(f"[{query_id}] ✅ TIER 2 SUCCESS: Found {len(web_laws)} laws from web crawl")
            response = await _process_web_results(
                web_laws, query_id, issue_en, detected_lang, language, start_time, cache_key
            )
            return response
        else:
            logger.warning(f"[{query_id}] Web crawl returned no results, falling back to Tier 3 LLM")
    
    # ▰▰▰ TIER 3: LLM Fallback ▰▰▰
    logger.info(f"[{query_id}] ═══ TIER 3: LLM Fallback ═══")
    logger.warning(f"[{query_id}] No good DB or web results (confidence: {db_confidence:.2f}) — using GPT-4o to generate answer")
    
    try:
        llm_answer = await general_legal_answer(issue_en, issue, language)
        if not llm_answer or str(llm_answer).strip().lower() in {"none", "null", ""}:
            if language == "ta":
                llm_answer = "⚠️ AI சட்ட சுருக்கம் கிடைக்கவில்லை\n\nஇந்த வினவலுக்கு தரவுத்தளத்தில் எந்த முடிவும் கிடைக்கவில்லை."
            elif language == "hi":
                llm_answer = "⚠️ AI कानूनी सारांश उपलब्ध नहीं है\n\nइस क्वेरी के लिए डेटाबेस में कोई परिणाम नहीं मिला।"
            else:
                llm_answer = (
                    "⚠️ AI LEGAL SUMMARY UNAVAILABLE\n\n"
                    "No database or external-source match was found for this query, and the LLM response was empty. "
                    "Please rephrase with more detail (who, what, where, when) or try a related legal keyword."
                )
        
        response = {
            "query_id": query_id,
            "detected_language": detected_lang,
            "ai_summary": llm_answer,
            "laws": [],  # No specific laws found
            "response_ms": int((time.perf_counter() - start_time) * 1000),
            "source": "AI Generated (Consult Qualified Lawyer)",
        }
        
        # Cache the LLM response
        await cache_service.set(cache_key, response)
        
        # Log the query
        asyncio.create_task(
            _log_query(None, issue, detected_lang, 0, response["response_ms"])
        )
        
        logger.info(f"[{query_id}] ✅ TIER 3 SUCCESS: LLM generated legal guidance")
        return response
        
    except Exception as e:
        logger.error(f"[{query_id}] LLM fallback failed: {e}")
        # Final fallback: Return helpful error message
        return {
            "query_id": query_id,
            "detected_language": detected_lang,
            "ai_summary": (
                "⚠️ SYSTEM ERROR: Unable to retrieve legal information at this time. "
                "Please try again in a moment or rephrase your question. "
                "For immediate legal assistance, please contact a legal professional."
            ),
            "laws": [],
            "response_ms": int((time.perf_counter() - start_time) * 1000),
            "source": "Error Response",
        }


async def _process_tier1_results(
    db_laws, rows, query_id, issue_en, detected_lang, language, start_time, cache_key
):
    """Process and return Tier 1 (database) results with LLM summary."""
    # Build context for LLM
    context = _build_rag_context(rows, issue_en)

    try:
        logger.info(f"[{query_id}] Calling GPT-4o for summary in {language}...")
        gpt_response = await generate_query_response(context, language)
        logger.info(f"[{query_id}] GPT-4o response received")
    except Exception as e:
        logger.error(f"[{query_id}] GPT-4o call failed: {e}")
        gpt_response = None

    if not gpt_response:
        logger.warning(f"[{query_id}] GPT-4o failed — returning raw results")
        gpt_response = {
            "ai_summary": (
                "⚠️ AI SUMMARY UNAVAILABLE: Database results below. "
                "Consult a legal professional for advice specific to your situation."
            ),
            "laws": [
                {
                    "section_id": law["section_id"],
                    "relevance_score": law["relevance_score"],
                    "severity": law["severity"],
                }
                for law in db_laws
            ],
        }

    # Assemble response
    row_lookup = {row.section_id: row for row in rows}
    law_results = []
    
    for law in gpt_response.get("laws", []):
        section_id = law.get("section_id")
        db_row = row_lookup.get(section_id)
        if not db_row:
            continue

        lang_mapping = {
            "en": db_row.simplified_en,
            "ta": db_row.simplified_ta,
            "hi": db_row.simplified_hi,
        }
        
        simplified = lang_mapping.get(language, db_row.simplified_en)
        if not simplified or not simplified.strip():
            simplified = db_row.simplified_en
        if not simplified or not simplified.strip():
            simplified = db_row.section_text[:300] if db_row.section_text else "No text available"

        severity = law.get("severity", db_row.severity or "medium")

        law_results.append({
            "section_id": section_id,
            "act_name": db_row.act_name,
            "section_number": db_row.section_number,
            "section_title": db_row.section_title,
            "original_text": db_row.section_text,
            "simplified": simplified,
            "severity": severity,
            "punishment": db_row.punishment or "Not specified",
            "filing_link": db_row.filing_link,
            "relevance_score": round(float(law.get("relevance_score", db_row.score)), 2),
        })

    # If language is not English, batch translate act names, titles, and punishments
    if language != "en" and law_results:
        try:
            lang_name = "Tamil" if language == "ta" else "Hindi"
            from app.services.generate_service import _call_llm_with_fallback
            
            translation_prompt = f"""Translate these legal metadata fields into {lang_name}.
Return ONLY a valid JSON array of objects with translated 'act_name', 'section_title', and 'punishment'.
Keep the exact same array order. Do not translate English legal codes like 'IPC' or 'CrPC' - keep them as is or transliterate."""
            
            payload = [
                {"act_name": l["act_name"], "section_title": l["section_title"], "punishment": l["punishment"]}
                for l in law_results
            ]
            
            translated_data = await _call_llm_with_fallback(
                translation_prompt,
                json.dumps(payload),
                f"Batch translate law metadata to {lang_name}"
            )
            
            if isinstance(translated_data, list) and len(translated_data) == len(law_results):
                for i, translated in enumerate(translated_data):
                    law_results[i]["act_name"] = translated.get("act_name", law_results[i]["act_name"])
                    law_results[i]["section_title"] = translated.get("section_title", law_results[i]["section_title"])
                    law_results[i]["punishment"] = translated.get("punishment", law_results[i]["punishment"])
        except Exception as e:
            logger.error(f"Failed to translate law metadata: {e}")

    law_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    response_ms = int((time.perf_counter() - start_time) * 1000)

    response = {
        "query_id": query_id,
        "detected_language": detected_lang,
        "ai_summary": gpt_response.get('ai_summary', '') if gpt_response else '',
        "laws": law_results,
        "response_ms": response_ms,
        "source": "Database Search (Tier 1)",
    }

    # Add translated disclaimer
    if language == "ta":
        response["ai_summary"] += "\n\n⚠️ சட்ட பொறுப்புத்துறப்பு: இந்தத் தகவல் பொதுவான குறிப்புக்காக மட்டுமே, இது சட்ட ஆலோசனை அல்ல. தயவுசெய்து தகுதியான வழக்கறிஞரை அணுகவும்."
    elif language == "hi":
        response["ai_summary"] += "\n\n⚠️ कानूनी अस्वीकरण: यह जानकारी केवल सामान्य संदर्भ के लिए है और कानूनी सलाह नहीं है। कृपया किसी योग्य वकील से सलाह लें।"
    else:
        response["ai_summary"] += (
            f"\n\n⚠️ LEGAL DISCLAIMER: This information is for general reference only and is NOT legal advice. "
            f"The simplified explanations may not capture all legal nuances. "
            f"Always consult a qualified legal professional for advice specific to your situation."
        )

    # Cache and log
    await cache_service.set(cache_key, response)
    asyncio.create_task(_log_query(None, issue_en, detected_lang, len(law_results), response_ms))
    
    logger.info(f"[{query_id}] Completed in {response_ms}ms with {len(law_results)} laws")
    return response


async def _process_web_results(
    web_laws, query_id, issue_en, detected_lang, language, start_time, cache_key
):
    """Process and return Tier 2 (web crawl) results."""
    response = {
        "query_id": query_id,
        "detected_language": detected_lang,
        "ai_summary": (
            "⚠️ WEB CRAWL RESULTS: Database search had low confidence, so we searched official legal sources. "
            "Results below are from government legal databases.\n\n"
            "DISCLAIMER: This information is for general reference only. "
            "Always consult a qualified legal professional."
        ),
        "laws": web_laws[:8],  # Limit to 8 results
        "response_ms": int((time.perf_counter() - start_time) * 1000),
        "source": "Web Crawl (Tier 2)",
    }
    
    await cache_service.set(cache_key, response)
    return response


async def _crawl_indiacode(query: str, query_id: str):
    """Crawl indiacode.nic.in and api.indiankanoon.org for real-time law sections.
    
    Returns list of laws found from:
    1. indiacode.nic.in - Official government law portal
    2. api.indiankanoon.org - Indian legal judgments database
    
    Returns list of laws or empty list if crawl fails.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        laws_found = []
        
        # ── Strategy 1: Query Indian Kanoon public HTML search (no API key) ──
        try:
            logger.info(f"[{query_id}] Querying indiankanoon.org for: {query}")

            search_url = "https://indiankanoon.org/docfragment/"
            params = {
                "formInput": query,
                "pagenum": 1,
            }

            response = requests.get(
                search_url,
                params=params,
                timeout=8,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            docs = soup.select("div.result")

            for doc in docs[:5]:
                try:
                    title_el = doc.select_one("a")
                    snippet_el = doc.select_one("div.snippet")
                    title = title_el.get_text(" ", strip=True) if title_el else "Indian Kanoon result"
                    snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
                    href = title_el.get("href", "") if title_el else ""

                    law_section = {
                        "section_id": f"IK-{hashlib.md5((title + href).encode()).hexdigest()[:12]}",
                        "section_title": title[:100],
                        "section_text": snippet[:500] if snippet else f"Found on indiankanoon.org: {title}",
                        "simplified_en": title[:200],
                        "act_name": "Case Law - Indian Kanoon",
                        "severity": "medium",
                        "punishment": "Refer to full judgment",
                        "relevance_score": 0.68,
                        "source": "indiankanoon.org"
                    }
                    laws_found.append(law_section)
                    logger.info(f"[{query_id}] Found from IndianKanoon: {law_section['section_title'][:50]}")

                except Exception as e:
                    logger.warning(f"[{query_id}] Error parsing IndianKanoon result: {e}")
                    continue

        except Exception as e:
            logger.warning(f"[{query_id}] IndianKanoon query failed: {e}")
        
        # ── Strategy 2: Query indiacode.nic.in via simple HTTP search ──
        try:
            logger.info(f"[{query_id}] Querying indiacode.nic.in for: {query}")
            
            # Construct search URL
            search_url = "https://www.indiacode.nic.in/handle/123456789/1362"
            
            response = requests.get(
                search_url,
                params={"query": query},
                timeout=8,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse search results
            result_links = soup.select("a[href*='handle/123456789/'], a[href*='bitstream/']")[:5]
            
            for link in result_links:
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if title and href:
                        law_section = {
                            "section_id": f"IC-{href.split('/')[-1][:20]}",
                            "section_title": title[:100],
                            "section_text": f"Found on indiacode.nic.in: {title}",
                            "simplified_en": title[:100],
                            "act_name": "Indian Law - IndiaCode",
                            "severity": "high",
                            "punishment": "Refer to official law portal",
                            "relevance_score": 0.72,
                            "source": "indiacode.nic.in"
                        }
                        laws_found.append(law_section)
                        logger.info(f"[{query_id}] Found from IndiaCode: {title[:50]}")
                        
                except Exception as e:
                    logger.warning(f"[{query_id}] Error parsing IndiaCode result: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"[{query_id}] IndiaCode query failed: {e}")
        
        if laws_found:
            logger.info(f"[{query_id}] Web crawl found {len(laws_found)} laws")
        else:
            logger.info(f"[{query_id}] Web crawl found no laws for: {query}")
            
        return laws_found
        
    except Exception as e:
        logger.error(f"[{query_id}] Web crawl critical error: {e}")
        return []


def _build_rag_context(rows: list, issue_en: str) -> str:
    """Build the context string for GPT-4o from retrieved law sections.

    Args:
        rows: Database rows from vector search.
        issue_en: The user's problem in English.

    Returns:
        Formatted context string for the LLM.
    """
    context_parts = [f"CITIZEN'S PROBLEM:\n{issue_en}\n\nRETRIEVED LAW SECTIONS:\n"]

    for i, row in enumerate(rows, 1):
        context_parts.append(
            f"--- Section {i} ---\n"
            f"Section ID: {row.section_id}\n"
            f"Act: {row.act_name}\n"
            f"Section: {row.section_number} — {row.section_title}\n"
            f"Simplified: {row.simplified_en}\n"
            f"Punishment: {row.punishment}\n"
            f"Original: {row.section_text[:500]}\n"
            f"Similarity Score: {float(row.score):.3f}\n"
        )

    return "\n".join(context_parts)


async def _log_query(
    db: Optional[AsyncSession],
    query_text: str,
    language: str,
    results_count: int,
    response_ms: int,
) -> None:
    """Log the query to the query_logs table (fire-and-forget)."""
    try:
            if db is None:
                async with async_session_factory() as session:
                    await session.execute(
                        text("""
                            INSERT INTO query_logs (query_text, language, results_count, response_ms)
                            VALUES (:query_text, :language, :results_count, :response_ms)
                        """),
                        {
                            "query_text": query_text,
                            "language": language,
                            "results_count": results_count,
                            "response_ms": response_ms,
                        },
                    )
                    await session.commit()
            else:
                await db.execute(
                    text("""
                        INSERT INTO query_logs (query_text, language, results_count, response_ms)
                        VALUES (:query_text, :language, :results_count, :response_ms)
                    """),
                    {
                        "query_text": query_text,
                        "language": language,
                        "results_count": results_count,
                        "response_ms": response_ms,
                    },
                )
                await db.commit()
    except Exception as e:
        logger.warning(f"Failed to log query: {e}")
