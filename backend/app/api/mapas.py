"""Endpoints proxy para búsqueda de direcciones y cálculo de rutas."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.schemas.mapa import (
    DireccionBuscarRequest,
    DireccionesRead,
    DireccionOpcionRead,
    RutaRead,
    RutaRequest,
)
from app.application.mapas.gestor_mapas import GestorMapas
from app.application.mapas.puertos import Coordenada
from app.core.dependencias import ROL_ADMIN, get_gestor_mapas, require_rol

router = APIRouter(
    prefix="/api/mapas",
    tags=["mapas"],
    dependencies=[Depends(require_rol(ROL_ADMIN))],
)


@router.post(
    "/direcciones",
    response_model=DireccionesRead,
    summary="Buscar direcciones para seleccionar origen o destino",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Autenticación requerida."},
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "La consulta no es válida."},
        status.HTTP_502_BAD_GATEWAY: {"description": "Respuesta inválida del servicio de mapas."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "El servicio de mapas no está disponible."
        },
    },
)
async def buscar_direcciones(
    datos: DireccionBuscarRequest,
    gestor: Annotated[GestorMapas, Depends(get_gestor_mapas)],
) -> DireccionesRead:
    sugerencias = await gestor.buscar_direcciones(datos.consulta)
    return DireccionesRead(
        opciones=[
            DireccionOpcionRead(
                etiqueta=sugerencia.etiqueta,
                longitud=sugerencia.coordenada.longitud,
                latitud=sugerencia.coordenada.latitud,
            )
            for sugerencia in sugerencias
        ]
    )


@router.post(
    "/ruta",
    response_model=RutaRead,
    summary="Calcular distancia y duración entre dos coordenadas",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Autenticación requerida."},
        status.HTTP_403_FORBIDDEN: {"description": "La operación requiere el rol admin."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Las coordenadas no son válidas o no existe una ruta."
        },
        status.HTTP_502_BAD_GATEWAY: {"description": "Respuesta inválida del servicio de mapas."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "El servicio de mapas no está disponible."
        },
    },
)
async def calcular_ruta(
    datos: RutaRequest,
    gestor: Annotated[GestorMapas, Depends(get_gestor_mapas)],
) -> RutaRead:
    ruta = await gestor.calcular_ruta(
        origen=Coordenada(longitud=datos.origen.longitud, latitud=datos.origen.latitud),
        destino=Coordenada(longitud=datos.destino.longitud, latitud=datos.destino.latitud),
    )
    return RutaRead(
        distancia_ida_km=ruta.distancia_ida_km,
        duracion_segundos=ruta.duracion_segundos,
    )
