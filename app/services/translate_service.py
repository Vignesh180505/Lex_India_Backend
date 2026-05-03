"""Language detection and query translation service.

Detects the input language (English, Tamil, or Hindi) and translates
non-English queries to English before embedding. This is necessary because
the embedding model and vector index operate in English-space.
"""

import logging
import re
from typing import Optional

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger("lexindia.services.translate")

# ── Unicode Range Detection ──────────────────────────────────────────────
# Tamil: U+0B80 to U+0BFF
TAMIL_PATTERN = re.compile(r"[\u0B80-\u0BFF]")
# Hindi (Devanagari): U+0900 to U+097F
HINDI_PATTERN = re.compile(r"[\u0900-\u097F]")

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """Get the OpenAI client (singleton)."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


async def detect(text: str) -> str:
    """Detect the language of the input text.

    Uses Unicode range analysis (fast, no API call needed).

    Returns:
        Language code: 'en', 'ta', or 'hi'.
    """
    if not text or not text.strip():
        return "en"

    # Count characters in each script range
    tamil_chars = len(TAMIL_PATTERN.findall(text))
    hindi_chars = len(HINDI_PATTERN.findall(text))
    total_chars = len(text.strip())

    # If >20% of characters are Tamil/Hindi, classify as that language
    if tamil_chars > 0 and tamil_chars / total_chars > 0.2:
        logger.info(f"Detected language: Tamil ({tamil_chars}/{total_chars} chars)")
        return "ta"

    if hindi_chars > 0 and hindi_chars / total_chars > 0.2:
        logger.info(f"Detected language: Hindi ({hindi_chars}/{total_chars} chars)")
        return "hi"

    return "en"


async def translate_to_english(text: str, source_lang: Optional[str] = None) -> str:
    """Translate Tamil or Hindi text to English using GPT-4o.

    The embedding model operates in English-space, so non-English queries
    must be translated before embedding for accurate vector search.

    Args:
        text: The text to translate.
        source_lang: Source language code ('ta' or 'hi'). Auto-detected if None.

    Returns:
        English translation of the input text.
    """
    if not source_lang:
        source_lang = await detect(text)

    if source_lang == "en":
        return text

    lang_name = "Tamil" if source_lang == "ta" else "Hindi"

    client = _get_client()

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a translator. Translate the following {lang_name} text "
                        f"to English. Preserve the original meaning accurately. "
                        f"Return ONLY the English translation, nothing else."
                    ),
                },
                {"role": "user", "content": text},
            ],
            max_tokens=500,
            temperature=0.1,
        )

        translated = response.choices[0].message.content.strip()
        logger.info(f"Translated {lang_name} → English: '{text[:50]}...' → '{translated[:50]}...'")
        return translated

    except Exception as e:
        logger.error(f"Translation failed ({lang_name} → English): {e}")
        # Fallback: return original text (search will be less accurate but won't crash)
        return text
