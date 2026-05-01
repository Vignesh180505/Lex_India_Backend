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
            raise HTTPException(
                status_code=503,
                detail=(
                    "Embedding service unavailable: no embeddings found in database. "
                    "Run setup/generate_embeddings.py first."
                ),
            )

        from app.services.rag_service import query_laws

        result = await query_laws(
            issue=request.issue,
            language=request.language,
            db=db,
        )
        logger.info("RAG pipeline successful")
        return QueryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query handler exception: {e}", exc_info=True)
        try:
            await db.rollback()
        except Exception:
            pass
        raise HTTPException(
            status_code=503,
            detail=f"Embedding service unavailable: {str(e)}. Run setup/generate_embeddings.py first.",
        )
