from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Identity, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class RolORM(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(120), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("codigo IN ('ADMIN', 'CHOFER')", name="ck_roles_codigo_valido"),
        UniqueConstraint("codigo", name="uq_roles_codigo"),
    )
