"""Schemas de Remitos según el modelo de datos (ERD)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RemitoBase(BaseModel):
    id_pago: int = Field(description="Pago o comprobante asociado")
    numero_remito: str = Field(
        min_length=1, max_length=50, description="Número legal o interno de remito"
    )
    fecha_emision: datetime = Field(description="Fecha y hora de emisión")


class RemitoCreate(RemitoBase):
    model_config = ConfigDict(extra="forbid")


class RemitoRead(RemitoBase):
    model_config = ConfigDict(from_attributes=True)

    id_remito: int = Field(description="Identificador único del remito")

