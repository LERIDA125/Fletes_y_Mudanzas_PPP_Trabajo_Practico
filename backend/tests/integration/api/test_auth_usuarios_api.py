"""Tests de integración de autenticación y alta de usuarios contra PostgreSQL real (H9)."""

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seguridad import crear_token_acceso, hashear_password
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.rol import RolORM
from app.infrastructure.models.usuario import UsuarioORM

PASSWORD = "una-clave-segura-123"
DETALLE_LOGIN = "Credenciales inválidas o cuenta no habilitada"


@pytest.fixture
def roles(sesion_test: Session) -> dict[str, RolORM]:
    roles: dict[str, RolORM] = {}
    for codigo in ("ADMIN", "CHOFER"):
        rol = RolORM(codigo=codigo, descripcion=f"Rol {codigo}")
        sesion_test.add(rol)
        sesion_test.commit()
        sesion_test.refresh(rol)
        roles[codigo] = rol
    return roles


@pytest.fixture
def crear_usuario(
    sesion_test: Session,
    roles: dict[str, RolORM],
) -> Callable[..., UsuarioORM]:
    def _crear(
        username: str,
        *,
        rol: str = "ADMIN",
        password: str = PASSWORD,
        activo: bool = True,
        id_chofer: int | None = None,
    ) -> UsuarioORM:
        usuario = UsuarioORM(
            username=username,
            password_hash=hashear_password(password),
            rol_id=roles[rol].id,
            id_chofer=id_chofer,
            activo=activo,
        )
        sesion_test.add(usuario)
        sesion_test.commit()
        sesion_test.refresh(usuario)
        return usuario

    return _crear


def _bearer(usuario: UsuarioORM, rol: str = "ADMIN") -> dict[str, str]:
    token = crear_token_acceso(
        usuario_id=usuario.id,
        username=usuario.username,
        rol=rol,
    )
    return {"Authorization": f"Bearer {token}"}


def _login(cliente: TestClient, username: str, password: str = PASSWORD):
    return cliente.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )


