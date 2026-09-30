"""Schemas de Rendición de choferes según el modelo de datos (ERD)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RendicionBase(BaseModel):
    id_chofer: int = Field(description="Chofer que rinde cuentas")
    fecha_cierre: date = Field(description="Fecha de cierre del turno o jornada")
    monto_esperado: Decimal = Field(
        ge=0, description="Monto total esperado según cobros percibidos"
    )
    monto_entregado: Decimal = Field(
        ge=0, description="Monto físico/digital efectivamente entregado"
    )
    diferencia: Decimal = Field(description="Diferencia contable (entregado - esperado)")
    estado_rendicion: str = Field(
        description="Estado de la rendición (ej. pendiente, cerrada, con_diferencia, aprobada)"
    )


class RendicionCreate(RendicionBase):
    model_config = ConfigDict(extra="forbid")


class RendicionUpdate(RendicionBase):
    model_config = ConfigDict(extra="forbid")


class RendicionRead(RendicionBase):
    model_config = ConfigDict(from_attributes=True)

    id_rendicion: int = Field(description="Identificador de la rendición")

