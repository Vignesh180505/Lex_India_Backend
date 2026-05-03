import asyncio
from sqlalchemy import text
from app.database import async_session_factory

async def check():
    async with async_session_factory() as session:
        res = await session.execute(text('SELECT COUNT(*) FROM laws WHERE simplified_en IS NULL'))
        print('NULL simplified:', res.scalar())
        res = await session.execute(text('SELECT COUNT(*) FROM laws'))
        print('Total rules:', res.scalar())

if __name__ == '__main__':
    asyncio.run(check())
