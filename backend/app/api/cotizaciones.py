"""Endpoints de cotización; las reglas viven en Aplicación."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.schemas.cotizacion import CotizacionRead, CotizacionRequest
from app.application.cotizacion.cotizador_servicios import CotizadorServicios
from app.core.dependencias import ROL_ADMIN, get_cotizador_servicios, require_rol

router = APIRouter(prefix="/api/cotizaciones", tags=["cotizaciones"])


@router.post(
    "/calcular",
    response_model=CotizacionRead,
    summary="Calcular el precio sugerido de un servicio",
    description=(
        "Calcula el desglose del precio sugerido con las tarifas del tipo de vehículo "
        "indicado y la configuración vigente de recargos. No requiere una unidad asignada, "
        "no persiste ningún dato ni valida "
        "el precio acordado que el operador informará al registrar el servicio."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "La autenticación no está habilitada para este entorno."
        },
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "El tipo, las horas, los kms o la configuración son inválidos."
        },
    },
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)
def calcular_cotizacion(
    datos: CotizacionRequest,
    cotizador: Annotated[CotizadorServicios, Depends(get_cotizador_servicios)],
) -> CotizacionRead:
    cotizacion = cotizador.cotizar_por_tipo(
        id_tipo_vehiculo=datos.id_tipo_vehiculo,
        horas_estimadas=datos.horas_estimadas,
        km_estimados=datos.km_estimados,
        requiere_ayudante=datos.requiere_ayudante,
        acceso_escalera=datos.acceso_escalera,
        zona_concurrida=datos.zona_concurrida,
        urgencia_mismo_dia=datos.urgencia_mismo_dia,
    )
    return CotizacionRead.de_cotizacion(cotizacion)
