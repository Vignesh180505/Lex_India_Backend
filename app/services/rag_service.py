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
from app.services.generate_service import generate_query_response, general_legal_answer, get_openai_client, _call_llm_with_fallback
from app.schemas.query import QueryResponse, LawResult

logger = logging.getLogger("lexindia.services.rag")


NORMALISE_PROMPT = """
You are a legal query parser for Indian law.
Given a citizen's complaint in plain language, extract:
1. The core legal issues (max 3, in plain legal terms referencing relevant IPC/Act sections where possible)
2. A normalised search query combining all issues using precise Indian legal terminology

Examples:
Input:  "bus conductor did not give me change and spoke rudely"
Output: {
  "issues": ["overcharging by transport conductor", "verbal abuse by public servant", "consumer service deficiency"],
  "normalised_query": "transport conductor overcharging passenger verbal abuse deficiency of service IPC 294"
}

Input:  "my landlord won't return deposit"
Output: {
  "issues": ["wrongful retention of security deposit"],
  "normalised_query": "landlord refusing to return security deposit breach of contract criminal breach of trust IPC 406"
}

Input: "someone is blackmailing me"
Output: {
  "issues": ["criminal intimidation blackmailing", "extortion by threat"],
  "normalised_query": "blackmailing criminal intimidation IPC 503 506 extortion putting person in fear of injury IPC 383 384 threat to damage reputation"
}

Input: "my husband is beating me"
Output: {
  "issues": ["domestic violence", "cruelty by husband", "physical assault"],
  "normalised_query": "domestic violence Protection of Women from Domestic Violence Act cruelty by husband IPC 498A assault causing hurt IPC 323"
}

Input: "my boss is harassing me at workplace"
Output: {
  "issues": ["sexual harassment at workplace", "workplace misconduct"],
  "normalised_query": "sexual harassment workplace POSH Act IPC 354A hostile work environment employer employee misconduct"
}

Input: "someone hacked my account and is threatening to post my photos"
Output: {
  "issues": ["cyber crime", "online blackmailing", "criminal intimidation anonymous"],
  "normalised_query": "cyber crime IT Act hacking account criminal intimidation IPC 503 506 507 online blackmail photo threat reputation damage"
}

Input: "met with an accident and other driver is not paying for damages"
Output: {
  "issues": ["motor vehicle accident compensation", "negligent driving"],
  "normalised_query": "motor vehicle accident negligent rash driving IPC 279 304A compensation Motor Vehicles Act damages"
}

Input: "company cheated me and took money but never delivered product"
Output: {
  "issues": ["cheating and fraud", "consumer complaint", "breach of contract"],
  "normalised_query": "cheating dishonestly inducing delivery IPC 420 consumer protection deficiency of service breach of contract"
}

Return ONLY valid JSON with keys "issues" (array of strings) and "normalised_query" (string). No extra text.
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

    if re.search(r"landlord|owner|deposit|security|rent|tenant|evict", q):
        issues.append("property and tenancy dispute")
        tokens.extend(["landlord refusing security deposit", "breach of contract", "criminal breach of trust", "tenant eviction"])

    if re.search(r"salary|wage|employer|not paid|unpaid|months|fire|dismiss", q):
        issues.append("employment and labour dispute")
        tokens.extend(["employer non payment salary", "delayed wages", "labour law wage dues", "wrongful termination"])

    if re.search(r"service|deficien|consumer|product|defective|warranty|mrp", q):
        issues.append("consumer service deficiency")
        tokens.extend(["deficiency of service", "consumer protection", "unfair trade practice"])

    if re.search(r"tree|cut|environment|pollution|smoke|noise|factory", q):
        issues.append("environmental protection and nuisance")
        tokens.extend(["tree preservation", "felling of trees", "environmental pollution", "public nuisance"])

    if re.search(r"divorce|dowry|husband|wife|marriage|maintenance|alimony", q):
        issues.append("matrimonial and family dispute")
        tokens.extend(["divorce", "dowry harassment", "domestic violence", "maintenance"])

    if re.search(r"stole|theft|snatch|cheat|fraud|scam|hack", q):
        issues.append("criminal offence property and cheating")
        tokens.extend(["theft", "cheating", "fraud", "cyber crime", "criminal breach"])

    if re.search(r"blackmail|extort|threat|intimidat|ransom|coerce|menace|criminal intimidation", q):
        issues.append("blackmailing extortion and criminal intimidation")
        tokens.extend([
            "extortion IPC 383 384",
            "criminal intimidation IPC 503 506",
            "threatening to damage reputation",
            "putting person in fear of injury",
            "blackmail demand money threat",
            "anonymous threat intimidation",
        ])

    if re.search(r"cyber|online threat|whatsapp|message threat|social media blackmail|photo blackmail|video blackmail", q):
        issues.append("cyber blackmail and online criminal intimidation")
        tokens.extend([
            "criminal intimidation IPC 503 506 507",
            "cyber crime online extortion",
            "anonymous communication threat",
            "IT Act blackmail online",
        ])

    if not issues:
        issues = ["general legal grievance"]
        tokens = [issue_en]

    # Preserve original meaning while adding legal anchors
    normalised_query = " ".join(dict.fromkeys([issue_en] + tokens))
    return {"issues": issues[:3], "normalised_query": normalised_query}


async def _normalise_query_for_embedding(issue_en: str, query_id: str) -> dict[str, Any]:
    """Normalize any plain-language complaint into precise Indian legal search terms.

    Uses the configured LLM provider (OpenAI → Gemini → Grok) to understand
    the query and expand it to proper legal terminology before vector search.
    Falls back to the rule-based heuristic if all LLM providers fail.

    This is the key step that ensures ANY query — blackmailing, dowry harassment,
    property dispute, consumer complaint, etc. — maps to the correct IPC/Act sections.
    """
    # ── Tier 1: LLM-based normalisation (provider-agnostic) ──────────────
    try:
        parsed = await _call_llm_with_fallback(
            system_prompt=NORMALISE_PROMPT,
            user_message=issue_en,
            task_name=f"QueryNormalise[{query_id[:8]}]",
            response_format="json_object",
        )

        if parsed and isinstance(parsed, dict):
            search_query = (parsed.get("normalised_query") or issue_en).strip()
            issues = parsed.get("issues") or []
            if search_query and issues:
                logger.info(f"[{query_id}] Query normalised via LLM: {issues}")
                return {"issues": issues, "normalised_query": search_query}

    except Exception as e:
        logger.warning(f"[{query_id}] LLM normalisation failed: {e}")

    # ── Tier 2: Rule-based heuristic fallback ─────────────────────────────
    fallback = _heuristic_normalise_query(issue_en)
    logger.info(f"[{query_id}] Query normalised via heuristic fallback: {fallback.get('issues', [])}")
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


def generate_fallback_summary(laws: list, query: str) -> str:
    if not laws:
        return "No relevant laws found for your query."
    
    top_laws = laws[:3]
    summary_parts = []
    
    summary_parts.append(
        f"Based on your query about '{query}', "
        f"the following laws may apply:\n"
    )
    
    for i, law in enumerate(top_laws, 1):
        def get_val(obj, key, default=""):
            if hasattr(obj, key):
                return getattr(obj, key) or default
            if isinstance(obj, dict):
                return obj.get(key) or default
            return default
            
        act_name = get_val(law, "act_name")
        section_number = get_val(law, "section_number")
        section_title = get_val(law, "section_title")
        simplified_en = get_val(law, "simplified_en") or get_val(law, "simplified")
        
        summary_parts.append(
            f"{i}. **{act_name} Section {section_number}** — {section_title}\n"
            f"   {simplified_en or section_title}\n"
        )
    
    summary_parts.append(
        "\n⚠️ This is an automated summary. "
        "Please consult a qualified lawyer for legal advice."
    )
    
    return "\n".join(summary_parts)


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
        if db.is_active:
            await db.rollback()
        raise e

    # Calculate confidence from DB results
    db_laws = [
        {
            "section_id": row.section_id,
            "act_name": row.act_name,
            "act_code": row.act_code,
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
        logger.warning(f"[{query_id}] GPT-4o failed — returning fallback summary")
        gpt_response = {
            "ai_summary": generate_fallback_summary(db_laws, issue_en),
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
            "act_code": db_row.act_code,
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



_FALLBACK_LAW_METADATA = {
    "copyright": {
        "act_name": {
            "en": "The Copyright Act, 1957",
            "hi": "कॉपीराइट अधिनियम, 1957",
            "ta": "பதிப்புரிமை சட்டம், 1957"
        },
        "section_number": "63",
        "section_title": {
            "en": "Offence of infringement of copyright or other rights",
            "hi": "कॉपीराइट या अन्य अधिकारों के उल्लंघन का अपराध",
            "ta": "பதிப்புரிமை அல்லது பிற உரிமைகளை மீறும் குற்றம்"
        },
        "simplified": {
            "en": "This section makes the knowing infringement of copyright (such as unauthorized copying or distribution of software source code) a criminal offense in India.",
            "hi": "यह धारा भारत में कॉपीराइट के जानबूझकर किए गए उल्लंघन (जैसे सॉफ्टवेयर सोर्स कोड का अनधिकृत प्रतिलिपि बनाना या वितरण) को एक आपराधिक अपराध बनाती है।",
            "ta": "இந்த பிரிவு இந்தியாவில் பதிப்புரிமையை (மென்பொருள் மூலக் குறியீட்டை அங்கீகரிக்கப்படாத நகலெடுப்பது அல்லது விநியோகிப்பது போன்ற) வேண்டுமென்றே மீறுவதை குற்றவியல் குற்றமாகாக்குகிறது."
        },
        "punishment": {
            "en": "Imprisonment for a term not less than six months but which may extend to three years and with fine not less than fifty thousand rupees but which may extend to two lakh rupees.",
            "hi": "छह महीने से कम नहीं लेकिन तीन साल तक की कैद और पचास हजार रुपये से कम नहीं लेकिन दो लाख रुपये तक का जुर्माना।",
            "ta": "ஆறு மாதங்களுக்குக் குறையாத ஆனால் மூன்று ஆண்டுகள் வரை நீட்டிக்கக்கூடிய சிறைத்தண்டனை மற்றும் ஐம்பதாயிரம் ரூபாய்க்கு குறையாத ஆனால் இரண்டு லட்சம் ரூபாய் வரை நீட்டிக்கக்கூடிய அபராதம்."
        },
        "severity": "high"
    },
    "child labour": {
        "act_name": {
            "en": "Child and Adolescent Labour (Prohibition and Regulation) Act, 1986",
            "hi": "बाल और किशोर श्रम (निषेध और विनियमन) अधिनियम, 1986",
            "ta": "குழந்தை மற்றும் இளம் பருவத்தினர் தொழிலாளர் (தடை மற்றும் ஒழுங்குமுறை) சட்டம், 1986"
        },
        "section_number": "3",
        "section_title": {
            "en": "Prohibition of employment of children",
            "hi": "बच्चों के रोजगार का निषेध",
            "ta": "குழந்தைகளை வேலைக்கு அமர்த்துவது தடை"
        },
        "simplified": {
            "en": "This section prohibits the employment of children below 14 years in all occupations and processes, except in family-run businesses without affecting their education.",
            "hi": "यह धारा 14 वर्ष से कम उम्र के बच्चों को सभी व्यवसायों और प्रक्रियाओं में काम पर रखने से रोकती है, सिवाय उनके पारिवारिक व्यवसायों के, बिना उनकी शिक्षा को प्रभावित किए।",
            "ta": "இந்த பிரிவு 14 வயதிற்குட்பட்ட குழந்தைகளை அனைத்து தொழில்களிலும் வேலைகளில் அமர்த்துவதை தடை செய்கிறது, குடும்பத் தொழில்களைத் தவிர, அவர்களின் கல்வியைப் பாதிக்காமல்."
        },
        "punishment": {
            "en": "Imprisonment for a term not less than six months but which may extend to two years, or fine from twenty thousand to fifty thousand rupees, or both.",
            "hi": "छह महीने से कम नहीं लेकिन दो साल तक की कैद, या बीस हजार से पचास हजार रुपये तक का जुर्माना, या दोनों।",
            "ta": "ஆறு மாதங்களுக்குக் குறையாத ஆனால் இரண்டு ஆண்டுகள் வரை நீட்டிக்கக்கூடிய சிறைத்தண்டனை, அல்லது இருபதாயிரம் முதல் ஐம்பதாயிரம் ரூபாய் வரை அபராதம், அல்லது இரண்டும்."
        },
        "severity": "high"
    },
    "cheating": {
        "act_name": {
            "en": "Indian Penal Code, 1860",
            "hi": "भारतीय दंड संहिता, 1860",
            "ta": "भारतीय दंडணைச் சட்டம், 1860"
        },
        "section_number": "420",
        "section_title": {
            "en": "Cheating and dishonestly inducing delivery of property",
            "hi": "धोखाधड़ी करना और बेईमानी से संपत्ति के वितरण के लिए प्रेरित करना",
            "ta": "ஏமாற்றுதல் மற்றும் சொத்துக்களை ஒப்படைக்க நேர்மையற்ற முறையில் தூண்டுதல்"
        },
        "simplified": {
            "en": "This section applies when someone cheats another person and dishonestly induces them to deliver any property or make/alter a valuable security.",
            "hi": "यह धारा तब लागू होती है जब कोई किसी को धोखा देता है और बेईमानी से उसे कोई संपत्ति देने या मूल्यवान प्रतिभूति बनाने/बदलने के लिए प्रेरित करता है।",
            "ta": "ஒருவர் மற்றொருவரை ஏமாற்றி, ஏதேனும் சொத்தை ஒப்படைக்க அல்லது மதிப்புமிக்க பத்திரத்தை உருவாக்க/மாற்ற நேர்மையற்ற முறையில் தூண்டும்போது இந்தப் பிரிவு பொருந்தும்."
        },
        "punishment": {
            "en": "Imprisonment for a term which may extend to seven years, and shall also be liable to fine.",
            "hi": "कैद जिसकी अवधि सात वर्ष तक हो सकती है, और जुर्माने के लिए भी उत्तरदायी होगा।",
            "ta": "ஏழு ஆண்டுகள் வரை நீட்டிக்கக்கூடிய சிறைத்தண்டனை, மேலும் அபராதமும் விதிக்கப்படும்."
        },
        "severity": "high"
    },
    "theft": {
        "act_name": {
            "en": "Indian Penal Code, 1860",
            "hi": "भारतीय दंड संहिता, 1860",
            "ta": "भारतीय தண்டணைச் சட்டம், 1860"
        },
        "section_number": "379",
        "section_title": {
            "en": "Punishment for theft",
            "hi": "चोरी के लिए सजा",
            "ta": "திருட்டிற்கான தண்டனை"
        },
        "simplified": {
            "en": "This section defines the punishment for committing theft, which is moving movable property out of the possession of any person without consent.",
            "hi": "यह धारा चोरी करने की सजा को परिभाषित करती है, जो सहमति के बिना किसी भी व्यक्ति के कब्जे से चल संपत्ति को हटाना है।",
            "ta": "அனுமதியின்றி எந்தவொரு நபரின் வசம் இருந்தும் அசையும் சொத்தை திருடுவது ஆகும், அதற்கான தண்டனையை இந்தப் பிரிவு வரையறுக்கிறது."
        },
        "punishment": {
            "en": "Imprisonment for a term which may extend to three years, or with fine, or with both.",
            "hi": "कैद जिसकी अवधि तीन वर्ष तक हो सकती है, या जुर्माना, या दोनों।",
            "ta": "மூன்று ஆண்டுகள் வரை நீட்டிக்கக்கூடிய சிறைத்தண்டனை, அல்லது அபராதம், அல்லது இரண்டும்."
        },
        "severity": "high"
    },
    "consumer": {
        "act_name": {
            "en": "Consumer Protection Act, 2019",
            "hi": "उपभोक्ता संरक्षण अधिनियम, 2019",
            "ta": "நுகர்வோர் பாதுகாப்புச் சட்டம், 2019"
        },
        "section_number": "35",
        "section_title": {
            "en": "Complaint before District Commission",
            "hi": "जिला आयोग के समक्ष शिकायत",
            "ta": "மாவட்ட ஆணையத்திடம் புகார்"
        },
        "simplified": {
            "en": "This section allows a consumer or registered consumer association to file a complaint against defective goods or deficient services before the District Commission.",
            "hi": "यह धारा एक उपभोक्ता या पंजीकृत उपभोक्ता संघ को दोषपूर्ण वस्तुओं या कमी वाली सेवाओं के खिलाफ जिला आयोग के समक्ष शिकायत दर्ज करने की अनुमति देती है।",
            "ta": "குறைபாடுள்ள பொருட்கள் அல்லது குறைபாடான சேவைகளுக்கு எதிராக மாவட்ட நுகர்வோர் ஆணையத்தில் நுகர்வோர் அல்லது பதிவுசெய்யப்பட்ட நுகர்வோர் சங்கம் புகார் அளிக்க இந்தப் பிரிவு அனுமதிக்கிறது."
        },
        "punishment": {
            "en": "The Commission can direct the seller to remove defects, replace goods, refund the price, or pay compensation for loss/injury.",
            "hi": "आयोग विक्रेता को दोषों को दूर करने, सामान बदलने, कीमत वापस करने, या नुकसान/चोट के लिए मुआवजे का भुगतान करने का निर्देश दे सकता है।",
            "ta": "குறைபாடுகளை நீக்கவோ, பொருட்களை மாற்றவோ, விலையைத் திருப்பித் தரவோ அல்லது இழப்பு/காயத்திற்கு இழப்பீடு வழங்கவோ ஆணையம் விற்பனையாளருக்கு உத்தரவிடலாம்."
        },
        "severity": "medium"
    }
}

def _local_heuristic_simplify(query: str) -> str:
    q = query.lower().strip()
    
    # Check for domain terms
    if "copyright" in q:
        return "copyright"
    if "trademark" in q:
        return "trademark"
    if "patent" in q:
        return "patent"
    if "child" in q and ("labour" in q or "labor" in q or "employ" in q or "work" in q):
        return "child labour"
    if "cheating" in q or "cheat" in q or "fraud" in q or "scam" in q:
        return "cheating"
    if "theft" in q or "stole" in q or "stolen" in q or "thief" in q or "rob" in q:
        return "theft"
    if "landlord" in q or "tenant" in q or "rent" in q or "deposit" in q or "evict" in q:
        return "rent"
    if "accident" in q or "car" in q or "driver" in q or "hit" in q or "vehicle" in q or "motor" in q:
        return "motor vehicles"
    if "defective" in q or "product" in q or "refund" in q or "warranty" in q or "consumer" in q or "mrp" in q:
        return "consumer"
    if "tree" in q or "forest" in q or "felling" in q or "cut" in q:
        return "forest"
    if "pollution" in q or "environment" in q or "smoke" in q:
        return "environment"
    if "dowry" in q or "harass" in q or "husband" in q or "wife" in q or "marriage" in q or "divorce" in q:
        if "dowry" in q:
            return "dowry"
        return "marriage"
    if "salary" in q or "wage" in q or "employer" in q or "employee" in q or "unpaid" in q or "wages" in q:
        return "wages"

    # Fallback stop words cleaning
    stop_words = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
        "he", "him", "his", "she", "her", "it", "its", "they", "them", "their", "what", 
        "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", 
        "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", 
        "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", 
        "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", 
        "through", "during", "before", "after", "above", "below", "to", "from", "up", 
        "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", 
        "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", 
        "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", 
        "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", 
        "just", "don", "should", "now", "want", "file", "case", "court", "someone", 
        "something", "please", "help", "need", "about", "legal", "issue", "problem"
    }
    
    words = [w for w in re.findall(r'\b\w+\b', q) if w not in stop_words]
    if words:
        return " ".join(words[:2])
    return query[:30]


async def _process_web_results(
    web_laws, query_id, issue_en, detected_lang, language, start_time, cache_key
):
    """Process and return Tier 2 (web crawl) results with LLM metadata enrichment and summary."""
    lang_name = "English"
    if language == "ta":
        lang_name = "Tamil"
    elif language == "hi":
        lang_name = "Hindi"

    # Normalize and enrich crawled laws using the LLM
    if web_laws:
        try:
            from app.services.generate_service import _call_llm_with_fallback

            enrichment_prompt = f"""You are an expert legal metadata generator for Indian Law.
