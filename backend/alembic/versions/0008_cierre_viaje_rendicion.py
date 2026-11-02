"""Agregar columnas de Prueba de Entrega (POD) y Rendición de Caja (H10).

Revision ID: 0008
Revises: 0007
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("servicios", sa.Column("foto_remito_url", sa.Text(), nullable=True))
    op.add_column("servicios", sa.Column("monto_cobrado_real", sa.Numeric(12, 2), nullable=True))
    op.add_column("servicios", sa.Column("estado_rendicion", sa.String(20), nullable=True))
    op.add_column("servicios", sa.Column("observacion_rendicion", sa.String(255), nullable=True))
    op.add_column("servicios", sa.Column("rendido_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "servicios",
        sa.Column(
            "rendido_por_id",
            sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_check_constraint(
        "ck_servicios_estado_rendicion_valido",
        "servicios",
        "estado_rendicion IS NULL OR estado_rendicion IN ('PENDIENTE', 'RENDIDO', 'OBSERVADO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_servicios_estado_rendicion_valido", "servicios", type_="check")
    op.drop_column("servicios", "rendido_por_id")
    op.drop_column("servicios", "rendido_en")
    op.drop_column("servicios", "observacion_rendicion")
    op.drop_column("servicios", "estado_rendicion")
    op.drop_column("servicios", "monto_cobrado_real")
    op.drop_column("servicios", "foto_remito_url")
