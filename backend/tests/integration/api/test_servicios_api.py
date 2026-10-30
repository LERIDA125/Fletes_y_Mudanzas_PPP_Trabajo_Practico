from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.seguridad import crear_token_acceso
from app.infrastructure.models.rol import RolORM
from app.infrastructure.models.usuario import UsuarioORM


def test_chofer_solo_lista_servicios_asignados(
    cliente: TestClient,
    sesion_test: Session,
    datos_cliente: dict[str, object],
) -> None:
    rol_admin = RolORM(codigo="ADMIN", descripcion="Administrador")
    rol_chofer = RolORM(codigo="CHOFER", descripcion="Chofer")
    sesion_test.add_all([rol_admin, rol_chofer])
    sesion_test.flush()

    usuario_admin = UsuarioORM(
        username="admin.servicios",
        password_hash="hash",
        rol_id=rol_admin.id,
    )
    sesion_test.add(usuario_admin)
    sesion_test.commit()
    sesion_test.refresh(usuario_admin)

    token_admin = crear_token_acceso(
        usuario_id=usuario_admin.id,
        username=usuario_admin.username,
        rol="ADMIN",
    )
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    respuesta_cliente = cliente.post(
        "/api/clientes",
        json=datos_cliente,
        headers=headers_admin,
    )
    assert respuesta_cliente.status_code == 201
    cliente_id = respuesta_cliente.json()["id"]

    respuesta_tipo = cliente.post(
        "/api/tipos-vehiculo",
        headers=headers_admin,
        json={
            "descripcion": "Furgón para chofer",
            "capacidad_carga_kg": 1000,
            "tarifa_hora_base": 25000,
            "tarifa_km_excedente": 850,
        },
    )
    assert respuesta_tipo.status_code == 201
    tipo_id = respuesta_tipo.json()["id"]

    choferes = []
    for nombre, telefono in [
        ("Chofer asignado", "3515550101"),
        ("Otro chofer", "3515550102"),
    ]:
        respuesta_chofer = cliente.post(
            "/api/choferes",
            headers=headers_admin,
            json={"nombre_completo": nombre, "telefono": telefono},
        )
        assert respuesta_chofer.status_code == 201
        choferes.append(respuesta_chofer.json()["id"])

    for chofer_id in [choferes[0], choferes[0], choferes[1]]:
        respuesta_servicio = cliente.post(
            "/api/servicios",
            headers=headers_admin,
            json={
                "id_cliente": cliente_id,
                "id_tipo_vehiculo": tipo_id,
                "id_chofer": chofer_id,
                "fecha": "2026-10-30",
                "hora_inicio": "09:00:00",
                "horas_estimadas": 2,
                "distancia_ida_km": 15,
            },
        )
        assert respuesta_servicio.status_code == 201

    usuario_chofer = UsuarioORM(
        username="chofer.asignado",
        password_hash="hash",
        rol_id=rol_chofer.id,
        id_chofer=choferes[0],
    )
    sesion_test.add(usuario_chofer)
    sesion_test.commit()
    sesion_test.refresh(usuario_chofer)

    token_chofer = crear_token_acceso(
        usuario_id=usuario_chofer.id,
        username=usuario_chofer.username,
        rol="CHOFER",
    )
    respuesta_chofer = cliente.get(
        f"/api/servicios?page=1&size=1&id_chofer={choferes[1]}",
        headers={"Authorization": f"Bearer {token_chofer}"},
    )

    assert respuesta_chofer.status_code == 200
    assert respuesta_chofer.json()["total"] == 2
    assert len(respuesta_chofer.json()["items"]) == 1
    assert all(item["id_chofer"] == choferes[0] for item in respuesta_chofer.json()["items"])

    respuesta_admin = cliente.get("/api/servicios", headers=headers_admin)
    assert respuesta_admin.status_code == 200
    assert respuesta_admin.json()["total"] == 3


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
