import asyncio
from sqlalchemy import text
from app.database import async_session_factory

async def check():
    async with async_session_factory() as db:
        # First get real column names
        cols = await db.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'laws' ORDER BY ordinal_position
        """))
        columns = [r[0] for r in cols.fetchall()]
        print(f"Laws table columns: {columns}")

        # Total laws
        total = await db.execute(text("SELECT COUNT(*) FROM laws"))
        print(f"Total laws in DB: {total.scalar()}")

        # Laws with embeddings
        emb = await db.execute(text("SELECT COUNT(*) FROM laws WHERE embedding IS NOT NULL"))
        print(f"Laws with embeddings: {emb.scalar()}")

        # Find the text column name
        text_col = None
        for c in ["section_text", "text", "content", "body", "law_text", "full_text"]:
            if c in columns:
                text_col = c
                break
        print(f"Text column: {text_col}")

        # Search for extortion/blackmail related laws using section_id/title
        q = """
            SELECT section_id, section_title, section_number
            FROM laws
            WHERE lower(section_title) LIKE '%extort%'
               OR lower(section_title) LIKE '%blackmail%'
               OR lower(section_title) LIKE '%threat%'
               OR lower(section_title) LIKE '%criminal intim%'
               OR section_id LIKE '%383%'
               OR section_id LIKE '%384%'
               OR section_id LIKE '%385%'
               OR section_id LIKE '%503%'
               OR section_id LIKE '%506%'
               OR section_id LIKE '%507%'
            LIMIT 20
        """
        r = await db.execute(text(q))
        rows = r.fetchall()
        print(f"\nExtortion/blackmail/threat laws in DB: {len(rows)}")
        for row in rows:
            print(f"  {row[0]} | {row[1]}")

        # Check kidnapping section that was returned
        kid = await db.execute(text("""
            SELECT section_id, section_title, section_number
            FROM laws
            WHERE section_id LIKE '%365%'
            LIMIT 5
        """))
        krows = kid.fetchall()
        print(f"\nKidnapping-related sections in DB:")
        for row in krows:
            print(f"  {row[0]} | {row[1]}")

        # Sample some laws to understand section_id format
        sample = await db.execute(text("""
            SELECT section_id, act_name, section_title
            FROM laws
            WHERE act_name LIKE '%Penal%'
            ORDER BY section_id
            LIMIT 15
        """))
        srows = sample.fetchall()
        print(f"\nSample IPC laws in DB:")
        for row in srows:
            print(f"  {row[0]} | {row[2]}")

asyncio.run(check())
