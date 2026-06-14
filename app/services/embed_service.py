"""all-MiniLM-L6-v2 embedding service (Call 2) — converts text to 384-dim vectors.

This is the EMBEDDING model — completely separate from GPT-4o (Call 1).
- Input: plain text string (always simplified_en, never section_text)
- Output: list of 384 floats (a mathematical vector, NOT readable text)
- Model: sentence-transformers/all-MiniLM-L6-v2 via FastEmbed (ONNX Runtime)

FastEmbed uses ONNX Runtime instead of PyTorch, reducing RAM from ~500MB to ~150MB.
The model produces IDENTICAL 384-dim vectors, so existing database embeddings remain
fully compatible — no re-embedding needed.

The model is loaded ONCE at startup and reused for all requests.
Must be the same model used in setup/generate_embeddings.py for compatible vectors.
"""

import logging
from typing import Optional

from fastembed import TextEmbedding

from app.config import settings

logger = logging.getLogger("lexindia.embed")

# ── Singleton Model ───────────────────────────────────────────────────────
_model: Optional[TextEmbedding] = None

# FastEmbed uses its own model naming convention
# Map from sentence-transformers name to fastembed name
_FASTEMBED_MODEL_MAP = {
    "sentence-transformers/all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
}


def get_model() -> TextEmbedding:
    """Load the embedding model (singleton — only loads once)."""
    global _model
    if _model is None:
        model_name = _FASTEMBED_MODEL_MAP.get(
            settings.EMBEDDING_MODEL, settings.EMBEDDING_MODEL
        )
        logger.info(f"Loading embedding model via FastEmbed (ONNX): {model_name}")
        _model = TextEmbedding(model_name=model_name)
        # Quick test to verify dimension
        test_vec = list(_model.embed(["test"]))[0]
        logger.info(
            f"Model loaded. Test embedding dim: {len(test_vec)}"
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
    # fastembed.embed() returns a generator of numpy arrays
    vector = list(model.embed([text]))[0]
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
    # fastembed handles batching internally
    vectors = list(model.embed(texts, batch_size=64))
    return [v.tolist() for v in vectors]
