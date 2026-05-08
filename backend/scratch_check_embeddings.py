import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT count(*) FROM laws WHERE embedding IS NULL"))
        print(f"NULL embeddings: {res.scalar()}")
        
        res = await conn.execute(text("SELECT count(*) FROM laws WHERE embedding IS NOT NULL"))
        print(f"NOT NULL embeddings: {res.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
