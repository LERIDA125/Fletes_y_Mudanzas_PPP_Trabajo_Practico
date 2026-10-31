"""agregar cancelación a servicios

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("servicios", sa.Column("hora_fin", sa.Time(), nullable=True))
    op.add_column(
        "servicios", sa.Column("motivo_cancelacion", sa.String(length=255), nullable=True)
    )

    op.drop_constraint("ck_servicios_estado_valido", "servicios", type_="check")
    op.create_check_constraint(
        "ck_servicios_estado_valido",
        "servicios",
        "estado IN ('pendiente', 'confirmado', 'en curso', 'finalizado', 'cobrado', 'cancelado')",
    )
    op.create_check_constraint(
        "ck_servicios_cancelacion_completa",
        "servicios",
        "estado <> 'cancelado' OR (motivo_cancelacion IS NOT NULL "
        "AND length(trim(motivo_cancelacion)) > 0 AND hora_fin IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_servicios_cancelacion_completa", "servicios", type_="check")
    op.drop_constraint("ck_servicios_estado_valido", "servicios", type_="check")
    op.create_check_constraint(
        "ck_servicios_estado_valido",
        "servicios",
        "estado IN ('pendiente', 'confirmado', 'en curso', 'finalizado', 'cobrado')",
    )
    op.drop_column("servicios", "motivo_cancelacion")
    op.drop_column("servicios", "hora_fin")
