"""Schemas de Pagos según el modelo de datos (ERD)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class PagoBase(BaseModel):
    id_servicio: int = Field(description="Servicio asociado al pago")
    monto: Decimal = Field(gt=0, description="Monto abonado")
    fecha_pago: datetime = Field(description="Fecha y hora de acreditación o cobro")
    medio_pago: str = Field(description="Medio de pago (ej. Efectivo, Transferencia, Cheque)")
    concepto: str | None = Field(default=None, description="Concepto o descripción del pago")
    recibido_por_chofer: bool = Field(default=False, description="Indica si el cobro fue percibido en mano por el chofer")


class PagoCreate(PagoBase):
    model_config = ConfigDict(extra="forbid")


class PagoUpdate(PagoBase):
    model_config = ConfigDict(extra="forbid")


class PagoRead(PagoBase):
    model_config = ConfigDict(from_attributes=True)

    id_pago: int = Field(description="Identificador único del pago")
