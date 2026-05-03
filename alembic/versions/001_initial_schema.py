"""Initial schema — laws, filing_links, query_logs tables + pgvector extension.

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-04-02

This migration creates the complete LexIndia database schema:
  - Enables the pgvector extension for vector similarity search
  - Creates the `laws` table with vector(384) embedding column
  - Creates the `filing_links` table for eCourts portal URLs
  - Creates the `query_logs` table for analytics
  - Creates the act_code index for browse filtering
  - NOTE: The IVFFlat embedding index is NOT created here —
    it must be built AFTER all embeddings are populated (see setup/build_index.py)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector


# Revision identifiers
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables and enable pgvector."""
    # ── Enable pgvector extension ──────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── Laws table ─────────────────────────────────────────────────────
    op.create_table(
        "laws",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("section_id", sa.String(50), unique=True, nullable=False),
        sa.Column("act_name", sa.Text(), nullable=False),
        sa.Column("act_code", sa.String(20), nullable=False),
        sa.Column("section_number", sa.String(20), nullable=False),
        sa.Column("section_title", sa.Text(), nullable=False),
        sa.Column("section_text", sa.Text(), nullable=False),
        sa.Column("simplified_en", sa.Text(), nullable=True),
        sa.Column("simplified_ta", sa.Text(), nullable=True),
        sa.Column("simplified_hi", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(10), nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("punishment", sa.Text(), nullable=True),
        sa.Column("amendment_year", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("filing_link", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Index for Act-based filtering in the browse page
    op.create_index("laws_act_code_idx", "laws", ["act_code"])

    # ── Filing Links table ─────────────────────────────────────────────
    op.create_table(
        "filing_links",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_type", sa.String(100), nullable=False),
        sa.Column("portal_name", sa.String(200), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── Query Logs table ───────────────────────────────────────────────
    op.create_table(
        "query_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(10), nullable=False),
        sa.Column("results_count", sa.Integer(), nullable=True),
        sa.Column("response_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Drop all tables and pgvector extension."""
    op.drop_table("query_logs")
    op.drop_table("filing_links")
    op.drop_index("laws_act_code_idx", table_name="laws")
    op.drop_table("laws")
    op.execute("DROP EXTENSION IF EXISTS vector")
