import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_url, create_engine, text
from app.config import settings

# Use SYNC URL for convenience in one-off script
sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
engine = create_engine(sync_url)

with engine.connect() as conn:
    res = conn.execute(text("SELECT section_id, punishment FROM laws LIMIT 5")).fetchall()
    print("Database Punishment Check:")
    for row in res:
        print(f"  {row.section_id}: {row.punishment}")
