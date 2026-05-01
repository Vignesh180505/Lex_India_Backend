"""SQLAlchemy ORM model for the judgments_cache table.

Stores court judgments fetched from Indian Kanoon locally so that:
- Full text doesn't need to be re-fetched on repeat queries.
- Outcome analysis results are cached alongside the judgment.
- 384-dim embeddings enable future vector-similarity search without API calls.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from pgvector.sqlalchemy import Vector

from app.database import Base


class JudgmentCache(Base):
    """ORM model for the `judgments_cache` table — one row per judgment."""

    __tablename__ = "judgments_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=True)
    court = Column(String(100), nullable=True)
    date = Column(Date, nullable=True)
    full_text = Column(Text, nullable=True)
    outcome = Column(String(50), nullable=True)
    petitioner_type = Column(String(100), nullable=True)
    respondent_type = Column(String(100), nullable=True)
    key_reason = Column(Text, nullable=True)
    embedding = Column(Vector(384), nullable=True)
    fetched_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"<JudgmentCache doc_id={self.doc_id}: {self.title}>"
