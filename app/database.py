"""PostgreSQL + pgvector async database connection management.

Provides:
- Async SQLAlchemy engine and session factory for FastAPI request lifecycle.
- Declarative Base for all ORM models.
- Dependency injection helper `get_db` for FastAPI router endpoints.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ── Async Engine ──────────────────────────────────────────────────────────
# pool_pre_ping=True ensures stale connections are recycled automatically.
# echo=True in development for SQL logging; disabled in production.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.is_development,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
)

# ── Session Factory ───────────────────────────────────────────────────────
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Declarative Base ─────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ── Dependency Injection ─────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing a transactional database session."""
    async with async_session_factory() as session:
        try:
            yield session
            # Only commit if the transaction is still active and NOT in a failed state
            if session.is_active:
                try:
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
        except Exception:
            # Thoroughly ensure the session is rolled back on any outer exception
            if session.is_active:
                await session.rollback()
            raise
        finally:
            await session.close()