def test_login_me_y_ultimo_acceso(
    cliente: TestClient,
    sesion_test: Session,
    crear_usuario: Callable[..., UsuarioORM],
) -> None:
    admin = crear_usuario("admin")

    respuesta = _login(cliente, "  ADMIN ")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["expires_in"] == 1800
    assert cuerpo["access_token"]

    me = cliente.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {cuerpo['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json() == {
        "id": admin.id,
        "username": "admin",
        "rol": "ADMIN",
        "id_chofer": None,
    }
    assert "password_hash" not in me.text

    sesion_test.refresh(admin)
    assert admin.ultimo_acceso is not None


def test_login_falla_generico_para_credenciales_o_cuentas_invalidas(
    cliente: TestClient,
    sesion_test: Session,
    crear_usuario: Callable[..., UsuarioORM],
) -> None:
    crear_usuario("admin")
    crear_usuario("inactivo", activo=False)

    chofer = ChoferORM(nombre_completo="Juan Pérez", telefono="351 555 0100", activo=False)
    sesion_test.add(chofer)
    sesion_test.commit()
    sesion_test.refresh(chofer)
    crear_usuario("chofer.inactivo", rol="CHOFER", id_chofer=chofer.id)

    for username, password in [
        ("no-existe", PASSWORD),
        ("admin", "otra-clave"),
        ("inactivo", PASSWORD),
        ("chofer.inactivo", PASSWORD),
    ]:
        respuesta = _login(cliente, username, password)
        assert respuesta.status_code == 401
        assert respuesta.json() == {"detail": DETALLE_LOGIN}
        assert respuesta.headers["www-authenticate"] == "Bearer"


def test_me_requiere_token_valido(
    cliente: TestClient,
    crear_usuario: Callable[..., UsuarioORM],
) -> None:
    admin = crear_usuario("admin")

    assert cliente.get("/api/auth/me").status_code == 401
    assert cliente.get("/api/auth/me", headers={"Authorization": "Bearer roto"}).status_code == 401
    assert cliente.get("/api/auth/me", headers=_bearer(admin)).status_code == 200


def test_post_usuarios_requiere_admin_autenticado(
    cliente: TestClient,
    sesion_test: Session,
    crear_usuario: Callable[..., UsuarioORM],
) -> None:
    admin = crear_usuario("admin")
    chofer = ChoferORM(nombre_completo="Juan Pérez", telefono="351 555 0100")
    sesion_test.add(chofer)
    sesion_test.commit()
    sesion_test.refresh(chofer)
    usuario_chofer = crear_usuario("chofer1", rol="CHOFER", id_chofer=chofer.id)

    payload = {
        "username": "nuevo.admin",
        "password": PASSWORD,
        "rol": "ADMIN",
        "id_chofer": None,
    }

    assert cliente.post("/api/usuarios", json=payload).status_code == 401

    token_chofer = _login(cliente, usuario_chofer.username).json()["access_token"]
    respuesta = cliente.post(
        "/api/usuarios",
        json=payload,
        headers={"Authorization": f"Bearer {token_chofer}"},
    )
    assert respuesta.status_code == 403

    token_admin = _login(cliente, admin.username).json()["access_token"]
    respuesta = cliente.post(
        "/api/usuarios",
        json=payload,
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert respuesta.status_code == 201
    creado = respuesta.json()
    assert creado["username"] == "nuevo.admin"
    assert creado["rol"] == "ADMIN"
    assert creado["id_chofer"] is None
    assert creado["activo"] is True
    assert creado["creado_por"] == admin.id
    assert "password_hash" not in respuesta.text

    persistido = sesion_test.scalar(
        select(UsuarioORM).where(UsuarioORM.username == "nuevo.admin")
    )
    assert persistido is not None
    assert persistido.password_hash.startswith("$argon2id$")


def test_post_usuarios_valida_chofer_duplicados_y_coherencia(
    cliente: TestClient,
    sesion_test: Session,
    crear_usuario: Callable[..., UsuarioORM],
) -> None:
    admin = crear_usuario("admin")
    headers = {"Authorization": f"Bearer {_login(cliente, admin.username).json()['access_token']}"}

    chofer = ChoferORM(nombre_completo="Juan Pérez", telefono="351 555 0100")
    sesion_test.add(chofer)
    sesion_test.commit()
    sesion_test.refresh(chofer)

    payload_chofer = {
        "username": "juan.perez",
        "password": PASSWORD,
        "rol": "CHOFER",
        "id_chofer": chofer.id,
    }
    assert cliente.post("/api/usuarios", json=payload_chofer, headers=headers).status_code == 201

    duplicado = {
        "username": "ADMIN",
        "password": PASSWORD,
        "rol": "ADMIN",
        "id_chofer": None,
    }
    assert cliente.post("/api/usuarios", json=duplicado, headers=headers).status_code == 409

    chofer_ya_vinculado = {**payload_chofer, "username": "otro.chofer"}
    assert (
        cliente.post("/api/usuarios", json=chofer_ya_vinculado, headers=headers).status_code
        == 409
    )

    chofer_inexistente = {**payload_chofer, "username": "sin.chofer", "id_chofer": 999}
    assert (
        cliente.post("/api/usuarios", json=chofer_inexistente, headers=headers).status_code
        == 422
    )

    admin_con_chofer = {
        "username": "admin.invalido",
        "password": PASSWORD,
        "rol": "ADMIN",
        "id_chofer": chofer.id,
    }
    assert cliente.post("/api/usuarios", json=admin_con_chofer, headers=headers).status_code == 422

    password_corta = {
        "username": "password.corta",
        "password": "corta",
        "rol": "ADMIN",
        "id_chofer": None,
    }
    assert cliente.post("/api/usuarios", json=password_corta, headers=headers).status_code == 422

    assert cliente.post(
        "/api/usuarios",
        json={"username": "campo.extra", "password": PASSWORD, "rol": "ADMIN", "extra": 1},
        headers=headers,
    ).status_code == 422
