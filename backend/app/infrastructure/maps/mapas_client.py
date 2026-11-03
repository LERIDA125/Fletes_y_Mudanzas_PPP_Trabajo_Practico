"""Cliente servidor-servidor para Nominatim y OSRM."""

import asyncio
from collections import OrderedDict
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from time import monotonic
from typing import Any

import httpx

from app.application.mapas.errores import (
    MapasNoDisponible,
    RespuestaMapasInvalida,
    RutaMapasNoEncontrada,
)
from app.application.mapas.puertos import (
    Coordenada,
    RutaCalculada,
    SugerenciaDireccion,
)

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving"
TIMEOUT_SECONDS = 8.0
NOMINATIM_INTERVAL_SECONDS = 1.0
USER_AGENT = "FletesExpressMVP/1.0"
MAX_SUGERENCIAS = 5
MAX_CONSULTAS_CACHEADAS = 256
KM_POR_METRO = Decimal("1000")
CENTESIMA = Decimal("0.01")


class ClienteMapas:
    def __init__(
        self,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._transport = transport
        self._nominatim_lock = asyncio.Lock()
        self._ultimo_inicio_nominatim: float | None = None
        self._consultas_cacheadas: OrderedDict[str, tuple[SugerenciaDireccion, ...]] = OrderedDict()

    async def buscar_direcciones(self, consulta: str) -> list[SugerenciaDireccion]:
        async with self._nominatim_lock:
            clave_cache = " ".join(consulta.split()).casefold()
            cacheada = self._consultas_cacheadas.get(clave_cache)
            if cacheada is not None:
                self._consultas_cacheadas.move_to_end(clave_cache)
                return list(cacheada)

            if self._ultimo_inicio_nominatim is not None:
                espera = NOMINATIM_INTERVAL_SECONDS - (monotonic() - self._ultimo_inicio_nominatim)
                if espera > 0:
                    await asyncio.sleep(espera)
            self._ultimo_inicio_nominatim = monotonic()
            respuesta = await self._request_json(
                "GET",
                NOMINATIM_SEARCH_URL,
                params={
                    "q": consulta,
                    "format": "jsonv2",
                    "limit": MAX_SUGERENCIAS,
                    "accept-language": "es",
                },
            )
            if not isinstance(respuesta, list):
                raise RespuestaMapasInvalida

            sugerencias = []
            for resultado in respuesta[:MAX_SUGERENCIAS]:
                if not isinstance(resultado, dict):
                    raise RespuestaMapasInvalida
                etiqueta = resultado.get("display_name")
                if not isinstance(etiqueta, str) or not etiqueta.strip():
                    raise RespuestaMapasInvalida
                coordenada = Coordenada(
                    longitud=self._coordenada(resultado.get("lon"), maximo=Decimal("180")),
                    latitud=self._coordenada(resultado.get("lat"), maximo=Decimal("90")),
                )
                sugerencias.append(SugerenciaDireccion(etiqueta=etiqueta, coordenada=coordenada))

            self._consultas_cacheadas[clave_cache] = tuple(sugerencias)
            if len(self._consultas_cacheadas) > MAX_CONSULTAS_CACHEADAS:
                self._consultas_cacheadas.popitem(last=False)
            return sugerencias

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> RutaCalculada:
        coordenadas = f"{origen.longitud},{origen.latitud};{destino.longitud},{destino.latitud}"
        respuesta = await self._request_json(
            "GET",
            f"{OSRM_ROUTE_URL}/{coordenadas}",
            params={"overview": "false", "alternatives": "false", "steps": "false"},
            ruta=True,
        )
        if not isinstance(respuesta, dict):
            raise RespuestaMapasInvalida
        codigo = respuesta.get("code")
        if codigo in {"NoRoute", "NoSegment"}:
            raise RutaMapasNoEncontrada
        if codigo != "Ok":
            raise RespuestaMapasInvalida
        rutas = respuesta.get("routes")
        if not isinstance(rutas, list):
            raise RespuestaMapasInvalida
        if not rutas:
            raise RutaMapasNoEncontrada

        primera_ruta = rutas[0]
        if not isinstance(primera_ruta, dict):
            raise RespuestaMapasInvalida
        distancia_metros = self._decimal_positivo(
            primera_ruta.get("distance"),
            permitir_cero=True,
        )
        duracion_segundos = self._decimal_positivo(
            primera_ruta.get("duration"),
            permitir_cero=True,
        )
        distancia_km = (distancia_metros / KM_POR_METRO).quantize(CENTESIMA, rounding=ROUND_HALF_UP)
        return RutaCalculada(
            distancia_ida_km=distancia_km,
            duracion_segundos=duracion_segundos,
        )

    async def _request_json(
        self, method: str, url: str, *, ruta: bool = False, **kwargs: Any
    ) -> Any:
        try:
            async with httpx.AsyncClient(
                timeout=TIMEOUT_SECONDS,
                transport=self._transport,
                follow_redirects=False,
            ) as cliente:
                respuesta = await cliente.request(
                    method,
                    url,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/json",
                    },
                    **kwargs,
                )
                if respuesta.is_error:
                    if ruta and respuesta.status_code < 500:
                        try:
                            contenido_error = respuesta.json()
                        except ValueError:
                            contenido_error = None
                        if isinstance(contenido_error, dict) and contenido_error.get("code") in {
                            "NoRoute",
                            "NoSegment",
                        }:
                            raise RutaMapasNoEncontrada
                    respuesta.raise_for_status()
                contenido = respuesta.json()
        except httpx.TimeoutException:
            raise MapasNoDisponible from None
        except httpx.HTTPError:
            raise MapasNoDisponible from None
        except ValueError:
            raise RespuestaMapasInvalida from None

        return contenido

    @classmethod
    def _coordenada(cls, valor: object, *, maximo: Decimal) -> Decimal:
        numero = cls._decimal_positivo(valor, permitir_cero=True, permitir_negativo=True)
        if not -maximo <= numero <= maximo:
            raise RespuestaMapasInvalida
        return numero

    @staticmethod
    def _decimal_positivo(
        valor: object,
        *,
        permitir_cero: bool,
        permitir_negativo: bool = False,
    ) -> Decimal:
        try:
            numero = Decimal(str(valor))
        except (InvalidOperation, ValueError, TypeError) as error:
            raise RespuestaMapasInvalida from error
        if not numero.is_finite():
            raise RespuestaMapasInvalida
        if not permitir_negativo and numero < 0:
            raise RespuestaMapasInvalida
        if not permitir_cero and numero == 0:
            raise RespuestaMapasInvalida
        return numero
