"""One-time enrichment script to parse laws and generate cross_references and amendment_note."""

import argparse
import asyncio
import json
import logging
from typing import List

from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_factory

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("enrichment")

ENRICH_PROMPT = """
You are an Indian legal expert. For the following law section, identify:

1. cross_references: Up to 5 related section IDs from other Indian acts
   that a lawyer would commonly cite alongside this section.
   Format each as "ACT_CODE-SECTION_NUMBER" e.g. "IPC-302", "CrPC-154".
   Only include sections that genuinely relate to the same legal issue.

2. amendment_note: If this section was amended, state which amendment act
   changed it and what changed. Maximum 30 words.
   If no known amendment, return null.

Respond ONLY in valid JSON with exactly these keys:
{
  "cross_references": ["IPC-302", "CrPC-154"],
  "amendment_note": "Substituted by Act 13 of 2013 to enhance punishment"
}

Section: {act_name} Section {section_number} — {section_title}
Text: {section_text}
"""

async def enrich_section(client: AsyncOpenAI, row: dict) -> dict:
    """Call GPT-4o to enrich a single row."""
    try:
        user_message = ENRICH_PROMPT.format(
            act_name=row['act_name'],
            section_number=row['section_number'],
            section_title=row['section_title'],
            section_text=row['section_text'][:400]
        )
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": user_message}],
            response_format={"type": "json_object"},
            max_tokens=200,
        )
        
        content = response.choices[0].message.content
        if not content:
            return {}
            
        parsed = json.loads(content)
        return {
            "cross_references": parsed.get("cross_references", []),
            "amendment_note": parsed.get("amendment_note")
        }
    except Exception as e:
        logger.warning(f"Failed to enrich {row['section_id']}: {e}")
        return {}


async def process_batch(client: AsyncOpenAI, session: AsyncSession, batch: List[dict]):
    """Process a batch of rows concurrently."""
    tasks = [enrich_section(client, row) for row in batch]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for row, result in zip(batch, results):
        if isinstance(result, Exception):
            logger.error(f"Error enriching {row['section_id']}: {result}")
            continue
            
        if not result:
            continue
            
        try:
            await session.execute(
                text("""
                    UPDATE laws
                    SET cross_references = :cr, amendment_note = :an
                    WHERE section_id = :sid
                """),
                {
                    "cr": result.get("cross_references", []),
                    "an": result.get("amendment_note"),
                    "sid": row["section_id"]
                }
            )
            logger.info(f"Enriched {row['section_id']}")
        except Exception as e:
            logger.error(f"DB update failed for {row['section_id']}: {e}")

    await session.commit()


async def enrich_acts(acts: List[str]):
    """Enrich laws for specified acts."""
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async with async_session_factory() as session:
        for act in acts:
            logger.info(f"Starting enrichment for act: {act}")
            
            # Use cardinality query to handle arrays
            result = await session.execute(
                text("""
                    SELECT section_id, act_name, section_number, section_title, section_text 
                    FROM laws 
                    WHERE act_code = :act 
                      AND (cross_references IS NULL OR cardinality(cross_references) = 0)
                """),
                {"act": act}
            )
            rows = [dict(r._mapping) for r in result.fetchall()]
            
            logger.info(f"Found {len(rows)} sections to enrich in {act}")
            
            batch_size = 20
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                await process_batch(client, session, batch)
                logger.info(f"Completed batch {i//batch_size + 1}")
                await asyncio.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--acts", nargs="+", required=True, help="Act codes to enrich (e.g. IPC CPA)")
    args = parser.parse_args()
    
    asyncio.run(enrich_acts(args.acts))
