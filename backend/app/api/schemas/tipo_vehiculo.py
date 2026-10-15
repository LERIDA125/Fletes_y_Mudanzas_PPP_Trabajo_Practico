"""Schemas de entrada y salida de tipos de vehículo en la capa de Presentación."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.tipo_vehiculo import (
    DESCRIPCION_MAX,
    DESCRIPCION_MIN,
    TipoVehiculo,
    normalizar_descripcion,
)


class TipoVehiculoBase(BaseModel):
    """Base compatible con ERD (H13)."""

    descripcion: str = Field(
        min_length=DESCRIPCION_MIN,
        max_length=DESCRIPCION_MAX,
        description="Descripción del tipo de vehículo (ej. Utilitario, Furgón Grande)",
        examples=["Camioneta 1/2 tonelada"],
    )
    capacidad_carga_kg: Decimal = Field(
        gt=0,
        description="Capacidad de carga en kilogramos. Debe ser positiva.",
        examples=[Decimal("500.0")],
    )
    tarifa_hora_base: Decimal = Field(
        ge=0,
        description="Tarifa base por hora de uso del vehículo. No puede ser negativa.",
        examples=[Decimal("3000.0")],
    )
    tarifa_km_excedente: Decimal = Field(
        ge=0,
        description="Tarifa por kilómetro excedente. No puede ser negativa.",
        examples=[Decimal("150.0")],
    )

    @field_validator("descripcion", mode="before")
    @classmethod
    def _normalizar_espacios(cls, valor: object) -> object:
        return normalizar_descripcion(valor) if isinstance(valor, str) else valor


class TipoVehiculoCreate(TipoVehiculoBase):
    """Los datos requeridos del alta de un tipo de vehículo."""

    model_config = ConfigDict(extra="forbid")


class TipoVehiculoUpdate(TipoVehiculoCreate):
    """La edición toma los mismos datos obligatorios que el alta (DD-5)."""


class TipoVehiculoRead(TipoVehiculoBase):
    """Tipo de vehículo tal como lo devuelve el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        description="Identificador del tipo de vehículo, asignado por el sistema.",
        validation_alias="id",
    )
    activo: bool = Field(
        default=True,
        description="False cuando el tipo de vehículo fue dado de baja.",
    )
    creado_en: datetime | None = Field(
        default=None,
        description="Fecha de alta, asignada por el sistema.",
    )
    actualizado_en: datetime | None = Field(
        default=None,
        description="Fecha de la última modificación.",
    )

    @property
    def id_tipo_vehiculo(self) -> int:
        """Alias para compatibilidad con el ERD (H13)."""
        return self.id

    @classmethod
    def de_tipo(cls, tipo: TipoVehiculo) -> TipoVehiculoRead:
        return cls.model_validate(tipo, from_attributes=True)


class TipoVehiculoListado(BaseModel):
    """Página de tipos de vehículo con el total de los que cumplen el filtro."""

    items: list[TipoVehiculoRead]
    total: int = Field(
        description="Cantidad total de tipos de vehículo que cumplen el filtro, no la de la página."
    )
    page: int
    size: int
