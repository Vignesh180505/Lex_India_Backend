"""GET /api/laws — browse and search laws endpoint.

Supports filtering by act_code, severity, and free-text search.
Returns paginated results with 20 items per page by default.
"""

import logging
import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.law import Law
from app.schemas.law import LawSchema, LawListResponse

logger = logging.getLogger("lexindia.laws")
router = APIRouter(tags=["Laws"])


@router.get("/laws", response_model=LawListResponse)
async def browse_laws(
    act_code: str | None = Query(None, description="Filter by Act code (e.g. IPC, CPA)."),
    search: str | None = Query(None, description="Search in section titles and text."),
    severity: str | None = Query(None, pattern="^(low|medium|high)$", description="Filter by severity."),
    page: int = Query(1, ge=1, description="Page number."),
    per_page: int = Query(20, ge=1, le=100, description="Results per page."),
    db: AsyncSession = Depends(get_db),
) -> LawListResponse:
    """Browse and search laws with filtering and pagination."""
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

    return LawListResponse(
        laws=[LawSchema.model_validate(law) for law in laws],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
