"""Modelo de Chofer.

H4 creó la tabla con los campos mínimos (`id`, `activo`, fechas) para sostener el FK
`id_chofer_habitual` de vehículos. H3 la completa con los campos de negocio:
`nombre_completo`, `telefono` y `saldo_a_favor`.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Identity, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ChoferORM(Base):
    __tablename__ = "choferes"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(120), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    saldo_a_favor: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, server_default="0")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_choferes_activo_nombre", "activo", "nombre_completo"),)
