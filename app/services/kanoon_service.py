"""Indian Kanoon API integration for judgment retrieval.

Fetches Supreme Court and High Court judgments for given law sections.
All failures return empty list — never propagates to main pipeline.
All calls have 8-second timeout. Concurrent fetches via asyncio.gather().
"""

import asyncio
import logging
import re
from app.config import settings
from app.schemas.query import JudgmentResult
from app.services.openai_client import openai_client
import httpx

logger = logging.getLogger("lexindia.kanoon")
KANOON_BASE_URL = "https://api.indiankanoon.org"


def classify_precedent(doc: dict) -> str:
    """Classify judgment precedent type from document metadata.

    Args:
        doc: Raw document dict from Indian Kanoon API response.

    Returns:
        One of: "positive" | "negative" | "neutral" | "overruled"
    """
    text = (
        doc.get("title", "") + " " + doc.get("headline", "")
    ).lower()

    if any(word in text for word in ["overruled", "overturned", "reversed"]):
        return "overruled"
    if any(word in text for word in ["upheld", "affirmed", "allowed", "granted"]):
        return "positive"
    if any(word in text for word in ["dismissed", "rejected", "denied", "quashed"]):
        return "negative"
    return "neutral"


def extract_court_name(doc: dict) -> str:
    """Extract court name from document. Returns 'Unknown Court' on failure."""
    return doc.get("docsource", doc.get("court", "Unknown Court"))


def extract_year(doc: dict) -> int:
    """Extract judgment year from document. Returns 0 on failure."""
    date_str = doc.get("decision_date", doc.get("judgement_date", ""))
    match = re.search(r"\d{4}", date_str)
    return int(match.group()) if match else 0


async def summarise_judgment(headline: str) -> str:
    """Generate 2-sentence judgment summary using GPT-4o.

    Args:
        headline: Raw headline text from Indian Kanoon API.

    Returns:
        2-sentence plain summary, or "Summary not available." on failure.
    """
    if not headline or len(headline) < 20:
        return "Summary not available."
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": (
                    "Summarise this Indian court judgment headline in exactly "
                    "2 sentences for a lawyer audience. Be precise and factual. "
                    f"Do not add information not present in the headline:\n\n{headline}"
                )
            }],
            max_tokens=120,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Judgment summarisation failed: {e}")
        return headline[:200] if headline else "Summary not available."


async def fetch_kanoon_judgments(
    section_id: str,
    act_name: str,
    section_number: str,
    max_results: int = 3,
) -> list[JudgmentResult]:
    """Fetch top judgments from Indian Kanoon for a specific law section.

    Args:
        section_id: e.g. "IPC-302"
        act_name: e.g. "Indian Penal Code 1860"
        section_number: e.g. "302"
        max_results: Maximum judgments to return (default 3).

    Returns:
        List of JudgmentResult. Returns [] on any error — never raises.
    """
    query = f"{act_name} section {section_number}"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                f"{KANOON_BASE_URL}/search/",
                data={"formInput": query, "pagenum": 0},
                headers={"Authorization": f"Token {settings.INDIAN_KANOON_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()

        docs = data.get("docs", [])[:max_results]
        summaries = await asyncio.gather(
            *[summarise_judgment(doc.get("headline", "")) for doc in docs],
            return_exceptions=True,
        )

        judgments = []
        for doc, summary in zip(docs, summaries):
            judgments.append(JudgmentResult(
                title=doc.get("title", "Untitled"),
                court=extract_court_name(doc),
                year=extract_year(doc),
                citation=doc.get("citation", ""),
                summary=summary if isinstance(summary, str) else "Summary unavailable.",
                precedent_type=classify_precedent(doc),
                url=f"https://indiankanoon.org/doc/{doc.get('tid', '')}/",
            ))
        return judgments

    except Exception as e:
        logger.warning(f"Kanoon fetch failed for {section_id}: {e}")
        return []
