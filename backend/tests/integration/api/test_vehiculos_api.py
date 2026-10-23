"""Tests de integración unificados de Vehículos y Tipos de Vehículo contra PostgreSQL real (H4).

Comprimido en exactamente 2 tests integrales:
1. `test_vehiculos_api_ciclo_completo_admin`: ciclo CRUD completo de tipos y vehículos.
2. `test_vehiculos_api_seguridad_y_reglas`: roles (admin/chofer), validaciones (422), unicidad (409)
   y bloqueo de baja de tipo con vehículos asociados (409).
"""

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_vehiculos_api_ciclo_completo_admin(
    cliente: TestClient,
    admin: dict[str, str],
    sesion_test: Session,
) -> None:
    # 1. Registrar tipo de vehículo
    payload_tipo = {
        "descripcion": "Camioneta Mediana",
        "capacidad_carga_kg": 1500.0,
        "tarifa_hora_base": 5000.0,
        "tarifa_km_excedente": 250.0,
    }
    resp_tipo = cliente.post("/api/tipos-vehiculo", json=payload_tipo, headers=admin)
    assert resp_tipo.status_code == 201
    tipo_id = resp_tipo.json()["id"]

    # 2. Registrar chofer y vehículo con relaciones para verificar el listado enriquecido
    resp_chofer = cliente.post(
        "/api/choferes",
        json={"nombre_completo": "Juan Pérez", "telefono": "351 555 0100"},
        headers=admin,
    )
    assert resp_chofer.status_code == 201
    chofer_id = resp_chofer.json()["id"]

    payload_vehiculo = {
        "patente": "AA 123 ABC",
        "id_tipo_vehiculo": tipo_id,
        "id_chofer_habitual": chofer_id,
    }
    resp_veh = cliente.post("/api/vehiculos", json=payload_vehiculo, headers=admin)
    assert resp_veh.status_code == 201
    veh_id = resp_veh.json()["id"]

    # Verificación en PostgreSQL
    fila_veh = (
        sesion_test.execute(
            text("SELECT activo, patente FROM vehiculos WHERE id = :id"),
            {"id": veh_id},
        )
        .mappings()
        .first()
    )
    assert fila_veh is not None and fila_veh["activo"] is True
    assert fila_veh["patente"] == "AA 123 ABC"

    # 3. Listados y filtros
    resp_listar_tipos = cliente.get("/api/tipos-vehiculo", headers=admin)
    assert resp_listar_tipos.status_code == 200
    assert any(t["id"] == tipo_id for t in resp_listar_tipos.json()["items"])

    resp_listar_veh = cliente.get("/api/vehiculos?q=AA", headers=admin)
    assert resp_listar_veh.status_code == 200
    vehiculo_listado = next(v for v in resp_listar_veh.json()["items"] if v["id"] == veh_id)
    assert vehiculo_listado["descripcion_tipo_vehiculo"] == "Camioneta Mediana"
    assert vehiculo_listado["capacidad_carga_kg"] == 1500.0
    assert vehiculo_listado["nombre_chofer_habitual"] == "Juan Pérez"

    # La baja lógica del chofer no debe ocultar su nombre en la relación histórica.
    assert cliente.delete(f"/api/choferes/{chofer_id}", headers=admin).status_code == 204
    resp_listar_veh_inactivo = cliente.get("/api/vehiculos?q=AA", headers=admin)
    assert resp_listar_veh_inactivo.json()["items"][0]["nombre_chofer_habitual"] == "Juan Pérez"

    # Un vehículo sin chofer sigue apareciendo y expone null para el dato opcional.
    vehiculo_sin_chofer = cliente.post(
        "/api/vehiculos",
        json={"patente": "AB 456 CDE", "id_tipo_vehiculo": tipo_id, "id_chofer_habitual": None},
        headers=admin,
    )
    assert vehiculo_sin_chofer.status_code == 201
    listado_sin_chofer = cliente.get("/api/vehiculos?q=AB", headers=admin).json()
    item_sin_chofer = next(
        v for v in listado_sin_chofer["items"] if v["id"] == vehiculo_sin_chofer.json()["id"]
    )
    assert item_sin_chofer["nombre_chofer_habitual"] is None

    # 4. Detalle y modificación
    resp_det = cliente.get(f"/api/vehiculos/{veh_id}", headers=admin)
    assert resp_det.status_code == 200
    assert resp_det.json()["patente"] == "AA 123 ABC"

    resp_mod = cliente.put(
        f"/api/vehiculos/{veh_id}",
        json={"patente": "AA 999 XYZ", "id_tipo_vehiculo": tipo_id, "id_chofer_habitual": None},
        headers=admin,
    )
    assert resp_mod.status_code == 200
    assert resp_mod.json()["patente"] == "AA 999 XYZ"

    # 5. Baja lógica de vehículo y luego de tipo
    assert cliente.delete(f"/api/vehiculos/{veh_id}", headers=admin).status_code == 204
    assert cliente.get(f"/api/vehiculos/{veh_id}", headers=admin).status_code == 404
    assert (
        cliente.delete(
            f"/api/vehiculos/{vehiculo_sin_chofer.json()['id']}", headers=admin
        ).status_code
        == 204
    )

    assert cliente.delete(f"/api/tipos-vehiculo/{tipo_id}", headers=admin).status_code == 204
    assert cliente.get(f"/api/tipos-vehiculo/{tipo_id}", headers=admin).status_code == 404


