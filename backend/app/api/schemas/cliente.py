"""Schemas de entrada y salida de clientes en la capa de Presentación.

Los límites y formatos se declaran acá para que un dato inválido se rechace con un `422` nombrando
el campo responsable (FR-011, FR-013), pero la fuente de verdad sigue siendo
`app/domain/cliente.py`: el dominio revalida siempre lo que llega desde acá. Los schemas no
inventan reglas, reusan las funciones puras del dominio.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.cliente import (
    DIRECCION_MAX,
    DIRECCION_MIN,
    RAZON_SOCIAL_MAX,
    RAZON_SOCIAL_MIN,
    TELEFONO_DIGITOS_MAX,
    TELEFONO_DIGITOS_MIN,
    Cliente,
    contar_digitos,
    normalizar_razon_visual,
)


class ClienteCreate(BaseModel):
    """Los cuatro datos requeridos del alta (FR-001, FR-002)."""

    model_config = ConfigDict(extra="forbid")

    razon_social: str = Field(
        min_length=RAZON_SOCIAL_MIN,
        max_length=RAZON_SOCIAL_MAX,
        description="Razón social del cliente. Es el dato que lo identifica y no puede repetirse.",
        examples=["Distribuidora del Sur S.A."],
    )
    telefono: str = Field(
        description=(
            "Teléfono de contacto. Se aceptan espacios, guiones y el prefijo internacional `+`; "
            f"solo se exige que tenga entre {TELEFONO_DIGITOS_MIN} y "
            f"{TELEFONO_DIGITOS_MAX} dígitos."
        ),
        examples=["351 555 0100"],
    )
    direccion_habitual: str = Field(
        min_length=DIRECCION_MIN,
        max_length=DIRECCION_MAX,
        description="Domicilio habitual del cliente.",
        examples=["Av. Colón 1250, Córdoba"],
    )
    tiene_cuenta_corriente: bool = Field(
        default=False,
        description=(
            "Si el cliente maneja cuenta corriente. Es obligatorio, pero si el usuario no lo elige "
            "explícitamente se guarda en `false` (FR-002)."
        ),
    )

    @field_validator("razon_social", "telefono", "direccion_habitual", mode="before")
    @classmethod
    def _normalizar_espacios(cls, valor: object) -> object:
        """Colapsa espacios sobrantes antes de medir, así un texto de solo espacios se rechaza."""
        return normalizar_razon_visual(valor) if isinstance(valor, str) else valor

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


class ClienteRead(BaseModel):
    """Cliente tal como lo devuelve el sistema, con los datos que calcula él (FR-003, FR-009)."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador del cliente, asignado por el sistema.")
    razon_social: str
    telefono: str
    direccion_habitual: str
    tiene_cuenta_corriente: bool
    activo: bool = Field(description="False cuando el cliente fue dado de baja (FR-014).")
    creado_en: datetime = Field(description="Fecha de alta, asignada por el sistema.")
    actualizado_en: datetime = Field(description="Fecha de la última modificación (FR-020).")

    @classmethod
    def de_cliente(cls, cliente: Cliente) -> ClienteRead:
        return cls.model_validate(cliente, from_attributes=True)


class ClienteListado(BaseModel):
    """Página de clientes con el total de los que cumplen el filtro (FR-007)."""

    items: list[ClienteRead]
    total: int = Field(
        description="Cantidad total de clientes que cumplen el filtro, no la de la página."
    )
    page: int
    size: int
