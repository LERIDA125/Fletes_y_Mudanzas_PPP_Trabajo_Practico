"""Pruebas del Cierre de Viaje, Prueba de Entrega (POD) y Rendición (Ticket H10)."""

from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.infrastructure.models  # noqa: F401
from app.core.dependencias import get_db
from app.infrastructure.db.base import Base
from app.main import app


@pytest.fixture
def cliente_api() -> Generator[TestClient, None, None]:
    engine: Engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

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


def _preparar_servicio(cliente: TestClient) -> tuple[int, int]:
    """Crea tipo, chofer, cliente y servicio confirmado. Devuelve (id_servicio, id_chofer)."""
    # 1. Tipo
    res_tipo = cliente.post(
        "/api/tipos-vehiculo",
        headers={"X-Rol": "admin"},
        json={
            "descripcion": "Furgon Test H10",
            "capacidad_carga_kg": 1000,
            "tarifa_hora_base": 15000,
            "tarifa_km_excedente": 500,
        },
    )
    assert res_tipo.status_code == 201
    id_tipo = res_tipo.json()["id"]

    # 2. Chofer
    res_chofer = cliente.post(
        "/api/choferes",
        headers={"X-Rol": "admin"},
        json={"nombre_completo": "Carlos Chofer", "telefono": "11-4567-8901"},
    )
    assert res_chofer.status_code == 201
    id_chofer = res_chofer.json()["id"]

    # 3. Cliente
    res_cli = cliente.post(
        "/api/clientes",
        headers={"X-Rol": "admin"},
        json={
            "razon_social": "Cliente Test H10",
            "telefono": "11-5555-6666",
            "direccion_habitual": "Av. Corrientes 1234",
        },
    )
    assert res_cli.status_code == 201
    id_cliente = res_cli.json()["id"]

    # 4. Servicio
    res_serv = cliente.post(
        "/api/servicios",
        headers={"X-Rol": "admin"},
        json={
            "id_cliente": id_cliente,
            "id_tipo_vehiculo": id_tipo,
            "id_chofer": id_chofer,
            "fecha": "2026-11-15",
            "hora_inicio": "10:00:00",
            "horas_estimadas": 2.0,
            "distancia_ida_km": 15.0,
        },
    )
    assert res_serv.status_code == 201
    id_servicio = res_serv.json()["id_servicio"]

    # Avanzar a confirmado
    res_conf = cliente.patch(
        f"/api/servicios/{id_servicio}/estado",
        headers={"X-Rol": "admin"},
        json={"estado": "confirmado"},
    )
    assert res_conf.status_code == 200
    assert res_conf.json()["estado"] == "confirmado"

    return id_servicio, id_chofer


def test_bloqueo_chofer_cambiar_a_finalizado_sin_remito(cliente_api: TestClient) -> None:
    """Un chofer no puede cambiar directamente el estado a 'finalizado' sin remito."""
    id_servicio, id_chofer = _preparar_servicio(cliente_api)

    # Intento de chofer de avanzar directamente a 'finalizado'
    res = cliente_api.patch(
        f"/api/servicios/{id_servicio}/estado",
        headers={"X-Rol": "chofer", "X-Chofer-Id": str(id_chofer)},
        json={"estado": "finalizado"},
    )
    # Debe ser rechazado (422 DatoInvalido / RemitoObligatorio)
    assert res.status_code == 422
    assert "remito" in res.json()["detail"].lower()


