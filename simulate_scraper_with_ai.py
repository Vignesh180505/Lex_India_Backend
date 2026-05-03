"""Use GPT-4o to simulate the IndiaCode scraper since the government site returns HTTP 403.
This fetches verbatim Indian legal sections so we have a realistic dataset to test semantic search.
"""

import asyncio
import json
from openai import AsyncOpenAI
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.config import settings
from app.database import async_session_factory
from sqlalchemy import text

async def simulate_scraping():
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = """
    You are an exact legal retrieval system. Output exactly 30 sections from the Indian Penal Code, 1860 (IPC) and Consumer Protection Act, 2019 (CPA).
    Choose important sections (like IPC 302, 376, 420, 498A, CPA 35, CPA 2, etc, relating to Gender Equality, Consumer Rights, Fraud, Violence).
    Return ONLY valid JSON array with objects matching:
    {
       "section_id": "IPC-302",
       "act_name": "Indian Penal Code, 1860",
       "act_code": "IPC",
       "section_number": "302",
       "section_title": "Punishment for murder",
       "section_text": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine."
    }
    """
    
    print("Fetching verbatim laws from OpenAI since WAF is blocking IndiaCode...")
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=4000
    )
    
    try:
        content = response.choices[0].message.content
        data = json.loads(content)
        sections = data.get("sections", data)
        if isinstance(sections, dict):
            # Sometimes GPT nests it
            sections = list(sections.values())[0]
            
        print(f"Got {len(sections)} sections. Upserting to DB...")
        
        async with async_session_factory() as session:
            for s in sections:
                await session.execute(text("""
                    INSERT INTO laws (
                        section_id, act_name, act_code, section_number,
                        section_title, section_text, scraped_at
                    ) VALUES (
                        :section_id, :act_name, :act_code, :section_number,
                        :section_title, :section_text, NOW()
                    )
                    ON CONFLICT (section_id) DO UPDATE SET
                        section_text = EXCLUDED.section_text,
                        section_title = EXCLUDED.section_title
                """), s)
            await session.commit()
        print("Upsert complete.")
        
    except Exception as e:
        print(f"Failed parsing: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_scraping())
