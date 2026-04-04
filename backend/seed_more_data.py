"""Mass seed the database with additional laws."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from app.database import async_session_factory

async def seed_more():
    """Insert bulk dummy laws into the database."""
    with open('more_laws.json', 'r') as f:
        more_laws = json.load(f)
        
    async with async_session_factory() as session:
        count = 0
        for law in more_laws:
            try:
                await session.execute(
                    text("""
                        INSERT INTO laws (
                            section_id, act_name, act_code, section_number,
                            section_title, section_text, simplified_en,
                            simplified_ta, simplified_hi, severity, punishment,
                            source_url, scraped_at
                        ) VALUES (
                            :section_id, :act_name, :act_code, :section_number,
                            :section_title, :section_text, :simplified_en,
                            :simplified_ta, :simplified_hi, :severity, :punishment,
                            '', NOW()
                        )
                        ON CONFLICT (section_id) DO UPDATE SET
                            section_text = EXCLUDED.section_text,
                            simplified_en = EXCLUDED.simplified_en,
                            simplified_ta = EXCLUDED.simplified_ta,
                            simplified_hi = EXCLUDED.simplified_hi,
                            severity = EXCLUDED.severity,
                            updated_at = NOW()
                    """),
                    {
                        "section_id": law["section_id"],
                        "act_name": law["act_name"],
                        "act_code": law["act_code"],
                        "section_number": law["section_number"],
                        "section_title": law["section_title"],
                        "section_text": law["section_text"],
                        "simplified_en": law["simplified_en"],
                        "simplified_ta": law["simplified_ta"],
                        "simplified_hi": law["simplified_hi"],
                        "severity": law["severity"],
                        "punishment": law.get("punishment"),
                    },
                )
                count += 1
            except Exception as e:
                print(f"  ✗ {law['section_id']}: {e}")

        await session.commit()
        print(f"\nSeeded {count} additional law sections successfully!")


if __name__ == "__main__":
    print("Seeding database with more dummy Indian law sections...\n")
    asyncio.run(seed_more())
