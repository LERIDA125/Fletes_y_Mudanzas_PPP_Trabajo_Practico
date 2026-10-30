"""Routers de autenticación (capa de Presentación)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.schemas.autenticacion import LoginRequest, TokenRead, UsuarioActualRead
from app.application.autenticacion.gestor_autenticacion import GestorAutenticacion
from app.core.dependencias import get_current_user, get_gestor_autenticacion
from app.domain.usuario import Usuario

router = APIRouter(prefix="/api/auth", tags=["autenticacion"])


@router.post(
    "/login",
    response_model=TokenRead,
    summary="Iniciar sesión",
    description=(
        "Valida las credenciales contra el hash Argon2id y devuelve un JWT de 30 minutos. "
        "Un usuario inexistente, inactivo o una contraseña incorrecta responden el mismo 401."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Credenciales inválidas o cuenta no habilitada."
        }
    },
)
def login(
    datos: LoginRequest,
    gestor: Annotated[GestorAutenticacion, Depends(get_gestor_autenticacion)],
) -> TokenRead:
    token = gestor.autenticar(username=datos.username, password=datos.password)
    return TokenRead(
        access_token=token.access_token,
        token_type="bearer",
        expires_in=token.expires_in,
    )


@router.get(
    "/me",
    response_model=UsuarioActualRead,
    summary="Ver el perfil autenticado",
    description="Devuelve la identidad resuelta desde el token y la base, sin datos sensibles.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido o cuenta no habilitada."
        }
    },
)
def me(usuario: Annotated[Usuario, Depends(get_current_user)]) -> UsuarioActualRead:
    return UsuarioActualRead.de_usuario(usuario)
