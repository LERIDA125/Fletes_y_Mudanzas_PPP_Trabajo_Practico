"""Routers de vehículos (capa de Presentación).

Cada ruta recibe el request, valida el rol y delega en **un** método del gestor de Aplicación.
Acá no hay ninguna regla de negocio.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.schemas.vehiculo import VehiculoCreate, VehiculoListado, VehiculoRead, VehiculoUpdate
from app.application.vehiculos.gestor_vehiculos import GestorVehiculos
from app.core.dependencias import ROL_ADMIN, get_gestor_vehiculos, require_rol

router = APIRouter(prefix="/api/vehiculos", tags=["vehiculos"])

TAMANO_DE_PAGINA_POR_DEFECTO = 20
TAMANO_DE_PAGINA_MAXIMO = 100

RESPUESTAS_ALTA = {
    status.HTTP_403_FORBIDDEN: {
        "description": "El rol del usuario no permite dar de alta vehículos."
    },
    status.HTTP_409_CONFLICT: {"description": "Ya existe un vehículo con esa patente."},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "description": "Alguno de los datos requeridos falta o no cumple el formato."
    },
}


@router.post(
    "",
    response_model=VehiculoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un vehículo",
    description=(
        "Da de alta un vehículo con patente, tipo de vehículo y opcionalmente un chofer habitual. "
        "La patente no puede repetirse. El identificador y las fechas los asigna el sistema."
    ),
    responses=RESPUESTAS_ALTA,
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def registrar_vehiculo(
    datos: VehiculoCreate,
    gestor: Annotated[GestorVehiculos, Depends(get_gestor_vehiculos)],
) -> VehiculoRead:
    vehiculo = gestor.registrar(
        patente=datos.patente,
        id_tipo_vehiculo=datos.id_tipo_vehiculo,
        id_chofer_habitual=datos.id_chofer_habitual,
    )
    return VehiculoRead.de_vehiculo(vehiculo)


@router.get(
    "",
    response_model=VehiculoListado,
    summary="Listar vehículos",
    description=(
        "Devuelve una página de vehículos dados de alta, con orden estable y la cantidad "
        "total de los que cumplen el filtro."
    ),
)
def listar_vehiculos(
    gestor: Annotated[GestorVehiculos, Depends(get_gestor_vehiculos)],
    q: Annotated[str | None, Query(description="Texto a buscar dentro de la patente.")] = None,
    page: Annotated[int, Query(ge=1, description="Número de página, empezando en 1.")] = 1,
    size: Annotated[
        int,
        Query(ge=1, le=TAMANO_DE_PAGINA_MAXIMO, description="Cantidad de vehículos por página."),
    ] = TAMANO_DE_PAGINA_POR_DEFECTO,
) -> VehiculoListado:
    vehiculos, total = gestor.listar(busqueda=q, offset=(page - 1) * size, limit=size)
    return VehiculoListado(
        items=[VehiculoRead.de_listado(vehiculo) for vehiculo in vehiculos],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{vehiculo_id}",
    response_model=VehiculoRead,
    summary="Ver el detalle de un vehículo",
    description=(
        "Devuelve patente, tipo de vehículo, chofer habitual y las fechas de alta y última "
        "modificación. Un vehículo dado de baja se trata como inexistente."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un vehículo activo con ese identificador."
        }
    },
)
def obtener_vehiculo(
    vehiculo_id: Annotated[int, Path(description="Identificador del vehículo.", ge=1)],
    gestor: Annotated[GestorVehiculos, Depends(get_gestor_vehiculos)],
) -> VehiculoRead:
    return VehiculoRead.de_vehiculo(gestor.obtener(vehiculo_id))


@router.put(
    "/{vehiculo_id}",
    response_model=VehiculoRead,
    summary="Modificar un vehículo",
    description=(
        "Corrige los datos de un vehículo existente. El identificador y la fecha de "
        "creación no se pueden cambiar, y la patente no puede quedar igual a la de otro vehículo."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite modificar vehículos."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un vehículo activo con ese identificador."
        },
        status.HTTP_409_CONFLICT: {"description": "La patente nueva ya pertenece a otro vehículo."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Alguno de los datos requeridos falta o no cumple el formato."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def actualizar_vehiculo(
    vehiculo_id: Annotated[int, Path(description="Identificador del vehículo.", ge=1)],
    datos: VehiculoUpdate,
    gestor: Annotated[GestorVehiculos, Depends(get_gestor_vehiculos)],
) -> VehiculoRead:
    vehiculo = gestor.actualizar(
        vehiculo_id,
        patente=datos.patente,
        id_tipo_vehiculo=datos.id_tipo_vehiculo,
        id_chofer_habitual=datos.id_chofer_habitual,
    )
    return VehiculoRead.de_vehiculo(vehiculo)


@router.delete(
    "/{vehiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Dar de baja un vehículo",
    description="Elimina un vehículo que no tenga servicios asociados. La baja es lógica.",
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite dar de baja vehículos."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un vehículo activo con ese identificador."
        },
        status.HTTP_409_CONFLICT: {"description": "El vehículo tiene servicios asociados."},
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def eliminar_vehiculo(
    vehiculo_id: Annotated[int, Path(description="Identificador del vehículo.", ge=1)],
    gestor: Annotated[GestorVehiculos, Depends(get_gestor_vehiculos)],
) -> Response:
    gestor.eliminar(vehiculo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
