"""Schemas Pydantic para Autenticación y Gestión de Usuarios (H9)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.usuario import Usuario


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., min_length=1, max_length=60, description="Nombre de usuario.")
    password: str = Field(..., min_length=1, max_length=128, description="Contraseña en claro.")


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(
        ...,
        min_length=3,
        max_length=60,
        description="Nombre de usuario único (se normaliza en minúsculas).",
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Contraseña inicial asignada por el administrador.",
    )
    rol: Literal["admin", "chofer"] = Field(
        ...,
        description="Rol de la cuenta: 'admin' (multi-admin) o 'chofer'.",
    )
    id_chofer: int | None = Field(
        default=None,
        gt=0,
        description="ID del chofer activo vinculado (obligatorio si rol='chofer').",
    )


class UsuarioRead(BaseModel):
    id: int
    username: str
    rol: str
    id_chofer: int | None = None
    activo: bool
    creado_por_id: int | None = None
    modificado_por_id: int | None = None
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None

    @classmethod
    def de_usuario(cls, usuario: Usuario) -> UsuarioRead:
        if usuario.id is None:
            raise ValueError("No se puede serializar un Usuario sin id")
        return cls(
            id=usuario.id,
            username=usuario.username,
            rol=usuario.rol,
            id_chofer=usuario.id_chofer,
            activo=usuario.activo,
            creado_por_id=usuario.creado_por_id,
            modificado_por_id=usuario.modificado_por_id,
            creado_en=usuario.creado_en,
            actualizado_en=usuario.actualizado_en,
        )


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: UsuarioRead
