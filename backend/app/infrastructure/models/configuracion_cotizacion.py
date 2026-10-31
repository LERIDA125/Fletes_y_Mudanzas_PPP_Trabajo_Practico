"""Modelo SQLAlchemy de la configuración singleton de cotización."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Identity, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ConfiguracionCotizacionORM(Base):
    __tablename__ = "configuracion_cotizacion"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    recargo_ayudante: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    recargo_escalera: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    porcentaje_zona_concurrida: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    porcentaje_urgencia_mismo_dia: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("id = 1", name="ck_configuracion_cotizacion_singleton"),
        CheckConstraint(
            "recargo_ayudante >= 0 AND recargo_escalera >= 0",
            name="ck_configuracion_cotizacion_importes_no_negativos",
        ),
        CheckConstraint(
            "porcentaje_zona_concurrida BETWEEN 0 AND 100 "
            "AND porcentaje_urgencia_mismo_dia BETWEEN 0 AND 100",
            name="ck_configuracion_cotizacion_porcentajes_validos",
        ),
    )
