"""Schemas de autenticación (capa de Presentación)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.usuario import PASSWORD_MAX, USERNAME_MAX, Usuario


class LoginRequest(BaseModel):
    """Credenciales de login. No se valida aquí la política de alta: un error de login es 401."""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(
        max_length=USERNAME_MAX,
        description="Nombre de usuario normalizado por el backend.",
        examples=["admin"],
    )
    password: str = Field(
        max_length=PASSWORD_MAX,
        description="Contraseña en claro; nunca se registra ni se devuelve.",
        examples=["una-clave-segura"],
    )


class TokenRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(description="JWT de acceso.")
    token_type: Literal["bearer"] = Field(default="bearer", description="Esquema del token.")
    expires_in: int = Field(description="Vigencia del token en segundos.")


class UsuarioActualRead(BaseModel):
    """Perfil del usuario autenticado; nunca incluye `password_hash` (CA-10)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    rol: str = Field(description="Código canónico: ADMIN o CHOFER.")
    id_chofer: int | None

    @classmethod
    def de_usuario(cls, usuario: Usuario) -> UsuarioActualRead:
        return cls.model_validate(usuario, from_attributes=True)
