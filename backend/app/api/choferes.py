"""Routers de choferes (capa de Presentación).

Cada ruta recibe el request, valida el rol y delega en **un** método del gestor de Aplicación.
Acá no hay ninguna regla de negocio.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.schemas.chofer import ChoferCreate, ChoferListado, ChoferRead, ChoferUpdate
from app.application.choferes.gestor_choferes import GestorChoferes
from app.core.dependencias import (
    ROL_ADMIN,
    UsuarioAutenticado,
    get_gestor_choferes,
    get_usuario_actual,
    require_rol,
)

router = APIRouter(prefix="/api/choferes", tags=["choferes"])

TAMANO_DE_PAGINA_POR_DEFECTO = 20
TAMANO_DE_PAGINA_MAXIMO = 100


@router.post(
    "",
    response_model=ChoferRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un chofer",
    description=(
        "Da de alta un chofer con nombre completo y teléfono. El identificador, las fechas, "
        "`activo` y `saldo_a_favor` los asigna el sistema."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite dar de alta choferes."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Alguno de los datos requeridos falta o no cumple el formato."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def registrar_chofer(
    datos: ChoferCreate,
    gestor: Annotated[GestorChoferes, Depends(get_gestor_choferes)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ChoferRead:
    chofer = gestor.registrar(
        nombre_completo=datos.nombre_completo,
        telefono=datos.telefono,
        usuario_id=usuario_actual.id,
    )
    return ChoferRead.de_chofer(chofer)


@router.get(
    "",
    response_model=ChoferListado,
    summary="Listar choferes activos",
    description=(
        "Devuelve una página de choferes activos, con orden estable y la cantidad total de los "
        "que cumplen el filtro. Los choferes dados de baja no aparecen."
    ),
)
def listar_choferes(
    gestor: Annotated[GestorChoferes, Depends(get_gestor_choferes)],
    q: Annotated[str | None, Query(description="Texto a buscar dentro del nombre.")] = None,
    page: Annotated[int, Query(ge=1, description="Número de página, empezando en 1.")] = 1,
    size: Annotated[
        int,
        Query(ge=1, le=TAMANO_DE_PAGINA_MAXIMO, description="Cantidad de choferes por página."),
    ] = TAMANO_DE_PAGINA_POR_DEFECTO,
) -> ChoferListado:
    choferes, total = gestor.listar(busqueda=q, offset=(page - 1) * size, limit=size)
    return ChoferListado(
        items=[ChoferRead.de_chofer(chofer) for chofer in choferes],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{chofer_id}",
    response_model=ChoferRead,
    summary="Ver el detalle de un chofer",
    description=(
        "Devuelve nombre completo, teléfono, estado, saldo a favor y las fechas de alta y última "
        "modificación. Un chofer dado de baja se trata como inexistente."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un chofer activo con ese identificador."
        }
    },
)
def obtener_chofer(
    chofer_id: Annotated[int, Path(description="Identificador del chofer.", ge=1)],
    gestor: Annotated[GestorChoferes, Depends(get_gestor_choferes)],
) -> ChoferRead:
    return ChoferRead.de_chofer(gestor.obtener(chofer_id))


@router.put(
    "/{chofer_id}",
    response_model=ChoferRead,
    summary="Modificar un chofer",
    description=(
        "Corrige el nombre completo y el teléfono de un chofer existente. El identificador, la "
        "fecha de creación y el saldo no se pueden cambiar."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite modificar choferes."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un chofer activo con ese identificador."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Alguno de los datos requeridos falta o no cumple el formato."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def actualizar_chofer(
    chofer_id: Annotated[int, Path(description="Identificador del chofer.", ge=1)],
    datos: ChoferUpdate,
    gestor: Annotated[GestorChoferes, Depends(get_gestor_choferes)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ChoferRead:
    chofer = gestor.actualizar(
        chofer_id,
        nombre_completo=datos.nombre_completo,
        telefono=datos.telefono,
        usuario_id=usuario_actual.id,
    )
    return ChoferRead.de_chofer(chofer)


@router.delete(
    "/{chofer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Dar de baja un chofer",
    description="Da de baja un chofer. La baja es lógica: la fila queda con `activo=false`.",
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite dar de baja choferes."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un chofer activo con ese identificador."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def eliminar_chofer(
    chofer_id: Annotated[int, Path(description="Identificador del chofer.", ge=1)],
    gestor: Annotated[GestorChoferes, Depends(get_gestor_choferes)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> Response:
    gestor.eliminar(chofer_id, usuario_id=usuario_actual.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
