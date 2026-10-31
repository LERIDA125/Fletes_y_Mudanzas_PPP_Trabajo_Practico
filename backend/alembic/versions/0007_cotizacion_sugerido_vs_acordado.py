"""separar precio sugerido de precio acordado y agregar configuración de cotización

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-30
"""

from collections.abc import Sequence
from decimal import Decimal

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

VALORES_CONFIGURACION = {
    "id": 1,
    "recargo_ayudante": Decimal("30000.00"),
    "recargo_escalera": Decimal("15000.00"),
    "porcentaje_zona_concurrida": Decimal("15.00"),
    "porcentaje_urgencia_mismo_dia": Decimal("20.00"),
}


def upgrade() -> None:
    op.create_table(
        "configuracion_cotizacion",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("recargo_ayudante", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("recargo_escalera", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("porcentaje_zona_concurrida", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column(
            "porcentaje_urgencia_mismo_dia", sa.Numeric(precision=5, scale=2), nullable=False
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
        [VALORES_CONFIGURACION],
    )

    op.drop_constraint("ck_servicios_distancias_no_negativas", "servicios", type_="check")
    op.drop_constraint("ck_servicios_importes_no_negativos", "servicios", type_="check")

    op.alter_column("servicios", "distancia_ida_km", new_column_name="km_estimados")
    op.alter_column("servicios", "precio_total", new_column_name="precio_acordado")

    op.add_column("servicios", sa.Column("precio_sugerido", sa.Numeric(12, 2), nullable=True))
    for columna, default in (
        ("requiere_ayudante", "false"),
        ("acceso_escalera", "false"),
        ("zona_concurrida", "false"),
        ("urgencia_mismo_dia", "false"),
    ):
        op.add_column(
            "servicios",
            sa.Column(
                columna,
                sa.Boolean(),
                nullable=False,
                server_default=sa.text(default),
            ),
        )
    for columna in (
        "recargo_ayudante_aplicado",
        "recargo_escalera_aplicado",
        "importe_recargo_zona_aplicado",
        "importe_recargo_urgencia_aplicado",
    ):
        op.add_column(
            "servicios",
            sa.Column(
                columna,
                sa.Numeric(12, 2),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )
    for columna in ("porcentaje_zona_aplicado", "porcentaje_urgencia_aplicado"):
        op.add_column(
            "servicios",
            sa.Column(
                columna,
                sa.Numeric(5, 2),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )

    op.execute(
        "UPDATE servicios SET precio_sugerido = precio_acordado WHERE precio_sugerido IS NULL"
    )
    op.alter_column(
        "servicios",
        "precio_sugerido",
        existing_type=sa.Numeric(12, 2),
        nullable=False,
    )

    op.create_check_constraint(
        "ck_servicios_distancias_no_negativas",
        "servicios",
        "km_estimados >= 0 AND distancia_total_km >= 0 "
        "AND km_franquicia >= 0 AND km_excedente >= 0",
    )
    op.create_check_constraint(
        "ck_servicios_importes_no_negativos",
        "servicios",
        "tarifa_hora_aplicada >= 0 AND tarifa_km_aplicada >= 0 "
        "AND precio_sugerido >= 0 AND precio_acordado >= 0 "
        "AND recargo_ayudante_aplicado >= 0 AND recargo_escalera_aplicado >= 0 "
        "AND importe_recargo_zona_aplicado >= 0 "
        "AND importe_recargo_urgencia_aplicado >= 0",
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
    op.drop_constraint("ck_servicios_distancias_no_negativas", "servicios", type_="check")

    for columna in (
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
        op.drop_column("servicios", columna)

    op.alter_column("servicios", "km_estimados", new_column_name="distancia_ida_km")
    op.alter_column("servicios", "precio_acordado", new_column_name="precio_total")

    op.create_check_constraint(
        "ck_servicios_distancias_no_negativas",
        "servicios",
        "distancia_ida_km >= 0 AND distancia_total_km >= 0 "
        "AND km_franquicia >= 0 AND km_excedente >= 0",
    )
    op.create_check_constraint(
        "ck_servicios_importes_no_negativos",
        "servicios",
        "tarifa_hora_aplicada >= 0 AND tarifa_km_aplicada >= 0 AND precio_total >= 0",
    )

    op.drop_table("configuracion_cotizacion")
