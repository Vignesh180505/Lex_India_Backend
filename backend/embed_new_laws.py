"""Generate embeddings for laws that are missing them."""
import asyncio, logging
from sqlalchemy import text
from app.database import async_session_factory
from app.services.embed_service import embed

logging.basicConfig(level=logging.WARNING)

async def generate():
    async with async_session_factory() as db:
        rows = await db.execute(text("""
            SELECT id, section_id, section_title, section_text, simplified_en
            FROM laws WHERE embedding IS NULL
        """))
        laws = rows.fetchall()
        print(f"Laws missing embeddings: {len(laws)}")

        for law in laws:
            text_to_embed = f"{law[2]}. {law[3]} {law[4] or ''}".strip()
            embedding = embed(text_to_embed)
            await db.execute(
                text("UPDATE laws SET embedding = :emb WHERE id = :id"),
                {"emb": str(embedding), "id": law[0]}
            )
            print(f"  Embedded: {law[1]} | {law[2]}")

        await db.commit()
        print("Done.")

asyncio.run(generate())
