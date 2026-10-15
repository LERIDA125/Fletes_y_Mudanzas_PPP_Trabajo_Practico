"""Modelo mínimo de Chofer para soportar el FK de vehículos en H4.

La entidad completa de chofer llega en H2. Por ahora solo existe la tabla
con los campos mínimos para mantener la integridad referencial.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Identity, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ChoferORM(Base):
    __tablename__ = "choferes"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
