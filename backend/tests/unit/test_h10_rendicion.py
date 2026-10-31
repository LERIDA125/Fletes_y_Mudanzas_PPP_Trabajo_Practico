"""Tests unitarios y de API para Cierre de Viaje, Prueba de Entrega (POD) y Rendición (H10)."""

from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.infrastructure.models  # noqa: F401
from app.application.autenticacion.gestor_autenticacion import GestorAutenticacion
from app.core.dependencias import get_db
from app.infrastructure.db.base import Base
from app.infrastructure.repositories.usuario_repo import UsuarioRepo
from app.infrastructure.security.jwt_service import JWTService
from app.infrastructure.security.password_hasher import PasswordHasher
from app.infrastructure.storage.almacenamiento_remitos import AlmacenamientoRemitosHibrido
from app.main import app

FOTO_PNG_1X1_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)
FOTO_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


def test_h10_almacenamiento_remitos_hibrido_base64() -> None:
    almacen = AlmacenamientoRemitosHibrido(blob_token=None)

    url_desde_bytes = almacen.guardar(
        id_servicio=10,
        contenido=FOTO_PNG_1X1_BYTES,
        content_type="image/png",
        nombre_archivo="remito.png",
    )
    assert url_desde_bytes.startswith("data:image/png;base64,")


@pytest.fixture
def escenario_h10() -> Generator[
    tuple[TestClient, dict[str, str], dict[str, str], int], None, None
]:
    engine: Engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sesion = Session(engine, expire_on_commit=False)

    def obtener_sesion() -> Generator[Session, None, None]:
        yield sesion

    app.dependency_overrides[get_db] = obtener_sesion
    try:
        with TestClient(app) as cliente:
            gestor = GestorAutenticacion(
                repositorio_usuarios=UsuarioRepo(sesion),
                hasher=PasswordHasher(),
                tokens=JWTService(secret_key="fletes-express-dev-secret-key-2026-mvp"),
            )
            gestor.crear_usuario(username="admin", password="Password123", rol="admin")
            token_admin = cliente.post(
                "/api/auth/login", json={"username": "admin", "password": "Password123"}
            ).json()["access_token"]
            headers_admin = {"Authorization": f"Bearer {token_admin}"}

            tipo_id = cliente.post(
                "/api/tipos-vehiculo",
                headers=headers_admin,
                json={
                    "descripcion": "Camión Mudancero",
                    "capacidad_carga_kg": 4000,
                    "tarifa_hora_base": 20000,
                    "tarifa_km_excedente": 900,
                },
            ).json()["id"]
            cliente_id = cliente.post(
                "/api/clientes",
                headers=headers_admin,
                json={
                    "razon_social": "Distribuidora Sur S.R.L.",
                    "telefono": "351 488 9900",
                    "direccion_habitual": "Av. Vélez Sarsfield 4100",
                    "tiene_cuenta_corriente": False,
                },
            ).json()["id"]
            chofer_id = cliente.post(
                "/api/choferes",
                headers=headers_admin,
                json={"nombre_completo": "Martín Pereyra", "telefono": "351 611 2233"},
            ).json()["id"]

            cliente.post(
                "/api/auth/usuarios",
                headers=headers_admin,
                json={
                    "username": "martin.chofer",
                    "password": "ChoferPass123",
                    "rol": "chofer",
                    "id_chofer": chofer_id,
                },
            )
            token_chofer = cliente.post(
                "/api/auth/login",
                json={"username": "martin.chofer", "password": "ChoferPass123"},
            ).json()["access_token"]
            headers_chofer = {"Authorization": f"Bearer {token_chofer}"}

            serv = cliente.post(
                "/api/servicios",
                headers=headers_admin,
                json={
                    "id_cliente": cliente_id,
                    "id_tipo_vehiculo": tipo_id,
                    "id_chofer": chofer_id,
                    "fecha": "2026-11-15",
                    "horas_estimadas": 2,
                    "distancia_ida_km": 10,
                },
            ).json()
            id_servicio = serv["id_servicio"]

            # Confirmar y pasar a 'en curso'
            cliente.patch(
                f"/api/servicios/{id_servicio}/estado",
                headers=headers_admin,
                json={"estado": "confirmado"},
            )
            cliente.patch(
                f"/api/servicios/{id_servicio}/estado",
                headers=headers_chofer,
                json={"estado": "en curso"},
            )

            yield cliente, headers_admin, headers_chofer, id_servicio
    finally:
        app.dependency_overrides.pop(get_db, None)
        sesion.close()
        engine.dispose()


def test_h10_flujo_completo_cierre_pod_multipart_y_aprobacion(
    escenario_h10: tuple[TestClient, dict[str, str], dict[str, str], int],
) -> None:
    cliente, headers_admin, headers_chofer, id_servicio = escenario_h10

    # 1. Bloqueo de cierre sin foto del remito (422)
    sin_foto = cliente.post(
        f"/api/servicios/{id_servicio}/finalizar",
        headers=headers_chofer,
        json={"monto_cobrado_real": "51500.00"},
    )
    assert sin_foto.status_code == 422

    # 2. Cierre exitoso del chofer enviando multipart/form-data con foto y monto real cobrado
    cierre = cliente.post(
        f"/api/servicios/{id_servicio}/finalizar",
        headers=headers_chofer,
        data={"monto_cobrado_real": "51500.00"},
        files={"foto": ("remito_firmado.png", FOTO_PNG_1X1_BYTES, "image/png")},
    )
    assert cierre.status_code == 200
    datos_cierre = cierre.json()
    assert datos_cierre["estado"] == "finalizado"
    assert datos_cierre["estado_rendicion"] == "PENDIENTE"
    assert Decimal(str(datos_cierre["monto_cobrado_real"])) == Decimal("51500.00")
    assert datos_cierre["foto_remito_url"].startswith("data:image/png;base64,")
    assert datos_cierre["hora_fin"] is not None

    # 3. Un chofer NO puede aprobar su propia rendición (403 Forbidden)
    assert (
        cliente.post(
            f"/api/servicios/{id_servicio}/rendicion/aprobar",
            headers=headers_chofer,
        ).status_code
        == 403
    )

    # 4. El administrador observa primero la rendición
    observada = cliente.post(
        f"/api/servicios/{id_servicio}/rendicion/observar",
        headers=headers_admin,
        json={"observacion": "Verificar diferencia de $2.500 por peaje"},
    )
    assert observada.status_code == 200
    assert observada.json()["estado_rendicion"] == "OBSERVADO"
    assert (
        observada.json()["observacion_rendicion"]
        == "Verificar diferencia de $2.500 por peaje"
    )

    # 5. El administrador aprueba la rendición -> RENDIDO y servicio pasa a 'cobrado'
    aprobada = cliente.post(
        f"/api/servicios/{id_servicio}/rendicion/aprobar",
        headers=headers_admin,
    )
    assert aprobada.status_code == 200
    datos_aprobada = aprobada.json()
    assert datos_aprobada["estado_rendicion"] == "RENDIDO"
    assert datos_aprobada["estado"] == "cobrado"
    assert datos_aprobada["rendido_en"] is not None
    assert datos_aprobada["rendido_por_id"] == 1

    # 6. No se puede volver a aprobar ni observar un viaje ya RENDIDO (409 Conflict)
    assert (
        cliente.post(
            f"/api/servicios/{id_servicio}/rendicion/aprobar",
            headers=headers_admin,
        ).status_code
        == 409
    )
