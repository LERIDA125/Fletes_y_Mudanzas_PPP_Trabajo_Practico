"""Modelo SQLAlchemy de cuentas de usuario (`admin` y `chofer`) (H9)."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    username: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    id_chofer: Mapped[int | None] = mapped_column(
        ForeignKey("choferes.id", ondelete="RESTRICT"), nullable=True, unique=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    modificado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("rol IN ('admin', 'chofer')", name="ck_usuarios_rol_valido"),
        CheckConstraint(
            "(rol = 'admin' AND id_chofer IS NULL) OR (rol = 'chofer' AND id_chofer IS NOT NULL)",
            name="ck_usuarios_rol_chofer",
        ),
        Index("ix_usuarios_activo_username", "activo", "username"),
    )
