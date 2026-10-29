"""Endpoints de cotización y servicios; las reglas están en Aplicación."""

from datetime import date, time
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.api.schemas.chofer import ChoferRead
from app.api.schemas.servicio import (
    CotizacionRead,
    CotizacionRequest,
    DisponibilidadRead,
    ServicioCancelar,
    ServicioCreate,
    ServicioEstadoUpdate,
    ServicioListado,
    ServicioRead,
)
from app.api.schemas.vehiculo import VehiculoRead
from app.application.servicios.gestor_servicios import GestorServicios
from app.core.dependencias import ROL_ADMIN, get_gestor_servicios, require_rol
from app.domain.cliente import Cliente

router = APIRouter(prefix="/api/servicios", tags=["servicios"])

TAMANO_DE_PAGINA_POR_DEFECTO = 20
TAMANO_DE_PAGINA_MAXIMO = 100


@router.get(
    "/disponibilidad",
    response_model=DisponibilidadRead,
    summary="Consultar choferes y vehículos disponibles",
    description=(
        "Devuelve los choferes activos y los vehículos activos del tipo indicado que no "
        "están ocupados por otro servicio no cancelado en la ventana solicitada. Si el "
        "servicio nuevo no informa hora de inicio, o un servicio existente del día tampoco "
        "la informa, el recurso se considera ocupado durante todo el día (supuesto "
        "conservador hasta que el cliente confirme la regla de agenda)."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "La fecha, el tipo o las horas son inválidos."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def consultar_disponibilidad(
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
    fecha: Annotated[date, Query(description="Fecha del servicio a programar.")],
    id_tipo_vehiculo: Annotated[
        int, Query(gt=0, description="Tipo de vehículo que se va a asignar.")
    ],
    horas_estimadas: Annotated[
        Decimal,
        Query(
            ge=1,
            max_digits=10,
            decimal_places=2,
            allow_inf_nan=False,
            description="Duración estimada del servicio; mínimo 1 hora.",
        ),
    ],
    hora_inicio: Annotated[
        time | None, Query(description="Hora de inicio; si falta se bloquea el día completo.")
    ] = None,
) -> DisponibilidadRead:
    disponibilidad = gestor.disponibilidad(
        fecha=fecha,
        id_tipo_vehiculo=id_tipo_vehiculo,
        hora_inicio=hora_inicio,
        horas_estimadas=horas_estimadas,
    )
    return DisponibilidadRead(
        id_tipo_vehiculo=id_tipo_vehiculo,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=disponibilidad.hora_fin,
        choferes=[ChoferRead.de_chofer(chofer) for chofer in disponibilidad.choferes],
        vehiculos=[VehiculoRead.de_listado(vehiculo) for vehiculo in disponibilidad.vehiculos],
    )


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
    nuevo_cliente = None
    if datos.nuevo_cliente is not None:
        nuevo_cliente = Cliente.crear(
            razon_social=datos.nuevo_cliente.razon_social,
            telefono=datos.nuevo_cliente.telefono,
            direccion_habitual=datos.nuevo_cliente.direccion_habitual,
            tiene_cuenta_corriente=datos.nuevo_cliente.tiene_cuenta_corriente,
        )

    item = gestor.crear(
        id_cliente=datos.id_cliente,
        id_tipo_vehiculo=datos.id_tipo_vehiculo,
        id_chofer=datos.id_chofer,
        id_vehiculo=datos.id_vehiculo,
        fecha=datos.fecha,
        hora_inicio=datos.hora_inicio,
        horas_estimadas=datos.horas_estimadas,
        distancia_ida_km=datos.distancia_ida_km,
        nuevo_cliente=nuevo_cliente,
    )
    return ServicioRead.de_item(item)


@router.patch(
    "/{id_servicio}/cancelar",
    response_model=ServicioRead,
    summary="Cancelar un servicio",
    description=(
        "Cancela un servicio en estado pendiente, confirmado o en curso. Exige un motivo y "
        "registra la hora de finalización con la hora del servidor; no acepta hora ni estado."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio está finalizado, cobrado o ya cancelado."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "El motivo es obligatorio o supera la longitud permitida."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def cancelar_servicio(
    id_servicio: Annotated[int, Path(gt=0, description="Identificador del servicio.")],
    datos: ServicioCancelar,
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
) -> ServicioRead:
    item = gestor.cancelar(id_servicio=id_servicio, motivo=datos.motivo)
    return ServicioRead.de_item(item)


@router.patch(
    "/{id_servicio}/estado",
    response_model=ServicioRead,
    summary="Cambiar el estado de un servicio",
    description=(
        "Transiciona al siguiente estado permitido por la máquina del dominio. La cancelación "
        "debe realizarse mediante la ruta específica que exige motivo."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "El estado o la transición solicitada no es válida."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def cambiar_estado_servicio(
    id_servicio: Annotated[int, Path(gt=0, description="Identificador del servicio.")],
    datos: ServicioEstadoUpdate,
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
) -> ServicioRead:
    item = gestor.cambiar_estado(id_servicio=id_servicio, estado=datos.estado)
    return ServicioRead.de_item(item)


@router.delete(
    "/{id_servicio}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Eliminar un servicio",
    description="Elimina un servicio sin dependencias; no admite borrado si hay referencias.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio tiene registros dependientes y no puede eliminarse."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def eliminar_servicio(
    id_servicio: Annotated[int, Path(gt=0, description="Identificador del servicio.")],
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
) -> Response:
    gestor.eliminar(id_servicio)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
