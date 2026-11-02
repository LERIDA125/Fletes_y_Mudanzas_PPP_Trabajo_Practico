"""Endpoints de cotización y servicios; las reglas están en Aplicación."""

from datetime import date, time
from decimal import Decimal
from email.parser import BytesParser
from email.policy import default
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Response, status

from app.api.schemas.chofer import ChoferRead
from app.api.schemas.servicio import (
    CotizacionRead,
    CotizacionRequest,
    DisponibilidadRead,
    RendicionObservarRequest,
    ServicioCancelar,
    ServicioCreate,
    ServicioEstadoUpdate,
    ServicioFinalizarRequest,
    ServicioListado,
    ServicioRead,
)
from app.api.schemas.vehiculo import VehiculoRead
from app.application.servicios.gestor_servicios import GestorServicios
from app.core.dependencias import (
    ROL_ADMIN,
    ROL_CHOFER,
    UsuarioAutenticado,
    get_gestor_servicios,
    get_usuario_actual,
    require_rol,
    require_roles,
)
from app.domain.cliente import Cliente
from app.domain.errores import DatoInvalido

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
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ServicioRead:
    nuevo_cliente = None
    if datos.nuevo_cliente is not None:
        nuevo_cliente = Cliente.crear(
            razon_social=datos.nuevo_cliente.razon_social,
            telefono=datos.nuevo_cliente.telefono,
            direccion_habitual=datos.nuevo_cliente.direccion_habitual,
            tiene_cuenta_corriente=datos.nuevo_cliente.tiene_cuenta_corriente,
            creado_por_id=usuario_actual.id,
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
        usuario_id=usuario_actual.id,
    )
    return ServicioRead.de_item(item)


