"""Schemas de Peón y asignación a servicios según el modelo de datos (ERD)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PeonBase(BaseModel):
    nombre_completo: str = Field(min_length=2, max_length=150, description="Nombre completo del peón/ayudante")
    telefono: str = Field(description="Teléfono de contacto")
    activo: bool = Field(default=True, description="Estado operativo del peón")


class PeonCreate(PeonBase):
    model_config = ConfigDict(extra="forbid")


class PeonUpdate(PeonBase):
    model_config = ConfigDict(extra="forbid")


class PeonRead(PeonBase):
    model_config = ConfigDict(from_attributes=True)

    id_peon: int = Field(description="Identificador único del peón")


class ServicioPeonCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_servicio: int
    id_peon: int


class ServicioPeonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_servicio: int
    id_peon: int
