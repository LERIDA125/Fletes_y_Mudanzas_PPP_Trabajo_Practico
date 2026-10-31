"""Endpoints de cotización y servicios; las reglas están en Aplicación."""

from datetime import date, time
from decimal import Decimal, InvalidOperation
from email.parser import BytesParser
from email.policy import HTTP as EMAIL_HTTP_POLICY
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

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
from app.domain.errores import MontoCobradoInvalido

router = APIRouter(prefix="/api/servicios", tags=["servicios"])

TAMANO_DE_PAGINA_POR_DEFECTO = 20
TAMANO_DE_PAGINA_MAXIMO = 100


async def _extraer_datos_finalizacion(
    request: Request,
) -> tuple[Decimal, bytes | None, str | None, str | None, str | None]:
    """Extrae monto_cobrado_real y comprobante desde JSON o multipart/form-data."""
    content_type = (request.headers.get("content-type") or "").strip()
    mime_principal = content_type.split(";", 1)[0].strip().lower()

    if mime_principal == "multipart/form-data":
        raw_body = await request.body()
        mensaje = BytesParser(policy=EMAIL_HTTP_POLICY).parsebytes(
            f"Content-Type: {content_type}\r\n\r\n".encode("latin-1") + raw_body
        )
        monto_texto: str | None = None
        foto_bytes: bytes | None = None
        foto_content_type: str | None = None
        foto_nombre_archivo: str | None = None
        foto_base64_o_url: str | None = None

        if mensaje.is_multipart():
            for parte in mensaje.iter_parts():
                nombre_campo = parte.get_param("name", header="content-disposition")
                nombre_archivo = parte.get_filename()
                contenido_bytes = parte.get_payload(decode=True) or b""

                if nombre_campo == "monto_cobrado_real":
                    monto_texto = contenido_bytes.decode("utf-8", errors="replace").strip()
                elif nombre_campo in ("foto", "foto_remito") and (
                    nombre_archivo is not None or contenido_bytes
                ):
                    if nombre_archivo is not None:
                        foto_bytes = contenido_bytes
                        foto_content_type = parte.get_content_type()
                        foto_nombre_archivo = nombre_archivo
                    else:
                        texto = contenido_bytes.decode("utf-8", errors="replace").strip()
                        if texto:
                            foto_base64_o_url = texto
                elif nombre_campo in ("foto_remito_url", "foto_remito_base64"):
                    texto = contenido_bytes.decode("utf-8", errors="replace").strip()
                    if texto:
                        foto_base64_o_url = texto

        if monto_texto is None or not monto_texto:
            raise MontoCobradoInvalido(
                "Debés declarar el monto real cobrado para finalizar el viaje"
            )
        try:
            monto_decimal = Decimal(monto_texto)
        except (InvalidOperation, ValueError) as exc:
            raise MontoCobradoInvalido(
                "El monto real cobrado debe ser un importe numérico válido"
            ) from exc

        return (
            monto_decimal,
            foto_bytes,
            foto_content_type,
            foto_nombre_archivo,
            foto_base64_o_url,
        )

    try:
        payload = await request.json()
    except Exception as exc:
        raise RequestValidationError(
            [
                {
                    "loc": ("body",),
                    "msg": "Cuerpo JSON inválido o ausente",
                    "type": "value_error.jsondecode",
                }
            ]
        ) from exc

    try:
        datos = ServicioFinalizarRequest.model_validate(payload)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc

    return datos.monto_cobrado_real, None, None, None, datos.foto_remito_url


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
        "chofer, solo permite avanzar viajes asignados a su propio id_chofer hacia 'en curso'; "
        "el cierre a 'finalizado' exige usar POST /{id_servicio}/finalizar con remito y monto."
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


@router.post(
    "/{id_servicio}/finalizar",
    response_model=ServicioRead,
    summary="Finalizar un viaje con Prueba de Entrega (POD) y monto cobrado (H10)",
    description=(
        "Marca el servicio como finalizado adjuntando la foto del remito firmado y declarando "
        "el monto real cobrado. Acepta tanto multipart/form-data como application/json y deja "
        "el estado económico en PENDIENTE de rendición."
    ),
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["monto_cobrado_real"],
                        "properties": {
                            "monto_cobrado_real": {
                                "anyOf": [{"type": "number"}, {"type": "string"}],
                                "description": "Monto real cobrado al finalizar el viaje.",
                            },
                            "foto_remito_url": {
                                "anyOf": [{"type": "string"}, {"type": "null"}],
                                "description": "Data URL Base64 o URL pública del remito firmado.",
                            },
                        },
                    }
                },
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["monto_cobrado_real"],
                        "properties": {
                            "monto_cobrado_real": {
                                "type": "string",
                                "description": "Monto real cobrado al finalizar el viaje.",
                            },
                            "foto": {
                                "type": "string",
                                "format": "binary",
                                "description": "Imagen del remito firmado (JPEG, PNG o WebP).",
                            },
                            "foto_remito_url": {
                                "type": "string",
                                "description": "Alternativa Base64 / Data URL del remito.",
                            },
                        },
                    }
                },
            },
        }
    },
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "El viaje no pertenece al chofer autenticado o el rol no tiene permiso."
        },
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio no está en estado confirmado o en curso."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Falta la foto del remito o el monto cobrado es inválido."
        },
    },
    dependencies=[Depends(require_roles(ROL_ADMIN, ROL_CHOFER))],
)
async def finalizar_viaje_servicio(
    id_servicio: Annotated[int, Path(gt=0, description="Identificador del servicio.")],
    request: Request,
    gestor: Annotated[GestorServicios, Depends(get_gestor_servicios)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> ServicioRead:
    (
        monto_cobrado_real,
        foto_bytes,
        foto_content_type,
        foto_nombre_archivo,
        foto_base64_o_url,
    ) = await _extraer_datos_finalizacion(request)

    item = gestor.finalizar_viaje(
        id_servicio=id_servicio,
        monto_cobrado_real=monto_cobrado_real,
        foto_remito_url=foto_base64_o_url,
        archivo_bytes=foto_bytes,
        content_type=foto_content_type,
        nombre_archivo=foto_nombre_archivo,
        usuario_id=usuario_actual.id,
        rol_usuario=usuario_actual.rol,
        id_chofer_usuario=usuario_actual.id_chofer,
    )
    return ServicioRead.de_item(item)


@router.post(
    "/{id_servicio}/rendicion/aprobar",
    response_model=ServicioRead,
    summary="Aprobar la rendición de un viaje finalizado (H10)",
    description=(
        "Aprueba la rendición del viaje, marca su estado económico como RENDIDO y su estado "
        "operativo como cobrado, dejando en cero la deuda pendiente del chofer por ese viaje."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio no está finalizado o ya fue rendido."
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
    )
    return ServicioRead.de_item(item)


@router.post(
    "/{id_servicio}/rendicion/observar",
    response_model=ServicioRead,
    summary="Observar la rendición de un viaje finalizado (H10)",
    description=(
        "Registra una observación administrativa sobre el remito o monto declarado y cambia "
        "el estado económico a OBSERVADO manteniendo el saldo pendiente de conciliación."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe un servicio con ese id."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio no está finalizado o ya fue rendido."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "La observación es obligatoria."
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
