"""Court Judgments API router — all four judgment capabilities.

Routes:
    POST /api/judgments/search          — Search judgments by query
    GET  /api/judgments/similar          — Similar past cases for a query
    POST /api/judgments/outcome-analysis — Win/loss stats for judgments
"""

import asyncio
import hashlib
import json
import logging
import re
from datetime import date as date_type
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.judgment import JudgmentCache
from app.schemas.judgment import (
    JudgmentCard,
    JudgmentSearchRequest,
    JudgmentSearchResponse,
    OutcomeAnalysisRequest,
    OutcomeAnalysisResponse,
    SimilarCasesResponse,
    SingleOutcome,
)
from app.services.cache_service import get_redis
from app.services.embed_service import embed

logger = logging.getLogger("lexindia.routers.judgments")
router = APIRouter(tags=["Court Judgments"])

KANOON_BASE_URL = "https://api.indiankanoon.org"
KANOON_TIMEOUT = 10.0


# ── Helpers ───────────────────────────────────────────────────────────────

def _query_hash(query: str) -> str:
    """Create a deterministic hash for a query string."""
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


def _extract_date(doc: dict) -> str:
    """Extract date string from an Indian Kanoon doc dict."""
    return doc.get("publishdate", doc.get("decision_date", doc.get("judgement_date", "")))


def _extract_court(doc: dict) -> str:
    """Extract court name from an Indian Kanoon doc dict."""
    return doc.get("docsource", doc.get("court", "Unknown Court"))


def _extract_snippet(doc: dict) -> str:
    """Extract a clean text snippet from headline/headnote."""
    raw = doc.get("headline", doc.get("headnote", ""))
    # Strip HTML tags
    clean = re.sub(r"<[^>]+>", "", raw)
    return clean[:500] if clean else "No snippet available."


def _build_card(doc: dict) -> JudgmentCard:
    """Build a JudgmentCard from a raw Indian Kanoon doc dict."""
    tid = str(doc.get("tid", doc.get("docid", "")))
    return JudgmentCard(
        title=doc.get("title", "Untitled"),
        court=_extract_court(doc),
        date=_extract_date(doc),
        snippet=_extract_snippet(doc),
        doc_id=tid,
        url=f"https://indiankanoon.org/doc/{tid}/",
    )


async def _simplify_snippet(snippet: str) -> str:
    """Use Gemini/LLM to simplify a legal snippet for citizen mode.

    Falls back to truncated raw snippet on any failure.
    """
    try:
        from app.services.generate_service import _call_llm_with_fallback

        result = await _call_llm_with_fallback(
            system_prompt=(
                "You are a legal simplifier. Rewrite the following court judgment "
                "excerpt in 2–3 simple sentences a non-lawyer can understand. "
                "Respond ONLY with the simplified text, no JSON."
            ),
            user_message=snippet[:1000],
            task_name="Simplify judgment snippet",
        )
        if isinstance(result, dict):
            return result.get("text", result.get("simplified", snippet[:300]))
        return str(result) if result else snippet[:300]
    except Exception as e:
        logger.warning(f"Snippet simplification failed: {e}")
        return snippet[:300]


