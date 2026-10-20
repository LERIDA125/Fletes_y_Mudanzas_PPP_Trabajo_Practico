"""completar tabla choferes con los campos de negocio

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-19

H4 creó `choferes` con solo `id`, `activo` y las fechas, para sostener el FK
`id_chofer_habitual` de vehículos. H3 agrega `nombre_completo`, `telefono` y `saldo_a_favor`.

Como la tabla puede tener filas creadas por H4 (sin nombre ni teléfono), las columnas se agregan
nullable, se backfillean y recién después se aplica NOT NULL.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("choferes", sa.Column("nombre_completo", sa.String(length=120), nullable=True))
    op.add_column("choferes", sa.Column("telefono", sa.String(length=20), nullable=True))
    op.add_column(
        "choferes",
        sa.Column("saldo_a_favor", sa.Numeric(precision=12, scale=2), nullable=True),
    )

    # Backfill de las filas preexistentes antes de aplicar NOT NULL.
    op.execute(
        """
        UPDATE choferes
        SET nombre_completo = COALESCE(nombre_completo, 'Chofer sin nombre'),
            telefono = COALESCE(telefono, '0000000'),
            saldo_a_favor = COALESCE(saldo_a_favor, 0)
        """
    )

    op.alter_column("choferes", "nombre_completo", nullable=False)
    op.alter_column("choferes", "telefono", nullable=False)
    op.alter_column("choferes", "saldo_a_favor", nullable=False, server_default=sa.text("0"))

    op.create_index("ix_choferes_activo_nombre", "choferes", ["activo", "nombre_completo"])


def downgrade() -> None:
    op.drop_index("ix_choferes_activo_nombre", table_name="choferes")
    op.drop_column("choferes", "saldo_a_favor")
    op.drop_column("choferes", "telefono")
    op.drop_column("choferes", "nombre_completo")
