"""Schemas de Tipo de Vehículo según el modelo de datos (ERD)."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TipoVehiculoBase(BaseModel):
    descripcion: str = Field(
        min_length=2,
        max_length=100,
        description="Descripción del tipo de vehículo (ej. Utilitario, Furgón Grande)",
    )
    capacidad_carga_kg: Decimal = Field(
        gt=0, description="Capacidad máxima de carga en kilogramos"
    )
    tarifa_hora_base: Decimal = Field(ge=0, description="Tarifa base por hora de servicio")
    tarifa_km_excedente: Decimal = Field(ge=0, description="Tarifa por kilómetro excedente")


class TipoVehiculoCreate(TipoVehiculoBase):
    model_config = ConfigDict(extra="forbid")


class TipoVehiculoUpdate(TipoVehiculoBase):
    model_config = ConfigDict(extra="forbid")


class TipoVehiculoRead(TipoVehiculoBase):
    model_config = ConfigDict(from_attributes=True)

    id_tipo_vehiculo: int = Field(description="Identificador único del tipo de vehículo")

