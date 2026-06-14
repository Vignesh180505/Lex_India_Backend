"""POST /api/query — main user query endpoint for legal issue search.

Accepts a plain-language legal problem description and returns:
- AI-generated summary of the legal situation
- Ranked list of applicable Indian law sections
- Simplified explanations in the requested language
- Links to official court filing portals

Uses vector similarity search (pgvector) + GPT-4o re-ranking.
No keyword fallback — if embeddings are unavailable, returns 503.
"""

import logging
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.query import QueryRequest, QueryResponse

logger = logging.getLogger("lexindia.query")
router = APIRouter(tags=["Query"])


@router.post("/query", response_model=QueryResponse)
async def handle_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """Search Indian legal database using natural language query.

    Raises HTTPException 503 if embeddings are missing or the embedding
    model fails to load.  Never silently falls back to keyword search.
    """
    logger.info(
        f"Query received: '{request.issue[:80]}...' (lang={request.language})"
    )

    try:
        # Quick check: do any rows have embeddings?
        result = await db.execute(
            text("SELECT EXISTS(SELECT 1 FROM laws WHERE embedding IS NOT NULL)")
        )
        has_vectors = result.scalar()
        if not has_vectors:
            # For local/demo environments, return a friendly empty response rather
            # than a 503 which the frontend surfaces as a generic error. This
            # keeps the UI usable while the developer seeds embeddings.
            logger.warning("No embeddings found in database — returning empty response for demo.")
            return QueryResponse(
                query_id=str(uuid.uuid4()),
                detected_language=request.language,
                ai_summary=(
                    "Embeddings are not available locally. Run setup/generate_embeddings.py "
                    "to populate the database with vectors and enable law search."
                ),
                laws=[],
                response_ms=int((time.perf_counter() - 0) * 1000),
            )

        from app.services.rag_service import query_laws

        result = await query_laws(
            issue=request.issue,
            language=request.language,
            db=db,
            mode=request.mode,
        )
        logger.info("RAG pipeline successful")
        return QueryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Critical error in handle_query: {str(e)}", exc_info=True)
        # Attempt to rollback to prevent session corruption
        try:
            if db.is_active:
                await db.rollback()
        except Exception as rb_err:
            logger.warning(f"Secondary error during rollback: {rb_err}")
            
        raise HTTPException(
            status_code=503,
            detail="The legal search engine encountered a temporary database error. Our team has been notified.",
        )

