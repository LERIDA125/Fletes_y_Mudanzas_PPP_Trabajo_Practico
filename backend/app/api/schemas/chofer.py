"""Schemas de entrada y salida de choferes en la capa de Presentación.

Los límites y formatos se declaran acá para que un dato inválido se rechace con un `422` nombrando
el campo responsable (FR-011), pero la fuente de verdad sigue siendo `app/domain/chofer.py`.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.schemas.comun import Pagina
from app.domain.chofer import (
    NOMBRE_MAX,
    NOMBRE_MIN,
    TELEFONO_DIGITOS_MAX,
    TELEFONO_DIGITOS_MIN,
    Chofer,
    contar_digitos,
    normalizar_nombre,
)


class ChoferCreate(BaseModel):
    """Los datos requeridos del alta (FR-001, FR-002).

    `activo` y `saldo_a_favor` no se aceptan del usuario (FR-006): el dominio los fija por
    defecto y `extra="forbid"` rechaza el intento con `422`.
    """

    model_config = ConfigDict(extra="forbid")

    nombre_completo: str = Field(
        min_length=NOMBRE_MIN,
        max_length=NOMBRE_MAX,
        description="Nombre completo del chofer.",
        examples=["Juan Pérez"],
    )
    telefono: str = Field(
        description=(
            "Teléfono de contacto. Se aceptan espacios, guiones y el prefijo internacional `+`; "
            f"solo se exige que tenga entre {TELEFONO_DIGITOS_MIN} y "
            f"{TELEFONO_DIGITOS_MAX} dígitos."
        ),
        examples=["351 555 0100"],
    )

    @field_validator("nombre_completo", "telefono", mode="before")
    @classmethod
    def _normalizar_espacios(cls, valor: object) -> object:
        """Colapsa espacios sobrantes antes de medir, así un texto de solo espacios se rechaza."""
        return normalizar_nombre(valor) if isinstance(valor, str) else valor

    @field_validator("telefono")
    @classmethod
    def _validar_digitos_del_telefono(cls, telefono: str) -> str:
        digitos = contar_digitos(telefono)
        if not TELEFONO_DIGITOS_MIN <= digitos <= TELEFONO_DIGITOS_MAX:
            raise ValueError(
                f"El teléfono debe tener entre {TELEFONO_DIGITOS_MIN} "
                f"y {TELEFONO_DIGITOS_MAX} dígitos"
            )
        return telefono


class ChoferUpdate(ChoferCreate):
    """La edición toma los mismos campos obligatorios que el alta (DD-5)."""


class ChoferRead(BaseModel):
    """Chofer tal como lo devuelve el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador del chofer, asignado por el sistema.")
    nombre_completo: str
    telefono: str
    activo: bool = Field(description="False cuando el chofer fue dado de baja (FR-013).")
    saldo_a_favor: float = Field(description="Saldo económico a favor del chofer.")
    creado_en: datetime = Field(description="Fecha de alta, asignada por el sistema.")
    actualizado_en: datetime = Field(description="Fecha de la última modificación (FR-019).")

    @classmethod
    def de_chofer(cls, chofer: Chofer) -> ChoferRead:
        return cls.model_validate(chofer, from_attributes=True)


class ChoferListado(Pagina[ChoferRead]):
    """Página de choferes activos con el total de los que cumplen el filtro (FR-007)."""
