"""Call 2: all-MiniLM-L6-v2 embedding generation script (run once after simplification).

This one-time setup script generates 384-dimensional vector embeddings for all
law sections that have simplified_en text but no embedding yet.

CRITICAL RULES:
  - Embeds simplified_en (NOT section_text) — because citizen queries use plain language
  - Never embeds NULL or empty strings
  - Must run AFTER setup/simplify_laws.py has populated simplified_en
  - Must run BEFORE setup/build_index.py creates the IVFFlat index

The model (all-MiniLM-L6-v2) is the same model used by embed_service.py at query time.

Usage:
    python -m setup.generate_embeddings
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy import text

from app.database import async_session_factory
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lexindia.setup.embeddings")

BATCH_SIZE = 64  # Process 64 rows at a time to manage memory


def _section_filter_ids() -> list[str]:
    """Optional comma-separated section filter from env.

    Example:
        EMBED_SECTION_IDS=MVA-117,MVA-66,IPC-294
    """
    raw = os.getenv("EMBED_SECTION_IDS", "").strip()
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


async def run_embedding_generation() -> None:
    """Generate embeddings for all sections with simplified_en but no embedding."""
    start_time = time.time()

    # Load the model once
    logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    dimension = model.get_sentence_embedding_dimension()
    logger.info(f"Model loaded. Output dimension: {dimension}")

    if dimension != settings.EMBEDDING_DIMENSION:
        logger.error(
            f"Dimension mismatch! Model outputs {dimension} but config expects "
            f"{settings.EMBEDDING_DIMENSION}. Aborting."
        )
        return

    processed = 0
    errors = 0
    filter_ids = _section_filter_ids()

    async with async_session_factory() as session:
        # Get all rows needing embeddings
        query = """
                SELECT id, section_id, simplified_en
                FROM laws
                WHERE simplified_en IS NOT NULL
                  AND simplified_en != ''
                  AND embedding IS NULL
            """
        params: dict[str, object] = {}
        if filter_ids:
            query += " AND section_id = ANY(:section_ids)"
            params["section_ids"] = filter_ids
            logger.info(f"Applying EMBED_SECTION_IDS filter: {filter_ids}")

        query += " ORDER BY act_code, section_number"

        result = await session.execute(text(query), params)
        rows = result.fetchall()
        total = len(rows)

        if total == 0:
            logger.info("All eligible sections already have embeddings — nothing to do")
            return

        logger.info(f"Generating embeddings for {total} sections (batch size: {BATCH_SIZE})")

        # Process in batches
        for batch_start in range(0, total, BATCH_SIZE):
            batch = rows[batch_start : batch_start + BATCH_SIZE]

            # Prepare texts for batch encoding
            ids = []
            section_ids = []
            texts = []

            for row in batch:
                row_id, section_id, simplified_en = row
                if simplified_en and simplified_en.strip():
                    ids.append(row_id)
                    section_ids.append(section_id)
                    texts.append(simplified_en)
                else:
                    logger.warning(f"Skipping {section_id} — empty simplified_en")
                    errors += 1

            if not texts:
                continue

            try:
                # Batch encode — much faster than one-at-a-time
                vectors = model.encode(texts, normalize_embeddings=True, batch_size=BATCH_SIZE)

                # Update each row with its embedding
                for row_id, section_id, vector in zip(ids, section_ids, vectors):
                    embedding_list = vector.tolist()

                    # Validate dimension
                    if len(embedding_list) != settings.EMBEDDING_DIMENSION:
                        logger.error(
                            f"Wrong dimension for {section_id}: {len(embedding_list)} "
                            f"(expected {settings.EMBEDDING_DIMENSION})"
                        )
                        errors += 1
                        continue

                    await session.execute(
                        text("""
                            UPDATE laws
                            SET embedding = :embedding,
                                updated_at = NOW()
                            WHERE id = :id
                        """),
                        {
                            "id": row_id,
                            "embedding": str(embedding_list),
                        },
                    )
                    processed += 1

                # Commit after each batch
                await session.commit()

                # Progress logging every 100 rows
                if processed % 100 == 0 or processed == total:
                    logger.info(f"Embedded {processed}/{total} sections...")

            except Exception as e:
                logger.error(f"Batch encoding error: {e}")
                errors += len(batch)
                continue

    elapsed = time.time() - start_time
    logger.info(
        f"\nEmbedding generation complete:\n"
        f"  Processed: {processed}/{total}\n"
        f"  Errors: {errors}\n"
        f"  Duration: {elapsed:.1f}s\n"
        f"  Avg time per section: {elapsed/max(processed,1):.3f}s"
    )

    if processed > 0:
        logger.info(
            "\nNext step: run 'python -m setup.build_index' to create the IVFFlat index."
        )


if __name__ == "__main__":
    asyncio.run(run_embedding_generation())
