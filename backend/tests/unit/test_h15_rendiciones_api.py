"""Pruebas HTTP del backend de Rendiciones (H15)."""

from collections.abc import Generator
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.infrastructure.models  # noqa: F401 - Registra todas las tablas en Base.metadata
from app.core.dependencias import get_db
from app.infrastructure.db.base import Base
from app.infrastructure.models.servicio import ServicioORM
from app.main import app

ADMIN = {"X-Rol": "admin"}


@pytest.fixture
def engine() -> Generator[Engine, None, None]:
    engine: Engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def cliente_api(engine: Engine) -> Generator[TestClient, None, None]:
    def obtener_sesion() -> Generator[Session, None, None]:
        with Session(engine, expire_on_commit=False) as sesion:
            yield sesion

    app.dependency_overrides[get_db] = obtener_sesion
    try:
        with TestClient(app) as cliente:
            yield cliente
    finally:
        app.dependency_overrides.pop(get_db, None)


def _crear_tipo(cliente: TestClient) -> int:
    respuesta = cliente.post(
        "/api/tipos-vehiculo",
        headers=ADMIN,
        json={
            "descripcion": f"Camioneta {uuid4().hex[:8]}",
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
        headers=ADMIN,
        json={
            "razon_social": f"Cliente {uuid4().hex[:8]}",
            "telefono": "3515550111",
            "direccion_habitual": "Av. Siempre Viva 742",
            "tiene_cuenta_corriente": False,
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _crear_chofer(cliente: TestClient) -> int:
    respuesta = cliente.post(
        "/api/choferes",
        headers=ADMIN,
        json={"nombre_completo": "Chofer Rendicion", "telefono": "3515550122"},
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _crear_servicio(
    cliente: TestClient,
    engine: Engine,
    *,
    con_chofer: bool = True,
    estado: str = "finalizado",
    fecha: str = "2026-11-03",
) -> dict:
    tipo_id = _crear_tipo(cliente)
    cliente_id = _crear_cliente(cliente)
    cuerpo: dict = {
        "id_cliente": cliente_id,
        "id_tipo_vehiculo": tipo_id,
        "fecha": fecha,
        "horas_estimadas": 2,
        "distancia_ida_km": 10,
    }
    if con_chofer:
        cuerpo["id_chofer"] = _crear_chofer(cliente)

    respuesta = cliente.post("/api/servicios", headers=ADMIN, json=cuerpo)
    assert respuesta.status_code == 201
    servicio = respuesta.json()

    with Session(engine) as sesion:
        orm = sesion.get(ServicioORM, servicio["id_servicio"])
        assert orm is not None
        orm.estado = estado
        sesion.commit()

    return servicio


def _payload(servicio_id: int, **overrides) -> dict:
    datos = {
        "id_servicio": servicio_id,
        "tarifa": "18500.00",
        "adelanto": "12000.00",
        "gastos_informados": {
            "combustible": "2000.00",
            "peajes": "300.00",
            "otros": "200.00",
        },
        "observaciones": "Comprobantes entregados",
    }
    datos.update(overrides)
    return datos


def test_registra_rendicion_y_calcula_saldo(cliente_api: TestClient, engine: Engine) -> None:
    servicio = _crear_servicio(cliente_api, engine, fecha=date.today().isoformat())

    respuesta = cliente_api.post(
        "/api/rendiciones", headers=ADMIN, json=_payload(servicio["id_servicio"])
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["codigo"] == "REN-001"
    assert cuerpo["id_servicio"] == servicio["id_servicio"]
    assert cuerpo["estado"] == "pendiente"
    assert Decimal(cuerpo["gastos_total"]) == Decimal("2500.00")
    assert Decimal(cuerpo["saldo"]) == Decimal("4000.00")
    assert cuerpo["nombre_chofer"] == "Chofer Rendicion"
    assert cuerpo["razon_social_cliente"].startswith("Cliente ")
    assert cuerpo["observaciones"] == "Comprobantes entregados"


def test_rechaza_campos_calculados_por_el_cliente(
    cliente_api: TestClient, engine: Engine
) -> None:
    servicio = _crear_servicio(cliente_api, engine)

    respuesta = cliente_api.post(
        "/api/rendiciones",
        headers=ADMIN,
        json=_payload(servicio["id_servicio"], saldo="9999.00"),
    )

    assert respuesta.status_code == 422


def test_rechaza_servicio_ya_rendido(cliente_api: TestClient, engine: Engine) -> None:
    servicio = _crear_servicio(cliente_api, engine)
    payload = _payload(servicio["id_servicio"])
    assert cliente_api.post("/api/rendiciones", headers=ADMIN, json=payload).status_code == 201

    repetida = cliente_api.post("/api/rendiciones", headers=ADMIN, json=payload)

    assert repetida.status_code == 409


def test_rechaza_servicio_no_rendible_o_sin_chofer(
    cliente_api: TestClient, engine: Engine
) -> None:
    pendiente = _crear_servicio(cliente_api, engine, estado="pendiente")
    sin_chofer = _crear_servicio(cliente_api, engine, con_chofer=False)

    no_rendible = cliente_api.post(
        "/api/rendiciones", headers=ADMIN, json=_payload(pendiente["id_servicio"])
    )
    sin_chofer_resp = cliente_api.post(
        "/api/rendiciones", headers=ADMIN, json=_payload(sin_chofer["id_servicio"])
    )

    assert no_rendible.status_code == 409
    assert sin_chofer_resp.status_code == 422


def test_lista_rendiciones_con_busqueda_y_resumen(
    cliente_api: TestClient, engine: Engine
) -> None:
    servicio = _crear_servicio(cliente_api, engine, fecha=date.today().isoformat())
    creada = cliente_api.post(
        "/api/rendiciones", headers=ADMIN, json=_payload(servicio["id_servicio"])
    )
    assert creada.status_code == 201

    listado = cliente_api.get("/api/rendiciones?page=1&size=10", headers=ADMIN)

    assert listado.status_code == 200
    cuerpo = listado.json()
    assert cuerpo["total"] == 1
    assert cuerpo["items"][0]["codigo"] == "REN-001"
    assert Decimal(cuerpo["resumen"]["pendiente_total"]) == Decimal("4000.00")
    assert cuerpo["resumen"]["pendiente_cantidad"] == 1
    assert Decimal(cuerpo["resumen"]["gastos_total"]) == Decimal("2500.00")

    filtrado = cliente_api.get("/api/rendiciones?q=Chofer", headers=ADMIN)
    assert filtrado.json()["total"] == 1
    sin_resultados = cliente_api.get("/api/rendiciones?q=inexistente", headers=ADMIN)
    assert sin_resultados.json()["total"] == 0


def test_cambia_estado_y_valida_errores(cliente_api: TestClient, engine: Engine) -> None:
    servicio = _crear_servicio(cliente_api, engine)
    creada = cliente_api.post(
        "/api/rendiciones", headers=ADMIN, json=_payload(servicio["id_servicio"])
    ).json()
    ruta = f"/api/rendiciones/{creada['id']}/estado"

    aprobada = cliente_api.patch(ruta, headers=ADMIN, json={"estado": "aprobada"})
    assert aprobada.status_code == 200
    assert aprobada.json()["estado"] == "aprobada"

    invalido = cliente_api.patch(ruta, headers=ADMIN, json={"estado": "cerrada"})
    assert invalido.status_code == 422

    inexistente = cliente_api.patch(
        "/api/rendiciones/999999/estado", headers=ADMIN, json={"estado": "aprobada"}
    )
    assert inexistente.status_code == 404


def test_servicios_elegibles_excluye_rendidos(cliente_api: TestClient, engine: Engine) -> None:
    servicio = _crear_servicio(cliente_api, engine)

    elegibles = cliente_api.get("/api/rendiciones/servicios-elegibles", headers=ADMIN)
    assert elegibles.status_code == 200
    assert [item["id_servicio"] for item in elegibles.json()] == [servicio["id_servicio"]]

    cliente_api.post(
        "/api/rendiciones", headers=ADMIN, json=_payload(servicio["id_servicio"])
    )

    elegibles_despues = cliente_api.get("/api/rendiciones/servicios-elegibles", headers=ADMIN)
    assert elegibles_despues.json() == []


def test_solo_admin_accede_a_rendiciones(cliente_api: TestClient) -> None:
    assert cliente_api.get("/api/rendiciones").status_code == 200
    assert (
        cliente_api.get("/api/rendiciones", headers={"X-Rol": "chofer"}).status_code == 403
    )
