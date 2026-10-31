"""agregar columnas de cierre de viaje, prueba de entrega (POD) y rendicion en servicios

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("servicios", sa.Column("foto_remito_url", sa.Text(), nullable=True))
    op.add_column(
        "servicios",
        sa.Column("monto_cobrado_real", sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column(
        "servicios",
        sa.Column("estado_rendicion", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "servicios",
        sa.Column("observacion_rendicion", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "servicios",
        sa.Column("rendido_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "servicios",
        sa.Column("rendido_por_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_servicios_rendido_por_id_usuarios",
        "servicios",
        "usuarios",
        ["rendido_por_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint(
        "ck_servicios_estado_rendicion_valido",
        "servicios",
        "estado_rendicion IS NULL OR estado_rendicion IN ('PENDIENTE', 'RENDIDO', 'OBSERVADO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_servicios_estado_rendicion_valido", "servicios", type_="check")
    op.drop_constraint("fk_servicios_rendido_por_id_usuarios", "servicios", type_="foreignkey")
    op.drop_column("servicios", "rendido_por_id")
    op.drop_column("servicios", "rendido_en")
    op.drop_column("servicios", "observacion_rendicion")
    op.drop_column("servicios", "estado_rendicion")
    op.drop_column("servicios", "monto_cobrado_real")
    op.drop_column("servicios", "foto_remito_url")
