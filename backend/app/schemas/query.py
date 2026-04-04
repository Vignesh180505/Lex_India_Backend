"""Pydantic schemas for query request and response validation.

These schemas enforce strict typing at the API boundary:
- QueryRequest validates incoming user queries.
- QueryResponse structures the full RAG pipeline output.
- LawResult represents a single matched law within the response.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """Request body for POST /api/query."""

    issue: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Plain-language description of the legal problem.",
        examples=["My landlord is not returning my security deposit after 3 months"],
    )
    language: str = Field(
        default="en",
        pattern="^(en|ta|hi)$",
        description="Response language code: en (English), ta (Tamil), hi (Hindi).",
    )


class LawResult(BaseModel):
    """A single law section returned in the query response."""

    section_id: str = Field(..., description="Unique section identifier, e.g. CPA-72.")
    act_name: str = Field(..., description="Full name of the Act.")
    section_number: str = Field(..., description="Section number within the Act.")
    section_title: str = Field(..., description="Title of the section.")
    original_text: str = Field(..., description="Verbatim original legal text.")
    simplified: str = Field(
        ..., description="Simplified explanation in the requested language."
    )
    severity: str = Field(
        ...,
        pattern="^(low|medium|high)$",
        description="Severity classification: low, medium, or high.",
    )
    punishment: Optional[str] = Field(
        None, description="The specific punishment/penalty for this law section."
    )
    filing_link: Optional[str] = Field(
        None, description="URL to the official eCourts filing portal."
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score (1.0 = most relevant).",
    )


class QueryResponse(BaseModel):
    """Response body for POST /api/query."""

    query_id: str = Field(..., description="Unique identifier for this query.")
    detected_language: str = Field(
        ..., description="Detected language of the input query."
    )
    ai_summary: str = Field(
        ..., description="AI-generated plain-language summary of the legal situation."
    )
    laws: List[LawResult] = Field(
        default_factory=list,
        description="List of applicable law sections, sorted by relevance.",
    )
    response_ms: int = Field(
        ..., description="Total response time in milliseconds."
    )
