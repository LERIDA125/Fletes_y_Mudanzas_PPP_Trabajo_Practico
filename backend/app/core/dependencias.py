"""Dependencias compartidas por los routers (capa de Presentación).

Acá se resuelve *cómo* se arma cada dependencia —el `Session`, los repositorios, el gestor de
Aplicación y la identidad/rol del usuario— y no *qué* se hace con los datos. Las reglas viven en
`app/application/` y `app/domain/` (AGENTS.md §2).
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.application.autenticacion.gestor_autenticacion import GestorAutenticacion
from app.application.autenticacion.puertos import UsuarioRepository
from app.application.choferes.gestor_choferes import GestorChoferes
from app.application.choferes.puertos import ChoferRepository
from app.application.clientes.gestor_clientes import GestorClientes
from app.application.clientes.puertos import ClienteRepository, ConsultaHistorialCliente
from app.application.cotizacion.calculadora import CalculadoraCotizacion
from app.application.servicios.gestor_servicios import GestorServicios
from app.application.servicios.puertos import AlmacenamientoRemitosPort, ServicioRepository
from app.application.tipos_vehiculo.gestor_tipos_vehiculo import GestorTiposVehiculo
from app.application.tipos_vehiculo.puertos import (
    ConsultaVehiculosPorTipo,
    TipoVehiculoRepository,
)
from app.application.vehiculos.gestor_vehiculos import GestorVehiculos
from app.application.vehiculos.puertos import (
    ConsultaChofer,
    ConsultaServiciosVehiculo,
    ConsultaTipoVehiculo,
    VehiculoRepository,
)
from app.core.config import get_settings
from app.domain.errores import CredencialesInvalidas
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.chofer_repo import ChoferRepo
from app.infrastructure.repositories.cliente_repo import ClienteRepo
from app.infrastructure.repositories.servicio_repo import ServicioRepo
from app.infrastructure.repositories.tipo_vehiculo_repo import TipoVehiculoRepo
from app.infrastructure.repositories.usuario_repo import UsuarioRepo
from app.infrastructure.repositories.vehiculo_repo import VehiculoRepo
from app.infrastructure.security.jwt_service import JWTService
from app.infrastructure.security.password_hasher import PasswordHasher
from app.infrastructure.storage.almacenamiento_remitos import AlmacenamientoRemitosHibrido

HEADER_ROL = "X-Rol"
ROL_ADMIN = "admin"
ROL_CHOFER = "chofer"


@dataclass(frozen=True)
class UsuarioAutenticado:
    """Identidad vigente resuelta por la capa de seguridad para auditoría y control de acceso."""

    id: int | None
    username: str
    rol: str
    id_chofer: int | None = None
    activo: bool = True


# ── Autenticación y Usuarios (H9) ─────────────────────────────────────────────


def get_repo_usuarios(db: Annotated[Session, Depends(get_db)]) -> UsuarioRepository:
    return UsuarioRepo(db)


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_service() -> JWTService:
    settings = get_settings()
    return JWTService(secret_key=settings.JWT_SECRET, ttl_segundos=settings.JWT_TTL_SECONDS)


def get_gestor_autenticacion(
    repositorio_usuarios: Annotated[UsuarioRepository, Depends(get_repo_usuarios)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    tokens: Annotated[JWTService, Depends(get_jwt_service)],
    db: Annotated[Session, Depends(get_db)],
) -> GestorAutenticacion:
    return GestorAutenticacion(
        repositorio_usuarios=repositorio_usuarios,
        hasher=hasher,
        tokens=tokens,
        consulta_choferes=ChoferRepo(db),
    )


def _extraer_bearer_token(authorization: str) -> str:
    esquema, _, token = authorization.strip().partition(" ")
    if esquema.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Encabezado Authorization inválido; se esperaba 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token.strip()


def get_usuario_actual(
    x_rol: Annotated[
        str | None, Header(alias=HEADER_ROL, description="Rol de prueba en modo desarrollo local.")
    ] = None,
    authorization: Annotated[
        str | None, Header(alias="Authorization", description="Token Bearer JWT.")
    ] = None,
    gestor_auth: Annotated[
        GestorAutenticacion | None, Depends(get_gestor_autenticacion)
    ] = None,
) -> UsuarioAutenticado:
    """Resuelve el usuario autenticado vía Bearer JWT o fallback explícito de desarrollo."""
    if isinstance(authorization, str) and authorization.strip():
        token = _extraer_bearer_token(authorization)
        if gestor_auth is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Servicio de autenticación no disponible.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            usuario = gestor_auth.resolver_token(token)
        except CredencialesInvalidas as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
                headers={"WWW-Authenticate": "Bearer"},
            ) from error
        return UsuarioAutenticado(
            id=usuario.id,
            username=usuario.username,
            rol=usuario.rol,
            id_chofer=usuario.id_chofer,
            activo=usuario.activo,
        )

    settings = get_settings()
    if settings.ENVIRONMENT.lower() == "dev" and settings.DEV_ASSUME_ADMIN:
        rol_dev = (x_rol if isinstance(x_rol, str) and x_rol else ROL_ADMIN).strip().lower()
        return UsuarioAutenticado(
            id=None,
            username=f"dev-{rol_dev}",
            rol=rol_dev,
            id_chofer=None,
            activo=True,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="La autenticación no está habilitada para este entorno.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_rol_actual(
    x_rol: Annotated[
        str | None, Header(alias=HEADER_ROL, description="Rol de prueba en modo desarrollo local.")
    ] = None,
    authorization: Annotated[
        str | None, Header(alias="Authorization", description="Token Bearer JWT.")
    ] = None,
    gestor_auth: Annotated[
        GestorAutenticacion | None, Depends(get_gestor_autenticacion)
    ] = None,
) -> str:
    """Devuelve el rol vigente del usuario autenticado (o fallback en modo dev explícito)."""
    usuario = get_usuario_actual(
        x_rol=x_rol,
        authorization=authorization,
        gestor_auth=gestor_auth,
    )
    return usuario.rol


def require_rol(rol_requerido: str) -> Callable[..., str]:
    """Dependencia que corta el request con `403` si el rol no es el esperado (FR-018)."""

    def _exigir_rol(rol_actual: Annotated[str, Depends(get_rol_actual)]) -> str:
        if rol_actual != rol_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere el rol {rol_requerido!r} para esta operación",
            )
        return rol_actual

    return _exigir_rol


def require_roles(*roles_permitidos: str) -> Callable[..., UsuarioAutenticado]:
    """Permite el acceso a cualquiera de los roles listados y devuelve el `UsuarioAutenticado`."""
    conjunto = set(roles_permitidos)

    def _exigir_roles(
        usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
    ) -> UsuarioAutenticado:
        if usuario_actual.rol not in conjunto:
            roles_txt = ", ".join(repr(r) for r in roles_permitidos)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los roles ({roles_txt}) para esta operación",
            )
        return usuario_actual

    return _exigir_roles


# ── Clientes (H1) ─────────────────────────────────────────────────────────────


def get_repo_clientes(db: Annotated[Session, Depends(get_db)]) -> ClienteRepository:
    return ClienteRepo(db)


def get_historial_clientes(
    db: Annotated[Session, Depends(get_db)],
) -> ConsultaHistorialCliente:
    """Consulta servicios reales antes de permitir la baja lógica de un cliente."""
    return ServicioRepo(db)


def get_gestor_clientes(
    repositorio_clientes: Annotated[ClienteRepository, Depends(get_repo_clientes)],
    consulta_historial: Annotated[ConsultaHistorialCliente, Depends(get_historial_clientes)],
) -> GestorClientes:
    """Único punto donde se arma el gestor de Aplicación.

    Los tests de integración la sobreescriben con `app.dependency_overrides` para inyectar dobles.
    """
    return GestorClientes(
        repositorio_clientes=repositorio_clientes,
        consulta_historial=consulta_historial,
    )


# ── Tipos de Vehículo (H4) ────────────────────────────────────────────────────


def get_repo_tipos_vehiculo(db: Annotated[Session, Depends(get_db)]) -> TipoVehiculoRepository:
    return TipoVehiculoRepo(db)


def get_consulta_vehiculos_por_tipo(
    db: Annotated[Session, Depends(get_db)],
) -> ConsultaVehiculosPorTipo:
    """Inyección del puerto de consulta de vehículos por tipo usando VehiculoRepo."""
    return VehiculoRepo(db)


def get_gestor_tipos_vehiculo(
    repositorio_tipos: Annotated[TipoVehiculoRepository, Depends(get_repo_tipos_vehiculo)],
    consulta_vehiculos: Annotated[
        ConsultaVehiculosPorTipo, Depends(get_consulta_vehiculos_por_tipo)
    ],
) -> GestorTiposVehiculo:
    """Único punto donde se arma el gestor de tipos de vehículo."""
    return GestorTiposVehiculo(
        repositorio_tipos=repositorio_tipos,
        consulta_vehiculos=consulta_vehiculos,
    )


# ── Vehículos (H4) ────────────────────────────────────────────────────────────


def get_repo_vehiculos(db: Annotated[Session, Depends(get_db)]) -> VehiculoRepository:
    return VehiculoRepo(db)


def get_consulta_tipo_vehiculo(
    db: Annotated[Session, Depends(get_db)],
) -> ConsultaTipoVehiculo:
    """Inyección del puerto de consulta de tipos de vehículo usando TipoVehiculoRepo."""
    return TipoVehiculoRepo(db)


def get_consulta_chofer(db: Annotated[Session, Depends(get_db)]) -> ConsultaChofer:
    """Inyección del puerto de consulta de choferes usando ChoferRepo (H3)."""
    return ChoferRepo(db)


def get_consulta_servicios_vehiculo(
    db: Annotated[Session, Depends(get_db)],
) -> ConsultaServiciosVehiculo:
    """Consulta servicios persistidos para proteger la baja lógica del vehículo."""
    return ServicioRepo(db)


def get_gestor_vehiculos(
    repositorio_vehiculos: Annotated[VehiculoRepository, Depends(get_repo_vehiculos)],
    consulta_tipos: Annotated[ConsultaTipoVehiculo, Depends(get_consulta_tipo_vehiculo)],
    consulta_choferes: Annotated[ConsultaChofer, Depends(get_consulta_chofer)],
    consulta_servicios: Annotated[
        ConsultaServiciosVehiculo, Depends(get_consulta_servicios_vehiculo)
    ],
) -> GestorVehiculos:
    """Único punto donde se arma el gestor de vehículos."""
    return GestorVehiculos(
        repositorio_vehiculos=repositorio_vehiculos,
        consulta_tipos=consulta_tipos,
        consulta_choferes=consulta_choferes,
        consulta_servicios=consulta_servicios,
    )


# ── Choferes (H3) ─────────────────────────────────────────────────────────────


def get_repo_choferes(db: Annotated[Session, Depends(get_db)]) -> ChoferRepository:
    return ChoferRepo(db)


def get_gestor_choferes(
    repositorio_choferes: Annotated[ChoferRepository, Depends(get_repo_choferes)],
) -> GestorChoferes:
    """Único punto donde se arma el gestor de choferes."""
    return GestorChoferes(repositorio_choferes=repositorio_choferes)


# ── Servicios y Cotizaciones (H8 / H10) ───────────────────────────────────────


def get_repo_servicios(db: Annotated[Session, Depends(get_db)]) -> ServicioRepository:
    return ServicioRepo(db)


def get_almacenamiento_remitos() -> AlmacenamientoRemitosPort:
    return AlmacenamientoRemitosHibrido()


def get_gestor_servicios(
    repositorio: Annotated[ServicioRepository, Depends(get_repo_servicios)],
    tipos: Annotated[TipoVehiculoRepository, Depends(get_repo_tipos_vehiculo)],
    clientes: Annotated[ClienteRepository, Depends(get_repo_clientes)],
    choferes: Annotated[ChoferRepository, Depends(get_repo_choferes)],
    vehiculos: Annotated[VehiculoRepository, Depends(get_repo_vehiculos)],
    almacenamiento_remitos: Annotated[
        AlmacenamientoRemitosPort, Depends(get_almacenamiento_remitos)
    ],
) -> GestorServicios:
    return GestorServicios(
        repositorio=repositorio,
        calculadora=CalculadoraCotizacion(tipos),
        consulta_clientes=clientes,
        consulta_choferes=choferes,
        consulta_vehiculos=vehiculos,
        consulta_tipos=tipos,
        registro_clientes=clientes,
        almacenamiento_remitos=almacenamiento_remitos,
    )
