"""Text cleaning and section-level chunking for scraped legal data.

Cleaning rules:
- Strip all residual HTML tags using BeautifulSoup's .get_text()
- Collapse multiple consecutive whitespace/newlines into single spaces
- Remove unicode control characters and zero-width spaces
- Preserve section numbering and original capitalisation exactly
- Do NOT paraphrase or modify the original legal text

Chunking rule:
- Each scraped section is already one chunk (1 section = 1 row = 1 vector)
- Never split sections further or merge multiple sections
- Discard records where section_text is empty or under 20 characters
"""

import re
import logging
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger("lexindia.scraper.cleaner")

# Unicode control characters and zero-width spaces to strip
UNICODE_JUNK_PATTERN = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f"       # C0 control chars (except \t \n \r)
    r"\u200b\u200c\u200d\ufeff\u00ad"           # Zero-width spaces, BOM, soft hyphen
    r"\u2028\u2029"                              # Line/paragraph separators
    r"]"
)

# Collapse multiple whitespace (but preserve single newlines for readability)
MULTI_SPACE_PATTERN = re.compile(r"[ \t]+")
MULTI_NEWLINE_PATTERN = re.compile(r"\n{3,}")

MIN_TEXT_LENGTH = 100  # Increased from 20 — require substantial content


def strip_html(text: str) -> str:
    """Remove any residual HTML tags from text."""
    if "<" in text and ">" in text:
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ")
    return text


def remove_unicode_junk(text: str) -> str:
    """Remove unicode control characters and zero-width spaces."""
    return UNICODE_JUNK_PATTERN.sub("", text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/tabs into single space, limit newlines."""
    text = MULTI_SPACE_PATTERN.sub(" ", text)
    text = MULTI_NEWLINE_PATTERN.sub("\n\n", text)
    return text.strip()


def clean_text(raw_text: str) -> str:
    """Apply all cleaning rules to raw scraped text.

    Processing order:
    1. Strip residual HTML tags
    2. Remove unicode junk characters
    3. Normalize whitespace
    """
    text = strip_html(raw_text)
    text = remove_unicode_junk(text)
    text = normalize_whitespace(text)
    return text


def clean_section(raw_section: Dict) -> Optional[Dict]:
    """Clean a single section dict and validate it.

    Args:
        raw_section: Raw dict from the scraper with section_text and metadata.

    Returns:
        Cleaned section dict, or None if the section is invalid.
    """
    section_id = raw_section.get("section_id", "unknown")

    # Clean the section text
    raw_text = raw_section.get("section_text", "")
    if not raw_text:
        logger.warning(f"Empty section_text for {section_id} — discarding")
        return None

    cleaned_text = clean_text(raw_text)

    # Validate minimum length
    if len(cleaned_text) < MIN_TEXT_LENGTH:
        logger.warning(
            f"Section {section_id} text too short ({len(cleaned_text)} chars) — discarding"
        )
        return None

    # Clean other text fields
    cleaned_title = clean_text(raw_section.get("section_title", ""))
    cleaned_punishment = None
    if raw_section.get("punishment"):
        cleaned_punishment = clean_text(raw_section["punishment"])

    # Build cleaned section dict
    cleaned = {
        "section_id": section_id,
        "act_name": raw_section.get("act_name", ""),
        "act_code": raw_section.get("act_code", ""),
        "section_number": raw_section.get("section_number", ""),
        "section_title": cleaned_title,
        "section_text": cleaned_text,         # Verbatim after cleaning — no paraphrasing
        "punishment": cleaned_punishment,
        "amendment_year": raw_section.get("amendment_year"),
        "source_url": raw_section.get("source_url", ""),
        "scraped_at": raw_section.get("scraped_at"),
    }

    return cleaned


def clean_and_chunk(raw_sections: List[Dict]) -> List[Dict]:
    """Clean and validate all sections — one section = one chunk = one future DB row.

    This function enforces the mandatory chunking rule:
    - Each section stays as one record (never split or merged)
    - Invalid sections are discarded and logged

    Args:
        raw_sections: List of raw section dicts from the scraper.

    Returns:
        List of cleaned, validated section dicts.
    """
    cleaned_sections: List[Dict] = []
    discarded_count = 0

    logger.info(f"Cleaning {len(raw_sections)} raw sections")

    for raw in raw_sections:
        cleaned = clean_section(raw)
        if cleaned:
            cleaned_sections.append(cleaned)
        else:
            discarded_count += 1

    logger.info(
        f"Cleaning complete: {len(cleaned_sections)} valid sections, "
        f"{discarded_count} discarded"
    )

    # Final validation — check for duplicate section_ids
    seen_ids = set()
    unique_sections = []
    for section in cleaned_sections:
        sid = section["section_id"]
        if sid in seen_ids:
            logger.warning(f"Duplicate section_id: {sid} — keeping first occurrence only")
            continue
        seen_ids.add(sid)
        unique_sections.append(section)

    if len(unique_sections) < len(cleaned_sections):
        logger.info(
            f"Deduplication: {len(cleaned_sections)} → {len(unique_sections)} sections"
        )

    return unique_sections
