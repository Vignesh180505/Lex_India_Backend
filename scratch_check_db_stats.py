import asyncio
from sqlalchemy import text
import sys
import os

# Add parent dir to path to import app
sys.path.append(os.getcwd())

from app.database import async_session_factory

async def check():
    try:
        async with async_session_factory() as session:
            # Count total laws
            res = await session.execute(text("SELECT count(*) FROM laws"))
            total = res.scalar()
            print(f"Total laws in database: {total}")

            # Top acts
            res = await session.execute(text("SELECT act_name, count(*) FROM laws GROUP BY act_name ORDER BY count(*) DESC LIMIT 20"))
            print("\nTop Acts in database:")
            for row in res.fetchall():
                print(f"  - {row[0]}: {row[1]}")

            # Check for tree related keywords
            res = await session.execute(text("SELECT section_title, act_name FROM laws WHERE section_text ILIKE '%tree%' OR section_title ILIKE '%tree%' OR simplified_en ILIKE '%tree%'"))
            rows = res.fetchall()
            print(f"\nTree related sections found: {len(rows)}")
            for row in rows[:10]:
                print(f"  - {row[0]} ({row[1]})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
