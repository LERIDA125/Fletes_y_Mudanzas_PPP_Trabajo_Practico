"""crear usuarios y roles para RBAC

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("codigo", sa.String(length=20), nullable=False),
        sa.Column("descripcion", sa.String(length=120), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("codigo IN ('ADMIN', 'CHOFER')", name="ck_roles_codigo_valido"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo", name="uq_roles_codigo"),
    )
    op.bulk_insert(
        sa.table(
            "roles",
            sa.column("codigo", sa.String()),
            sa.column("descripcion", sa.String()),
        ),
        [
            {"codigo": "ADMIN", "descripcion": "Administrador del sistema"},
            {"codigo": "CHOFER", "descripcion": "Chofer de la flota"},
        ],
    )

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("rol_id", sa.Integer(), nullable=False),
        sa.Column("id_chofer", sa.Integer(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("creado_por", sa.Integer(), nullable=True),
        sa.Column("ultimo_acceso", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["rol_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_chofer"], ["choferes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["creado_por"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_usuarios_username"),
        sa.UniqueConstraint("id_chofer", name="uq_usuarios_id_chofer"),
    )
    op.create_index("ix_usuarios_activo_rol", "usuarios", ["activo", "rol_id"])


def downgrade() -> None:
    op.drop_index("ix_usuarios_activo_rol", table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_table("roles")
