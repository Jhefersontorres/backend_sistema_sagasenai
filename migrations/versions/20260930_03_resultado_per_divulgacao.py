"""Scope result uniqueness to its disclosure.

Revision ID: 20260930_03
Revises: 20260930_02
Create Date: 2026-09-30
"""
from alembic import context, op
from sqlalchemy import inspect


revision = "20260930_03"
down_revision = "20260930_02"
branch_labels = None
depends_on = None


OLD_UNIQUE_COLUMNS = {"id_escuderia", "nota_final"}
NEW_UNIQUE_NAME = "uq_resultado_escuderia_divulgacao"


def _old_unique_name():
    if context.is_offline_mode():
        return "uq_resultado_escuderia_nota_final"

    constraints = inspect(op.get_bind()).get_unique_constraints("resultado")
    for constraint in constraints:
        if set(constraint.get("column_names") or ()) == OLD_UNIQUE_COLUMNS:
            return constraint["name"]

    raise RuntimeError(
        "Could not find the legacy unique constraint on resultado "
        "(id_escuderia, nota_final)."
    )


def upgrade():
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("resultado") as batch_op:
            batch_op.drop_constraint(
                _old_unique_name(),
                type_="unique",
            )
            batch_op.create_unique_constraint(
                NEW_UNIQUE_NAME,
                ["id_escuderia", "id_divulgacao"],
            )
        return

    op.drop_constraint(
        _old_unique_name(),
        "resultado",
        type_="unique",
    )
    op.create_unique_constraint(
        NEW_UNIQUE_NAME,
        "resultado",
        ["id_escuderia", "id_divulgacao"],
    )


def downgrade():
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("resultado") as batch_op:
            batch_op.drop_constraint(
                NEW_UNIQUE_NAME,
                type_="unique",
            )
            batch_op.create_unique_constraint(
                "uq_resultado_escuderia_nota_final",
                ["id_escuderia", "nota_final"],
            )
        return

    op.drop_constraint(
        NEW_UNIQUE_NAME,
        "resultado",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_resultado_escuderia_nota_final",
        "resultado",
        ["id_escuderia", "nota_final"],
    )
