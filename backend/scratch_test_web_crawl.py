import asyncio
import json
from app.database import async_session_factory
from app.services.rag_service import query_laws

async def test():
    async with async_session_factory() as db:
        # A query that is likely to trigger Tier 2 fallback (crawling)
        query = "My neighbor illegally cut down a tree on my private property land boundary."
        print(f"Executing query_laws for: '{query}'")
        res = await query_laws(query, "en", db)
        print("Response Source:", res.get("source"))
        print("Response Summary:")
        print(res.get("ai_summary"))
        print("\nLaws Found:")
        for law in res.get("laws", []):
            print(f"- Section {law.get('section_number')}: {law.get('section_title')} under {law.get('act_name')}")
            print(f"  Description: {law.get('simplified')}")
            print(f"  Punishment: {law.get('punishment')}")
            print(f"  Severity: {law.get('severity')} | Relevance: {law.get('relevance_score')}")

if __name__ == '__main__':
    asyncio.run(test())
