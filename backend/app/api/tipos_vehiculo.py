"""Routers de tipos de vehículo (capa de Presentación).

Cada ruta recibe el request, valida el rol y delega en **un** método del gestor de Aplicación.
Acá no hay ninguna regla de negocio.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.schemas.tipo_vehiculo import (
    TipoVehiculoCreate,
    TipoVehiculoListado,
    TipoVehiculoRead,
    TipoVehiculoUpdate,
)
from app.application.tipos_vehiculo.gestor_tipos_vehiculo import GestorTiposVehiculo
from app.core.dependencias import ROL_ADMIN, get_gestor_tipos_vehiculo, require_rol

router = APIRouter(prefix="/api/tipos-vehiculo", tags=["tipos-vehiculo"])

TAMANO_DE_PAGINA_POR_DEFECTO = 20
TAMANO_DE_PAGINA_MAXIMO = 100

RESPUESTAS_ALTA = {
    status.HTTP_403_FORBIDDEN: {
        "description": "El rol del usuario no permite dar de alta tipos de vehículo."
    },
    status.HTTP_409_CONFLICT: {"description": "Ya existe un tipo de vehículo con esa descripción."},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "description": "Alguno de los datos requeridos falta o no cumple el formato."
    },
}


@router.post(
    "",
    response_model=TipoVehiculoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un tipo de vehículo",
    description=(
        "Da de alta un tipo de vehículo con descripción, capacidad de carga y tarifas base. "
        "La descripción no puede repetirse. El identificador y las fechas los asigna el sistema."
    ),
    responses=RESPUESTAS_ALTA,
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def registrar_tipo_vehiculo(
    datos: TipoVehiculoCreate,
    gestor: Annotated[GestorTiposVehiculo, Depends(get_gestor_tipos_vehiculo)],
) -> TipoVehiculoRead:
    tipo = gestor.registrar(
        descripcion=datos.descripcion,
        capacidad_carga_kg=datos.capacidad_carga_kg,
        tarifa_hora_base=datos.tarifa_hora_base,
        tarifa_km_excedente=datos.tarifa_km_excedente,
    )
    return TipoVehiculoRead.de_tipo(tipo)


@router.get(
    "",
    response_model=TipoVehiculoListado,
    summary="Listar tipos de vehículo",
    description=(
        "Devuelve una página de tipos de vehículo dados de alta, con orden estable y la cantidad "
        "total de los que cumplen el filtro."
    ),
)
def listar_tipos_vehiculo(
    gestor: Annotated[GestorTiposVehiculo, Depends(get_gestor_tipos_vehiculo)],
    q: Annotated[
        str | None,
        Query(description="Texto a buscar dentro de la descripción. No distingue mayúsculas."),
    ] = None,
    page: Annotated[int, Query(ge=1, description="Número de página, empezando en 1.")] = 1,
    size: Annotated[
        int,
        Query(
            ge=1,
            le=TAMANO_DE_PAGINA_MAXIMO,
            description="Cantidad de tipos de vehículo por página.",
        ),
    ] = TAMANO_DE_PAGINA_POR_DEFECTO,
) -> TipoVehiculoListado:
    tipos, total = gestor.listar(busqueda=q, offset=(page - 1) * size, limit=size)
    return TipoVehiculoListado(
        items=[TipoVehiculoRead.de_tipo(tipo) for tipo in tipos],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{tipo_id}",
    response_model=TipoVehiculoRead,
    summary="Ver el detalle de un tipo de vehículo",
    description=(
        "Devuelve descripción, capacidad de carga, tarifas y las fechas de alta y última "
        "modificación. Un tipo de vehículo dado de baja se trata como inexistente."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un tipo de vehículo activo con ese identificador."
        }
    },
)
def obtener_tipo_vehiculo(
    tipo_id: Annotated[int, Path(description="Identificador del tipo de vehículo.", ge=1)],
    gestor: Annotated[GestorTiposVehiculo, Depends(get_gestor_tipos_vehiculo)],
) -> TipoVehiculoRead:
    return TipoVehiculoRead.de_tipo(gestor.obtener(tipo_id))


@router.put(
    "/{tipo_id}",
    response_model=TipoVehiculoRead,
    summary="Modificar un tipo de vehículo",
    description=(
        "Corrige los datos de un tipo de vehículo existente. El identificador y la fecha de "
        "creación no se pueden cambiar, y la descripción no puede quedar igual a la de otro "
        "tipo de vehículo."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite modificar tipos de vehículo."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un tipo de vehículo activo con ese identificador."
        },
        status.HTTP_409_CONFLICT: {
            "description": "La descripción nueva ya pertenece a otro tipo de vehículo."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Alguno de los datos requeridos falta o no cumple el formato."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def actualizar_tipo_vehiculo(
    tipo_id: Annotated[int, Path(description="Identificador del tipo de vehículo.", ge=1)],
    datos: TipoVehiculoUpdate,
    gestor: Annotated[GestorTiposVehiculo, Depends(get_gestor_tipos_vehiculo)],
) -> TipoVehiculoRead:
    tipo = gestor.actualizar(
        tipo_id,
        descripcion=datos.descripcion,
        capacidad_carga_kg=datos.capacidad_carga_kg,
        tarifa_hora_base=datos.tarifa_hora_base,
        tarifa_km_excedente=datos.tarifa_km_excedente,
    )
    return TipoVehiculoRead.de_tipo(tipo)


@router.delete(
    "/{tipo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Dar de baja un tipo de vehículo",
    description=(
        "Elimina un tipo de vehículo que no tenga vehículos asociados. La baja es lógica."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "El rol del usuario no permite dar de baja tipos de vehículo."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No existe un tipo de vehículo activo con ese identificador."
        },
        status.HTTP_409_CONFLICT: {"description": "El tipo de vehículo tiene vehículos asociados."},
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def eliminar_tipo_vehiculo(
    tipo_id: Annotated[int, Path(description="Identificador del tipo de vehículo.", ge=1)],
    gestor: Annotated[GestorTiposVehiculo, Depends(get_gestor_tipos_vehiculo)],
) -> Response:
    gestor.eliminar(tipo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
