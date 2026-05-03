import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [r[0] for r in res]
        print(f"Tables: {tables}")
        
        for table in tables:
            try:
                res = await conn.execute(text(f"SELECT count(*) FROM {table}"))
                count = res.scalar()
                print(f"  {table}: {count} rows")
            except Exception as e:
                print(f"  {table}: Error {e}")

if __name__ == "__main__":
    asyncio.run(check())
