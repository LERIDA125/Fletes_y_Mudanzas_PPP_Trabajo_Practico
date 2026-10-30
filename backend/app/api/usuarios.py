"""Routers de gestión de usuarios (capa de Presentación)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.schemas.usuarios import UsuarioCreate, UsuarioRead
from app.application.usuarios.gestor_usuarios import GestorUsuarios
from app.core.dependencias import ROL_ADMIN, get_gestor_usuarios, require_rol_autenticado
from app.domain.usuario import Usuario

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.post(
    "",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una cuenta de usuario",
    description=(
        "Crea una cuenta ADMIN o CHOFER. Solo un ADMIN autenticado puede hacerlo; "
        "una cuenta CHOFER exige un chofer activo y sin otra cuenta asociada."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido o cuenta no habilitada."
        },
        status.HTTP_403_FORBIDDEN: {"description": "El rol del usuario no es ADMIN."},
        status.HTTP_409_CONFLICT: {
            "description": "El username ya existe o el chofer ya tiene una cuenta."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": (
                "Payload inválido, rol/chofer inconsistente, chofer inexistente o inactivo."
            )
        },
    },
)
def crear_usuario(
    datos: UsuarioCreate,
    solicitante: Annotated[Usuario, Depends(require_rol_autenticado(ROL_ADMIN))],
    gestor: Annotated[GestorUsuarios, Depends(get_gestor_usuarios)],
) -> UsuarioRead:
    usuario = gestor.registrar(
        username=datos.username,
        password=datos.password,
        rol=datos.rol,
        id_chofer=datos.id_chofer,
        creado_por=solicitante.id,
    )
    return UsuarioRead.de_usuario(usuario)
