"""crear tabla usuarios y columnas de auditoria creado_por_id y modificado_por_id

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLAS_AUDITADAS: tuple[str, ...] = (
    "clientes",
    "choferes",
    "tipos_vehiculo",
    "vehiculos",
    "servicios",
)


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("username", sa.String(length=60), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("rol", sa.String(length=20), nullable=False),
        sa.Column("id_chofer", sa.Integer(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
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
        sa.CheckConstraint("rol IN ('admin', 'chofer')", name="ck_usuarios_rol_valido"),
        sa.CheckConstraint(
            "(rol = 'admin' AND id_chofer IS NULL) OR (rol = 'chofer' AND id_chofer IS NOT NULL)",
            name="ck_usuarios_rol_chofer",
        ),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["modificado_por_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("id_chofer"),
    )
    op.create_index("ix_usuarios_activo_username", "usuarios", ["activo", "username"])

    for tabla in TABLAS_AUDITADAS:
        op.add_column(tabla, sa.Column("creado_por_id", sa.Integer(), nullable=True))
        op.add_column(tabla, sa.Column("modificado_por_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            f"fk_{tabla}_creado_por_id_usuarios",
            tabla,
            "usuarios",
            ["creado_por_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_foreign_key(
            f"fk_{tabla}_modificado_por_id_usuarios",
            tabla,
            "usuarios",
            ["modificado_por_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    for tabla in reversed(TABLAS_AUDITADAS):
        op.drop_constraint(f"fk_{tabla}_modificado_por_id_usuarios", tabla, type_="foreignkey")
        op.drop_constraint(f"fk_{tabla}_creado_por_id_usuarios", tabla, type_="foreignkey")
        op.drop_column(tabla, "modificado_por_id")
        op.drop_column(tabla, "creado_por_id")

    op.drop_index("ix_usuarios_activo_username", table_name="usuarios")
    op.drop_table("usuarios")
