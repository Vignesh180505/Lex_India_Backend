import asyncio
from sqlalchemy import text
from app.database import async_session_factory

async def delete_fake():
    async with async_session_factory() as session:
        await session.execute(text("DELETE FROM laws WHERE section_text LIKE 'Text for section%'"))
        await session.commit()
        print('Deleted fake laws')

if __name__ == '__main__':
    asyncio.run(delete_fake())