Given the citizen's legal issue and a list of web-crawled search results (which might contain Act names or partial titles), enrich and complete the legal details for each search result.

User issue: "{issue_en}"

For each search result in the input list, return a JSON object with:
1. "act_name": The official name of the Act in {lang_name} (e.g., "भारतीय दंड संहिता, 1860" or "Indian Penal Code, 1860").
2. "section_number": The specific section number of the law (e.g. "378", "138", "420") that is most relevant to the user's issue under this Act, or "—" if it's the general act.
3. "section_title": The specific section title in {lang_name} (e.g. "चोरी", "Theft", "Dishonour of cheque").
4. "simplified": A clear, 1-2 sentence simplified description in {lang_name} explaining how this law applies to the user's issue.
5. "punishment": The legal penalty/punishment in {lang_name} for violating this law (e.g. "3 साल तक की कैद, या जुर्माना, या दोनों"). If none or not specified, write "Consult official portal/lawyer" in {lang_name}.
6. "severity": One of "low", "medium", or "high".

Respond ONLY with a JSON object containing a "laws" key, whose value is an array of objects matching the input array order. Do not include markdown code block formatting.

Example output:
{{
  "laws": [
    {{
      "act_name": "Indian Penal Code, 1860",
      "section_number": "379",
      "section_title": "Punishment for theft",
      "simplified": "This section defines the punishment for committing theft of someone else's property.",
      "punishment": "Imprisonment up to 3 years, or fine, or both.",
      "severity": "high"
    }}
  ]
}}
"""

            payload = {
                "results": [
                    {
                        "act_name": l.get("act_name"),
                        "section_title": l.get("section_title"),
                        "snippet": l.get("section_text")
                    }
                    for l in web_laws[:5]
                ]
            }

            enriched_data = await _call_llm_with_fallback(
                enrichment_prompt,
                json.dumps(payload),
                f"Enrich crawled law metadata for {query_id}",
                response_format="json_object"
            )

            if enriched_data and "laws" in enriched_data:
                enriched_list = enriched_data["laws"]
                for i, item in enumerate(enriched_list):
                    if i < len(web_laws):
                        web_laws[i]["act_name"] = item.get("act_name", web_laws[i].get("act_name"))
                        web_laws[i]["section_number"] = item.get("section_number", "—")
                        web_laws[i]["section_title"] = item.get("section_title", web_laws[i].get("section_title"))
                        web_laws[i]["simplified_en"] = item.get("simplified", web_laws[i].get("simplified_en"))
                        web_laws[i]["punishment"] = item.get("punishment", web_laws[i].get("punishment"))
                        web_laws[i]["severity"] = item.get("severity", web_laws[i].get("severity"))
        except Exception as e:
            logger.error(f"Failed to enrich crawled law metadata: {e}")
            
            # Local fallback metadata mapping
            logger.info(f"[{query_id}] Applying local fallback metadata mapping for crawled results")
            q_lower = issue_en.lower()
            lang_code = language if language in {"en", "hi", "ta"} else "en"
            for key, meta in _FALLBACK_LAW_METADATA.items():
                if key in q_lower:
                    for law in web_laws:
                        crawled_act = law.get("act_name", "").lower()
                        fallback_act_en = meta["act_name"]["en"].lower()
                        if fallback_act_en in crawled_act or crawled_act in fallback_act_en:
                            law["act_name"] = meta["act_name"].get(lang_code, meta["act_name"]["en"])
                            law["section_number"] = meta["section_number"]
                            law["section_title"] = meta["section_title"].get(lang_code, meta["section_title"]["en"])
                            law["simplified_en"] = meta["simplified"].get(lang_code, meta["simplified"]["en"])
                            law["punishment"] = meta["punishment"].get(lang_code, meta["punishment"]["en"])
                            law["severity"] = meta["severity"]
                            logger.info(f"[{query_id}] Locally enriched crawled result for '{law['act_name']}' using key '{key}' and language '{lang_code}'")

    # Generate custom legal summary using the LLM
    custom_summary = ""
    try:
        from app.services.generate_service import _call_llm_with_fallback
        summary_prompt = f"""You are LexIndia, an AI legal assistant specialising in Indian law.
