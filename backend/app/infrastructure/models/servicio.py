"""Modelo SQLAlchemy de los servicios registrados (incluye POD y rendición H10)."""

from datetime import date, datetime, time
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
    Text,
    Time,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ServicioORM(Base):
    __tablename__ = "servicios"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    id_tipo_vehiculo: Mapped[int] = mapped_column(
        ForeignKey("tipos_vehiculo.id", ondelete="RESTRICT"), nullable=False
    )
    id_chofer: Mapped[int | None] = mapped_column(
        ForeignKey("choferes.id", ondelete="RESTRICT"), nullable=True
    )
    id_vehiculo: Mapped[int | None] = mapped_column(
        ForeignKey("vehiculos.id", ondelete="RESTRICT"), nullable=True
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time | None] = mapped_column(Time, nullable=True)
    hora_fin: Mapped[time | None] = mapped_column(Time, nullable=True)
    horas_estimadas: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    distancia_ida_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    distancia_total_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    km_franquicia: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    km_excedente: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tarifa_hora_aplicada: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tarifa_km_aplicada: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    precio_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pendiente'")
    )
    motivo_cancelacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    foto_remito_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    monto_cobrado_real: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    estado_rendicion: Mapped[str | None] = mapped_column(String(20), nullable=True)
    observacion_rendicion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rendido_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rendido_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
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
        CheckConstraint("horas_estimadas >= 1", name="ck_servicios_horas_minimas"),
        CheckConstraint(
            "distancia_ida_km >= 0 AND distancia_total_km >= 0 "
            "AND km_franquicia >= 0 AND km_excedente >= 0",
            name="ck_servicios_distancias_no_negativas",
        ),
        CheckConstraint(
            "tarifa_hora_aplicada >= 0 AND tarifa_km_aplicada >= 0 AND precio_total >= 0",
            name="ck_servicios_importes_no_negativos",
        ),
        CheckConstraint(
            "estado IN ('pendiente', 'confirmado', 'en curso', 'finalizado', 'cobrado', "
            "'cancelado')",
            name="ck_servicios_estado_valido",
        ),
        CheckConstraint(
            "estado <> 'cancelado' OR (motivo_cancelacion IS NOT NULL "
            "AND length(trim(motivo_cancelacion)) > 0 AND hora_fin IS NOT NULL)",
            name="ck_servicios_cancelacion_completa",
        ),
        CheckConstraint(
            "estado_rendicion IS NULL OR estado_rendicion IN ('PENDIENTE', 'RENDIDO', 'OBSERVADO')",
            name="ck_servicios_estado_rendicion_valido",
        ),
        Index("ix_servicios_id_cliente", "id_cliente"),
        Index("ix_servicios_id_vehiculo", "id_vehiculo"),
        Index("ix_servicios_fecha_id", "fecha", "id"),
    )
