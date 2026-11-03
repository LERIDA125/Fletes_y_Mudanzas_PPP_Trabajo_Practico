"""crear tabla de rendiciones de choferes

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-03
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rendiciones",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("codigo", sa.String(length=16), nullable=True),
        sa.Column("id_servicio", sa.Integer(), nullable=False),
        sa.Column("id_chofer", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("tarifa", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("adelanto", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "gasto_combustible",
            sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "gasto_peajes",
            sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "gasto_otros",
            sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "estado",
            sa.String(length=20),
            server_default=sa.text("'pendiente'"),
            nullable=False,
        ),
        sa.Column("observaciones", sa.String(length=500), nullable=True),
        sa.Column("creado_por_id", sa.Integer(), nullable=True),
        sa.Column("modificado_por_id", sa.Integer(), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "tarifa >= 0 AND adelanto >= 0 AND gasto_combustible >= 0 "
            "AND gasto_peajes >= 0 AND gasto_otros >= 0",
            name="ck_rendiciones_importes_no_negativos",
        ),
        sa.CheckConstraint(
            "estado IN ('pendiente', 'en revision', 'aprobada')",
            name="ck_rendiciones_estado_valido",
        ),
        sa.CheckConstraint(
            "observaciones IS NULL OR length(observaciones) <= 500",
            name="ck_rendiciones_observaciones_max",
        ),
        sa.ForeignKeyConstraint(["id_servicio"], ["servicios.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_chofer"], ["choferes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
        sa.UniqueConstraint("id_servicio", name="uq_rendiciones_id_servicio"),
    )
    op.create_index("ix_rendiciones_estado", "rendiciones", ["estado"])
    op.create_index("ix_rendiciones_fecha_id", "rendiciones", ["fecha", "id"])


def downgrade() -> None:
    op.drop_index("ix_rendiciones_fecha_id", table_name="rendiciones")
    op.drop_index("ix_rendiciones_estado", table_name="rendiciones")
    op.drop_table("rendiciones")