def test_flujo_cierre_viaje_con_remito_y_aprobacion_admin(cliente_api: TestClient) -> None:
    """Flujo completo H10: En camino -> Finalizar con remito -> Rendición PENDIENTE -> Admin."""
    id_servicio, id_chofer = _preparar_servicio(cliente_api)

    # 1. Chofer inicia el viaje (pasa a en curso)
    res_inicio = cliente_api.patch(
        f"/api/servicios/{id_servicio}/estado",
        headers={"X-Rol": "chofer", "X-Chofer-Id": str(id_chofer)},
        json={"estado": "en curso"},
    )
    assert res_inicio.status_code == 200
    assert res_inicio.json()["estado"] == "en curso"

    # 2. Chofer finaliza viaje enviando foto remito y monto cobrado real
    res_fin = cliente_api.post(
        f"/api/servicios/{id_servicio}/finalizar",
        headers={"X-Rol": "chofer", "X-Chofer-Id": str(id_chofer)},
        json={
            "foto_remito_url": "data:image/jpeg;base64,ZmFrZV9waG90bw==",
            "monto_cobrado_real": "45000.00",
        },
    )
    assert res_fin.status_code == 200
    datos_fin = res_fin.json()
    assert datos_fin["estado"] == "finalizado"
    assert datos_fin["estado_rendicion"] == "PENDIENTE"
    assert Decimal(str(datos_fin["monto_cobrado_real"])) == Decimal("45000.00")
    assert datos_fin["foto_remito_url"] == "data:image/jpeg;base64,ZmFrZV9waG90bw=="

    # 3. Chofer no puede aprobar su propia rendición (requiere admin)
    res_aprob_chofer = cliente_api.post(
        f"/api/servicios/{id_servicio}/rendicion/aprobar",
        headers={"X-Rol": "chofer"},
    )
    assert res_aprob_chofer.status_code == 403

    # 4. Admin aprueba la rendición
    res_aprob_admin = cliente_api.post(
        f"/api/servicios/{id_servicio}/rendicion/aprobar",
        headers={"X-Rol": "admin"},
    )
    assert res_aprob_admin.status_code == 200
    datos_aprobados = res_aprob_admin.json()
    assert datos_aprobados["estado_rendicion"] == "RENDIDO"
    assert datos_aprobados["estado"] == "cobrado"
    assert datos_aprobados["rendido_en"] is not None


def test_observar_rendicion_por_admin(cliente_api: TestClient) -> None:
    """Admin puede observar la rendición con motivo específico."""
    id_servicio, _ = _preparar_servicio(cliente_api)

    # Finalizar
    res_fin = cliente_api.post(
        f"/api/servicios/{id_servicio}/finalizar",
        headers={"X-Rol": "admin"},
        json={
            "foto_remito_url": "data:image/png;base64,YWJj",
            "monto_cobrado_real": "30000.00",
        },
    )
    assert res_fin.status_code == 200

    # Admin observa con motivo
    res_obs = cliente_api.post(
        f"/api/servicios/{id_servicio}/rendicion/observar",
        headers={"X-Rol": "admin"},
        json={"observacion": "Falta la firma del cliente al pie del remito"},
    )
    assert res_obs.status_code == 200
    datos_obs = res_obs.json()
    assert datos_obs["estado_rendicion"] == "OBSERVADO"
    assert datos_obs["observacion_rendicion"] == "Falta la firma del cliente al pie del remito"


def test_finalizar_servicio_valida_monto_y_remito(cliente_api: TestClient) -> None:
    """Valida que no se pueda finalizar con monto negativo ni sin remito."""
    id_servicio, _ = _preparar_servicio(cliente_api)

    # Sin remito
    res_sin_foto = cliente_api.post(
        f"/api/servicios/{id_servicio}/finalizar",
        headers={"X-Rol": "admin"},
        json={
            "foto_remito_url": "",
            "monto_cobrado_real": "10000.00",
        },
    )
    assert res_sin_foto.status_code == 422

    # Monto negativo
    res_monto_neg = cliente_api.post(
        f"/api/servicios/{id_servicio}/finalizar",
        headers={"X-Rol": "admin"},
        json={
            "foto_remito_url": "data:image/jpeg;base64,YWJj",
            "monto_cobrado_real": "-50.00",
        },
    )
    assert res_monto_neg.status_code == 422
