"""Schemas de Vehículo según el modelo de datos (ERD)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VehiculoBase(BaseModel):
    patente: str = Field(min_length=6, max_length=15, description="Patente / dominio del vehículo")
    id_tipo_vehiculo: int = Field(description="Referencia al tipo de vehículo")
    id_chofer_habitual: int | None = Field(default=None, description="Chofer asignado habitualmente")


class VehiculoCreate(VehiculoBase):
    model_config = ConfigDict(extra="forbid")


class VehiculoUpdate(VehiculoBase):
    model_config = ConfigDict(extra="forbid")


class VehiculoRead(VehiculoBase):
    model_config = ConfigDict(from_attributes=True)

    id_vehiculo: int = Field(description="Identificador único del vehículo")