@router.patch(
    "/{id_servicio}/cancelar",
    response_model=ServicioRead,
    summary="Cancelar un servicio",
    description=(
        "Cancela un servicio en estado pendiente, confirmado o en curso. Exige un motivo y "
        "registra la hora de finalización con la hora de Buenos Aires. Si faltan entre 0 y 2 horas "
        "para el inicio y hay un chofer asignado, guarda una compensación del 30 % de precio_total "
        "en el servicio; sin hora o chofer, o si el inicio ya pasó, la compensación es cero. "
        "El importe es un snapshot, no un pago ni un movimiento de rendición. No acepta hora, "
        "estado ni importe de compensación en el request."
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
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ServicioRead:
    item = gestor.cancelar(
        id_servicio=id_servicio,
        motivo=datos.motivo,
        usuario_id=usuario_actual.id,
    )
    return ServicioRead.de_item(item)


@router.patch(
    "/{id_servicio}/estado",
    response_model=ServicioRead,
    summary="Cambiar el estado de un servicio",
    description=(
        "Transiciona al siguiente estado permitido por la máquina del dominio. La cancelación "
        "debe realizarse mediante la ruta específica que exige motivo. Si el token es de rol "
        "chofer, solo permite actualizar viajes asignados a su propio id_chofer hacia 'en curso' "
        "o 'finalizado'."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "La operación requiere el rol adecuado o pertenencia del viaje."
        },
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "El estado o la transición solicitada no es válida."
        },
    },
    dependencies=[Depends(require_roles(ROL_ADMIN, ROL_CHOFER))],
)
def cambiar_estado_servicio(
    id_servicio: Annotated[int, Path(gt=0, description="Identificador del servicio.")],
    datos: ServicioEstadoUpdate,
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ServicioRead:
    item = gestor.cambiar_estado(
        id_servicio=id_servicio,
        estado=datos.estado,
        usuario_id=usuario_actual.id,
        rol_usuario=usuario_actual.rol,
        id_chofer_usuario=usuario_actual.id_chofer,
    )
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
        "asignaciones opcionales. Si el token es de rol chofer, se inyecta de forma obligatoria "
        "el filtro id_chofer igual al id_chofer del token autenticado."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
    },
    dependencies=[Depends(require_roles(ROL_ADMIN, ROL_CHOFER))],
)
def listar_servicios(
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
    page: Annotated[int, Query(ge=1, description="Número de página, empezando en 1.")] = 1,
    size: Annotated[
        int,
        Query(
            ge=1,
            le=TAMANO_DE_PAGINA_MAXIMO,
            description="Cantidad de servicios por página.",
        ),
    ] = TAMANO_DE_PAGINA_POR_DEFECTO,
    id_chofer: Annotated[
        int | None,
        Query(gt=0, description="Filtro opcional por chofer (solo respetado para rol admin)."),
    ] = None,
) -> ServicioListado:
    filtro_chofer = id_chofer
    if usuario_actual.rol == ROL_CHOFER:
        filtro_chofer = usuario_actual.id_chofer if usuario_actual.id_chofer is not None else -1

    items, total = gestor.listar(
        offset=(page - 1) * size,
        limit=size,
        id_chofer=filtro_chofer,
    )
    return ServicioListado(
        items=[ServicioRead.de_item(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.post(
    "/{id_servicio}/finalizar",
    response_model=ServicioRead,
    summary="Finalizar viaje con remito y monto cobrado",
    description=(
        "Marca el servicio como finalizado adjuntando la foto del remito firmado y declarando "
        "el monto real cobrado. Acepta tanto JSON (con foto_remito_url en base64 o link) como "
        "multipart/form-data con archivo de foto."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El chofer solo puede finalizar viajes asignados a sí mismo."
        },
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio no está en estado confirmado o en curso."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "La foto del remito o el monto cobrado es inválido."
        },
    },
    dependencies=[Depends(require_roles(ROL_ADMIN, ROL_CHOFER))],
)
async def finalizar_servicio(
    id_servicio: Annotated[int, Path(gt=0, description="Identificador del servicio.")],
    request: Request,
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ServicioRead:
    content_type = request.headers.get("content-type", "")
    foto_url: str | None = None
    foto_bytes: bytes | None = None
    foto_ct: str = "image/jpeg"
    foto_nombre: str | None = None
    monto_cobrado: Decimal | None = None

    if "multipart/form-data" in content_type:
        raw_body = await request.body()
        cabecera_ct = f"Content-Type: {content_type}\r\n\r\n".encode()
        msg = BytesParser(policy=default).parsebytes(cabecera_ct + raw_body)
        for part in msg.iter_parts():
            nombre_campo = part.get_param("name", header="content-disposition")
            nombre_archivo = part.get_filename()
            cuerpo_parte = part.get_payload(decode=True)
            if nombre_campo in ("foto_remito", "foto", "remito", "imagen") or (
                nombre_archivo and cuerpo_parte
            ):
                foto_bytes = cuerpo_parte
                foto_ct = part.get_content_type() or "image/jpeg"
                foto_nombre = nombre_archivo
            elif nombre_campo == "monto_cobrado_real" and cuerpo_parte:
                monto_str = cuerpo_parte.decode("utf-8", errors="replace").strip()
                try:
                    monto_cobrado = Decimal(monto_str)
                except Exception as exc:
                    raise DatoInvalido("El monto cobrado debe ser un número válido.") from exc
            elif nombre_campo == "foto_remito_url" and cuerpo_parte:
                foto_url = cuerpo_parte.decode("utf-8", errors="replace").strip()

        if monto_cobrado is None:
            raise DatoInvalido("El campo 'monto_cobrado_real' es obligatorio.")
    else:
        try:
            datos_json = await request.json()
        except Exception as exc:
            raise DatoInvalido("El cuerpo de la solicitud no es un JSON válido.") from exc
        try:
            solicitud = ServicioFinalizarRequest.model_validate(datos_json)
        except Exception as exc:
            raise DatoInvalido(f"Datos inválidos para finalizar servicio: {exc}") from exc
        foto_url = solicitud.foto_remito_url
        monto_cobrado = solicitud.monto_cobrado_real

    item = gestor.finalizar_viaje(
        id_servicio=id_servicio,
        foto_remito_url=foto_url,
        foto_bytes=foto_bytes,
        foto_content_type=foto_ct,
        foto_nombre=foto_nombre,
        monto_cobrado_real=monto_cobrado,
        usuario_id=usuario_actual.id,
        rol_usuario=usuario_actual.rol,
        id_chofer_usuario=usuario_actual.id_chofer,
    )
    return ServicioRead.de_item(item)


@router.post(
    "/{id_servicio}/rendicion/aprobar",
    response_model=ServicioRead,
    summary="Aprobar rendición de viaje",
    description=(
        "El administrador aprueba la rendición del servicio luego de revisar el remito y el "
        "dinero recaudado. Deja el saldo en cero para la caja y marca el servicio como "
        "RENDIDO/cobrado."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio no está en estado finalizado o rendición pendiente."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def aprobar_rendicion_servicio(
    id_servicio: Annotated[int, Path(gt=0, description="Identificador del servicio.")],
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ServicioRead:
    item = gestor.aprobar_rendicion(
        id_servicio=id_servicio,
        usuario_id=usuario_actual.id,
        rol_usuario=usuario_actual.rol,
    )
    return ServicioRead.de_item(item)


@router.post(
    "/{id_servicio}/rendicion/observar",
    response_model=ServicioRead,
    summary="Observar rendición de viaje",
    description="Permite al administrador rechazar u observar la rendición adjuntando un motivo.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio no está disponible para observar rendición."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "La observación es inválida o vacía."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def observar_rendicion_servicio(
    id_servicio: Annotated[int, Path(gt=0, description="Identificador del servicio.")],
    datos: RendicionObservarRequest,
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ServicioRead:
    item = gestor.observar_rendicion(
        id_servicio=id_servicio,
        observacion=datos.observacion,
        usuario_id=usuario_actual.id,
        rol_usuario=usuario_actual.rol,
    )
    return ServicioRead.de_item(item)

