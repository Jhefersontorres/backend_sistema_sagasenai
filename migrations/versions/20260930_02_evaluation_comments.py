"""Add evaluation comments.

Revision ID: 20260930_02
Revises: 20260930_01
Create Date: 2026-09-30
"""
from alembic import op
import sqlalchemy as sa


revision = "20260930_02"
down_revision = "20260930_01"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "avaliacao",
        sa.Column("comentario", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column("avaliacao", "comentario")
