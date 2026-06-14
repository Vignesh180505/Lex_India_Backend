import asyncio
import sys
import os

sys.path.insert(0, os.getcwd())

from app.database import async_session_factory
from app.services.rag_service import query_laws

async def test_tree_query():
    issue = "my hoa wants me to cut down a 150+year old tree in my property"
    print(f"Testing query: '{issue}'")
    
    try:
        async with async_session_factory() as db:
            result = await query_laws(issue, "en", db)
            
            print("\n--- RESULTS ---")
            print(f"AI Summary:\n{result.get('ai_summary', '')}\n")
            
            laws = result.get('laws', [])
            print(f"Found {len(laws)} laws:")
            for i, law in enumerate(laws):
                print(f"[{i+1}] {law.get('act_name')} - {law.get('section_title')} (Confidence: {law.get('relevance_score')})")
                print(f"    {law.get('simplified')}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tree_query())
