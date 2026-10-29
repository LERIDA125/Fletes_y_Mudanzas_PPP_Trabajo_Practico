"""Router de Autenticación, Multi-Admin y Creación de Usuarios (H9)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.autenticacion import (
    LoginRequest,
    TokenRead,
    UsuarioCreate,
    UsuarioRead,
)
from app.application.autenticacion.gestor_autenticacion import GestorAutenticacion
from app.core.dependencias import (
    ROL_ADMIN,
    UsuarioAutenticado,
    get_gestor_autenticacion,
    get_usuario_actual,
    require_rol,
)

router = APIRouter(prefix="/api/auth", tags=["autenticacion"])


@router.post(
    "/login",
    response_model=TokenRead,
    summary="Iniciar sesión con usuario y contraseña",
    description=(
        "Autentica cuentas activas de rol 'admin' o 'chofer' y emite un token JWT Bearer "
        "con expiración de 30 minutos."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Usuario o contraseña incorrectos, o cuenta inactiva."
        }
    },
)
def login(
    datos: LoginRequest,
    gestor: Annotated[GestorAutenticacion, Depends(get_gestor_autenticacion)],
) -> TokenRead:
    sesion = gestor.iniciar_sesion(username=datos.username, password=datos.password)
    return TokenRead(
        access_token=sesion.access_token,
        token_type="bearer",
        expires_in=sesion.expires_in,
        usuario=UsuarioRead.de_usuario(sesion.usuario),
    )


@router.get(
    "/me",
    response_model=UsuarioRead,
    summary="Obtener identidad del usuario autenticado",
    description="Devuelve los datos vigentes del usuario dueño del token Bearer.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token ausente, inválido, expirado o usuario inactivo."
        }
    },
)
def obtener_perfil_actual(
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> UsuarioRead:
    if usuario_actual.id is None:
        return UsuarioRead(
            id=0,
            username=usuario_actual.username,
            rol=usuario_actual.rol,
            id_chofer=usuario_actual.id_chofer,
            activo=usuario_actual.activo,
        )
    return UsuarioRead(
        id=usuario_actual.id,
        username=usuario_actual.username,
        rol=usuario_actual.rol,
        id_chofer=usuario_actual.id_chofer,
        activo=usuario_actual.activo,
    )


@router.get(
    "/usuarios",
    response_model=list[UsuarioRead],
    summary="Listar cuentas de usuarios (Administradores y Choferes)",
    description=(
        "Devuelve todas las cuentas de usuario registradas para auditoría y gestión "
        "multi-admin. Requiere rol 'admin'."
    ),
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def listar_usuarios(
    gestor: Annotated[GestorAutenticacion, Depends(get_gestor_autenticacion)],
) -> list[UsuarioRead]:
    return [UsuarioRead.de_usuario(u) for u in gestor.listar_usuarios()]


@router.post(
    "/usuarios",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cuenta de Administrador o de Chofer",
    description=(
        "Permite a un administrador dar de alta otro administrador (soporte multi-admin) "
        "o crearle el usuario de acceso a un chofer activo (vinculando `id_chofer`)."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Solo un usuario con rol 'admin' puede crear cuentas."
        },
        status.HTTP_409_CONFLICT: {
            "description": "El username ya existe o el chofer ya tiene un usuario asignado."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Datos inválidos o chofer inexistente/inactivo."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def crear_usuario(
    datos: UsuarioCreate,
    gestor: Annotated[GestorAutenticacion, Depends(get_gestor_autenticacion)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> UsuarioRead:
    if datos.rol == "admin" and datos.id_chofer is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Una cuenta con rol 'admin' no puede vincularse a un chofer",
        )
    if datos.rol == "chofer" and datos.id_chofer is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Para crear una cuenta de rol 'chofer' debés indicar id_chofer",
        )
    creado = gestor.crear_usuario(
        username=datos.username,
        password=datos.password,
        rol=datos.rol,
        id_chofer=datos.id_chofer,
        creado_por_id=usuario_actual.id,
    )
    return UsuarioRead.de_usuario(creado)
