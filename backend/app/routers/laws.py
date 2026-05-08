"""GET /api/laws — browse and search laws endpoint.

Supports filtering by act_code, severity, and free-text search.
Returns paginated results with 20 items per page by default.
"""

import logging
import math
import json

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.law import Law
from app.schemas.law import LawSchema, LawListResponse
from app.services.cache_service import get_redis
from app.config import settings

logger = logging.getLogger("lexindia.laws")
router = APIRouter(tags=["Laws"])


@router.get("/laws", response_model=LawListResponse)
async def browse_laws(
    act_code: str | None = Query(None, description="Filter by Act code (e.g. IPC, CPA)."),
    search: str | None = Query(None, description="Search in section titles and text."),
    severity: str | None = Query(None, pattern="^(low|medium|high)$", description="Filter by severity."),
    page: int = Query(1, ge=1, description="Page number."),
    per_page: int = Query(20, ge=1, le=100, description="Results per page."),
    language: str = Query("en", description="Language code (en, ta, hi)."),
    db: AsyncSession = Depends(get_db),
) -> LawListResponse:
    """Browse and search laws with filtering and pagination. Results are cached in Redis."""
    # Check Redis cache first
    cache_key = f"lexindia:laws:browse:{act_code}:{search}:{severity}:{page}:{per_page}:{language}"
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            logger.info(f"Laws cache HIT: {cache_key}")
            return LawListResponse(**json.loads(cached))
    except Exception as e:
        logger.warning(f"Redis cache check failed: {e}")
    # Build base query
    stmt = select(Law)
    count_stmt = select(func.count(Law.id))

    # Apply filters
    if act_code:
        stmt = stmt.where(Law.act_code == act_code)
        count_stmt = count_stmt.where(Law.act_code == act_code)

    if severity:
        stmt = stmt.where(Law.severity == severity)
        count_stmt = count_stmt.where(Law.severity == severity)

    if search:
        search_filter = or_(
            Law.section_title.ilike(f"%{search}%"),
            Law.section_text.ilike(f"%{search}%"),
            Law.section_number.ilike(f"%{search}%"),
            Law.section_id.ilike(f"%{search}%"),
            Law.act_code.ilike(f"%{search}%"),
            Law.act_name.ilike(f"%{search}%"),
            Law.simplified_en.ilike(f"%{search}%"),
            Law.punishment.ilike(f"%{search}%"),
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)

    # Get total count
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    total_pages = max(1, math.ceil(total / per_page))

    # Apply pagination
    offset = (page - 1) * per_page
    stmt = stmt.order_by(Law.act_code, Law.section_number).offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(stmt)
    laws = result.scalars().all()

    logger.info(f"Browse: act={act_code}, search={search}, page={page} → {len(laws)} results")

    law_dicts = [LawSchema.model_validate(law).model_dump() for law in laws]

    # Batch translate if language is not English
    if language != "en" and law_dicts:
        try:
            lang_name = "Tamil" if language == "ta" else "Hindi"
            from app.services.generate_service import _call_llm_with_fallback
            
            translation_prompt = f"""Translate these legal metadata fields into {lang_name}.
Return ONLY a valid JSON array of objects with translated 'act_name', 'section_title', 'punishment', and 'simplified_en' (which should be returned as 'simplified').
Keep the exact same array order. Do not translate English legal codes like 'IPC' or 'CrPC' - keep them as is or transliterate."""
            
            payload = [
                {
                    "act_name": l["act_name"], 
                    "section_title": l["section_title"], 
                    "punishment": l["punishment"] or "Not specified",
                    "simplified_en": l["simplified_en"] or "No simplified text available."
                }
                for l in law_dicts
            ]
            
            translated_data = await _call_llm_with_fallback(
                translation_prompt,
                json.dumps(payload),
                f"Batch translate laws browse page to {lang_name}"
            )
            
            if isinstance(translated_data, list) and len(translated_data) == len(law_dicts):
                for i, translated in enumerate(translated_data):
                    law_dicts[i]["act_name"] = translated.get("act_name", law_dicts[i]["act_name"])
                    law_dicts[i]["section_title"] = translated.get("section_title", law_dicts[i]["section_title"])
                    law_dicts[i]["punishment"] = translated.get("punishment", law_dicts[i]["punishment"])
                    # If we don't have the native simplified text, use the dynamically translated one
                    if language == "ta" and not law_dicts[i].get("simplified_ta"):
                        law_dicts[i]["simplified_ta"] = translated.get("simplified")
                    elif language == "hi" and not law_dicts[i].get("simplified_hi"):
                        law_dicts[i]["simplified_hi"] = translated.get("simplified")
        except Exception as e:
            logger.error(f"Failed to translate laws browse payload: {e}")

    response = LawListResponse(
        laws=law_dicts,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )

    # Store in Redis
    try:
        redis = await get_redis()
        await redis.setex(
            cache_key,
            settings.CACHE_TTL_SECONDS,
            json.dumps(response.model_dump(), ensure_ascii=False, default=str),
        )
    except Exception as e:
        logger.warning(f"Redis cache set failed: {e}")

    return response