async def _search_kanoon(
    query: str,
    pagenum: int = 0,
) -> dict:
    """Call Indian Kanoon search API and return the raw JSON response.

    Raises HTTPException 503 if the API is unreachable.
    """
    if not settings.INDIAN_KANOON_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Indian Kanoon API key not configured.",
        )

    try:
        async with httpx.AsyncClient(timeout=KANOON_TIMEOUT, follow_redirects=True) as client:
            response = await client.post(
                f"{KANOON_BASE_URL}/search/",
                data={"formInput": query, "pagenum": pagenum},
                headers={"Authorization": f"Token {settings.INDIAN_KANOON_API_KEY}"},
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error("Indian Kanoon API timeout")
        raise HTTPException(
            status_code=503,
            detail="Indian Kanoon API is temporarily unavailable (timeout).",
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Indian Kanoon API HTTP error: {e.response.status_code}")
        raise HTTPException(
            status_code=503,
            detail=f"Indian Kanoon API returned error {e.response.status_code}.",
        )
    except Exception as e:
        logger.error(f"Indian Kanoon API error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Indian Kanoon API is temporarily unavailable.",
        )


async def _fetch_doc_text(doc_id: str) -> str:
    """Fetch the full text of a judgment from Indian Kanoon doc API."""
    try:
        async with httpx.AsyncClient(timeout=KANOON_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(
                f"{KANOON_BASE_URL}/doc/{doc_id}/",
                headers={"Authorization": f"Token {settings.INDIAN_KANOON_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()
            # The doc endpoint returns the text in the "doc" field
            raw = data.get("doc", data.get("text", ""))
            # Strip HTML tags
            return re.sub(r"<[^>]+>", "", raw)[:15000]  # Cap at 15k chars for LLM
    except Exception as e:
        logger.warning(f"Failed to fetch doc {doc_id}: {e}")
        return ""


async def _cache_judgment_to_db(
    doc_id: str,
    title: str,
    court: str,
    date_str: str,
    full_text: str,
    db: AsyncSession,
) -> None:
    """Store a fetched judgment in the judgments_cache table with embedding."""
    try:
        # Check if already cached
        existing = await db.execute(
            select(JudgmentCache).where(JudgmentCache.doc_id == doc_id)
        )
        if existing.scalars().first():
            return

        # Parse date
        parsed_date = None
        if date_str:
            match = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", date_str)
            if match:
                try:
                    parsed_date = date_type(
                        int(match.group(3)),
                        int(match.group(2)),
                        int(match.group(1)),
                    )
                except ValueError:
                    pass

        # Generate embedding from the full text (first 2000 chars)
        embedding_vector = None
        if full_text and len(full_text.strip()) > 50:
            try:
                embedding_vector = embed(full_text[:2000])
            except Exception as e:
                logger.warning(f"Embedding generation failed for doc {doc_id}: {e}")

        judgment = JudgmentCache(
            doc_id=doc_id,
            title=title,
            court=court,
            date=parsed_date,
            full_text=full_text[:50000] if full_text else None,
            embedding=embedding_vector,
        )
        db.add(judgment)
        await db.flush()
        logger.info(f"Cached judgment doc_id={doc_id}")
    except Exception as e:
        logger.warning(f"Failed to cache judgment {doc_id}: {e}")


# ── Route 1: Search Judgments ─────────────────────────────────────────────

@router.post("/judgments/search", response_model=JudgmentSearchResponse)
async def search_judgments(
    request: JudgmentSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> JudgmentSearchResponse:
    """Search Indian Kanoon for court judgments matching the query.

    Results are cached in Redis for 24 hours. In Citizen Mode, snippets
    are simplified using the LLM before returning.
    """
    # Build the full query with optional court/category filters
    full_query = request.query
    if request.court:
        full_query += f" {request.court}"
    if request.category:
        full_query += f" {request.category}"

    logger.info(f"Judgment search: '{full_query[:80]}' (mode={request.mode}, page={request.page})")

    # Check Redis cache
    cache_key = f"lexindia:judgment:{_query_hash(full_query)}:p{request.page}"
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            logger.info(f"Judgment cache HIT: {cache_key}")
            data = json.loads(cached)
            return JudgmentSearchResponse(**data)
    except Exception as e:
        logger.warning(f"Redis cache check failed: {e}")

    # Call Indian Kanoon API
    raw = await _search_kanoon(full_query, pagenum=request.page)
    docs = raw.get("docs", [])
    raw_found = raw.get("found", len(docs))
    
    total = len(docs)
    if isinstance(raw_found, int):
        total = raw_found
    elif isinstance(raw_found, str):
        match = re.search(r'of\s+([\d,]+)', raw_found)
        if match:
            total = int(match.group(1).replace(',', ''))
        else:
            try:
                total = int(raw_found)
            except ValueError:
                pass

    # Build judgment cards
    cards = [_build_card(doc) for doc in docs[:10]]

    # Citizen mode: simplify snippets using LLM
    if request.mode == "citizen" and cards:
        simplified = await asyncio.gather(
            *[_simplify_snippet(card.snippet) for card in cards],
            return_exceptions=True,
        )
        for card, simp in zip(cards, simplified):
            if isinstance(simp, str) and simp:
                card.snippet = simp

    # Cache the full text of each judgment in the background
    for doc in docs[:10]:
        tid = str(doc.get("tid", doc.get("docid", "")))
        if tid:
            try:
                await _cache_judgment_to_db(
                    doc_id=tid,
                    title=doc.get("title", ""),
                    court=_extract_court(doc),
                    date_str=_extract_date(doc),
                    full_text="",  # Full text fetched on demand in outcome analysis
                    db=db,
                )
            except Exception:
                pass

    response = JudgmentSearchResponse(
        query=request.query,
        total_found=total,
        page=request.page,
        judgments=cards,
    )

    # Store in Redis cache (24h TTL)
    try:
        redis = await get_redis()
        await redis.setex(
            cache_key,
            settings.CACHE_TTL_SECONDS,
            json.dumps(response.model_dump(), ensure_ascii=False, default=str),
        )
    except Exception as e:
        logger.warning(f"Redis cache set failed: {e}")

    return response


# ── Route 2: Similar Past Cases ───────────────────────────────────────────

@router.get("/judgments/similar", response_model=SimilarCasesResponse)
async def get_similar_cases(
    query: str = Query(..., min_length=3, description="Legal query to find similar cases for."),
    mode: str = Query(default="citizen", description="citizen or lawyer"),
    db: AsyncSession = Depends(get_db),
) -> SimilarCasesResponse:
    """Fetch 3-5 similar past judgments for a given legal query.

    Used on the /results page to show related court cases below the
    law explanation.
    """
    logger.info(f"Similar cases for: '{query[:80]}'")

    # Check Redis cache
    cache_key = f"lexindia:similar:{_query_hash(query)}"
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            logger.info(f"Similar cases cache HIT: {cache_key}")
            data = json.loads(cached)
            return SimilarCasesResponse(**data)
    except Exception as e:
        logger.warning(f"Redis cache check failed: {e}")

    # Fetch from Indian Kanoon (top 5)
    raw = await _search_kanoon(query, pagenum=0)
    docs = raw.get("docs", [])[:5]

    cards = [_build_card(doc) for doc in docs]

    # Citizen mode: simplify snippets
    if mode == "citizen" and cards:
        simplified = await asyncio.gather(
            *[_simplify_snippet(card.snippet) for card in cards],
            return_exceptions=True,
        )
        for card, simp in zip(cards, simplified):
            if isinstance(simp, str) and simp:
                card.snippet = simp

    response = SimilarCasesResponse(query=query, cases=cards)

    # Cache for 24h
    try:
        redis = await get_redis()
        await redis.setex(
            cache_key,
            settings.CACHE_TTL_SECONDS,
            json.dumps(response.model_dump(), ensure_ascii=False, default=str),
        )
    except Exception as e:
        logger.warning(f"Redis cache set failed: {e}")

    return response


# ── Route 3: Outcome Analysis ────────────────────────────────────────────

OUTCOME_PROMPT = """Analyze this Indian court judgment. Return ONLY a JSON object with:
{
  "outcome": "petitioner_won" | "respondent_won" | "partial" | "unclear",
  "petitioner_type": string (e.g. "tenant", "employee", "citizen"),
  "respondent_type": string (e.g. "landlord", "employer", "state"),
  "key_reason": string (one sentence summary of why)
}

Do not include any text outside the JSON object."""


@router.post("/judgments/outcome-analysis", response_model=OutcomeAnalysisResponse)
async def analyze_outcomes(
    request: OutcomeAnalysisRequest,
    db: AsyncSession = Depends(get_db),
) -> OutcomeAnalysisResponse:
    """Analyse win/loss outcomes for a set of judgment documents.

    Fetches full text from Indian Kanoon for each doc_id, passes it
    through the LLM for outcome classification, then aggregates results.
    """
    logger.info(f"Outcome analysis: query='{request.query[:60]}', docs={len(request.doc_ids)}")

    from app.services.generate_service import _call_llm_with_fallback

    outcomes: list[SingleOutcome] = []

    # Fetch and analyse each judgment concurrently
    async def _analyse_single(doc_id: str) -> Optional[SingleOutcome]:
        """Fetch full text and run LLM outcome analysis for one judgment."""
        try:
            # Check DB cache first
            result = await db.execute(
                select(JudgmentCache).where(JudgmentCache.doc_id == doc_id)
            )
            cached = result.scalars().first()

            if cached and cached.outcome:
                return SingleOutcome(
                    doc_id=doc_id,
                    outcome=cached.outcome,
                    petitioner_type=cached.petitioner_type or "unknown",
                    respondent_type=cached.respondent_type or "unknown",
                    key_reason=cached.key_reason or "Cached result",
                )

            # Fetch full text
            full_text = ""
            if cached and cached.full_text:
                full_text = cached.full_text
            else:
                full_text = await _fetch_doc_text(doc_id)

            if not full_text or len(full_text.strip()) < 100:
                return SingleOutcome(
                    doc_id=doc_id,
                    outcome="unclear",
                    petitioner_type="unknown",
                    respondent_type="unknown",
                    key_reason="Insufficient judgment text available.",
                )

            # Call LLM for outcome analysis
            parsed = await _call_llm_with_fallback(
                OUTCOME_PROMPT,
                full_text[:10000],
                f"Outcome analysis for doc {doc_id}",
            )

            if not parsed:
                return SingleOutcome(
                    doc_id=doc_id,
                    outcome="unclear",
                    petitioner_type="unknown",
                    respondent_type="unknown",
                    key_reason="LLM analysis failed.",
                )

            outcome_val = parsed.get("outcome", "unclear")
            if outcome_val not in ("petitioner_won", "respondent_won", "partial", "unclear"):
                outcome_val = "unclear"

            single = SingleOutcome(
                doc_id=doc_id,
                outcome=outcome_val,
                petitioner_type=parsed.get("petitioner_type", "unknown"),
                respondent_type=parsed.get("respondent_type", "unknown"),
                key_reason=parsed.get("key_reason", "No reason provided."),
            )

            # Update DB cache with outcome analysis
            try:
                if cached:
                    cached.outcome = single.outcome
                    cached.petitioner_type = single.petitioner_type
                    cached.respondent_type = single.respondent_type
                    cached.key_reason = single.key_reason
                    if not cached.full_text:
                        cached.full_text = full_text[:50000]
                else:
                    await _cache_judgment_to_db(
                        doc_id=doc_id,
                        title="",
                        court="",
                        date_str="",
                        full_text=full_text,
                        db=db,
                    )
                    # Re-fetch and update outcome fields
                    result = await db.execute(
                        select(JudgmentCache).where(JudgmentCache.doc_id == doc_id)
                    )
                    new_cached = result.scalars().first()
                    if new_cached:
                        new_cached.outcome = single.outcome
                        new_cached.petitioner_type = single.petitioner_type
                        new_cached.respondent_type = single.respondent_type
                        new_cached.key_reason = single.key_reason

                await db.flush()
            except Exception as e:
                logger.warning(f"Failed to update DB cache for doc {doc_id}: {e}")

            return single

        except Exception as e:
            logger.error(f"Outcome analysis failed for doc {doc_id}: {e}")
            return SingleOutcome(
                doc_id=doc_id,
                outcome="unclear",
                petitioner_type="unknown",
                respondent_type="unknown",
                key_reason=f"Analysis error: {str(e)[:100]}",
            )

    # Run all analyses concurrently
    results = await asyncio.gather(
        *[_analyse_single(did) for did in request.doc_ids],
        return_exceptions=True,
    )

    for r in results:
        if isinstance(r, SingleOutcome):
            outcomes.append(r)
        elif isinstance(r, Exception):
            logger.error(f"Outcome analysis exception: {r}")

    # Aggregate results
    total = len(outcomes)
    pet_wins = sum(1 for o in outcomes if o.outcome == "petitioner_won")
    resp_wins = sum(1 for o in outcomes if o.outcome == "respondent_won")
    partial = sum(1 for o in outcomes if o.outcome == "partial")
    unclear = sum(1 for o in outcomes if o.outcome == "unclear")

    win_pct = round((pet_wins / total) * 100, 1) if total > 0 else 0.0

    # Build human-readable favour label
    # Try to use the most common petitioner/respondent types
    pet_types = [o.petitioner_type for o in outcomes if o.petitioner_type != "unknown"]
    resp_types = [o.respondent_type for o in outcomes if o.respondent_type != "unknown"]
    pet_label = max(set(pet_types), key=pet_types.count) if pet_types else "petitioners"
    resp_label = max(set(resp_types), key=resp_types.count) if resp_types else "respondents"

    if win_pct >= 60:
        favour_label = f"Courts favour {pet_label} in {win_pct}% of similar cases"
    elif (100 - win_pct - (partial / total * 100 if total > 0 else 0)) >= 60:
        favour_label = f"Courts favour {resp_label} in {round(resp_wins / total * 100, 1) if total > 0 else 0}% of similar cases"
    else:
        favour_label = f"Mixed outcomes — no clear trend ({pet_wins} for {pet_label}, {resp_wins} for {resp_label})"

    return OutcomeAnalysisResponse(
        total_cases=total,
        petitioner_wins=pet_wins,
        respondent_wins=resp_wins,
        partial=partial,
        unclear=unclear,
        win_percentage=win_pct,
        favour_label=favour_label,
        outcomes=outcomes,
    )
