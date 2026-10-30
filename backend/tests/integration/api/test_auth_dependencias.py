from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.seguridad import crear_token_acceso, hashear_password
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.rol import RolORM
from app.infrastructure.models.usuario import UsuarioORM

DATOS_CLIENTE = {
    "razon_social": "Distribuidora del Sur S.A.",
    "telefono": "351 555 0100",
    "direccion_habitual": "Av. Colón 1250, Córdoba",
    "tiene_cuenta_corriente": True,
}


def _crear_rol(sesion: Session, codigo: str) -> RolORM:
    rol = RolORM(codigo=codigo, descripcion=f"Rol {codigo}")
    sesion.add(rol)
    sesion.commit()
    sesion.refresh(rol)
    return rol


def _crear_usuario(
    sesion: Session,
    *,
    username: str,
    codigo_rol: str,
    activo: bool = True,
    id_chofer: int | None = None,
    password: str = "una-clave-segura-123",
) -> UsuarioORM:
    rol = _crear_rol(sesion, codigo_rol)
    usuario = UsuarioORM(
        username=username,
        password_hash=hashear_password(password),
        rol_id=rol.id,
        id_chofer=id_chofer,
        activo=activo,
    )
    sesion.add(usuario)
    sesion.commit()
    sesion.refresh(usuario)
    return usuario


def _headers(usuario: UsuarioORM, rol_claim: str | None = None) -> dict[str, str]:
    token = crear_token_acceso(
        usuario_id=usuario.id,
        username=usuario.username,
        rol=rol_claim or "ADMIN",
    )
    return {"Authorization": f"Bearer {token}"}


def test_token_valido_resuelve_rol_admin_desde_la_base(
    cliente: TestClient, sesion_test: Session
) -> None:
    usuario = _crear_usuario(
        sesion_test,
        username="admin",
        codigo_rol="ADMIN",
    )

    respuesta = cliente.post("/api/clientes", json=DATOS_CLIENTE, headers=_headers(usuario))

    assert respuesta.status_code == 201


def test_usuario_inactivo_rechaza_token_vigente(
    cliente: TestClient, sesion_test: Session
) -> None:
    usuario = _crear_usuario(
        sesion_test,
        username="admin",
        codigo_rol="ADMIN",
        activo=False,
    )

    respuesta = cliente.post("/api/clientes", json=DATOS_CLIENTE, headers=_headers(usuario))

    assert respuesta.status_code == 401


def test_rol_del_token_no_escala_permisos(
    cliente: TestClient, sesion_test: Session
) -> None:
    chofer = ChoferORM(nombre_completo="Juan Pérez", telefono="351 555 0100")
    sesion_test.add(chofer)
    sesion_test.commit()
    sesion_test.refresh(chofer)

    usuario = _crear_usuario(
        sesion_test,
        username="chofer1",
        codigo_rol="CHOFER",
        id_chofer=chofer.id,
    )

    respuesta = cliente.post(
        "/api/clientes",
        json=DATOS_CLIENTE,
        headers=_headers(usuario, rol_claim="ADMIN"),
    )

    assert respuesta.status_code == 403


def test_chofer_inactivo_rechaza_token_vigente(
    cliente: TestClient, sesion_test: Session
) -> None:
    chofer = ChoferORM(nombre_completo="Juan Pérez", telefono="351 555 0100", activo=False)
    sesion_test.add(chofer)
    sesion_test.commit()
    sesion_test.refresh(chofer)

    usuario = _crear_usuario(
        sesion_test,
        username="chofer1",
        codigo_rol="CHOFER",
        id_chofer=chofer.id,
    )

    respuesta = cliente.post("/api/clientes", json=DATOS_CLIENTE, headers=_headers(usuario))

    assert respuesta.status_code == 401
