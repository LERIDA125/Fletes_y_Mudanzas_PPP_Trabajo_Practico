"""Endpoints de cotización y servicios; las reglas están en Aplicación."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.servicio import (
    CotizacionRead,
    CotizacionRequest,
    ServicioCreate,
    ServicioListado,
    ServicioRead,
)
from app.application.servicios.gestor_servicios import GestorServicios
from app.core.dependencias import ROL_ADMIN, get_gestor_servicios, require_rol

router = APIRouter(prefix="/api/servicios", tags=["servicios"])

TAMANO_DE_PAGINA_POR_DEFECTO = 20
TAMANO_DE_PAGINA_MAXIMO = 100


@router.post(
    "/cotizar",
    response_model=CotizacionRead,
    summary="Cotizar un viaje",
    description=(
        "Calcula el precio en ARS con las tarifas activas del tipo de vehículo. La distancia "
        "recibida es de ida; el servidor la duplica y aplica una franquicia de 10 km."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Los datos son inválidos o el tipo no está activo."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def cotizar_servicio(
    datos: CotizacionRequest,
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
) -> CotizacionRead:
    cotizacion = gestor.cotizar(
        id_tipo_vehiculo=datos.id_tipo_vehiculo,
        horas_estimadas=datos.horas_estimadas,
        distancia_ida_km=datos.distancia_ida_km,
    )
    return CotizacionRead.de_cotizacion(cotizacion)


@router.post(
    "",
    response_model=ServicioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un servicio",
    description=(
        "Registra un servicio en estado pendiente. El servidor obtiene las tarifas vigentes, "
        "recalcula el precio y guarda el detalle tarifario; el cliente no puede enviar importes."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Los datos o las referencias activas del servicio son inválidos."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def crear_servicio(
    datos: ServicioCreate,
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
) -> ServicioRead:
    item = gestor.crear(
        id_cliente=datos.id_cliente,
        id_tipo_vehiculo=datos.id_tipo_vehiculo,
        id_chofer=datos.id_chofer,
        id_vehiculo=datos.id_vehiculo,
        fecha=datos.fecha,
        hora_inicio=datos.hora_inicio,
        horas_estimadas=datos.horas_estimadas,
        distancia_ida_km=datos.distancia_ida_km,
    )
    return ServicioRead.de_item(item)


@router.get(
    "",
    response_model=ServicioListado,
    summary="Listar servicios",
    description=(
        "Devuelve servicios paginados con cliente, tipo, estado y nombres legibles de las "
        "asignaciones opcionales."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def listar_servicios(
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
    page: Annotated[int, Query(ge=1, description="Número de página, empezando en 1.")] = 1,
    size: Annotated[
        int,
        Query(
            ge=1,
            le=TAMANO_DE_PAGINA_MAXIMO,
            description="Cantidad de servicios por página.",
        ),
    ] = TAMANO_DE_PAGINA_POR_DEFECTO,
) -> ServicioListado:
    items, total = gestor.listar(offset=(page - 1) * size, limit=size)
    return ServicioListado(
        items=[ServicioRead.de_item(item) for item in items],
        total=total,
        page=page,
        size=size,
    )
