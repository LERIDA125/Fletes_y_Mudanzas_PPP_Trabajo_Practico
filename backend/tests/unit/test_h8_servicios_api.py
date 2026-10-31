"""Pruebas HTTP del backend de Servicios y Cotizaciones (H8)."""

from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.infrastructure.models  # noqa: F401 - Registra todas las tablas en Base.metadata
from app.core.dependencias import get_db
from app.infrastructure.db.base import Base
from app.infrastructure.models import ConfiguracionCotizacionORM
from app.main import app


@pytest.fixture
def cliente_api() -> Generator[TestClient, None, None]:
    engine: Engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as sesion:
        sesion.add(
            ConfiguracionCotizacionORM(
                id=1,
                recargo_ayudante=Decimal("500.00"),
                recargo_escalera=Decimal("300.00"),
                porcentaje_zona_concurrida=Decimal("15.00"),
                porcentaje_urgencia_mismo_dia=Decimal("20.00"),
            )
        )
        sesion.commit()

    def obtener_sesion() -> Generator[Session, None, None]:
        with Session(engine, expire_on_commit=False) as sesion:
            yield sesion

    app.dependency_overrides[get_db] = obtener_sesion
    try:
        with TestClient(app) as cliente:
            yield cliente
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


def _crear_tipo(cliente: TestClient) -> int:
    respuesta = cliente.post(
        "/api/tipos-vehiculo",
        headers={"X-Rol": "admin"},
        json={
            "descripcion": "Camioneta Cotizacion",
            "capacidad_carga_kg": 1500,
            "tarifa_hora_base": 3000,
            "tarifa_km_excedente": 150,
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _crear_cliente(cliente: TestClient) -> int:
    respuesta = cliente.post(
        "/api/clientes",
        headers={"X-Rol": "admin"},
        json={
            "razon_social": "Cliente de Prueba",
            "telefono": "3515550100",
            "direccion_habitual": "Av. Siempre Viva 123",
            "tiene_cuenta_corriente": False,
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _crear_vehiculo(cliente: TestClient, tipo_id: int) -> int:
    respuesta = cliente.post(
        "/api/vehiculos",
        headers={"X-Rol": "admin"},
        json={"patente": "CC 789 GHI", "id_tipo_vehiculo": tipo_id},
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def test_cotiza_crea_y_lista_servicio_con_sugerido_y_acordado(
    cliente_api: TestClient,
) -> None:
    tipo_id = _crear_tipo(cliente_api)
    cliente_id = _crear_cliente(cliente_api)
    admin = {"X-Rol": "admin"}
    entrada = {
        "id_cliente": cliente_id,
        "id_tipo_vehiculo": tipo_id,
        "fecha": "2026-10-25",
        "hora_inicio": "09:30:00",
        "horas_estimadas": 2,
        "km_estimados": 15,
        "precio_acordado": 9000,
        "requiere_ayudante": True,
        "acceso_escalera": True,
        "zona_concurrida": True,
        "urgencia_mismo_dia": True,
    }

    cotizacion = cliente_api.post(
        "/api/cotizaciones/calcular",
        headers=admin,
        json={
            "id_tipo_vehiculo": tipo_id,
            "horas_estimadas": 2,
            "km_estimados": 15,
            "requiere_ayudante": True,
            "acceso_escalera": True,
            "zona_concurrida": True,
            "urgencia_mismo_dia": True,
        },
    )
    assert cotizacion.status_code == 200
    datos_cotizacion = cotizacion.json()
    assert Decimal(datos_cotizacion["base_horas"]) == Decimal("6000.00")
    assert Decimal(datos_cotizacion["base_km"]) == Decimal("2250.00")
    assert Decimal(datos_cotizacion["subtotal_con_fijos"]) == Decimal("9050.00")
    assert Decimal(datos_cotizacion["precio_sugerido"]) == Decimal("12217.50")
    assert datos_cotizacion["id_tipo_vehiculo"] == tipo_id

    alta = cliente_api.post("/api/servicios", headers=admin, json=entrada)
    assert alta.status_code == 201
    servicio = alta.json()
    assert servicio["razon_social_cliente"] == "Cliente de Prueba"
    assert servicio["descripcion_tipo_vehiculo"] == "Camioneta Cotizacion"
    assert servicio["estado"] == "pendiente"
    assert Decimal(servicio["tarifa_hora_aplicada"]) == Decimal("3000.00")
    assert Decimal(servicio["tarifa_km_aplicada"]) == Decimal("150.00")
    assert Decimal(servicio["km_estimados"]) == Decimal("15.00")
    assert Decimal(servicio["precio_sugerido"]) == Decimal("12217.50")
    assert Decimal(servicio["precio_acordado"]) == Decimal("9000.00")
    assert servicio["requiere_ayudante"] is True
    assert servicio["acceso_escalera"] is True
    assert servicio["zona_concurrida"] is True
    assert servicio["urgencia_mismo_dia"] is True

    listado = cliente_api.get("/api/servicios?page=1&size=10", headers=admin)
    assert listado.status_code == 200
    assert listado.json()["total"] == 1
    assert listado.json()["items"][0]["id_servicio"] == servicio["id_servicio"]
    assert listado.json()["items"][0]["nombre_chofer"] is None
    assert listado.json()["items"][0]["patente_vehiculo"] is None


def test_cotiza_por_tipo_sin_requerir_unidad_de_flota(cliente_api: TestClient) -> None:
    admin = {"X-Rol": "admin"}
    tipo_id = _crear_tipo(cliente_api)

    cotizacion = cliente_api.post(
        "/api/cotizaciones/calcular",
        headers=admin,
        json={
            "id_tipo_vehiculo": tipo_id,
            "horas_estimadas": 2,
            "km_estimados": 10,
        },
    )

    assert cotizacion.status_code == 200
    assert cotizacion.json()["id_tipo_vehiculo"] == tipo_id
    assert "id_vehiculo" not in cotizacion.json()
    assert Decimal(cotizacion.json()["precio_sugerido"]) == Decimal("7500.00")


def test_no_acepta_precio_sugerido_enviado_por_el_cliente(cliente_api: TestClient) -> None:
    tipo_id = _crear_tipo(cliente_api)
    cliente_id = _crear_cliente(cliente_api)

    respuesta = cliente_api.post(
        "/api/servicios",
        headers={"X-Rol": "admin"},
        json={
            "id_cliente": cliente_id,
            "id_tipo_vehiculo": tipo_id,
            "fecha": "2026-10-25",
            "horas_estimadas": 1,
            "km_estimados": 0,
            "precio_acordado": 3000,
            "precio_sugerido": 1,
        },
    )

    assert respuesta.status_code == 422
    assert cliente_api.get("/api/servicios", headers={"X-Rol": "admin"}).json()["total"] == 0


def test_asume_admin_en_demo_y_falla_cerrado_fuera_de_dev(
    cliente_api: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.config import get_settings

    assert cliente_api.get("/api/servicios").status_code == 200

    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    try:
        listado = cliente_api.get("/api/servicios", headers={"X-Rol": "admin"})
    finally:
        get_settings.cache_clear()

    assert listado.status_code == 401


def test_cancela_servicio_con_motivo_y_hora_del_servidor(cliente_api: TestClient) -> None:
    admin = {"X-Rol": "admin"}
    tipo_id = _crear_tipo(cliente_api)
    cliente_id = _crear_cliente(cliente_api)

    alta = cliente_api.post(
        "/api/servicios",
        headers=admin,
        json={
            "id_cliente": cliente_id,
            "id_tipo_vehiculo": tipo_id,
            "fecha": "2026-10-25",
            "horas_estimadas": 1,
            "km_estimados": 0,
            "precio_acordado": 3000,
        },
    )
    assert alta.status_code == 201
    servicio_id = alta.json()["id_servicio"]
    ruta = f"/api/servicios/{servicio_id}/cancelar"

    sin_motivo = cliente_api.patch(ruta, headers=admin, json={"motivo": "   "})
    assert sin_motivo.status_code == 422
    assert cliente_api.get("/api/servicios", headers=admin).json()["items"][0]["estado"] == (
        "pendiente"
    )

    cancelacion = cliente_api.patch(ruta, headers=admin, json={"motivo": "  Cliente reprogramó  "})
    assert cancelacion.status_code == 200
    assert cancelacion.json()["estado"] == "cancelado"
    assert cancelacion.json()["motivo_cancelacion"] == "Cliente reprogramó"
    assert cancelacion.json()["hora_fin"] is not None

    assert cliente_api.patch(ruta, headers=admin, json={"motivo": "Otra vez"}).status_code == 409
    assert (
        cliente_api.patch(
            "/api/servicios/999999/cancelar", headers=admin, json={"motivo": "No existe"}
        ).status_code
        == 404
    )


def test_cambia_estado_siguiendo_la_maquina_y_requiere_admin(cliente_api: TestClient) -> None:
    admin = {"X-Rol": "admin"}
    tipo_id = _crear_tipo(cliente_api)
    cliente_id = _crear_cliente(cliente_api)
    alta = cliente_api.post(
        "/api/servicios",
        headers=admin,
        json={
            "id_cliente": cliente_id,
            "id_tipo_vehiculo": tipo_id,
            "fecha": "2026-10-25",
            "horas_estimadas": 1,
            "km_estimados": 0,
            "precio_acordado": 3000,
        },
    )
    servicio_id = alta.json()["id_servicio"]
    ruta = f"/api/servicios/{servicio_id}/estado"

    # La UI arma el <select> con lo que el backend declara como transición válida.
    assert alta.json()["transiciones_validas"] == ["confirmado", "cancelado"]

    no_admin = cliente_api.patch(ruta, headers={"X-Rol": "chofer"}, json={"estado": "confirmado"})
    assert no_admin.status_code == 403

    confirmado = cliente_api.patch(ruta, headers=admin, json={"estado": "confirmado"})
    assert confirmado.status_code == 200
    assert confirmado.json()["estado"] == "confirmado"
    assert confirmado.json()["transiciones_validas"] == ["en curso", "cancelado"]

    salto = cliente_api.patch(ruta, headers=admin, json={"estado": "finalizado"})
    assert salto.status_code == 422
    assert cliente_api.get("/api/servicios", headers=admin).json()["items"][0]["estado"] == (
        "confirmado"
    )

    assert (
        cliente_api.patch(
            "/api/servicios/999999/estado",
            headers=admin,
            json={"estado": "confirmado"},
        ).status_code
        == 404
    )
    assert cliente_api.patch(ruta, headers=admin, json={"estado": "cancelado"}).status_code == 422


def test_elimina_servicio_con_respuesta_204_y_404_si_no_existe(cliente_api: TestClient) -> None:
    admin = {"X-Rol": "admin"}
    tipo_id = _crear_tipo(cliente_api)
    cliente_id = _crear_cliente(cliente_api)
    alta = cliente_api.post(
        "/api/servicios",
        headers=admin,
        json={
            "id_cliente": cliente_id,
            "id_tipo_vehiculo": tipo_id,
            "fecha": "2026-10-25",
            "horas_estimadas": 1,
            "km_estimados": 0,
            "precio_acordado": 3000,
        },
    )
    servicio_id = alta.json()["id_servicio"]
    ruta = f"/api/servicios/{servicio_id}"

    no_admin = cliente_api.delete(ruta, headers={"X-Rol": "chofer"})
    assert no_admin.status_code == 403

    eliminacion = cliente_api.delete(ruta, headers=admin)
    assert eliminacion.status_code == 204
    assert eliminacion.content == b""
    assert cliente_api.get("/api/servicios", headers=admin).json()["total"] == 0
    assert cliente_api.delete(ruta, headers=admin).status_code == 404


def test_asociaciones_legibles_y_bajas_bloqueadas_por_historial(
    cliente_api: TestClient,
) -> None:
    admin = {"X-Rol": "admin"}
    tipo_id = _crear_tipo(cliente_api)
    cliente_id = _crear_cliente(cliente_api)

    chofer = cliente_api.post(
        "/api/choferes",
        headers=admin,
        json={"nombre_completo": "Chofer de Prueba", "telefono": "3515550101"},
    )
    assert chofer.status_code == 201
    chofer_id = chofer.json()["id"]

    vehiculo = cliente_api.post(
        "/api/vehiculos",
        headers=admin,
        json={
            "patente": "AA 123 ABC",
            "id_tipo_vehiculo": tipo_id,
            "id_chofer_habitual": None,
        },
    )
    assert vehiculo.status_code == 201
    vehiculo_id = vehiculo.json()["id"]

    servicio = cliente_api.post(
        "/api/servicios",
        headers=admin,
        json={
            "id_cliente": cliente_id,
            "id_tipo_vehiculo": tipo_id,
            "id_chofer": chofer_id,
            "id_vehiculo": vehiculo_id,
            "fecha": "2026-10-25",
            "horas_estimadas": 1,
            "km_estimados": 1,
            "precio_acordado": 3000,
        },
    )
    assert servicio.status_code == 201
    assert servicio.json()["nombre_chofer"] == "Chofer de Prueba"
    assert servicio.json()["patente_vehiculo"] == "AA 123 ABC"

    assert cliente_api.delete(f"/api/clientes/{cliente_id}", headers=admin).status_code == 409
    assert cliente_api.delete(f"/api/vehiculos/{vehiculo_id}", headers=admin).status_code == 409


def test_alta_con_cliente_nuevo_lo_crea_y_reutiliza(cliente_api: TestClient) -> None:
    admin = {"X-Rol": "admin"}
    tipo_id = _crear_tipo(cliente_api)
    entrada = {
        "id_tipo_vehiculo": tipo_id,
        "horas_estimadas": 1,
        "km_estimados": 0,
        "precio_acordado": 3000,
        "fecha": "2026-10-25",
        "nuevo_cliente": {
            "razon_social": "Mudanzas Nueva",
            "telefono": "3515559999",
            "direccion_habitual": "Av. Nueva 456",
            "tiene_cuenta_corriente": False,
        },
    }

    primera = cliente_api.post("/api/servicios", headers=admin, json=entrada)
    assert primera.status_code == 201, primera.text
    assert primera.json()["razon_social_cliente"] == "Mudanzas Nueva"

    segunda = cliente_api.post(
        "/api/servicios",
        headers=admin,
        json={
            **entrada,
            "fecha": "2026-10-26",
            "nuevo_cliente": {
                **entrada["nuevo_cliente"],
                "razon_social": "  mudanzas   NUEVA ",
            },
        },
    )
    assert segunda.status_code == 201, segunda.text

    listado = cliente_api.get("/api/clientes?page=1&size=10", headers=admin)
    assert listado.status_code == 200
    assert listado.json()["total"] == 1
    assert primera.json()["id_cliente"] == segunda.json()["id_cliente"]


def test_alta_rechaza_cliente_existente_y_nuevo_a_la_vez(cliente_api: TestClient) -> None:
    admin = {"X-Rol": "admin"}
    tipo_id = _crear_tipo(cliente_api)
    cliente_id = _crear_cliente(cliente_api)

    respuesta = cliente_api.post(
        "/api/servicios",
        headers=admin,
        json={
            "id_cliente": cliente_id,
            "nuevo_cliente": {
                "razon_social": "Otro cliente",
                "telefono": "3515559999",
                "direccion_habitual": "Otra calle 123",
                "tiene_cuenta_corriente": False,
            },
            "id_tipo_vehiculo": tipo_id,
            "fecha": "2026-10-25",
            "horas_estimadas": 1,
            "km_estimados": 0,
            "precio_acordado": 3000,
        },
    )

    assert respuesta.status_code == 422
    assert cliente_api.get("/api/servicios", headers=admin).json()["total"] == 0


def test_disponibilidad_excluye_choferes_y_vehiculos_ocupados(cliente_api: TestClient) -> None:
    admin = {"X-Rol": "admin"}
    tipo_id = _crear_tipo(cliente_api)
    cliente_id = _crear_cliente(cliente_api)

    choferes = []
    for nombre in ("Chofer Uno", "Chofer Dos"):
        respuesta = cliente_api.post(
            "/api/choferes",
            headers=admin,
            json={"nombre_completo": nombre, "telefono": "3515550101"},
        )
        assert respuesta.status_code == 201
        choferes.append(respuesta.json()["id"])

    vehiculos = []
    for patente in ("AA 123 ABC", "BB 456 DEF"):
        respuesta = cliente_api.post(
            "/api/vehiculos",
            headers=admin,
            json={"patente": patente, "id_tipo_vehiculo": tipo_id},
        )
        assert respuesta.status_code == 201
        vehiculos.append(respuesta.json()["id"])

    alta = cliente_api.post(
        "/api/servicios",
        headers=admin,
        json={
            "id_cliente": cliente_id,
            "id_tipo_vehiculo": tipo_id,
            "id_chofer": choferes[0],
            "id_vehiculo": vehiculos[0],
            "fecha": "2026-10-25",
            "hora_inicio": "09:00:00",
            "horas_estimadas": 2,
            "km_estimados": 0,
            "precio_acordado": 6000,
        },
    )
    assert alta.status_code == 201

    solapada = cliente_api.get(
        "/api/servicios/disponibilidad",
        headers=admin,
        params={
            "fecha": "2026-10-25",
            "id_tipo_vehiculo": tipo_id,
            "hora_inicio": "10:00:00",
            "horas_estimadas": 1,
        },
    )
    assert solapada.status_code == 200, solapada.text
    assert [item["id"] for item in solapada.json()["choferes"]] == [choferes[1]]
    assert [item["id"] for item in solapada.json()["vehiculos"]] == [vehiculos[1]]

    libre = cliente_api.get(
        "/api/servicios/disponibilidad",
        headers=admin,
        params={
            "fecha": "2026-10-25",
            "id_tipo_vehiculo": tipo_id,
            "hora_inicio": "12:00:00",
            "horas_estimadas": 1,
        },
    )
    assert libre.status_code == 200
    assert len(libre.json()["choferes"]) == 2
    assert len(libre.json()["vehiculos"]) == 2
