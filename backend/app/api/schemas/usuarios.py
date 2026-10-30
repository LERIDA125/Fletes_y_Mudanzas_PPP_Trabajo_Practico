"""Schemas de gestión de usuarios (capa de Presentación)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.rol import normalizar_rol
from app.domain.usuario import (
    PASSWORD_MAX,
    USERNAME_MAX,
    USERNAME_MIN,
    Usuario,
    normalizar_username,
)


class UsuarioCreate(BaseModel):
    """Alta de cuenta ADMIN o CHOFER; la coherencia rol/chofer la valida el dominio."""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(
        min_length=USERNAME_MIN,
        max_length=USERNAME_MAX,
        description="Nombre de usuario único; se normaliza a minúsculas.",
    )
    password: str = Field(
        min_length=1,
        max_length=PASSWORD_MAX,
        description="Contraseña; la política completa se valida en dominio.",
    )
    rol: str = Field(description="ADMIN o CHOFER.")
    id_chofer: int | None = Field(
        default=None,
        ge=1,
        description="Chofer activo y libre para cuentas CHOFER; debe ser null para ADMIN.",
    )

    @field_validator("username", mode="before")
    @classmethod
    def _normalizar_username(cls, valor: object) -> object:
        return normalizar_username(valor) if isinstance(valor, str) else valor

    @field_validator("rol", mode="before")
    @classmethod
    def _normalizar_rol(cls, valor: object) -> object:
        return normalizar_rol(valor) if isinstance(valor, str) else valor


class UsuarioRead(BaseModel):
    """Cuenta de usuario sin datos sensibles (CA-10)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    rol: str = Field(description="Código canónico: ADMIN o CHOFER.")
    id_chofer: int | None
    activo: bool
    creado_por: int | None
    creado_en: datetime | None
    actualizado_en: datetime | None

    @classmethod
    def de_usuario(cls, usuario: Usuario) -> UsuarioRead:
        return cls.model_validate(usuario, from_attributes=True)
