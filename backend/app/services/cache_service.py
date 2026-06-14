"""Redis caching service for repeated query results.

Caches complete query responses with a 24-hour TTL (configurable).
Cache key is the MD5 hash of the lowered+stripped English query text.

Resilience: if Redis is unavailable the cache is transparently skipped.
The connection is re-attempted on every request so the cache automatically
re-enables itself if Redis recovers — no restart required.
"""

import asyncio
import json
import hashlib
import logging
from typing import Optional, Any

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger("lexindia.services.cache")

# ── Redis Connection ──────────────────────────────────────────────────────
_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    """Get (or lazily create) the Redis connection.

    Re-attempts the connection on every call when _redis is None so the
    cache automatically re-enables itself if Redis recovers after a
    transient failure — without requiring an application restart.
    """
    global _redis

    # Fast path: already connected and healthy
    if _redis is not None:
        try:
            await _redis.ping()
            return _redis
        except Exception:
            # Connection went stale — reset and fall through to reconnect
            logger.warning("Redis connection lost, will attempt reconnect.")
            try:
                await _redis.aclose()
            except Exception:
                pass
            _redis = None

    # Attempt (re-)connection with a short timeout to avoid blocking requests
    try:
        candidate = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=1,
        )
        await asyncio.wait_for(candidate.ping(), timeout=1.0)
        _redis = candidate
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}. Caching is disabled for this request.")
        _redis = None

    return _redis


def make_cache_key(query_text: str) -> str:
    """Generate a deterministic cache key from a query string.

    Args:
        query_text: The English query text (should be lowered and stripped).

    Returns:
        MD5 hex digest as cache key.
    """
    normalized = query_text.lower().strip()
    return f"lexindia:query:{settings.CACHE_VERSION}:{hashlib.md5(normalized.encode()).hexdigest()}"


async def get(cache_key: str) -> Optional[dict]:
    """Retrieve a cached query response.

    Args:
        cache_key: The cache key (from make_cache_key).

    Returns:
        Cached response dict, or None if not found / expired.
    """
    r = await get_redis()
    if not r:
        return None  # Redis is unavailable

    try:
        cached = await r.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return json.loads(cached)
        logger.debug(f"Cache MISS: {cache_key}")
        return None
    except Exception as e:
        logger.warning(f"Redis get error: {e}")
        return None


async def set(cache_key: str, data: dict, ttl: Optional[int] = None) -> bool:
    """Store a query response in cache.

    Args:
        cache_key: The cache key (from make_cache_key).
        data: Response dict to cache.
        ttl: Time-to-live in seconds (defaults to CACHE_TTL_SECONDS from config).

    Returns:
        True if cached successfully, False on error.
    """
    if ttl is None:
        ttl = settings.CACHE_TTL_SECONDS

    r = await get_redis()
    if not r:
        return False  # Redis is unavailable

    try:
        serialized = json.dumps(data, ensure_ascii=False, default=str)
        await r.setex(cache_key, ttl, serialized)
        logger.info(f"Cache SET: {cache_key} (TTL={ttl}s)")
        return True
    except Exception as e:
        logger.warning(f"Redis set error: {e}")
        return False


async def invalidate(cache_key: str) -> bool:
    """Remove a specific key from cache."""
    r = await get_redis()
    if not r:
        return False
    try:
        await r.delete(cache_key)
        logger.info(f"Cache INVALIDATED: {cache_key}")
        return True
    except Exception as e:
        logger.warning(f"Redis delete error: {e}")
        return False


async def invalidate_section(section_id: str) -> int:
    """Invalidate all cached queries that might include this section.
    
    Since we can't track which sections are in which queries,
    we invalidate all query caches when a section is updated.
    
    Args:
        section_id: The section that was updated
        
    Returns:
        Number of keys deleted
    """
    try:
        r = await get_redis()
        # Delete all query cache keys (pattern-based)
        keys = await r.keys("lexindia:query:*")
        if keys:
            deleted = await r.delete(*keys)
            logger.warning(f"Cache BULK INVALIDATION: Deleted {deleted} query caches due to section {section_id} update")
            return deleted
        return 0
    except Exception as e:
        logger.warning(f"Redis pattern delete error: {e}")
        return 0


async def clear_all() -> int:
    """Clear entire cache (use with caution - typically during data rebuild).
    
    Returns:
        Number of keys deleted
    """
    r = await get_redis()
    if not r:
        return 0
    try:
        keys = await r.keys("lexindia:*")
        if keys:
            deleted = await r.delete(*keys)
            logger.warning(f"Cache CLEARED: Deleted {deleted} total keys")
            return deleted
        return 0
    except Exception as e:
        logger.warning(f"Redis clear error: {e}")
        return 0


async def close() -> None:
    """Close the Redis connection."""
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("Redis connection closed")
