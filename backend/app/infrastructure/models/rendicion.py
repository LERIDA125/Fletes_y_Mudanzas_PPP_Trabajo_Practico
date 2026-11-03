"""Modelo SQLAlchemy de las rendiciones de choferes."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class RendicionORM(Base):
    __tablename__ = "rendiciones"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    codigo: Mapped[str | None] = mapped_column(String(16), nullable=True, unique=True)
    id_servicio: Mapped[int] = mapped_column(
        ForeignKey("servicios.id", ondelete="RESTRICT"), nullable=False
    )
    id_chofer: Mapped[int] = mapped_column(
        ForeignKey("choferes.id", ondelete="RESTRICT"), nullable=False
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    tarifa: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    adelanto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gasto_combustible: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    gasto_peajes: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    gasto_otros: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pendiente'")
    )
    observaciones: Mapped[str | None] = mapped_column(String(500), nullable=True)
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
        UniqueConstraint("id_servicio", name="uq_rendiciones_id_servicio"),
        CheckConstraint(
            "tarifa >= 0 AND adelanto >= 0 AND gasto_combustible >= 0 "
            "AND gasto_peajes >= 0 AND gasto_otros >= 0",
            name="ck_rendiciones_importes_no_negativos",
        ),
        CheckConstraint(
            "estado IN ('pendiente', 'en revision', 'aprobada')",
            name="ck_rendiciones_estado_valido",
        ),
        CheckConstraint(
            "observaciones IS NULL OR length(observaciones) <= 500",
            name="ck_rendiciones_observaciones_max",
        ),
        Index("ix_rendiciones_estado", "estado"),
        Index("ix_rendiciones_fecha_id", "fecha", "id"),
    )
