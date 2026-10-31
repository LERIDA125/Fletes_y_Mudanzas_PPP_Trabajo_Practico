"""Dependencias compartidas por los routers (capa de Presentación).

Acá se resuelve *cómo* se arma cada dependencia —el `Session`, los repositorios, el gestor de
Aplicación y el rol del usuario— y no *qué* se hace con los datos. Las reglas viven en
`app/application/` y `app/domain/` (AGENTS.md §2).
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.autenticacion.gestor_autenticacion import GestorAutenticacion
from app.application.autenticacion.puertos import UsuarioRepository
from app.application.choferes.gestor_choferes import GestorChoferes
from app.application.choferes.puertos import ChoferRepository
from app.application.clientes.gestor_clientes import GestorClientes
from app.application.clientes.puertos import ClienteRepository, ConsultaHistorialCliente
from app.application.cotizacion.calculadora import CalculadoraCotizacion
from app.application.cotizacion.cotizador_servicios import CotizadorServicios
from app.application.cotizacion.puertos import ConsultaConfiguracionCotizacion
from app.application.servicios.gestor_servicios import GestorServicios
from app.application.servicios.puertos import (
    ServicioRepository,
)
from app.application.tipos_vehiculo.gestor_tipos_vehiculo import GestorTiposVehiculo
from app.application.tipos_vehiculo.puertos import (
    ConsultaVehiculosPorTipo,
    TipoVehiculoRepository,
)
from app.application.usuarios.gestor_usuarios import GestorUsuarios
from app.application.vehiculos.gestor_vehiculos import GestorVehiculos
from app.application.vehiculos.puertos import (
    ConsultaChofer,
    ConsultaServiciosVehiculo,
    ConsultaTipoVehiculo,
    VehiculoRepository,
)
from app.core.config import get_settings
from app.core.seguridad import TokenInvalido, decodificar_token
from app.domain.rol import ROL_CHOFER as ROL_CHOFER_CANONICO
from app.domain.usuario import Usuario
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.chofer_repo import ChoferRepo
from app.infrastructure.repositories.cliente_repo import ClienteRepo
from app.infrastructure.repositories.configuracion_cotizacion_repo import (
    ConfiguracionCotizacionRepo,
)
from app.infrastructure.repositories.servicio_repo import ServicioRepo
from app.infrastructure.repositories.tipo_vehiculo_repo import TipoVehiculoRepo
from app.infrastructure.repositories.usuario_repo import UsuarioRepo
from app.infrastructure.repositories.vehiculo_repo import VehiculoRepo

HEADER_ROL = "X-Rol"
ROL_ADMIN = "admin"
ROL_CHOFER = "chofer"

esquema_bearer = HTTPBearer(auto_error=False)


def _error_no_autenticado() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o ausentes.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_repo_usuarios(db: Annotated[Session, Depends(get_db)]) -> UsuarioRepository:
    return UsuarioRepo(db)


def get_gestor_autenticacion(
    repositorio_usuarios: Annotated[UsuarioRepository, Depends(get_repo_usuarios)],
) -> GestorAutenticacion:
    return GestorAutenticacion(repositorio_usuarios)


def get_gestor_usuarios(
    repositorio_usuarios: Annotated[UsuarioRepository, Depends(get_repo_usuarios)],
) -> GestorUsuarios:
    return GestorUsuarios(repositorio_usuarios)


def _resolver_usuario(
    credenciales: HTTPAuthorizationCredentials,
    repo: UsuarioRepository,
) -> Usuario:
    try:
        payload = decodificar_token(credenciales.credentials)
        usuario_id = int(str(payload["sub"]))
    except (TokenInvalido, KeyError, TypeError, ValueError) as exc:
        raise _error_no_autenticado() from exc

    usuario = repo.obtener_por_id(usuario_id)
    if usuario is None or not usuario.activo:
        raise _error_no_autenticado()

    if usuario.rol == ROL_CHOFER_CANONICO and usuario.chofer_activo is not True:
        raise _error_no_autenticado()

    return usuario


def get_usuario_actual_opcional(
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
    repositorio: Annotated[UsuarioRepo, Depends(get_repo_usuarios)],
) -> Usuario | None:
    if credenciales is None:
        return None
    return _resolver_usuario(credenciales, repositorio)


def get_current_user(
    usuario: Annotated[Usuario | None, Depends(get_usuario_actual_opcional)],
) -> Usuario:
    if usuario is None:
        raise _error_no_autenticado()
    return usuario


def get_rol_actual(
    x_rol: Annotated[
        str | None, Header(alias=HEADER_ROL, description="Rol de prueba en modo desarrollo local.")
    ] = None,
    usuario: Annotated[Usuario | None, Depends(get_usuario_actual_opcional)] = None,
) -> str:
    """Devuelve el rol en minúsculas que consumen los routers existentes."""
    if usuario is not None:
        return usuario.rol_minusculas

    settings = get_settings()
    if settings.ENVIRONMENT.lower() == "dev" and settings.DEV_ASSUME_ADMIN:
        return (x_rol or ROL_ADMIN).strip().lower()

    raise _error_no_autenticado()


def require_rol(rol_requerido: str) -> Callable[..., str]:
    """Dependencia que corta el request con `403` si el rol no es el esperado (FR-018).

    Se usa como `dependencies=[Depends(require_rol("admin"))]`, así el handler no necesita el rol.
    """

    def _exigir_rol(rol_actual: Annotated[str, Depends(get_rol_actual)]) -> str:
        if rol_actual != rol_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere el rol {rol_requerido!r} para esta operación",
            )
        return rol_actual

    return _exigir_rol


def require_rol_autenticado(rol_requerido: str) -> Callable[..., Usuario]:
    """Exige un JWT válido y el rol indicado, sin aceptar el modo demo `X-Rol`.

    Las rutas nuevas de RBAC usan esta dependencia para que un request anónimo sea siempre
    `401`, incluso cuando `DEV_ASSUME_ADMIN` está activo (CA-04).
    """

    def _exigir_rol(usuario: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
        if usuario.rol_minusculas != rol_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere el rol {rol_requerido!r} para esta operación",
            )
        return usuario

    return _exigir_rol


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


# ── Servicios y Cotizaciones (H8) ─────────────────────────────────────────────


def get_repo_servicios(db: Annotated[Session, Depends(get_db)]) -> ServicioRepository:
    return ServicioRepo(db)


def get_repo_configuracion_cotizacion(
    db: Annotated[Session, Depends(get_db)],
) -> ConsultaConfiguracionCotizacion:
    return ConfiguracionCotizacionRepo(db)


def get_calculadora_cotizacion(
    tipos: Annotated[TipoVehiculoRepository, Depends(get_repo_tipos_vehiculo)],
    configuracion: Annotated[
        ConsultaConfiguracionCotizacion, Depends(get_repo_configuracion_cotizacion)
    ],
) -> CalculadoraCotizacion:
    return CalculadoraCotizacion(tipos, configuracion)


def get_gestor_servicios(
    repositorio: Annotated[ServicioRepository, Depends(get_repo_servicios)],
    tipos: Annotated[TipoVehiculoRepository, Depends(get_repo_tipos_vehiculo)],
    clientes: Annotated[ClienteRepository, Depends(get_repo_clientes)],
    choferes: Annotated[ChoferRepository, Depends(get_repo_choferes)],
    vehiculos: Annotated[VehiculoRepository, Depends(get_repo_vehiculos)],
    calculadora: Annotated[CalculadoraCotizacion, Depends(get_calculadora_cotizacion)],
) -> GestorServicios:
    return GestorServicios(
        repositorio=repositorio,
        calculadora=calculadora,
        consulta_clientes=clientes,
        consulta_choferes=choferes,
        consulta_vehiculos=vehiculos,
        consulta_tipos=tipos,
        registro_clientes=clientes,
    )


def get_cotizador_servicios(
    calculadora: Annotated[CalculadoraCotizacion, Depends(get_calculadora_cotizacion)],
) -> CotizadorServicios:
    return CotizadorServicios(calculadora=calculadora)
