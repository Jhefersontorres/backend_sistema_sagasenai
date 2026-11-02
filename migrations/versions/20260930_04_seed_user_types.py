"""Seed the required user types.

Revision ID: 20260930_04
Revises: 20260930_03
Create Date: 2026-09-30
"""
from alembic import op


revision = "20260930_04"
down_revision = "20260930_03"
branch_labels = None
depends_on = None


def upgrade():
    for user_type in ("MENTOR", "AVALIADOR"):
        op.execute(
            "INSERT INTO tipousuario (descricao) "
            f"SELECT '{user_type}' "
            "WHERE NOT EXISTS ("
            "SELECT 1 FROM tipousuario "
            f"WHERE descricao = '{user_type}'"
            ")"
        )


def downgrade():
    op.execute(
        "DELETE FROM tipousuario "
        "WHERE descricao IN ('MENTOR', 'AVALIADOR') "
        "AND id_tipousuario NOT IN ("
        "SELECT id_tipousuario FROM usuario"
        ")"
    )
