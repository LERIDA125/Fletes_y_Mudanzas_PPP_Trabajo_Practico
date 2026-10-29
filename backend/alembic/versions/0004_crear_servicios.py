"""crear tabla de servicios con snapshot de cotización

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "servicios",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("id_cliente", sa.Integer(), nullable=False),
        sa.Column("id_tipo_vehiculo", sa.Integer(), nullable=False),
        sa.Column("id_chofer", sa.Integer(), nullable=True),
        sa.Column("id_vehiculo", sa.Integer(), nullable=True),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=True),
        sa.Column("horas_estimadas", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("distancia_ida_km", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("distancia_total_km", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("km_franquicia", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("km_excedente", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("tarifa_hora_aplicada", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tarifa_km_aplicada", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("precio_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "estado",
            sa.String(length=20),
            server_default=sa.text("'pendiente'"),
            nullable=False,
        ),
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
        sa.CheckConstraint("horas_estimadas >= 1", name="ck_servicios_horas_minimas"),
        sa.CheckConstraint(
            "distancia_ida_km >= 0 AND distancia_total_km >= 0 "
            "AND km_franquicia >= 0 AND km_excedente >= 0",
            name="ck_servicios_distancias_no_negativas",
        ),
        sa.CheckConstraint(
            "tarifa_hora_aplicada >= 0 AND tarifa_km_aplicada >= 0 AND precio_total >= 0",
            name="ck_servicios_importes_no_negativos",
        ),
        sa.CheckConstraint(
            "estado IN ('pendiente', 'confirmado', 'en curso', 'finalizado', 'cobrado')",
            name="ck_servicios_estado_valido",
        ),
        sa.ForeignKeyConstraint(["id_cliente"], ["clientes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_tipo_vehiculo"], ["tipos_vehiculo.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_chofer"], ["choferes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_vehiculo"], ["vehiculos.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_servicios_id_cliente", "servicios", ["id_cliente"])
    op.create_index("ix_servicios_id_vehiculo", "servicios", ["id_vehiculo"])
    op.create_index("ix_servicios_fecha_id", "servicios", ["fecha", "id"])


def downgrade() -> None:
    op.drop_index("ix_servicios_fecha_id", table_name="servicios")
    op.drop_index("ix_servicios_id_vehiculo", table_name="servicios")
    op.drop_index("ix_servicios_id_cliente", table_name="servicios")
    op.drop_table("servicios")
