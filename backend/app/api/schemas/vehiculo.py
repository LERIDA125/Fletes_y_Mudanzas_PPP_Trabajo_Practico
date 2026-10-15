"""Schemas de entrada y salida de vehículos en la capa de Presentación."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.vehiculo import Vehiculo, normalizar_patente


class VehiculoCreate(BaseModel):
    """Los datos requeridos del alta de un vehículo."""

    model_config = ConfigDict(extra="forbid")

    patente: str = Field(
        description="Patente del vehículo. Formato argentino: AAA 123 o AA 123 ABC.",
        examples=["ABC 123"],
    )
    id_tipo_vehiculo: int = Field(gt=0, description="Identificador del tipo de vehículo.")
    id_chofer_habitual: int | None = Field(
        default=None, description="Identificador del chofer habitual. Opcional."
    )

    @field_validator("patente", mode="before")
    @classmethod
    def _normalizar_patente(cls, valor: object) -> object:
        return normalizar_patente(valor) if isinstance(valor, str) else valor


class VehiculoUpdate(VehiculoCreate):
    """La edición toma los mismos datos obligatorios que el alta (DD-5)."""


class VehiculoRead(BaseModel):
    """Vehículo tal como lo devuelve el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador del vehículo, asignado por el sistema.")
    patente: str
    id_tipo_vehiculo: int
    id_chofer_habitual: int | None
    activo: bool = Field(description="False cuando el vehículo fue dado de baja.")
    creado_en: datetime = Field(description="Fecha de alta, asignada por el sistema.")
    actualizado_en: datetime = Field(description="Fecha de la última modificación.")

    @classmethod
    def de_vehiculo(cls, vehiculo: Vehiculo) -> VehiculoRead:
        return cls.model_validate(vehiculo, from_attributes=True)


class VehiculoListado(BaseModel):
    """Página de vehículos con el total de los que cumplen el filtro."""

    items: list[VehiculoRead]
    total: int = Field(
        description="Cantidad total de vehículos que cumplen el filtro, no la de la página."
    )
    page: int
    size: int
