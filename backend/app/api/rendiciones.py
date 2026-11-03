"""Routers de rendiciones; las reglas viven en Aplicación."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.schemas.rendicion import (
    RendicionCreate,
    RendicionEstadoUpdate,
    RendicionListado,
    RendicionRead,
    ResumenRendicionesRead,
    ServicioElegibleRead,
)
from app.application.rendiciones.gestor_rendiciones import GestorRendiciones
from app.core.dependencias import (
    ROL_ADMIN,
    UsuarioAutenticado,
    get_gestor_rendiciones,
    get_usuario_actual,
    require_rol,
)

router = APIRouter(prefix="/api/rendiciones", tags=["rendiciones"])

TAMANO_DE_PAGINA_POR_DEFECTO = 20
TAMANO_DE_PAGINA_MAXIMO = 100


@router.get(
    "/servicios-elegibles",
    response_model=list[ServicioElegibleRead],
    summary="Listar servicios rendibles",
    description=(
        "Devuelve los servicios con chofer asignado, estado finalizado o cobrado, que todavía "
        "no tienen una rendición registrada."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def listar_servicios_elegibles(
    gestor: Annotated[GestorRendiciones, Depends(get_gestor_rendiciones)],
) -> list[ServicioElegibleRead]:
    return [
        ServicioElegibleRead.de_item(item) for item in gestor.listar_servicios_elegibles()
    ]


@router.get(
    "",
    response_model=RendicionListado,
    summary="Listar rendiciones",
    description=(
        "Devuelve rendiciones paginadas, ordenadas por id descendente, con el chofer y el "
        "cliente del servicio. Incluye un resumen global para los KPIs de la pantalla."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def listar_rendiciones(
    gestor: Annotated[GestorRendiciones, Depends(get_gestor_rendiciones)],
    q: Annotated[
        str | None,
        Query(description="Texto a buscar en código, chofer, cliente o servicio."),
    ] = None,
    page: Annotated[int, Query(ge=1, description="Número de página, empezando en 1.")] = 1,
    size: Annotated[
        int,
        Query(
            ge=1,
            le=TAMANO_DE_PAGINA_MAXIMO,
            description="Cantidad de rendiciones por página.",
        ),
    ] = TAMANO_DE_PAGINA_POR_DEFECTO,
) -> RendicionListado:
    items, total, resumen = gestor.listar(
        busqueda=q,
        offset=(page - 1) * size,
        limit=size,
    )
    return RendicionListado(
        items=[RendicionRead.de_item(item) for item in items],
        total=total,
        page=page,
        size=size,
        resumen=ResumenRendicionesRead.de_resumen(resumen),
    )


@router.post(
    "",
    response_model=RendicionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una rendición",
    description=(
        "Registra la liquidación de un servicio elegible. El backend deriva el chofer y la fecha "
        "del servicio, genera el código y calcula gastos totales y saldo; el cliente no puede "
        "enviar esos campos."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe el servicio indicado."},
        status.HTTP_409_CONFLICT: {
            "description": "El servicio no está finalizado/cobrado o ya tiene una rendición."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "El servicio no tiene chofer o los importes son inválidos."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def crear_rendicion(
    datos: RendicionCreate,
    gestor: Annotated[GestorRendiciones, Depends(get_gestor_rendiciones)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> RendicionRead:
    item = gestor.registrar(
        id_servicio=datos.id_servicio,
        tarifa=datos.tarifa,
        adelanto=datos.adelanto,
        gasto_combustible=datos.gastos_informados.combustible,
        gasto_peajes=datos.gastos_informados.peajes,
        gasto_otros=datos.gastos_informados.otros,
        observaciones=datos.observaciones,
        usuario_id=usuario_actual.id,
    )
    return RendicionRead.de_item(item)


@router.patch(
    "/{rendicion_id}/estado",
    response_model=RendicionRead,
    summary="Cambiar el estado de una rendición",
    description=(
        "Actualiza el estado de una rendición existente a pendiente, en revisión o aprobada."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_404_NOT_FOUND: {"description": "No existe una rendición con ese id."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "El estado no es válido."},
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def cambiar_estado_rendicion(
    rendicion_id: Annotated[int, Path(gt=0, description="Identificador de la rendición.")],
    datos: RendicionEstadoUpdate,
    gestor: Annotated[GestorRendiciones, Depends(get_gestor_rendiciones)],
    usuario_actual: Annotated[UsuarioAutenticado, Depends(get_usuario_actual)],
) -> RendicionRead:
    item = gestor.cambiar_estado(
        rendicion_id,
        estado=datos.estado,
        usuario_id=usuario_actual.id,
    )
    return RendicionRead.de_item(item)
