"""Pruebas aisladas de los adaptadores HTTP de Nominatim y OSRM."""

import asyncio
from decimal import Decimal
from time import monotonic

import httpx
import pytest

from app.application.mapas.errores import (
    MapasNoDisponible,
    RespuestaMapasInvalida,
    RutaMapasNoEncontrada,
)
from app.application.mapas.puertos import Coordenada
from app.infrastructure.maps.mapas_client import ClienteMapas


def test_busca_direcciones_con_user_agent_y_mapea_respuesta_nominatim() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "nominatim.openstreetmap.org"
        assert request.url.path == "/search"
        assert request.url.params["q"] == "Córdoba"
        assert request.url.params["format"] == "jsonv2"
        assert request.url.params["limit"] == "5"
        assert request.url.params["accept-language"] == "es"
        assert request.headers["User-Agent"] == "FletesExpressMVP/1.0"
        return httpx.Response(
            200,
            json=[
                {
                    "display_name": "Córdoba, Argentina",
                    "lon": "-64.1888",
                    "lat": "-31.4201",
                }
            ],
        )

    cliente = ClienteMapas(transport=httpx.MockTransport(responder))
    opciones = asyncio.run(cliente.buscar_direcciones("Córdoba"))

    assert len(opciones) == 1
    assert opciones[0].etiqueta == "Córdoba, Argentina"
    assert opciones[0].coordenada.longitud == Decimal("-64.1888")


def test_espacia_solicitudes_nominatim_al_menos_un_segundo() -> None:
    inicios: list[float] = []

    def responder(_request: httpx.Request) -> httpx.Response:
        inicios.append(monotonic())
        return httpx.Response(200, json=[])

    cliente = ClienteMapas(transport=httpx.MockTransport(responder))

    async def buscar_dos() -> None:
        await cliente.buscar_direcciones("Córdoba")
        await cliente.buscar_direcciones("Rosario")

    asyncio.run(buscar_dos())

    assert len(inicios) == 2
    assert inicios[1] - inicios[0] >= 0.99


def test_reutiliza_resultados_cacheados_para_consultas_equivalentes() -> None:
    solicitudes: list[httpx.Request] = []

    def responder(request: httpx.Request) -> httpx.Response:
        solicitudes.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "display_name": "Córdoba, Argentina",
                    "lon": "-64.1888",
                    "lat": "-31.4201",
                }
            ],
        )

    cliente = ClienteMapas(transport=httpx.MockTransport(responder))

    async def buscar_repetido() -> tuple[list, list]:
        primera = await cliente.buscar_direcciones("Córdoba")
        repetida = await cliente.buscar_direcciones("  CÓRDOBA  ")
        return primera, repetida

    primera, repetida = asyncio.run(buscar_repetido())

    assert primera == repetida
    assert len(solicitudes) == 1


def test_calcula_ruta_osrm_y_redondea_kilometros_de_ida() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "router.project-osrm.org"
        assert request.url.path == ("/route/v1/driving/-64.1888,-31.4201;-64.2,-31.43")
        assert request.url.params["overview"] == "false"
        assert request.url.params["alternatives"] == "false"
        assert request.url.params["steps"] == "false"
        assert request.headers["User-Agent"] == "FletesExpressMVP/1.0"
        return httpx.Response(
            200,
            json={
                "code": "Ok",
                "routes": [{"distance": 12345, "duration": 1234.5}],
            },
        )

    cliente = ClienteMapas(transport=httpx.MockTransport(responder))
    ruta = asyncio.run(
        cliente.calcular_ruta(
            Coordenada(Decimal("-64.1888"), Decimal("-31.4201")),
            Coordenada(Decimal("-64.2"), Decimal("-31.43")),
        )
    )

    assert ruta.distancia_ida_km == Decimal("12.35")
    assert ruta.duracion_segundos == Decimal("1234.5")


def test_rechaza_distancia_negativa_en_respuesta_externa() -> None:
    cliente = ClienteMapas(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(
                200,
                json={
                    "code": "Ok",
                    "routes": [{"distance": -1, "duration": 10}],
                },
            )
        ),
    )

    with pytest.raises(RespuestaMapasInvalida):
        asyncio.run(
            cliente.calcular_ruta(
                Coordenada(Decimal("0"), Decimal("0")),
                Coordenada(Decimal("1"), Decimal("1")),
            )
        )


@pytest.mark.parametrize(
    "respuesta",
    [
        httpx.Response(200, json={"code": "NoRoute", "routes": []}),
        httpx.Response(400, json={"code": "NoSegment", "message": "no match"}),
    ],
)
def test_informa_cuando_osrm_no_encuentra_ruta(respuesta: httpx.Response) -> None:
    cliente = ClienteMapas(
        transport=httpx.MockTransport(lambda _request: respuesta),
    )

    with pytest.raises(RutaMapasNoEncontrada):
        asyncio.run(
            cliente.calcular_ruta(
                Coordenada(Decimal("0"), Decimal("0")),
                Coordenada(Decimal("1"), Decimal("1")),
            )
        )


def test_convierte_error_http_externo_a_error_seguro() -> None:
    cliente = ClienteMapas(
        transport=httpx.MockTransport(lambda _request: httpx.Response(500)),
    )

    with pytest.raises(MapasNoDisponible):
        asyncio.run(cliente.buscar_direcciones("Córdoba"))


def test_convierte_timeout_a_error_seguro() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    cliente = ClienteMapas(transport=httpx.MockTransport(responder))

    with pytest.raises(MapasNoDisponible):
        asyncio.run(cliente.buscar_direcciones("Córdoba"))
