"""Tests de integración unificados de Clientes contra PostgreSQL real (H1).

Comprimido en exactamente 2 tests integrales:
1. `test_clientes_api_ciclo_completo_admin`: ciclo CRUD completo.
2. `test_clientes_api_seguridad_y_errores`: roles, 422, 409, 404 y regla de baja.
"""

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.integration.conftest import HistorialSimulado


def test_clientes_api_ciclo_completo_admin(
    cliente: TestClient,
    admin: dict[str, str],
    sesion_test: Session,
) -> None:
    # 1. Registrar cliente (POST)
    payload = {
        "razon_social": "Distribuidora del Sur S.A.",
        "telefono": "351 555 0100",
        "direccion_habitual": "Av. Colón 1250, Córdoba",
        "tiene_cuenta_corriente": True,
    }
    resp_crear = cliente.post("/api/clientes", json=payload, headers=admin)
    assert resp_crear.status_code == 201
    datos_creado = resp_crear.json()
    cid = datos_creado["id"]
    assert isinstance(cid, int)
    assert datos_creado["razon_social"] == "Distribuidora del Sur S.A."
    assert datos_creado["tiene_cuenta_corriente"] is True

    # Verificación en base de datos PostgreSQL
    fila = (
        sesion_test.execute(
            text("SELECT activo, razon_social_key FROM clientes WHERE id = :id"),
            {"id": cid},
        )
        .mappings()
        .first()
    )
    assert fila is not None and fila["activo"] is True
    assert fila["razon_social_key"] == "distribuidora del sur s.a."

    # 2. Consultar listado y filtrado (GET /api/clientes)
    resp_listar = cliente.get("/api/clientes?page=1&size=10", headers=admin)
    assert resp_listar.status_code == 200
    lista = resp_listar.json()
    assert lista["total"] >= 1
    assert any(item["id"] == cid for item in lista["items"])

    resp_filtro = cliente.get("/api/clientes?q=distribuidora", headers=admin)
    assert resp_filtro.status_code == 200
    assert any(item["id"] == cid for item in resp_filtro.json()["items"])

    # 3. Detalle de cliente (GET /api/clientes/{id})
    resp_detalle = cliente.get(f"/api/clientes/{cid}", headers=admin)
    assert resp_detalle.status_code == 200
    assert resp_detalle.json()["id"] == cid

    # 4. Modificar cliente (PUT /api/clientes/{id})
    payload_mod = {
        "razon_social": "Distribuidora del Sur SRL",
        "telefono": "351 999 8888",
        "direccion_habitual": "Av. Colón 2000, Córdoba",
        "tiene_cuenta_corriente": False,
    }
    resp_mod = cliente.put(f"/api/clientes/{cid}", json=payload_mod, headers=admin)
    assert resp_mod.status_code == 200
    assert resp_mod.json()["razon_social"] == "Distribuidora del Sur SRL"
    assert resp_mod.json()["tiene_cuenta_corriente"] is False

    # 5. Baja lógica (DELETE /api/clientes/{id})
    resp_baja = cliente.delete(f"/api/clientes/{cid}", headers=admin)
    assert resp_baja.status_code == 204

    # Idempotencia al eliminar
    assert cliente.delete(f"/api/clientes/{cid}", headers=admin).status_code == 204

    # Ya no aparece en detalle ni en listado
    assert cliente.get(f"/api/clientes/{cid}", headers=admin).status_code == 404
    resp_post_baja = cliente.get("/api/clientes", headers=admin).json()
    assert all(item["id"] != cid for item in resp_post_baja["items"])

    # La fila persiste en PostgreSQL con activo=False
    fila_inactiva = sesion_test.execute(
        text("SELECT activo FROM clientes WHERE id = :id"),
        {"id": cid},
    ).scalar_one()
    assert fila_inactiva is False


def test_clientes_api_seguridad_y_errores(
    cliente: TestClient,
    admin: dict[str, str],
    chofer: dict[str, str],
    historial_fake: HistorialSimulado,
) -> None:
    # 1. Crear un cliente base como admin
    payload1 = {
        "razon_social": "Transportes Norte S.A.",
        "telefono": "351 111 2222",
        "direccion_habitual": "Ruta 9 Km 5",
        "tiene_cuenta_corriente": False,
    }
    c1 = cliente.post("/api/clientes", json=payload1, headers=admin).json()
    c1_id = c1["id"]

    # 2. Control de accesos de Chofer
    # Puede ver listado y detalle
    assert cliente.get("/api/clientes", headers=chofer).status_code == 200
    assert cliente.get(f"/api/clientes/{c1_id}", headers=chofer).status_code == 200
    # No puede crear, modificar ni eliminar (403)
    assert cliente.post("/api/clientes", json=payload1, headers=chofer).status_code == 403
    assert cliente.put(f"/api/clientes/{c1_id}", json=payload1, headers=chofer).status_code == 403
    assert cliente.delete(f"/api/clientes/{c1_id}", headers=chofer).status_code == 403

    # 3. Validaciones 422
    assert cliente.post("/api/clientes", json={}, headers=admin).status_code == 422
    assert (
        cliente.post(
            "/api/clientes",
            json={**payload1, "razon_social": "Ab"},
            headers=admin,
        ).status_code
        == 422
    )
    assert (
        cliente.post(
            "/api/clientes",
            json={
                **payload1,
                "telefono": "1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0",
            },
            headers=admin,
        ).status_code
        == 422
    )
    assert cliente.get("/api/clientes?page=0", headers=admin).status_code == 422
    assert cliente.get("/api/clientes?size=0", headers=admin).status_code == 422

    # 4. Unicidad 409
    resp_dup = cliente.post(
        "/api/clientes",
        json={**payload1, "razon_social": "TRANSPORTES  NORTE S.A."},
        headers=admin,
    )
    assert resp_dup.status_code == 409

    # 5. Inexistente 404
    assert cliente.get("/api/clientes/999999", headers=admin).status_code == 404
    assert cliente.put("/api/clientes/999999", json=payload1, headers=admin).status_code == 404
    assert cliente.delete("/api/clientes/999999", headers=admin).status_code == 404

    # 6. Rechazo de baja con historial 409
    historial_fake.marcar_con_historial(c1_id)
    resp_baja_historial = cliente.delete(f"/api/clientes/{c1_id}", headers=admin)
    assert resp_baja_historial.status_code == 409
    # Sigue activo y disponible
    assert cliente.get(f"/api/clientes/{c1_id}", headers=admin).status_code == 200
