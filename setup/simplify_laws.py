"""Call 1: GPT-4o simplification + translation script (run once after scraping).

This one-time setup script processes all law sections that don't yet have
simplified text. For each section, it calls GPT-4o to generate:
  - simplified_en: Plain English at 8th-grade reading level (max 80 words)
  - simplified_ta: Tamil translation of the simplified text
  - simplified_hi: Hindi translation of the simplified text
  - severity: low | medium | high classification

Must be run BEFORE setup/generate_embeddings.py (which embeds simplified_en).

Usage:
    python -m setup.simplify_laws
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from app.database import async_session_factory
from app.services.generate_service import simplify_section
from app.services.validation_service import validate_section_for_storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lexindia.setup.simplify")

BATCH_SIZE = 20
BATCH_DELAY = 1.0  # seconds between batches (rate limit safety)


def _section_filter_ids() -> list[str]:
    """Optional comma-separated section filter from env.

    Example:
        SIMPLIFY_SECTION_IDS=MVA-117,MVA-66,IPC-294
    """
    raw = os.getenv("SIMPLIFY_SECTION_IDS", "").strip()
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


async def run_simplification() -> None:
    """Process all unsimplified laws through GPT-4o."""
    start_time = time.time()
    processed = 0
    errors = 0
    total_tokens = 0

    filter_ids = _section_filter_ids()

    async with async_session_factory() as session:
        # Get all rows that need simplification
        query = """
                SELECT id, section_id, act_name, section_text
                FROM laws
                WHERE simplified_en IS NULL
            """
        params: dict[str, object] = {}
        if filter_ids:
            query += " AND section_id = ANY(:section_ids)"
            params["section_ids"] = filter_ids
            logger.info(f"Applying SIMPLIFY_SECTION_IDS filter: {filter_ids}")

        query += " ORDER BY act_code, section_number"

        result = await session.execute(text(query), params)
        rows = result.fetchall()
        total = len(rows)

        if total == 0:
            logger.info("All sections already simplified — nothing to do")
            return

        logger.info(f"Starting simplification of {total} sections (batch size: {BATCH_SIZE})")

        # Process in batches
        for batch_start in range(0, total, BATCH_SIZE):
            batch = rows[batch_start : batch_start + BATCH_SIZE]
            batch_num = (batch_start // BATCH_SIZE) + 1
            total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

            logger.info(f"Processing batch {batch_num}/{total_batches}")

            for row in batch:
                row_id, section_id, act_name, section_text = row

                try:
                    result = await simplify_section(section_text, section_id, act_name)

                    if result is None:
                        logger.error(f"Simplification failed for {section_id} — skipping")
                        errors += 1
                        continue

                    # VALIDATE before storing
                    is_valid, error_msg = validate_section_for_storage(
                        section_id=section_id,
                        section_text=section_text,
                        simplified_en=result["simplified_en"],
                        severity=result["severity"],
                        punishment=result.get("punishment"),
                    )
                    
                    if not is_valid:
                        logger.error(f"  ✗ {section_id}: Validation failed — {error_msg}")
                        errors += 1
                        continue

                    # Update the database row
                    await session.execute(
                        text("""
                            UPDATE laws
                            SET simplified_en = :simplified_en,
                                simplified_ta = :simplified_ta,
                                simplified_hi = :simplified_hi,
                                severity = :severity,
                                punishment = :punishment,
                                updated_at = NOW()
                            WHERE id = :id
                        """),
                        {
                            "id": row_id,
                            "simplified_en": result["simplified_en"],
                            "simplified_ta": result["simplified_ta"],
                            "simplified_hi": result["simplified_hi"],
                            "severity": result["severity"],
                            "punishment": result.get("punishment"),
                        },
                    )

                    processed += 1
                    logger.info(f"  ✓ {section_id} (severity: {result['severity']})")

                except Exception as e:
                    logger.error(f"  ✗ {section_id}: {e}")
                    errors += 1
                    continue

            # Commit after each batch
            await session.commit()

            # Rate limit delay between batches
            if batch_start + BATCH_SIZE < total:
                logger.info(f"  Waiting {BATCH_DELAY}s before next batch...")
                await asyncio.sleep(BATCH_DELAY)

    elapsed = time.time() - start_time
    logger.info(
        f"\nSimplification complete:\n"
        f"  Processed: {processed}/{total}\n"
        f"  Errors: {errors}\n"
        f"  Duration: {elapsed:.1f}s\n"
        f"  Avg time per section: {elapsed/max(processed,1):.2f}s"
    )


if __name__ == "__main__":
    asyncio.run(run_simplification())
