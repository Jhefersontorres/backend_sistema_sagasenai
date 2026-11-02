"""Create the legacy Sistema GP schema.

Revision ID: 20260930_01
Revises:
Create Date: 2026-09-30
"""
from alembic import op
import sqlalchemy as sa


revision = "20260930_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tipousuario",
        sa.Column("id_tipousuario", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("descricao", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id_tipousuario"),
    )

    op.create_table(
        "criterio",
        sa.Column("id_criterio", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("descricao", sa.String(length=250), nullable=False),
        sa.Column(
            "peso",
            sa.Numeric(precision=3, scale=2),
            server_default=sa.text("0.25"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_criterio"),
    )

    op.create_table(
        "divulgacao",
        sa.Column(
            "id_divulgacao",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "mostrar_resultado",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("data_divulgacao", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id_divulgacao"),
    )

    op.create_table(
        "usuario",
        sa.Column("id_usuario", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_tipousuario", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_tipousuario"],
            ["tipousuario.id_tipousuario"],
            name="fk_usuario_tipousuario",
        ),
        sa.PrimaryKeyConstraint("id_usuario"),
    )

    op.create_table(
        "escuderia",
        sa.Column("id_escuderia", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_mentor", sa.Integer(), nullable=False),
        sa.Column("nome_escuderia", sa.String(length=100), nullable=False),
        sa.Column("turma", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_mentor"],
            ["usuario.id_usuario"],
            name="fk_escuderia_mentor",
        ),
        sa.PrimaryKeyConstraint("id_escuderia"),
    )

    op.create_table(
        "avaliacao",
        sa.Column("id_avaliacao", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_escuderia", sa.Integer(), nullable=False),
        sa.Column("id_avaliador", sa.Integer(), nullable=False),
        sa.Column("id_criterio", sa.Integer(), nullable=False),
        sa.Column("nota", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_escuderia"],
            ["escuderia.id_escuderia"],
            name="fk_avaliacao_escuderia",
        ),
        sa.ForeignKeyConstraint(
            ["id_avaliador"],
            ["usuario.id_usuario"],
            name="fk_avaliacao_avaliador",
        ),
        sa.ForeignKeyConstraint(
            ["id_criterio"],
            ["criterio.id_criterio"],
            name="fk_avaliacao_criterio",
        ),
        sa.PrimaryKeyConstraint("id_avaliacao"),
        sa.UniqueConstraint(
            "id_escuderia",
            "id_avaliador",
            "id_criterio",
            name="uq_avaliacao_escuderia_avaliador_criterio",
        ),
    )

    op.create_table(
        "resultado",
        sa.Column("id_resultado", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_escuderia", sa.Integer(), nullable=False),
        sa.Column("id_divulgacao", sa.Integer(), nullable=False),
        sa.Column("nota_final", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_escuderia"],
            ["escuderia.id_escuderia"],
            name="fk_resultado_escuderia",
        ),
        sa.ForeignKeyConstraint(
            ["id_divulgacao"],
            ["divulgacao.id_divulgacao"],
            name="fk_resultado_divulgacao",
        ),
        sa.PrimaryKeyConstraint("id_resultado"),
        sa.UniqueConstraint(
            "id_escuderia",
            "nota_final",
            name="uq_resultado_escuderia_nota_final",
        ),
    )


def downgrade():
    op.drop_table("resultado")
    op.drop_table("avaliacao")
    op.drop_table("escuderia")
    op.drop_table("usuario")
    op.drop_table("divulgacao")
    op.drop_table("criterio")
    op.drop_table("tipousuario")
