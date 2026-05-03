import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT * FROM query_logs ORDER BY created_at DESC LIMIT 5"))
        rows = res.fetchall()
        print(f"Last 5 query logs:")
        for row in rows:
            print(f"  {row}")

if __name__ == "__main__":
    asyncio.run(check())
