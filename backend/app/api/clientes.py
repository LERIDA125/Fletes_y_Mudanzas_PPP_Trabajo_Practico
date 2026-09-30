"""Routers de clientes (capa de Presentación).

Cada ruta recibe el request, valida el rol y delega en **un** método del gestor de Aplicación.
Acá no hay ninguna regla de negocio: si hace falta una regla nueva, va en
`app/application/clientes/gestor_clientes.py` (AGENTS.md §2).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.schemas.cliente import ClienteCreate, ClienteListado, ClienteRead, ClienteUpdate
from app.application.clientes.gestor_clientes import GestorClientes
from app.core.dependencias import ROL_ADMIN, get_gestor_clientes, require_rol

router = APIRouter(prefix="/api/clientes", tags=["clientes"])

TAMANO_DE_PAGINA_POR_DEFECTO = 20
TAMANO_DE_PAGINA_MAXIMO = 100

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


@router.get(
    "",
    response_model=ClienteListado,
    summary="Listar clientes",
    description=(
        "Devuelve una página de clientes dados de alta, con orden estable y la cantidad total de "
        "los que cumplen el filtro. Un filtro sin coincidencias devuelve la lista vacía con el "
        "total en cero, no un error."
    ),
)
def listar_clientes(
    gestor: Annotated[GestorClientes, Depends(get_gestor_clientes)],
    q: Annotated[
        str | None,
        Query(description="Texto a buscar dentro de la razón social. No distingue mayúsculas."),
    ] = None,
    page: Annotated[int, Query(ge=1, description="Número de página, empezando en 1.")] = 1,
    size: Annotated[
        int,
        Query(
            ge=1,
            le=TAMANO_DE_PAGINA_MAXIMO,
            description="Cantidad de clientes por página.",
        ),
    ] = TAMANO_DE_PAGINA_POR_DEFECTO,
) -> ClienteListado:
    clientes, total = gestor.listar(busqueda=q, offset=(page - 1) * size, limit=size)
    return ClienteListado(
        items=[ClienteRead.de_cliente(cliente) for cliente in clientes],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{cliente_id}",
    response_model=ClienteRead,
    summary="Ver el detalle de un cliente",
    description=(
        "Devuelve razón social, teléfono, dirección habitual, indicador de cuenta corriente y las "
        "fechas de alta y última modificación. Un cliente dado de baja se trata como inexistente."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un cliente activo con ese identificador (FR-016)."
        }
    },
)
def obtener_cliente(
    cliente_id: Annotated[int, Path(description="Identificador del cliente.", ge=1)],
    gestor: Annotated[GestorClientes, Depends(get_gestor_clientes)],
) -> ClienteRead:
    return ClienteRead.de_cliente(gestor.obtener(cliente_id))


@router.put(
    "/{cliente_id}",
    response_model=ClienteRead,
    summary="Modificar un cliente",
    description=(
        "Corrige los cuatro datos de un cliente existente. El identificador y la fecha de creación "
        "no se pueden cambiar, y la razón social no puede quedar igual a la de otro cliente. "
        "Guardar los mismos datos también refresca la fecha de última modificación."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite modificar clientes (FR-018)."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un cliente activo con ese identificador (FR-016)."
        },
        status.HTTP_409_CONFLICT: {
            "description": "La razón social nueva ya pertenece a otro cliente (FR-012)."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": (
                "Alguno de los cuatro datos requeridos falta o no cumple el formato, y no se "
                "guarda ningún cambio parcial (FR-011)."
            )
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def actualizar_cliente(
    cliente_id: Annotated[int, Path(description="Identificador del cliente.", ge=1)],
    datos: ClienteUpdate,
    gestor: Annotated[GestorClientes, Depends(get_gestor_clientes)],
) -> ClienteRead:
    cliente = gestor.actualizar(
        cliente_id,
        razon_social=datos.razon_social,
        telefono=datos.telefono,
        direccion_habitual=datos.direccion_habitual,
        tiene_cuenta_corriente=datos.tiene_cuenta_corriente,
    )
    return ClienteRead.de_cliente(cliente)


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Dar de baja un cliente",
    description=(
        "Elimina un cliente que no tenga servicios registrados. La baja es lógica —el registro "
        "queda desactivado pero conserva su identidad— por lo que repetir la baja no da error y la "
        "razón social no vuelve a estar disponible para otro cliente. Un cliente con servicios "
        "recién podrá eliminarse cuando se resuelva su historial."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite dar de baja clientes (FR-018)."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un cliente activo con ese identificador (FR-016)."
        },
        status.HTTP_409_CONFLICT: {
            "description": (
                "El cliente tiene servicios registrados y no se puede dar de baja (FR-015)."
            )
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def eliminar_cliente(
    cliente_id: Annotated[int, Path(description="Identificador del cliente.", ge=1)],
    gestor: Annotated[GestorClientes, Depends(get_gestor_clientes)],
) -> Response:
    gestor.eliminar(cliente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
