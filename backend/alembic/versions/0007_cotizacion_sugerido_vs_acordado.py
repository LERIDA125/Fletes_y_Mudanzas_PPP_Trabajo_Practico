"""Agregar modificadores y snapshots de cotización sugerida/acordada.

Revision ID: 0007
Revises: 418d1b224011
"""

from collections.abc import Sequence
from decimal import Decimal

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | None = "418d1b224011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "configuracion_cotizacion",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("recargo_ayudante", sa.Numeric(12, 2), nullable=False),
        sa.Column("recargo_escalera", sa.Numeric(12, 2), nullable=False),
        sa.Column("porcentaje_zona_concurrida", sa.Numeric(5, 2), nullable=False),
        sa.Column("porcentaje_urgencia_mismo_dia", sa.Numeric(5, 2), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name="ck_configuracion_cotizacion_singleton"),
        sa.CheckConstraint(
            "recargo_ayudante >= 0 AND recargo_escalera >= 0",
            name="ck_configuracion_cotizacion_importes_no_negativos",
        ),
        sa.CheckConstraint(
            "porcentaje_zona_concurrida BETWEEN 0 AND 100 "
            "AND porcentaje_urgencia_mismo_dia BETWEEN 0 AND 100",
            name="ck_configuracion_cotizacion_porcentajes_validos",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        sa.table(
            "configuracion_cotizacion",
            sa.column("id", sa.Integer()),
            sa.column("recargo_ayudante", sa.Numeric(12, 2)),
            sa.column("recargo_escalera", sa.Numeric(12, 2)),
            sa.column("porcentaje_zona_concurrida", sa.Numeric(5, 2)),
            sa.column("porcentaje_urgencia_mismo_dia", sa.Numeric(5, 2)),
        ),
        [
            {
                "id": 1,
                "recargo_ayudante": Decimal("30000.00"),
                "recargo_escalera": Decimal("15000.00"),
                "porcentaje_zona_concurrida": Decimal("15.00"),
                "porcentaje_urgencia_mismo_dia": Decimal("20.00"),
            }
        ],
    )

    op.drop_constraint("ck_servicios_importes_no_negativos", "servicios", type_="check")
    for name, type_, default in (
        ("requiere_ayudante", sa.Boolean(), "false"),
        ("acceso_escalera", sa.Boolean(), "false"),
        ("zona_concurrida", sa.Boolean(), "false"),
        ("urgencia_mismo_dia", sa.Boolean(), "false"),
        ("recargo_ayudante_aplicado", sa.Numeric(12, 2), "0"),
        ("recargo_escalera_aplicado", sa.Numeric(12, 2), "0"),
        ("importe_recargo_zona_aplicado", sa.Numeric(12, 2), "0"),
        ("importe_recargo_urgencia_aplicado", sa.Numeric(12, 2), "0"),
        ("porcentaje_zona_aplicado", sa.Numeric(5, 2), "0"),
        ("porcentaje_urgencia_aplicado", sa.Numeric(5, 2), "0"),
    ):
        op.add_column(
            "servicios",
            sa.Column(name, type_, nullable=False, server_default=sa.text(default)),
        )
    op.add_column("servicios", sa.Column("precio_sugerido", sa.Numeric(12, 2), nullable=True))
    op.execute("UPDATE servicios SET precio_sugerido = precio_total WHERE precio_sugerido IS NULL")
    op.alter_column(
        "servicios",
        "precio_sugerido",
        existing_type=sa.Numeric(12, 2),
        nullable=False,
        server_default=None,
    )
    op.create_check_constraint(
        "ck_servicios_importes_no_negativos",
        "servicios",
        "tarifa_hora_aplicada >= 0 AND tarifa_km_aplicada >= 0 "
        "AND precio_sugerido >= 0 AND precio_total >= 0 "
        "AND recargo_ayudante_aplicado >= 0 AND recargo_escalera_aplicado >= 0 "
        "AND importe_recargo_zona_aplicado >= 0 AND importe_recargo_urgencia_aplicado >= 0",
    )
    op.create_check_constraint(
        "ck_servicios_porcentajes_validos",
        "servicios",
        "porcentaje_zona_aplicado BETWEEN 0 AND 100 "
        "AND porcentaje_urgencia_aplicado BETWEEN 0 AND 100",
    )


def downgrade() -> None:
    op.drop_constraint("ck_servicios_porcentajes_validos", "servicios", type_="check")
    op.drop_constraint("ck_servicios_importes_no_negativos", "servicios", type_="check")
    for name in (
        "precio_sugerido",
        "requiere_ayudante",
        "acceso_escalera",
        "zona_concurrida",
        "urgencia_mismo_dia",
        "recargo_ayudante_aplicado",
        "recargo_escalera_aplicado",
        "importe_recargo_zona_aplicado",
        "importe_recargo_urgencia_aplicado",
        "porcentaje_zona_aplicado",
        "porcentaje_urgencia_aplicado",
    ):
        op.drop_column("servicios", name)
    op.drop_table("configuracion_cotizacion")
