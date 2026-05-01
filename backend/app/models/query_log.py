"""SQLAlchemy ORM model for the query_logs table.

Logs every user query for analytics, cache-miss tracking, and performance monitoring.
Writes are non-blocking (fire-and-forget via asyncio.create_task in the RAG service).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class QueryLog(Base):
    """ORM model for the `query_logs` table."""

    __tablename__ = "query_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    query_text = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    results_count = Column(Integer, nullable=True)
    response_ms = Column(Integer, nullable=True)
    mode = Column(String(10), default="citizen", nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"<QueryLog {self.id}: {self.language} ({self.results_count} results)>"
