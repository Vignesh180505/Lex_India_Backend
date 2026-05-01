"""SQLAlchemy ORM models for the laws and filing_links tables.

The `laws` table stores scraped Indian legal sections with:
- Original verbatim text (never modified after scraping)
- AI-simplified translations (populated by setup/simplify_laws.py — Call 1)
- 384-dim vector embedding of simplified_en (populated by setup/generate_embeddings.py — Call 2)

The `filing_links` table stores eCourt portal URLs by case type.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    func,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.database import Base


class Law(Base):
    """ORM model for the `laws` table — one row per legal section."""

    __tablename__ = "laws"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    section_id = Column(String(50), unique=True, nullable=False, index=True)
    act_name = Column(Text, nullable=False)
    act_code = Column(String(20), nullable=False, index=True)
    section_number = Column(String(20), nullable=False)
    section_title = Column(Text, nullable=False)

    # Original legal text — verbatim, never modified after scraping
    section_text = Column(Text, nullable=False)

    # AI-generated simplified text (populated by Call 1 — GPT-4o)
    simplified_en = Column(Text, nullable=True)
    simplified_ta = Column(Text, nullable=True)
    simplified_hi = Column(Text, nullable=True)
    severity = Column(String(10), nullable=True)  # 'low' | 'medium' | 'high'

    # Vector embedding of simplified_en (populated by Call 2 — all-MiniLM-L6-v2)
    # Dimension 384 matches the model output exactly
    embedding = Column(Vector(384), nullable=True)

    # Additional metadata
    punishment = Column(Text, nullable=True)
    amendment_year = Column(Integer, nullable=True)
    source_url = Column(Text, nullable=True)
    filing_link = Column(Text, nullable=True)
    cross_references = Column(ARRAY(Text), default=[])
    amendment_note = Column(Text, nullable=True)

    # Timestamps
    scraped_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"<Law {self.section_id}: {self.section_title}>"


class FilingLink(Base):
    """ORM model for the `filing_links` table — eCourts portal URLs."""

    __tablename__ = "filing_links"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    case_type = Column(String(100), nullable=False)
    portal_name = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"<FilingLink {self.case_type}: {self.portal_name}>"
