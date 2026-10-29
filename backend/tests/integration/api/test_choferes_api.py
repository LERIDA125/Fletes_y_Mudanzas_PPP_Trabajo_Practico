"""Tests de integración unificados de Choferes contra PostgreSQL real (H3).

Comprimido en exactamente 2 tests integrales:
1. `test_choferes_api_ciclo_completo_admin`: ciclo CRUD completo, persistencia y baja lógica.
2. `test_choferes_api_seguridad_y_reglas`: roles (admin/chofer), validaciones (422), rechazo de
   campos del sistema y comportamiento de baja lógica a nivel HTTP.
"""

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_choferes_api_ciclo_completo_admin(
    cliente: TestClient,
    admin: dict[str, str],
    sesion_test: Session,
) -> None:
    # 1. Registrar chofer
    payload = {"nombre_completo": "Juan Pérez", "telefono": "351 555 0100"}
    resp = cliente.post("/api/choferes", json=payload, headers=admin)
    assert resp.status_code == 201
    cuerpo = resp.json()
    chofer_id = cuerpo["id"]
    assert cuerpo["nombre_completo"] == "Juan Pérez"
    assert cuerpo["telefono"] == "351 555 0100"
    assert cuerpo["activo"] is True
    assert cuerpo["saldo_a_favor"] == 0.0
    assert cuerpo["creado_en"] and cuerpo["actualizado_en"]

    # Verificación en PostgreSQL
    fila = (
        sesion_test.execute(
            text("SELECT activo, nombre_completo FROM choferes WHERE id = :id"),
            {"id": chofer_id},
        )
        .mappings()
        .first()
    )
    assert fila is not None and fila["activo"] is True
    assert fila["nombre_completo"] == "Juan Pérez"

    # 2. Listado y filtro
    resp_listar = cliente.get("/api/choferes?q=juan", headers=admin)
    assert resp_listar.status_code == 200
    listado = resp_listar.json()
    assert listado["total"] == 1
    assert any(c["id"] == chofer_id for c in listado["items"])

    # 3. Detalle
    resp_det = cliente.get(f"/api/choferes/{chofer_id}", headers=admin)
    assert resp_det.status_code == 200
    assert resp_det.json()["nombre_completo"] == "Juan Pérez"

    # 4. Modificación (conserva id, creado_en y saldo; refresca actualizado_en)
    resp_mod = cliente.put(
        f"/api/choferes/{chofer_id}",
        json={"nombre_completo": "Juan C. Pérez", "telefono": "351 999 8888"},
        headers=admin,
    )
    assert resp_mod.status_code == 200
    modificado = resp_mod.json()
    assert modificado["nombre_completo"] == "Juan C. Pérez"
    assert modificado["telefono"] == "351 999 8888"
    assert modificado["id"] == chofer_id
    assert modificado["creado_en"] == cuerpo["creado_en"]
    assert modificado["saldo_a_favor"] == 0.0
    assert modificado["actualizado_en"] >= cuerpo["actualizado_en"]

    # 5. Baja lógica: 204, desaparece del listado y del detalle, la fila persiste con activo=false
    resp_del = cliente.delete(f"/api/choferes/{chofer_id}", headers=admin)
    assert resp_del.status_code == 204
    assert resp_del.content == b""

    assert cliente.get(f"/api/choferes/{chofer_id}", headers=admin).status_code == 404
    assert cliente.get("/api/choferes", headers=admin).json()["total"] == 0

    fila_baja = (
        sesion_test.execute(
            text("SELECT activo FROM choferes WHERE id = :id"),
            {"id": chofer_id},
        )
        .mappings()
        .first()
    )
    assert fila_baja is not None and fila_baja["activo"] is False

    # Baja repetida → 404
    assert cliente.delete(f"/api/choferes/{chofer_id}", headers=admin).status_code == 404


def test_choferes_api_seguridad_y_reglas(
    cliente: TestClient,
    admin: dict[str, str],
    chofer: dict[str, str],
) -> None:
    # Validaciones de alta (422)
    assert (
        cliente.post(
            "/api/choferes",
            json={"nombre_completo": "  ", "telefono": "351 555 0100"},
            headers=admin,
        ).status_code
        == 422
    )
    assert (
        cliente.post(
            "/api/choferes",
            json={"nombre_completo": "Juan Pérez", "telefono": "123"},
            headers=admin,
        ).status_code
        == 422
    )
    # Teléfono con 20 dígitos separados por espacios: el texto supera VARCHAR(20) y debe
    # rechazarse con 422, no reventar en el INSERT con un 500.
    assert (
        cliente.post(
            "/api/choferes",
            json={
                "nombre_completo": "Juan Pérez",
                "telefono": "1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0",
            },
            headers=admin,
        ).status_code
        == 422
    )
    # No se puede mandar un campo del sistema (extra="forbid")
    assert (
        cliente.post(
            "/api/choferes",
            json={
                "nombre_completo": "Juan Pérez",
                "telefono": "351 555 0100",
                "saldo_a_favor": 999,
            },
            headers=admin,
        ).status_code
        == 422
    )
    assert (
        cliente.post(
            "/api/choferes",
            json={"nombre_completo": "Juan Pérez", "telefono": "351 555 0100", "activo": False},
            headers=admin,
        ).status_code
        == 422
    )

    # Roles: el chofer solo lee (FR-017)
    creado = cliente.post(
        "/api/choferes",
        json={"nombre_completo": "María Gómez", "telefono": "351 555 0200"},
        headers=admin,
    ).json()
    chofer_id = creado["id"]

    assert (
        cliente.post(
            "/api/choferes",
            json={"nombre_completo": "Otro", "telefono": "351 555 0300"},
            headers=chofer,
        ).status_code
        == 403
    )
    assert (
        cliente.put(
            f"/api/choferes/{chofer_id}",
            json={"nombre_completo": "X Y", "telefono": "351 555 0200"},
            headers=chofer,
        ).status_code
        == 403
    )
    assert cliente.delete(f"/api/choferes/{chofer_id}", headers=chofer).status_code == 403
    assert cliente.get("/api/choferes", headers=chofer).status_code == 200
    assert cliente.get(f"/api/choferes/{chofer_id}", headers=chofer).status_code == 200

    # Modificación inexistente → 404 y no crea registros
    assert (
        cliente.put(
            "/api/choferes/9999",
            json={"nombre_completo": "Fantasma", "telefono": "351 555 0100"},
            headers=admin,
        ).status_code
        == 404
    )

    # Baja inexistente → 404
    assert cliente.delete("/api/choferes/9999", headers=admin).status_code == 404
