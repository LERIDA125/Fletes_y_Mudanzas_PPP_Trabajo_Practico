from decimal import Decimal

from fastapi.testclient import TestClient


def test_servicios_api_cotiza_crea_y_lista_en_postgresql(
    cliente: TestClient,
    admin: dict[str, str],
    datos_cliente: dict[str, object],
) -> None:
    respuesta_cliente = cliente.post("/api/clientes", json=datos_cliente, headers=admin)
    assert respuesta_cliente.status_code == 201
    cliente_id = respuesta_cliente.json()["id"]

    respuesta_tipo = cliente.post(
        "/api/tipos-vehiculo",
        headers=admin,
        json={
            "descripcion": "Camioneta Servicio Integracion",
            "capacidad_carga_kg": 1500,
            "tarifa_hora_base": 3000,
            "tarifa_km_excedente": 150,
        },
    )
    assert respuesta_tipo.status_code == 201
    tipo_id = respuesta_tipo.json()["id"]

    entrada_cotizacion = {
        "id_tipo_vehiculo": tipo_id,
        "horas_estimadas": 2,
        "distancia_ida_km": 15,
    }
    respuesta_cotizacion = cliente.post(
        "/api/servicios/cotizar",
        json=entrada_cotizacion,
        headers=admin,
    )
    assert respuesta_cotizacion.status_code == 200
    assert Decimal(respuesta_cotizacion.json()["precio_final"]) == Decimal("9000.00")

    respuesta_servicio = cliente.post(
        "/api/servicios",
        json={
            **entrada_cotizacion,
            "id_cliente": cliente_id,
            "fecha": "2026-10-25",
        },
        headers=admin,
    )
    assert respuesta_servicio.status_code == 201
    servicio = respuesta_servicio.json()
    assert servicio["estado"] == "pendiente"
    assert servicio["razon_social_cliente"] == datos_cliente["razon_social"]
    assert Decimal(servicio["precio_total"]) == Decimal("9000.00")

    respuesta_listado = cliente.get("/api/servicios?page=1&size=10", headers=admin)
    assert respuesta_listado.status_code == 200
    assert respuesta_listado.json()["total"] == 1
    assert respuesta_listado.json()["items"][0]["id_servicio"] == servicio["id_servicio"]

    respuesta_manipulada = cliente.post(
        "/api/servicios",
        json={
            **entrada_cotizacion,
            "id_cliente": cliente_id,
            "fecha": "2026-10-25",
            "precio_total": 1,
        },
        headers=admin,
    )
    assert respuesta_manipulada.status_code == 422

    ruta_cancelacion = f"/api/servicios/{servicio['id_servicio']}/cancelar"
    sin_motivo = cliente.patch(ruta_cancelacion, json={"motivo": "   "}, headers=admin)
    assert sin_motivo.status_code == 422

    cancelacion = cliente.patch(
        ruta_cancelacion,
        json={"motivo": "  El cliente reprogramó el viaje  "},
        headers=admin,
    )
    assert cancelacion.status_code == 200
    cancelado = cancelacion.json()
    assert cancelado["estado"] == "cancelado"
    assert cancelado["motivo_cancelacion"] == "El cliente reprogramó el viaje"
    assert cancelado["hora_fin"] is not None

    repetida = cliente.patch(
        ruta_cancelacion,
        json={"motivo": "Segundo intento"},
        headers=admin,
    )
    assert repetida.status_code == 409

    inexistente = cliente.patch(
        "/api/servicios/999999/cancelar",
        json={"motivo": "No existe"},
        headers=admin,
    )
    assert inexistente.status_code == 404

    listado_cancelado = cliente.get("/api/servicios?page=1&size=10", headers=admin)
    item_cancelado = listado_cancelado.json()["items"][0]
    assert item_cancelado["estado"] == "cancelado"
    assert item_cancelado["motivo_cancelacion"] == "El cliente reprogramó el viaje"
    assert item_cancelado["hora_fin"] is not None
