"""GET /health — healthcheck endpoint.

Returns service status and dependency connectivity (database, Redis).
Used by Docker healthchecks, load balancers, and monitoring dashboards.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

logger = logging.getLogger("lexindia.health")
router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Return service health status with dependency checks."""
    status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "lexindia-backend",
        "checks": {},
    }

    # ── Database check ────────────────────────────────────────────────
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        status["checks"]["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status["checks"]["database"] = "disconnected"
        status["status"] = "degraded"

    # ── Redis check ───────────────────────────────────────────────────
    try:
        import redis.asyncio as aioredis
        from app.config import settings

        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        status["checks"]["redis"] = "connected"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        status["checks"]["redis"] = "disconnected"
        status["status"] = "degraded"

    return status
