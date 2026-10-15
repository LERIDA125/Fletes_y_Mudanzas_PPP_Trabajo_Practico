"""Schemas de entrada y salida de vehículos en la capa de Presentación."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.schemas.comun import Pagina
from app.domain.vehiculo import Vehiculo, normalizar_patente


class VehiculoBase(BaseModel):
    """Base compatible con ERD (H13)."""

    patente: str = Field(
        min_length=6,
        max_length=15,
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


class VehiculoCreate(VehiculoBase):
    """Los datos requeridos del alta de un vehículo."""

    model_config = ConfigDict(extra="forbid")


class VehiculoUpdate(VehiculoCreate):
    """La edición toma los mismos datos obligatorios que el alta (DD-5)."""


class VehiculoRead(VehiculoBase):
    """Vehículo tal como lo devuelve el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        description="Identificador del vehículo, asignado por el sistema.",
        validation_alias="id",
    )
    activo: bool = Field(
        default=True,
        description="False cuando el vehículo fue dado de baja.",
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
    def id_vehiculo(self) -> int:
        """Alias para compatibilidad con el ERD (H13)."""
        return self.id

    @classmethod
    def de_vehiculo(cls, vehiculo: Vehiculo) -> VehiculoRead:
        return cls.model_validate(vehiculo, from_attributes=True)


class VehiculoListado(Pagina[VehiculoRead]):
    """Página de vehículos con el total de los que cumplen el filtro."""
