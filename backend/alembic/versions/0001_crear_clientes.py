"""crear tabla clientes

Revision ID: 0001
Revises:
Create Date: 2026-09-27

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("razon_social", sa.String(length=120), nullable=False),
        sa.Column("razon_social_key", sa.String(length=120), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=False),
        sa.Column("direccion_habitual", sa.String(length=250), nullable=False),
        sa.Column("tiene_cuenta_corriente", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("razon_social_key"),
    )
    op.create_index(
        "ix_clientes_activo_razon_social_key", "clientes", ["activo", "razon_social_key"]
    )


def downgrade() -> None:
    op.drop_index("ix_clientes_activo_razon_social_key", table_name="clientes")
    op.drop_table("clientes")
