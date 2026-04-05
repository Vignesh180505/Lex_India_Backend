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
import time
import uuid
from typing import Optional, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services import embed_service, cache_service, translate_service
from app.services.generate_service import generate_query_response, general_legal_answer
from app.services import indiakanoon_service, indiacode_scraper_service
from app.schemas.query import QueryResponse, LawResult

logger = logging.getLogger("lexindia.services.rag")


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
    cache_key = cache_service.make_cache_key(issue_en)
    cached = await cache_service.get(cache_key)
    if cached:
        logger.info(f"[{query_id}] Cache hit — returning cached response")
        cached["query_id"] = query_id
        cached["response_ms"] = int((time.perf_counter() - start_time) * 1000)
        return cached

    # ▰▰▰ TIER 1: Fast Database Search ▰▰▰
    logger.info(f"[{query_id}] ═══ TIER 1: Fast Database Search ═══")
    
    # ── Step 4: Embed the English query ──────────────────────────────
    query_vector = embed_service.embed(issue_en)
    logger.info(f"[{query_id}] Query embedded ({len(query_vector)} dimensions)")

    try:
        results = await db.execute(
            text("""
                SELECT
                    section_id, act_name, act_code, section_number, section_title,
                    section_text, simplified_en, simplified_ta, simplified_hi,
                    severity, filing_link, punishment,
                    1 - (embedding <=> :qvec::vector) AS score
                FROM laws
                WHERE embedding IS NOT NULL
                  AND 1 - (embedding <=> :qvec::vector) > :threshold
                ORDER BY embedding <=> :qvec::vector
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
    if db_confidence > 0.70:
        logger.info(f"[{query_id}] ✅ TIER 1 SUCCESS: Confidence {db_confidence:.2f} > 0.70 threshold")
        logger.info(f"[{query_id}] Using database results directly")
        
        # Proceed with Tier 1 results (same as original flow)
        response = await _process_tier1_results(
            db_laws, rows, query_id, issue_en, detected_lang, language, start_time, cache_key
        )
        return response
    
    # ▰▰▰ TIER 2: Web Crawl Fallback ▰▰▰
    if 0.50 <= db_confidence <= 0.70:
        logger.info(f"[{query_id}] ═══ TIER 2: Web Crawl Fallback ═══")
        logger.warning(f"[{query_id}] Low DB confidence ({db_confidence:.2f}) — attempting web crawl")
        
        # Try to crawl indiacode.nic.in for better results
        web_laws = await _crawl_indiacode(issue_en, query_id)
        
        if web_laws and len(web_laws) > 0:
            logger.info(f"[{query_id}] ✅ TIER 2 SUCCESS: Found {len(web_laws)} laws from web crawl")
            response = await _process_web_results(
                web_laws, query_id, issue_en, detected_lang, language, start_time, cache_key
            )
            return response
        else:
            logger.warning(f"[{query_id}] Web crawl returned no results, falling back to LLM")
    
    # ▰▰▰ TIER 3: LLM Fallback ▰▰▰
    logger.info(f"[{query_id}] ═══ TIER 3: LLM Fallback ═══")
    logger.warning(f"[{query_id}] No good DB or web results (confidence: {db_confidence:.2f}) — using GPT-4o to generate answer")
    
    try:
        llm_answer = await general_legal_answer(issue_en, issue)
        
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
            _log_query(db, issue, detected_lang, 0, response["response_ms"])
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

    # Call GPT-4o for AI summary + re-ranking
    try:
        logger.info(f"[{query_id}] Calling GPT-4o for summary...")
        gpt_response = await generate_query_response(context)
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

    law_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    response_ms = int((time.perf_counter() - start_time) * 1000)

    response = {
        "query_id": query_id,
        "detected_language": detected_lang,
        "ai_summary": (
            f"{gpt_response.get('ai_summary', '')}\n\n"
            f"⚠️ LEGAL DISCLAIMER: This information is for general reference only and is NOT legal advice. "
            f"The simplified explanations may not capture all legal nuances. "
            f"Always consult a qualified legal professional for advice specific to your situation."
        ),
        "laws": law_results,
        "response_ms": response_ms,
        "source": "Database Search (Tier 1)",
    }

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
    """Real web crawl using Indian Kanoon API + Indiacode scraper.
    
    Tier 2 fallback: When database confidence is medium (50-70%), 
    try to find laws from official government sources.
    
    Uses:
    1. api.indiankanoon.org - For case law and judicial precedents
    2. indiacode.nic.in scraper - For official law text (with Playwright)
    
    Returns list of laws found on official websites or empty list if crawl fails.
    """
    try:
        logger.info(f"[{query_id}] === TIER 2: Web Crawl Starting ===")
        web_results = []
        
        # ── Step 1: Search Indian Kanoon API (Fast, no browser needed) ──
        logger.info(f"[{query_id}] Searching Indian Kanoon API...")
        kanoon_results = await indiakanoon_service.search_indiakanoon(query, limit=3)
        
        if kanoon_results:
            logger.info(f"[{query_id}] Indian Kanoon found {len(kanoon_results)} results")
            for result in kanoon_results:
                web_results.append({
                    "title": result.get("title"),
                    "summary": result.get("summary"),
                    "url": result.get("url"),
                    "source": "Indian Kanoon (Case Law)",
                    "relevance_score": min(result.get("relevance", 0) / 100, 1.0),  # Normalize score
                    "severity": "high" if any(keyword in result.get("title", "").lower() 
                                             for keyword in ["criminal", "punishment", "imprisonment"]) else "medium"
                })
        else:
            logger.info(f"[{query_id}] Indian Kanoon returned no results")
        
        # ── Step 2: Search Indiacode.nic.in (Slower, uses Playwright scraper) ──
        # Only attempt if Playwright is available and we need more results
        if len(web_results) < 3:
            logger.info(f"[{query_id}] Attempting Indiacode scrape...")
            try:
                indiacode_results = await indiacode_scraper_service.search_indiacode(query, limit=3)
                
                if indiacode_results:
                    logger.info(f"[{query_id}] Indiacode found {len(indiacode_results)} results")
                    for result in indiacode_results:
                        web_results.append({
                            "title": result.get("title"),
                            "summary": result.get("summary"),
                            "url": result.get("url"),
                            "source": "Indiacode.nic.in (Official)",
                            "relevance_score": 0.75,  # Official source
                            "severity": "high"
                        })
                else:
                    logger.info(f"[{query_id}] Indiacode returned no results (Playwright may not be installed)")
            except ImportError:
                logger.warning(f"[{query_id}] Playwright not installed - skipping Indiacode scrape")
                logger.info("To enable: pip install playwright && playwright install chromium")
            except Exception as e:
                logger.error(f"[{query_id}] Indiacode scrape failed: {e}")
        
        logger.info(f"[{query_id}] Web crawl complete: {len(web_results)} total results")
        return web_results
        
    except Exception as e:
        logger.error(f"[{query_id}] Web crawl failed: {e}")
        return []


    # Handle no results - shouldn't reach here due to Tier 2/3 fallbacks
    if not rows:
        logger.warning(f"[{query_id}] No results from any tier")
        response = {
            "query_id": query_id,
            "detected_language": detected_lang,
            "ai_summary": "No applicable laws found. Please try rephrasing your question.",
            "laws": [],
            "response_ms": int((time.perf_counter() - start_time) * 1000),
        }
        return response

    # ── Step 6: Build LLM context ────────────────────────────────────
    context = _build_rag_context(rows, issue_en)

    # ── Step 7: Call GPT-4o for AI summary + re-ranking ──────────────
    try:
        logger.info(f"[{query_id}] Calling GPT-4o for summary...")
        gpt_response = await generate_query_response(context)
        logger.info(f"[{query_id}] GPT-4o response received")
    except Exception as e:
        logger.error(f"[{query_id}] GPT-4o call failed: {e}")
        gpt_response = None

    if not gpt_response:
        # Fallback: return raw vector search results without AI summary
        logger.warning(f"[{query_id}] GPT-4o failed — returning raw vector search results with degraded confidence")
        gpt_response = {
            "ai_summary": (
                "⚠️ AI SUMMARY UNAVAILABLE: The AI ranking system encountered an error. "
                "Here are the raw vector search results sorted by similarity confidence.\n\n"
                "DISCLAIMER: This is direct database retrieval without AI re-ranking. "
                "Consult a legal professional for advice specific to your situation."
            ),
            "laws": [
                {
                    "section_id": row.section_id,
                    "relevance_score": round(float(row.score), 2),
                    "severity": row.severity or "medium",
                }
                for row in rows
            ],
        }

    # ── Step 8: Assemble response with language-specific text ────────
    # Create a lookup from section_id to DB row for quick access
    row_lookup = {row.section_id: row for row in rows}

    law_results = []
    for law in gpt_response.get("laws", []):
        section_id = law.get("section_id")
        db_row = row_lookup.get(section_id)
        if not db_row:
            continue

        # Select simplified text in the requested language
        lang_mapping = {
            "en": db_row.simplified_en,
            "ta": db_row.simplified_ta,
            "hi": db_row.simplified_hi,
        }
        
        # Try requested language first, fallback to English, then to section_text
        simplified = lang_mapping.get(language, db_row.simplified_en)
        if not simplified or not simplified.strip():
            simplified = db_row.simplified_en
        if not simplified or not simplified.strip():
            # Fallback to original text (truncated) with warning
            logger.warning(f"No simplified text for section {section_id} — using original text")
            simplified = db_row.section_text[:300] if db_row.section_text else "No text available"
        
        # Log warning if severity is missing
        severity = law.get("severity", db_row.severity or "medium")
        if not db_row.severity:
            logger.warning(f"Severity missing for section {section_id}")

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

    # Sort by relevance (highest first)
    law_results.sort(key=lambda x: x["relevance_score"], reverse=True)

    response_ms = int((time.perf_counter() - start_time) * 1000)

    response = {
        "query_id": query_id,
        "detected_language": detected_lang,
        "ai_summary": (
            f"{gpt_response.get('ai_summary', '')}\n\n"
            f"⚠️ LEGAL DISCLAIMER: This information is for general reference only and is NOT legal advice. "
            f"The simplified explanations may not capture all legal nuances. "
            f"Laws change frequently. Always consult a qualified legal professional for advice specific to your situation."
        ),
        "laws": law_results,
        "response_ms": response_ms,
    }

    # ── Step 9: Cache the response ───────────────────────────────────
    await cache_service.set(cache_key, response)

    # ── Step 10: Log query (non-blocking) ────────────────────────────
    asyncio.create_task(
        _log_query(db, issue, detected_lang, len(law_results), response_ms)
    )

    logger.info(
        f"[{query_id}] Query completed in {response_ms}ms — {len(law_results)} laws returned"
    )

    return response


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
    db: AsyncSession,
    query_text: str,
    language: str,
    results_count: int,
    response_ms: int,
) -> None:
    """Log the query to the query_logs table (fire-and-forget)."""
    try:
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
