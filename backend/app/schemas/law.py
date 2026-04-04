"""Pydantic schemas for law data validation.

Used by the GET /api/laws browse endpoint for listing and filtering laws.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class LawSchema(BaseModel):
    """Schema for a single law section in browse/list views."""

    section_id: str
    act_name: str
    act_code: str
    section_number: str
    section_title: str
    section_text: str
    simplified_en: Optional[str] = None
    simplified_ta: Optional[str] = None
    simplified_hi: Optional[str] = None
    severity: Optional[str] = None
    punishment: Optional[str] = None
    amendment_year: Optional[int] = None
    source_url: Optional[str] = None
    filing_link: Optional[str] = None
    scraped_at: Optional[datetime] = None

    class Config:
        """Enable ORM mode for SQLAlchemy model conversion."""
        from_attributes = True


class LawListResponse(BaseModel):
    """Paginated response for GET /api/laws."""

    laws: List[LawSchema]
    total: int = Field(..., description="Total number of matching records.")
    page: int = Field(..., description="Current page number (1-indexed).")
    per_page: int = Field(default=20, description="Results per page.")
    total_pages: int = Field(..., description="Total number of pages.")


class LawFilterParams(BaseModel):
    """Query parameters for filtering laws in browse view."""

    act_code: Optional[str] = Field(
        None, description="Filter by Act code (e.g. IPC, CPA, CPC)."
    )
    search: Optional[str] = Field(
        None, description="Full-text search within section titles and text."
    )
    severity: Optional[str] = Field(
        None,
        pattern="^(low|medium|high)$",
        description="Filter by severity level.",
    )
    page: int = Field(default=1, ge=1, description="Page number (1-indexed).")
    per_page: int = Field(default=20, ge=1, le=100, description="Results per page.")
