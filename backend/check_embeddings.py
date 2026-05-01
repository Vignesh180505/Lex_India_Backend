"""STEP 1: Check if embeddings exist in the database."""
import asyncio
from sqlalchemy import text
from app.database import async_session_factory

async def check():
    async with async_session_factory() as session:
        result = await session.execute(text("""
            SELECT 
                COUNT(*) AS total_rows,
                COUNT(embedding) AS rows_with_embedding,
                COUNT(*) - COUNT(embedding) AS rows_without_embedding
            FROM laws
        """))
        row = result.fetchone()
        print(f"total_rows:            {row[0]}")
        print(f"rows_with_embedding:   {row[1]}")
        print(f"rows_without_embedding: {row[2]}")

if __name__ == '__main__':
    asyncio.run(check())
