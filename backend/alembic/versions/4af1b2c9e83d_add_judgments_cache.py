"""add_judgments_cache table

Revision ID: 4af1b2c9e83d
Revises: 3ee00c1dd27a
Create Date: 2026-05-01 18:58:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4af1b2c9e83d'
down_revision: Union[str, None] = '3ee00c1dd27a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgvector extension exists (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        'judgments_cache',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('doc_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('court', sa.String(length=100), nullable=True),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('outcome', sa.String(length=50), nullable=True),
        sa.Column('petitioner_type', sa.String(length=100), nullable=True),
        sa.Column('respondent_type', sa.String(length=100), nullable=True),
        sa.Column('key_reason', sa.Text(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doc_id'),
    )
    op.create_index('ix_judgments_cache_doc_id', 'judgments_cache', ['doc_id'])

    # Add the vector column using raw SQL (pgvector type not natively supported by Alembic)
    op.execute("ALTER TABLE judgments_cache ADD COLUMN embedding vector(384)")


def downgrade() -> None:
    op.drop_index('ix_judgments_cache_doc_id', table_name='judgments_cache')
    op.drop_table('judgments_cache')
