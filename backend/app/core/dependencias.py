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
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.cliente_repo import ClienteRepo
from app.infrastructure.repositories.historial_cliente_repo import HistorialClienteRepoVacio

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