def test_vehiculos_api_seguridad_y_reglas(
    cliente: TestClient,
    admin: dict[str, str],
    chofer: dict[str, str],
) -> None:
    # 1. Crear tipo y vehículo base
    t = cliente.post(
        "/api/tipos-vehiculo",
        json={
            "descripcion": "Furgon Especial",
            "capacidad_carga_kg": 800.0,
            "tarifa_hora_base": 3000.0,
            "tarifa_km_excedente": 150.0,
        },
        headers=admin,
    ).json()
    tid = t["id"]

    v = cliente.post(
        "/api/vehiculos",
        json={"patente": "AF 555 ZZZ", "id_tipo_vehiculo": tid, "id_chofer_habitual": None},
        headers=admin,
    ).json()
    vid = v["id"]

    # 2. Permisos de Chofer
    assert cliente.get("/api/vehiculos", headers=chofer).status_code == 200
    assert cliente.get(f"/api/vehiculos/{vid}", headers=chofer).status_code == 200
    assert (
        cliente.post(
            "/api/vehiculos",
            json={"patente": "AC 111 AAA", "id_tipo_vehiculo": tid, "id_chofer_habitual": None},
            headers=chofer,
        ).status_code
        == 403
    )
    assert cliente.delete(f"/api/vehiculos/{vid}", headers=chofer).status_code == 403

    # 3. Validaciones 422
    assert (
        cliente.post(
            "/api/vehiculos",
            json={"patente": "PATENTE_MAL", "id_tipo_vehiculo": tid, "id_chofer_habitual": None},
            headers=admin,
        ).status_code
        == 422
    )
    assert (
        cliente.post(
            "/api/vehiculos",
            json={"patente": "AC 222 BBB", "id_tipo_vehiculo": 99999, "id_chofer_habitual": None},
            headers=admin,
        ).status_code
        == 422
    )

    # 4. Unicidad 409
    assert (
        cliente.post(
            "/api/tipos-vehiculo",
            json={
                "descripcion": "Furgon Especial",
                "capacidad_carga_kg": 900.0,
                "tarifa_hora_base": 3000.0,
                "tarifa_km_excedente": 150.0,
            },
            headers=admin,
        ).status_code
        == 409
    )
    assert (
        cliente.post(
            "/api/vehiculos",
            json={"patente": "AF 555 ZZZ", "id_tipo_vehiculo": tid, "id_chofer_habitual": None},
            headers=admin,
        ).status_code
        == 409
    )

    # 5. Bloqueo de eliminación de tipo con vehículos activos (409)
    assert cliente.delete(f"/api/tipos-vehiculo/{tid}", headers=admin).status_code == 409
