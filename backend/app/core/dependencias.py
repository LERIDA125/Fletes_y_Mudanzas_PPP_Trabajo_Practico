"""Dependencias compartidas por los routers (capa de Presentación).

Acá se resuelve *cómo* se arma cada dependencia —el `Session`, los repositorios, el gestor de
Aplicación y el rol del usuario— y no *qué* se hace con los datos. Las reglas viven en
`app/application/` y `app/domain/` (AGENTS.md §2).
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.application.clientes.gestor_clientes import GestorClientes
from app.application.clientes.puertos import ClienteRepository, ConsultaHistorialCliente
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
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.cliente_repo import ClienteRepo
from app.infrastructure.repositories.historial_cliente_repo import HistorialClienteRepoVacio
from app.infrastructure.repositories.tipo_vehiculo_repo import TipoVehiculoRepo
from app.infrastructure.repositories.vehiculo_repo import VehiculoRepo

HEADER_ROL = "X-Rol"
ROL_ADMIN = "admin"
ROL_CHOFER = "chofer"


def get_rol_actual(
    x_rol: Annotated[
        str | None, Header(alias=HEADER_ROL, description="Rol del usuario autenticado.")
    ] = None,
) -> str:
    """Devuelve el rol del usuario que hace el request.

    TODO(AGENTS): es un **stub** hasta que exista la historia de autenticación. Se lee el rol del
    header `X-Rol` en vez de decodificar un JWT, así que cualquiera puede mandarlo. Cuando llegue
    la historia de autenticación se cambia solo el cuerpo de esta función y las rutas no se tocan.
    """
    return (x_rol or ROL_CHOFER).strip().lower()


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


# ── Clientes (H1) ─────────────────────────────────────────────────────────────


def get_repo_clientes(db: Annotated[Session, Depends(get_db)]) -> ClienteRepository:
    return ClienteRepo(db)


def get_historial_clientes() -> ConsultaHistorialCliente:
    """Inyección del puerto de historial. Ver `HistorialClienteRepoVacio` para el TODO(AGENTS)."""
    return HistorialClienteRepoVacio()


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


def get_consulta_chofer() -> ConsultaChofer:
    """Inyección del puerto de consulta de choferes.

    STUB temporal: devuelve False hasta que exista la historia de Choferes (H2). Ver spec H4.
    """
    from app.infrastructure.repositories.consulta_stub import ConsultaChoferVacio

    return ConsultaChoferVacio()


def get_consulta_servicios_vehiculo() -> ConsultaServiciosVehiculo:
    """Inyección del puerto de consulta de servicios por vehículo.

    STUB temporal: devuelve False hasta que exista la historia de Servicios (H6).
    Ver spec H4, DP-03.
    """
    from app.infrastructure.repositories.consulta_stub import ConsultaServiciosVehiculoVacio

    return ConsultaServiciosVehiculoVacio()


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
