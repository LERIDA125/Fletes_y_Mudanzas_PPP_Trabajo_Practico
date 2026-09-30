"""Schemas de Entrega / Tramo según el modelo de datos (ERD)."""

from __future__ import annotations

from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class EntregaBase(BaseModel):
    id_servicio: int = Field(description="Servicio al que pertenece la entrega")
    id_zona_origen: int | None = Field(default=None, description="Zona de origen")
    id_zona_destino: int | None = Field(default=None, description="Zona de destino")
    origen_direccion: str = Field(min_length=3, max_length=250, description="Dirección de origen")
    destino_direccion: str = Field(min_length=3, max_length=250, description="Dirección de destino")
    distancia_km: Decimal = Field(ge=0, description="Distancia estimada o real en kilómetros")
    detalle_bultos_grandes: str | None = Field(default=None, description="Descripción de carga y bultos grandes")
    orden_ruta: int = Field(default=1, ge=1, description="Secuencia u orden dentro de la ruta del servicio")


class EntregaCreate(EntregaBase):
    model_config = ConfigDict(extra="forbid")


class EntregaUpdate(EntregaBase):
    model_config = ConfigDict(extra="forbid")


class EntregaRead(EntregaBase):
    model_config = ConfigDict(from_attributes=True)

    id_entrega: int = Field(description="Identificador único del tramo/entrega")
