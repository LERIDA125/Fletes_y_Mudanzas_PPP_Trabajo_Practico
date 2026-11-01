"""Persistir compensación al chofer por cancelación tardía.

Revision ID: 0007
Revises: 0006
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "servicios",
        sa.Column(
            "compensacion_chofer",
            sa.Numeric(12, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_servicios_compensacion_chofer_no_negativa",
        "servicios",
        "compensacion_chofer >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_servicios_compensacion_chofer_no_negativa",
        "servicios",
        type_="check",
    )
    op.drop_column("servicios", "compensacion_chofer")
