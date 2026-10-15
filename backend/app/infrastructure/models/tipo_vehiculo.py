from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Identity, Index, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class TipoVehiculoORM(Base):
    __tablename__ = "tipos_vehiculo"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion_key: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    capacidad_carga_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default=text("0")
    )
    tarifa_hora_base: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    tarifa_km_excedente: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_tipos_vehiculo_activo_descripcion_key", "activo", "descripcion_key"),
    )
