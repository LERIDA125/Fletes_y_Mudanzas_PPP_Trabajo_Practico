"""Pruebas del contrato HTTP de los endpoints de Mapas."""

from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.application.mapas.errores import (
    MapasNoDisponible,
    RespuestaMapasInvalida,
    RutaMapasNoEncontrada,
)
from app.application.mapas.gestor_mapas import GestorMapas
from app.application.mapas.puertos import (
    Coordenada,
    RutaCalculada,
    SugerenciaDireccion,
)
from app.core.dependencias import get_gestor_mapas, get_rol_actual
from app.main import app


class ServicioMapasFalso:
    async def buscar_direcciones(self, consulta: str) -> list[SugerenciaDireccion]:
        assert consulta == "Av. Siempre Viva"
        return [
            SugerenciaDireccion(
                etiqueta="Av. Siempre Viva, Córdoba",
                coordenada=Coordenada(
                    longitud=Decimal("-64.1888"),
                    latitud=Decimal("-31.4201"),
                ),
            )
        ]

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> RutaCalculada:
        assert origen.longitud == Decimal("-64.1888")
        assert destino.latitud == Decimal("-31.43")
        return RutaCalculada(
            distancia_ida_km=Decimal("12.35"),
            duracion_segundos=Decimal("1234.5"),
        )


@pytest.fixture
def cliente_api() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_gestor_mapas] = lambda: GestorMapas(ServicioMapasFalso())
    app.dependency_overrides[get_rol_actual] = lambda: "admin"
    try:
        with TestClient(app) as cliente:
            yield cliente
    finally:
        app.dependency_overrides.pop(get_gestor_mapas, None)
        app.dependency_overrides.pop(get_rol_actual, None)


def test_busca_direcciones_y_devuelve_coordenadas(cliente_api: TestClient) -> None:
    respuesta = cliente_api.post(
        "/api/mapas/direcciones",
        json={"consulta": " Av. Siempre Viva "},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "opciones": [
            {
                "etiqueta": "Av. Siempre Viva, Córdoba",
                "longitud": "-64.1888",
                "latitud": "-31.4201",
            }
        ]
    }


def test_busqueda_sin_resultados_devuelve_lista_vacia(cliente_api: TestClient) -> None:
    class ServicioSinSugerencias(ServicioMapasFalso):
        async def buscar_direcciones(self, consulta: str) -> list[SugerenciaDireccion]:
            return []

    app.dependency_overrides[get_gestor_mapas] = lambda: GestorMapas(ServicioSinSugerencias())

    respuesta = cliente_api.post(
        "/api/mapas/direcciones",
        json={"consulta": "Calle inexistente"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {"opciones": []}


def test_calcula_ruta_y_devuelve_kilometros_y_duracion(cliente_api: TestClient) -> None:
    respuesta = cliente_api.post(
        "/api/mapas/ruta",
        json={
            "origen": {"longitud": -64.1888, "latitud": -31.4201},
            "destino": {"longitud": -64.2, "latitud": -31.43},
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "distancia_ida_km": "12.35",
        "duracion_segundos": "1234.5",
    }


def test_rechaza_coordenadas_fuera_de_rango(cliente_api: TestClient) -> None:
    respuesta = cliente_api.post(
        "/api/mapas/ruta",
        json={
            "origen": {"longitud": -64.1888, "latitud": -91},
            "destino": {"longitud": -64.2, "latitud": -31.43},
        },
    )

    assert respuesta.status_code == 422


def test_requiere_rol_admin(cliente_api: TestClient) -> None:
    app.dependency_overrides[get_rol_actual] = lambda: "chofer"

    respuesta = cliente_api.post(
        "/api/mapas/ruta",
        json={
            "origen": {"longitud": -64.1888, "latitud": -31.4201},
            "destino": {"longitud": -64.2, "latitud": -31.43},
        },
    )

    assert respuesta.status_code == 403


def test_openapi_no_publica_credenciales() -> None:
    openapi = app.openapi()

    assert "/api/mapas/ruta" in openapi["paths"]
    assert "/api/mapas/direcciones" in openapi["paths"]
    assert "api_key" not in str(openapi).lower()


@pytest.mark.parametrize(
    ("error", "status_code", "mensaje"),
    [
        (MapasNoDisponible(), 503, "El servicio de mapas no está disponible temporalmente."),
        (
            RespuestaMapasInvalida(),
            502,
            "El servicio de mapas devolvió una respuesta inválida.",
        ),
        (
            RutaMapasNoEncontrada(),
            422,
            "No se encontró una ruta entre las ubicaciones seleccionadas.",
        ),
    ],
)
def test_traduce_errores_del_proveedor_sin_detalles_internos(
    cliente_api: TestClient,
    error: Exception,
    status_code: int,
    mensaje: str,
) -> None:
    class ServicioMapasConError(ServicioMapasFalso):
        async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> RutaCalculada:
            raise error

    app.dependency_overrides[get_gestor_mapas] = lambda: GestorMapas(ServicioMapasConError())

    respuesta = cliente_api.post(
        "/api/mapas/ruta",
        json={
            "origen": {"longitud": -64.1888, "latitud": -31.4201},
            "destino": {"longitud": -64.2, "latitud": -31.43},
        },
    )

    assert respuesta.status_code == status_code
    assert respuesta.json() == {"detail": mensaje}
