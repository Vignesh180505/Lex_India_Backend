"""Pydantic schemas for court judgment search, outcome analysis, and browsing.

Covers all four judgment capabilities:
1. Search Judgments by Query
2. Similar Past Cases
3. Win/Loss Outcome Analysis
4. Browse by Court and Category
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# ── Shared / Common ──────────────────────────────────────────────────────

class JudgmentCard(BaseModel):
    """A single judgment returned in search or similar-cases results."""

    title: str = Field(..., description="Case title.")
    court: str = Field(..., description="Court name (e.g. Supreme Court of India).")
    date: str = Field(..., description="Judgment date as string.")
    snippet: str = Field(..., description="Short excerpt from the judgment.")
    doc_id: str = Field(..., description="Indian Kanoon document ID.")
    url: str = Field(..., description="Full URL to the judgment on Indian Kanoon.")


# ── Capability 1: Search Judgments ────────────────────────────────────────

class JudgmentSearchRequest(BaseModel):
    """Request body for POST /api/judgments/search."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Legal search query.",
    )
    language: str = Field(
        default="en",
        pattern="^(en|ta|hi)$",
        description="Response language code.",
    )
    mode: Literal["citizen", "lawyer"] = Field(
        default="citizen",
        description="citizen = simplified snippets; lawyer = raw legal text.",
    )
    court: Optional[str] = Field(
        default=None,
        description="Optional court filter (e.g. 'Supreme Court').",
    )
    category: Optional[str] = Field(
        default=None,
        description="Optional category filter (e.g. 'Criminal', 'Civil').",
    )
    page: int = Field(default=0, ge=0, description="Page number (0-indexed).")


class JudgmentSearchResponse(BaseModel):
    """Response body for POST /api/judgments/search."""

    query: str
    total_found: int
    page: int
    judgments: List[JudgmentCard]


# ── Capability 2: Similar Past Cases ─────────────────────────────────────

class SimilarCasesResponse(BaseModel):
    """Response body for GET /api/judgments/similar."""

    query: str
    cases: List[JudgmentCard]


# ── Capability 3: Outcome Analysis ───────────────────────────────────────

class OutcomeAnalysisRequest(BaseModel):
    """Request body for POST /api/judgments/outcome-analysis."""

    query: str = Field(..., min_length=3, description="The legal query context.")
    doc_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of Indian Kanoon doc IDs to analyse.",
    )


class SingleOutcome(BaseModel):
    """LLM-parsed outcome for a single judgment."""

    doc_id: str
    outcome: Literal["petitioner_won", "respondent_won", "partial", "unclear"]
    petitioner_type: str
    respondent_type: str
    key_reason: str


class OutcomeAnalysisResponse(BaseModel):
    """Aggregated outcome analysis across multiple judgments."""

    total_cases: int
    petitioner_wins: int
    respondent_wins: int
    partial: int
    unclear: int
    win_percentage: float = Field(
        ..., description="Percentage of cases won by petitioner."
    )
    favour_label: str = Field(
        ...,
        description='Human-readable label, e.g. "Courts favour tenants in 68% of similar cases".',
    )
    outcomes: List[SingleOutcome]
