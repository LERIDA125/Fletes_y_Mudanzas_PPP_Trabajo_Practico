"""Schemas de Chofer según el modelo de datos (ERD)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChoferBase(BaseModel):
    nombre_completo: str = Field(min_length=2, max_length=150, description="Nombre y apellido del chofer")
    telefono: str = Field(description="Teléfono de contacto")
    activo: bool = Field(default=True, description="Estado operativo del chofer")


class ChoferCreate(ChoferBase):
    model_config = ConfigDict(extra="forbid")


class ChoferUpdate(ChoferBase):
    model_config = ConfigDict(extra="forbid")


class ChoferRead(ChoferBase):
    model_config = ConfigDict(from_attributes=True)

    id_chofer: int = Field(description="Identificador único del chofer")
