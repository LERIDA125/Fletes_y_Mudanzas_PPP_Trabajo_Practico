"""crear tablas tipos_vehiculo, choferes y vehiculos

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-15

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tipos_vehiculo",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("descripcion", sa.String(length=80), nullable=False),
        sa.Column("descripcion_key", sa.String(length=80), nullable=False),
        sa.Column(
            "capacidad_carga_kg",
            sa.Numeric(precision=10, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "tarifa_hora_base",
            sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "tarifa_km_excedente",
            sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
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
        sa.UniqueConstraint("descripcion_key"),
    )
    op.create_index(
        "ix_tipos_vehiculo_activo_descripcion_key",
        "tipos_vehiculo",
        ["activo", "descripcion_key"],
    )

    op.create_table(
        "choferes",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
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
    )

    op.create_table(
        "vehiculos",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("patente", sa.String(length=10), nullable=False),
        sa.Column(
            "id_tipo_vehiculo",
            sa.Integer(),
            sa.ForeignKey("tipos_vehiculo.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "id_chofer_habitual",
            sa.Integer(),
            sa.ForeignKey("choferes.id", ondelete="RESTRICT"),
            nullable=True,
        ),
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
        sa.UniqueConstraint("patente"),
    )
    op.create_index("ix_vehiculos_activo_patente", "vehiculos", ["activo", "patente"])


def downgrade() -> None:
    op.drop_index("ix_vehiculos_activo_patente", table_name="vehiculos")
    op.drop_table("vehiculos")
    op.drop_table("choferes")
    op.drop_index("ix_tipos_vehiculo_activo_descripcion_key", table_name="tipos_vehiculo")
    op.drop_table("tipos_vehiculo")
