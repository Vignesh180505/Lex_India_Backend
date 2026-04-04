"""SQLAlchemy ORM models package.

Import all models here so Alembic's `target_metadata` can discover them.
"""

from app.models.law import Law, FilingLink
from app.models.query_log import QueryLog

__all__ = ["Law", "FilingLink", "QueryLog"]
