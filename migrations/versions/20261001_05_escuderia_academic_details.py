"""Add course and school details to teams.

Revision ID: 20261001_05
Revises: 20260930_04
Create Date: 2026-10-01
"""
from alembic import op
import sqlalchemy as sa


revision = "20261001_05"
down_revision = "20260930_04"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("escuderia", sa.Column("curso", sa.String(length=100), nullable=True))
    op.add_column("escuderia", sa.Column("etapa", sa.String(length=50), nullable=True))
    op.add_column("escuderia", sa.Column("periodo", sa.String(length=50), nullable=True))
    op.add_column("escuderia", sa.Column("escola", sa.String(length=150), nullable=True))


def downgrade():
    op.drop_column("escuderia", "escola")
    op.drop_column("escuderia", "periodo")
    op.drop_column("escuderia", "etapa")
    op.drop_column("escuderia", "curso")
