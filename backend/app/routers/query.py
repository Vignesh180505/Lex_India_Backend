"""POST /api/query — main user query endpoint for legal issue search.

Accepts a plain-language legal problem description and returns:
- AI-generated summary of the legal situation
- Ranked list of applicable Indian law sections
- Simplified explanations in the requested language
- Links to official court filing portals

Supports two modes:
1. Full RAG (when embeddings exist) — vector similarity + GPT-4o re-ranking
2. Text search fallback (when no embeddings) — SQL ILIKE keyword matching
"""

import logging
import time
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.query import QueryRequest, QueryResponse, LawResult

logger = logging.getLogger("lexindia.query")
router = APIRouter(tags=["Query"])


async def _has_embeddings(db: AsyncSession) -> bool:
    """Check if any laws have embeddings (to decide RAG vs fallback)."""
    try:
        result = await db.execute(
            text("SELECT COUNT(*) as cnt FROM laws WHERE embedding IS NOT NULL")
        )
        count = result.scalar() or 0
        return count > 0
    except Exception as e:
        logger.warning(f"Error checking embeddings: {e}")
        # If there's an error, rollback the transaction to get out of aborted state
        await db.rollback()
        return False


async def _text_search(issue: str, language: str, db: AsyncSession) -> dict:
    """Fallback text-based search when no embeddings are available.

    Splits the query into keywords and finds laws where section_text
    or simplified_en contains any of those keywords.
    """
    start_time = time.perf_counter()
    query_id = str(uuid.uuid4())

    try:
        # Extract meaningful keywords (skip very short words)
        words = [w.strip().lower() for w in issue.split() if len(w.strip()) > 3]
        if not words:
            words = [issue.lower()]

        # Build ILIKE conditions for each keyword
        conditions = []
        params = {}
        for i, word in enumerate(words[:8]):  # limit to 8 keywords
            key = f"kw{i}"
            conditions.append(
                f"(LOWER(section_text) LIKE :{key} OR LOWER(simplified_en) LIKE :{key} "
                f"OR LOWER(section_title) LIKE :{key} OR LOWER(act_name) LIKE :{key})"
            )
            params[key] = f"%{word}%"

        where_clause = " OR ".join(conditions) if conditions else "TRUE"

        # Select language-specific simplified text
        lang_col = {
            "en": "simplified_en",
            "ta": "simplified_ta",
            "hi": "simplified_hi",
        }.get(language, "simplified_en")

        result = await db.execute(
            text(f"""
                SELECT section_id, act_name, section_number, section_title,
                       section_text, {lang_col} as simplified, severity, punishment
                FROM laws
                WHERE {where_clause}
                ORDER BY
                    CASE severity
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END
                LIMIT 10
            """),
            params,
        )
        rows = result.fetchall()

        # If no keyword matches, return all laws sorted by severity
        if not rows:
            result = await db.execute(
                text(f"""
                    SELECT section_id, act_name, section_number, section_title,
                           section_text, {lang_col} as simplified, severity, punishment
                    FROM laws
                    ORDER BY
                        CASE severity
                            WHEN 'high' THEN 1
                            WHEN 'medium' THEN 2
                            WHEN 'low' THEN 3
                            ELSE 4
                        END
                    LIMIT 8
                """)
            )
            rows = result.fetchall()

        response_ms = int((time.perf_counter() - start_time) * 1000)

        laws = []
        for row in rows:
            # Log warning if severity is missing
            severity = row.severity or "medium"
            if not row.severity:
                logger.warning(f"Severity missing for section {row.section_id}")
            
            laws.append({
                "section_id": row.section_id,
                "act_name": row.act_name,
                "section_number": row.section_number,
                "section_title": row.section_title,
                "original_text": row.section_text,
                "simplified": row.simplified or row.section_text[:200],
                "severity": severity,
                "punishment": row.punishment or "Not specified",
                "filing_link": None,
                "relevance_score": 0.50,
                "is_fallback_search": True,
            })

        # Generate a summary with fallback warning
        if laws:
            top_acts = list(set(l["act_name"] for l in laws[:3]))
            summary = (
                f"⚠️ FALLBACK MODE: Keyword search was used (embeddings unavailable).\n\n"
                f"Based on your query, we found {len(laws)} potentially applicable law sections "
                f"from {', '.join(top_acts)}. Results are sorted by severity.\n\n"
                f"DISCLAIMER: This information is for general reference only and is NOT legal advice. "
                f"The simplified explanations may not capture all legal nuances. "
                f"Consult a qualified legal professional for advice specific to your situation."
            )
        else:
            summary = (
                "No directly applicable laws were found for your query. "
                "Please try rephrasing your problem or using different keywords.\n\n"
                "DISCLAIMER: This information is for general reference only and is NOT legal advice."
            )

        return {
            "query_id": query_id,
            "detected_language": "en",
            "ai_summary": summary,
            "laws": laws,
            "response_ms": response_ms,
        }
    except Exception as e:
        logger.error(f"Text search failed: {e}", exc_info=True)
        await db.rollback()
        return {
            "query_id": query_id,
            "detected_language": "en",
            "ai_summary": (
                "⚠️ ERROR: Text search failed. Please try again.\n\n"
                "DISCLAIMER: This system is for reference only, not legal advice."
            ),
            "laws": [],
            "response_ms": int((time.perf_counter() - start_time) * 1000),
        }


@router.post("/query", response_model=QueryResponse)
async def handle_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """Search Indian legal database using natural language query."""
    logger.info(
        f"Query received: '{request.issue[:80]}...' (lang={request.language})"
    )

    try:
        # Check if we can use the full RAG pipeline
        has_vectors = await _has_embeddings(db)

        if has_vectors:
            # Full RAG mode: embed → vector search → GPT-4o re-rank
            try:
                from app.services.rag_service import query_laws
                result = await query_laws(
                    issue=request.issue,
                    language=request.language,
                    db=db,
                )
                logger.info(f"RAG pipeline successful")
                return QueryResponse(**result)
            except Exception as e:
                logger.error(f"RAG pipeline failed: {e}", exc_info=True)
                await db.rollback()
                result = await _text_search(request.issue, request.language, db)
                return QueryResponse(**result)
        else:
            # Fallback: keyword-based text search
            logger.info("No embeddings found — using text search fallback")
            result = await _text_search(request.issue, request.language, db)
            return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Query handler exception: {e}", exc_info=True)
        try:
            await db.rollback()
        except Exception:
            pass
        return QueryResponse(
            query_id=str(uuid.uuid4()),
            detected_language="en",
            ai_summary=(
                "⚠️ ERROR: An error occurred processing your query. Please try again.\n\n"
                "DISCLAIMER: This system is for reference only, not legal advice."
            ),
            laws=[],
            response_ms=0,
        )
        logger.info("No embeddings found — using text search fallback")
        result = await _text_search(request.issue, request.language, db)
        return QueryResponse(**result)
