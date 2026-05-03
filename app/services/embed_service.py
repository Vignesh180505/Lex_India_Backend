"""all-MiniLM-L6-v2 embedding service (Call 2) — converts text to 384-dim vectors.

This is the EMBEDDING model — completely separate from GPT-4o (Call 1).
- Input: plain text string (always simplified_en, never section_text)
- Output: list of 384 floats (a mathematical vector, NOT readable text)
- Model: sentence-transformers/all-MiniLM-L6-v2 (runs locally, free, no API key)

The model is loaded ONCE at startup and reused for all requests.
Must be the same model used in setup/generate_embeddings.py for compatible vectors.
"""

import logging

from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger("lexindia.embed")

# ── Singleton Model ───────────────────────────────────────────────────────
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Load the embedding model (singleton — only loads once)."""
    global _model
    if _model is None:
        logger.info("Loading all-MiniLM-L6-v2 model...")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(
            f"Model loaded. Test embedding dim: {len(_model.encode('test').tolist())}"
        )
    return _model


def embed(text: str) -> list[float]:
    """Encode text into a 384-dimensional vector using all-MiniLM-L6-v2.

    Args:
        text: The text to embed (should be simplified English, not legal jargon).

    Returns:
        A list of 384 floats representing the text's position in vector space.
    """
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Encode multiple texts into vectors in a single batch (more efficient).

    Args:
        texts: List of texts to embed.

    Returns:
        List of 384-float vectors, one per input text.
    """
    if not texts:
        return []

    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=64)
    return [v.tolist() for v in vectors]
