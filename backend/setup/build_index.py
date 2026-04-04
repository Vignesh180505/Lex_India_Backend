"""Build IVFFlat index on the embedding column after all embeddings are populated.

IMPORTANT: Run this ONLY after setup/generate_embeddings.py has finished.
An index on a column of NULLs wastes space and slows inserts.

The IVFFlat index enables fast approximate nearest-neighbour search
using cosine similarity (vector_cosine_ops).

Usage:
    python -m setup.build_index
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from app.database import async_session_factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lexindia.setup.build_index")


async def build_index() -> None:
    """Create the IVFFlat index on the laws.embedding column."""
    start_time = time.time()

    async with async_session_factory() as session:
        # Check how many rows have embeddings
        result = await session.execute(
            text("SELECT COUNT(*) FROM laws WHERE embedding IS NOT NULL")
        )
        embedded_count = result.scalar()

        total_result = await session.execute(text("SELECT COUNT(*) FROM laws"))
        total_count = total_result.scalar()

        logger.info(f"Rows with embeddings: {embedded_count}/{total_count}")

        if embedded_count == 0:
            logger.error(
                "No embeddings found! Run setup/generate_embeddings.py first. Aborting."
            )
            return

        if embedded_count < total_count:
            logger.warning(
                f"{total_count - embedded_count} rows still missing embeddings. "
                f"Index will only cover {embedded_count} rows."
            )

        # Drop existing index if present (for re-runs)
        logger.info("Dropping existing index (if any)...")
        await session.execute(
            text("DROP INDEX IF EXISTS laws_embedding_idx")
        )
        await session.commit()

        # Create the IVFFlat index
        # lists = 100 is a good default for collections up to ~100k vectors
        logger.info("Building IVFFlat index (this may take a few minutes)...")
        await session.execute(
            text("""
                CREATE INDEX laws_embedding_idx
                ON laws USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
        )
        await session.commit()

        elapsed = time.time() - start_time
        logger.info(
            f"IVFFlat index created successfully!\n"
            f"  Rows indexed: {embedded_count}\n"
            f"  Time: {elapsed:.1f}s\n"
            f"  Index: laws_embedding_idx (cosine similarity, 100 lists)"
        )


if __name__ == "__main__":
    asyncio.run(build_index())