Given a citizen's legal issue and the applicable law sections found, write a clear, helpful legal summary.
Citizen's issue: "{issue_en}"
Applicable Laws: {json.dumps(web_laws[:3])}
Output Language: {lang_name}

Write 3-4 plain, comforting sentences in {lang_name} explaining the citizen's legal position, what laws apply, and what their options are. Write for a layperson with no legal background. Do not include markdown code block formatting."""

        ai_summary_res = await _call_llm_with_fallback(
            summary_prompt,
            issue_en,
            f"Generate web results legal summary for {query_id}",
            response_format="text"
        )
        if ai_summary_res:
            custom_summary = ai_summary_res.strip()
    except Exception as e:
        logger.error(f"Failed to generate web results legal summary: {e}")

    # Fallback to standard summary if LLM failed
    if not custom_summary:
        custom_summary = generate_fallback_summary(web_laws, issue_en)

    # Ensure each result has the fields expected by LawResult schema
    normalised_laws = []
    for law in web_laws[:8]:
        normalised_laws.append({
            "section_id": law.get("section_id", ""),
            "act_name": law.get("act_name", "External Legal Source"),
            "act_code": law.get("section_id", "").split("-")[0] if "-" in law.get("section_id", "") else None,
            "section_number": law.get("section_number", "—"),
            "section_title": law.get("section_title", ""),
            "original_text": law.get("section_text", law.get("original_text", "")),
            "simplified": law.get("simplified_en", law.get("simplified", law.get("section_title", ""))),
            "severity": law.get("severity", "medium"),
            "punishment": law.get("punishment", None),
            "filing_link": law.get("filing_link", None),
            "relevance_score": float(law.get("relevance_score", 0.6)),
        })
    
    # Add translated disclaimer
    if language == "ta":
        custom_summary += "\n\n⚠️ சட்ட பொறுப்புத்துறப்பு: இந்தத் தகவல் பொதுவான குறிப்புக்காக மட்டுமே, இது சட்ட ஆலோசனை அல்ல. தயவுசெய்து தகுதியான வழக்கறிஞரை அணுகவும்."
    elif language == "hi":
        custom_summary += "\n\n⚠️ कानूनी अस्वीकरण: यह जानकारी केवल सामान्य संदर्भ के लिए है और कानूनी सलाह नहीं है। कृपया किसी योग्य वकील से सलाह लें।"
    else:
        custom_summary += (
            "\n\n⚠️ LEGAL DISCLAIMER: This information is for general reference only and is NOT legal advice. "
            "Always consult a qualified legal professional."
        )

    response = {
        "query_id": query_id,
        "detected_language": detected_lang,
        "ai_summary": custom_summary,
        "laws": normalised_laws,
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
        
        # Simplify conversational query to 1-3 keyword terms for crawling
        if len(query.split()) > 3:
            simplified_query = None
            try:
                from app.services.generate_service import _call_llm_with_fallback
                keyword_prompt = """You are a legal search keyword extractor.
Given a citizen's conversational legal issue, extract 1 to 3 search keywords suitable for searching a government law database (like IndiaCode) to find the relevant Act.
For example:
Input: "file a case about copyright infringement of software source code" -> Output: "copyright"
Input: "neighbor cut down a tree on my property" -> Output: "tree preservation"
Input: "landlord won't return my deposit" -> Output: "rent control"

Return ONLY the search keyword(s). No quotes, no explanations, no formatting."""
                keywords = await _call_llm_with_fallback(
                    keyword_prompt,
                    query,
                    f"Extract keywords for crawling for {query_id}",
                    response_format="text"
                )
                if keywords and len(keywords.strip()) > 0:
                    simplified_query = keywords.strip().replace('"', '').replace("'", "")
            except Exception as e:
                logger.warning(f"[{query_id}] Failed to simplify crawling query via LLM: {e}")

            if not simplified_query:
                # Local heuristic fallback
                logger.info(f"[{query_id}] Using local heuristic fallback to simplify crawling query")
                simplified_query = _local_heuristic_simplify(query)

            if simplified_query:
                logger.info(f"[{query_id}] Simplified query from '{query}' to '{simplified_query}' for crawling")
                query = simplified_query
                
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
            search_url = "https://www.indiacode.nic.in/handle/123456789/1362/simple-search"
            
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
            
            # Parse search results table
            table = soup.find("table", class_="table")
            if table:
                rows = table.select("tr")
                for row in rows[1:]: # Skip header row
                    try:
                        cells = row.select("td")
                        if len(cells) >= 4:
                            title = cells[2].get_text(strip=True)
                            link_el = cells[3].find("a")
                            href = link_el.get("href", "") if link_el else ""
                            
                            if title and href:
                                law_section = {
                                    "section_id": f"IC-{href.split('/')[-1].split('?')[0][:20]}",
                                    "section_title": title,
                                    "section_text": f"Found on indiacode.nic.in: {title}",
                                    "simplified_en": title,
                                    "act_name": title,
                                    "severity": "high",
                                    "punishment": "Refer to official law portal",
                                    "relevance_score": 0.72,
                                    "source": "indiacode.nic.in",
                                    "filing_link": f"https://www.indiacode.nic.in{href}" if href.startswith("/") else href
                                }
                                laws_found.append(law_section)
                                logger.info(f"[{query_id}] Found from IndiaCode: {title[:50]}")
                                if len(laws_found) >= 5:
                                    break
                    except Exception as e:
                        logger.warning(f"[{query_id}] Error parsing IndiaCode row: {e}")
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
            # Use the provided session but don't commit it here — let the owner commit
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
            # await db.commit() <- REMOVED: Never commit a shared session in a fire-and-forget task
    except Exception as e:
        logger.warning(f"Failed to log query: {e}")
