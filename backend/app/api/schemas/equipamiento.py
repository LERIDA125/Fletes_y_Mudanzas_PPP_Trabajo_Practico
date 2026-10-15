"""Schemas de Equipamiento y asignación a servicios según el modelo de datos (ERD)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EquipamientoBase(BaseModel):
    descripcion: str = Field(
        min_length=2,
        max_length=150,
        description="Descripción del equipamiento (ej. Carretilla, Rampas, Mantas)",
    )


class EquipamientoCreate(EquipamientoBase):
    model_config = ConfigDict(extra="forbid")


class EquipamientoUpdate(EquipamientoBase):
    model_config = ConfigDict(extra="forbid")


class EquipamientoRead(EquipamientoBase):
    model_config = ConfigDict(from_attributes=True)

    id_equipamiento: int = Field(description="Identificador del equipamiento")


class ServicioEquipamientoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_servicio: int
    id_equipamiento: int
    cantidad: int = Field(gt=0, default=1, description="Cantidad requerida para el servicio")


class ServicioEquipamientoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_servicio: int
    id_equipamiento: int
    cantidad: int

