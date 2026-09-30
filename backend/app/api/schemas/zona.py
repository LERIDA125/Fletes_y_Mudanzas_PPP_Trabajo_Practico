"""Schemas de Zona según el modelo de datos (ERD)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ZonaBase(BaseModel):
    nombre_zona: str = Field(
        min_length=2,
        max_length=100,
        description="Nombre de la zona (ej. CABA Centro, Zona Norte)",
    )
    permite_tarde: bool = Field(default=False, description="Indica si admite turnos tarde")
    observaciones_horarias: str | None = Field(
        default=None, description="Restricciones u observaciones horarias"
    )


class ZonaCreate(ZonaBase):
    model_config = ConfigDict(extra="forbid")


class ZonaUpdate(ZonaBase):
    model_config = ConfigDict(extra="forbid")


class ZonaRead(ZonaBase):
    model_config = ConfigDict(from_attributes=True)

    id_zona: int = Field(description="Identificador de la zona")
