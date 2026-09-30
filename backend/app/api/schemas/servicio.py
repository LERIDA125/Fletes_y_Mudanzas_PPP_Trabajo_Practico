"""Schemas de Servicio y Estado de Servicio según el modelo de datos (ERD)."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EstadoServicioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_estado: int
    descripcion: str = Field(
        description=(
            "Descripción del estado (ej. pendiente, confirmado, en curso, finalizado, cancelado)"
        )
    )


class ServicioBase(BaseModel):
    id_cliente: int = Field(description="Cliente que solicita el servicio")
    id_chofer: int | None = Field(default=None, description="Chofer asignado")
    id_vehiculo: int | None = Field(default=None, description="Vehículo asignado")
    id_estado: int = Field(default=1, description="Estado actual del servicio")
    fecha: date = Field(description="Fecha programada del servicio")
    hora_inicio: time | None = Field(default=None, description="Hora estimada o real de inicio")
    hora_fin: time | None = Field(default=None, description="Hora estimada o real de finalización")
    precio_total: Decimal = Field(ge=0, description="Precio total cotizado o facturado")
    motivo_cancelacion: str | None = Field(
        default=None, description="Motivo en caso de haber sido cancelado"
    )


class ServicioCreate(ServicioBase):
    model_config = ConfigDict(extra="forbid")


class ServicioUpdate(ServicioBase):
    model_config = ConfigDict(extra="forbid")


class ServicioRead(ServicioBase):
    model_config = ConfigDict(from_attributes=True)

    id_servicio: int = Field(description="Identificador único del servicio")
