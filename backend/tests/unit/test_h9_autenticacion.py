"""Tests unitarios y de API para Autenticación JWT, Multi-Admin y Creación de Usuarios (H9)."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.infrastructure.models  # noqa: F401
from app.application.autenticacion.gestor_autenticacion import GestorAutenticacion
from app.core.dependencias import get_db
from app.domain.errores import CredencialesInvalidas, DatoInvalido
from app.domain.usuario import Usuario
from app.infrastructure.db.base import Base
from app.infrastructure.repositories.usuario_repo import UsuarioRepo
from app.infrastructure.security.jwt_service import JWTService
from app.infrastructure.security.password_hasher import PasswordHasher
from app.main import app


def test_h9_dominio_y_seguridad_jwt_scrypt() -> None:
    hasher = PasswordHasher()
    hash_1 = hasher.hashear("SecretoSeguro123")
    hash_2 = hasher.hashear("SecretoSeguro123")
    assert hash_1 != hash_2
    assert hasher.verificar("SecretoSeguro123", hash_1) is True
    assert hasher.verificar("ClaveIncorrecta", hash_1) is False

    u_admin = Usuario.crear(
        username="  Admin_Principal  ",
        password_hash=hash_1,
        rol="admin",
        creado_por_id=1,
    )
    assert u_admin.username == "admin_principal"
    assert u_admin.rol == "admin"
    assert u_admin.id_chofer is None
    assert u_admin.creado_por_id == 1

    with pytest.raises(DatoInvalido):
        Usuario.crear(username="admin2", password_hash=hash_1, rol="admin", id_chofer=5)

    with pytest.raises(DatoInvalido):
        Usuario.crear(username="chofer1", password_hash=hash_1, rol="chofer", id_chofer=None)

    jwt = JWTService(secret_key="clave-secreta-de-prueba-muy-larga", ttl_segundos=1800)
    token = jwt.emitir(usuario_id=7, username="chofer_juan", rol="chofer", id_chofer=10, ahora=1000)
    payload = jwt.verificar(token, ahora=1500)
    assert payload.usuario_id == 7
    assert payload.username == "chofer_juan"
    assert payload.rol == "chofer"
    assert payload.id_chofer == 10

    with pytest.raises(CredencialesInvalidas):
        jwt.verificar(token, ahora=3000)

    with pytest.raises(CredencialesInvalidas):
        jwt.verificar(token + "manipulado", ahora=1500)


@pytest.fixture
def cliente_auth() -> Generator[tuple[TestClient, Session], None, None]:
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
            yield cliente, sesion
    finally:
        app.dependency_overrides.pop(get_db, None)
        sesion.close()
        engine.dispose()


def test_h9_api_login_multi_admin_y_usuario_chofer(
    cliente_auth: tuple[TestClient, Session],
) -> None:
    cliente, sesion = cliente_auth
    gestor = GestorAutenticacion(
        repositorio_usuarios=UsuarioRepo(sesion),
        hasher=PasswordHasher(),
        tokens=JWTService(secret_key="fletes-express-dev-secret-key-2026-mvp"),
    )
    admin_1 = gestor.crear_usuario(username="dueno1", password="Password123", rol="admin")
    assert admin_1.id == 1

    # 1. Login de Dueño 1
    resp_login = cliente.post(
        "/api/auth/login",
        json={"username": "DUENO1", "password": "Password123"},
    )
    assert resp_login.status_code == 200
    token_admin_1 = resp_login.json()["access_token"]
    headers_admin_1 = {"Authorization": f"Bearer {token_admin_1}"}

    # Login fallido devuelve 401
    assert (
        cliente.post(
            "/api/auth/login",
            json={"username": "dueno1", "password": "MalPassword"},
        ).status_code
        == 401
    )

    # 2. Dueño 1 crea a Dueño 2 (Multi-Admin)
    resp_admin_2 = cliente.post(
        "/api/auth/usuarios",
        headers=headers_admin_1,
        json={"username": "dueno2", "password": "Password456", "rol": "admin"},
    )
    assert resp_admin_2.status_code == 201
    datos_admin_2 = resp_admin_2.json()
    assert datos_admin_2["rol"] == "admin"
    assert datos_admin_2["creado_por_id"] == 1

    # 3. Dueño 2 inicia sesión y registra un chofer + su usuario de acceso
    login_admin_2 = cliente.post(
        "/api/auth/login",
        json={"username": "dueno2", "password": "Password456"},
    )
    assert login_admin_2.status_code == 200
    headers_admin_2 = {"Authorization": f"Bearer {login_admin_2.json()['access_token']}"}

    resp_chofer = cliente.post(
        "/api/choferes",
        headers=headers_admin_2,
        json={"nombre_completo": "Carlos Gómez", "telefono": "351 555 0199"},
    )
    assert resp_chofer.status_code == 201
    chofer_id = resp_chofer.json()["id"]

    resp_user_chofer = cliente.post(
        "/api/auth/usuarios",
        headers=headers_admin_2,
        json={
            "username": "carlos.chofer",
            "password": "ChoferPass123",
            "rol": "chofer",
            "id_chofer": chofer_id,
        },
    )
    assert resp_user_chofer.status_code == 201
    assert resp_user_chofer.json()["id_chofer"] == chofer_id
    assert resp_user_chofer.json()["creado_por_id"] == datos_admin_2["id"]

    # No permite crear segundo usuario para el mismo chofer (409)
    assert (
        cliente.post(
            "/api/auth/usuarios",
            headers=headers_admin_2,
            json={
                "username": "otro.carlos",
                "password": "ChoferPass123",
                "rol": "chofer",
                "id_chofer": chofer_id,
            },
        ).status_code
        == 409
    )

    # 4. El chofer inicia sesión con el usuario que le creó el administrador
    login_chofer = cliente.post(
        "/api/auth/login",
        json={"username": "carlos.chofer", "password": "ChoferPass123"},
    )
    assert login_chofer.status_code == 200
    headers_chofer = {"Authorization": f"Bearer {login_chofer.json()['access_token']}"}

    perfil_chofer = cliente.get("/api/auth/me", headers=headers_chofer)
    assert perfil_chofer.status_code == 200
    assert perfil_chofer.json()["rol"] == "chofer"
    assert perfil_chofer.json()["id_chofer"] == chofer_id

    # 5. El chofer NO puede crear otros choferes ni cuentas de usuario (403 Forbidden)
    assert (
        cliente.post(
            "/api/choferes",
            headers=headers_chofer,
            json={"nombre_completo": "Intruso", "telefono": "351 555 0999"},
        ).status_code
        == 403
    )
    assert (
        cliente.post(
            "/api/auth/usuarios",
            headers=headers_chofer,
            json={"username": "intruso", "password": "Password123", "rol": "admin"},
        ).status_code
        == 403
    )



def test_h9_trazabilidad_y_auditoria_multi_admin(
    cliente_auth: tuple[TestClient, Session],
) -> None:
    cliente, sesion = cliente_auth
    gestor = GestorAutenticacion(
        repositorio_usuarios=UsuarioRepo(sesion),
        hasher=PasswordHasher(),
        tokens=JWTService(secret_key="fletes-express-dev-secret-key-2026-mvp"),
    )
    admin_a = gestor.crear_usuario(username="admin_a", password="Password123", rol="admin")
    admin_b = gestor.crear_usuario(username="admin_b", password="Password456", rol="admin")
    assert admin_a.id == 1 and admin_b.id == 2

    token_a = cliente.post(
        "/api/auth/login", json={"username": "admin_a", "password": "Password123"}
    ).json()["access_token"]
    token_b = cliente.post(
        "/api/auth/login", json={"username": "admin_b", "password": "Password456"}
    ).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Admin A crea registros -> creado_por_id=1, modificado_por_id=1
    c_resp = cliente.post(
        "/api/clientes",
        headers=headers_a,
        json={
            "razon_social": "Logística Austral S.A.",
            "telefono": "351 444 5566",
            "direccion_habitual": "Av. Sabattini 2500",
            "tiene_cuenta_corriente": True,
        },
    ).json()
    assert c_resp["creado_por_id"] == 1
    assert c_resp["modificado_por_id"] == 1

    t_resp = cliente.post(
        "/api/tipos-vehiculo",
        headers=headers_a,
        json={
            "descripcion": "Camión Chasis",
            "capacidad_carga_kg": 3500,
            "tarifa_hora_base": 8000,
            "tarifa_km_excedente": 350,
        },
    ).json()
    assert t_resp["creado_por_id"] == 1
    assert t_resp["modificado_por_id"] == 1

    ch_resp = cliente.post(
        "/api/choferes",
        headers=headers_a,
        json={"nombre_completo": "Pedro Sosa", "telefono": "351 777 8899"},
    ).json()
    assert ch_resp["creado_por_id"] == 1
    assert ch_resp["modificado_por_id"] == 1

    v_resp = cliente.post(
        "/api/vehiculos",
        headers=headers_a,
        json={
            "patente": "AF 123 BCD",
            "id_tipo_vehiculo": t_resp["id"],
            "id_chofer_habitual": ch_resp["id"],
        },
    ).json()
    assert v_resp["creado_por_id"] == 1
    assert v_resp["modificado_por_id"] == 1

    s_resp = cliente.post(
        "/api/servicios",
        headers=headers_a,
        json={
            "id_cliente": c_resp["id"],
            "id_tipo_vehiculo": t_resp["id"],
            "id_chofer": ch_resp["id"],
            "id_vehiculo": v_resp["id"],
            "fecha": "2026-11-10",
            "horas_estimadas": 3,
            "distancia_ida_km": 12,
        },
    ).json()
    assert s_resp["creado_por_id"] == 1
    assert s_resp["modificado_por_id"] == 1

    # 2. Admin B modifica registros -> creado_por_id=1, modificado_por_id=2
    c_mod = cliente.put(
        f"/api/clientes/{c_resp['id']}",
        headers=headers_b,
        json={
            "razon_social": "Logística Austral S.R.L.",
            "telefono": "351 444 5566",
            "direccion_habitual": "Av. Sabattini 2600",
            "tiene_cuenta_corriente": False,
        },
    ).json()
    assert c_mod["creado_por_id"] == 1
    assert c_mod["modificado_por_id"] == 2

    s_mod = cliente.patch(
        f"/api/servicios/{s_resp['id_servicio']}/estado",
        headers=headers_b,
        json={"estado": "confirmado"},
    ).json()
    assert s_mod["creado_por_id"] == 1
    assert s_mod["modificado_por_id"] == 2
