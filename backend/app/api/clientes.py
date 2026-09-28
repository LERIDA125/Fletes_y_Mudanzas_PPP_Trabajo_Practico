"""Routers de clientes (capa de Presentación).

Cada ruta recibe el request, valida el rol y delega en **un** método del gestor de Aplicación.
Acá no hay ninguna regla de negocio: si hace falta una regla nueva, va en
`app/application/clientes/gestor_clientes.py` (AGENTS.md §2).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.schemas.cliente import ClienteCreate, ClienteRead
from app.application.clientes.gestor_clientes import GestorClientes
from app.core.dependencias import ROL_ADMIN, get_gestor_clientes, require_rol

router = APIRouter(prefix="/api/clientes", tags=["clientes"])

RESPUESTAS_ALTA = {
    status.HTTP_403_FORBIDDEN: {
        "description": "El rol del usuario no permite dar de alta clientes (FR-018)."
    },
    status.HTTP_409_CONFLICT: {
        "description": "Ya existe un cliente registrado con esa razón social (FR-004)."
    },
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "description": (
            "Alguno de los cuatro datos requeridos falta o no cumple el formato (FR-011)."
        )
    },
}


@router.post(
    "",
    response_model=ClienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un cliente",
    description=(
        "Da de alta un cliente con razón social, teléfono, dirección habitual e indicador de "
        "cuenta corriente. La razón social no puede repetirse, aunque cambie de mayúsculas, "
        "minúsculas o acentos. El identificador y las fechas los asigna el sistema."
    ),
    responses=RESPUESTAS_ALTA,
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def registrar_cliente(
    datos: ClienteCreate,
    gestor: Annotated[GestorClientes, Depends(get_gestor_clientes)],
) -> ClienteRead:
    cliente = gestor.registrar(
        razon_social=datos.razon_social,
        telefono=datos.telefono,
        direccion_habitual=datos.direccion_habitual,
        tiene_cuenta_corriente=datos.tiene_cuenta_corriente,
    )
    return ClienteRead.de_cliente(cliente)
