from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.seguridad import verificar_password
from app.infrastructure.db.base import Base
from app.infrastructure.models.rol import RolORM
from app.infrastructure.models.usuario import UsuarioORM
from scripts import crear_admin


@pytest.fixture
def sesiones_locales() -> Iterator[sessionmaker[Session]]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    sesiones = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with sesiones.begin() as db:
        db.add_all(
            [
                RolORM(codigo="ADMIN", descripcion="Administrador del sistema"),
                RolORM(codigo="CHOFER", descripcion="Chofer de la flota"),
            ]
        )

    yield sesiones
    engine.dispose()


def _preparar_entrada(
    monkeypatch: pytest.MonkeyPatch,
    username: str,
    password: str,
    confirmacion: str,
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: username)
    respuestas = iter([password, confirmacion])
    monkeypatch.setattr(crear_admin, "getpass", lambda _: next(respuestas))


def test_crear_admin_persiste_usuario_con_hash_y_rol_correctos(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    sesiones_locales: sessionmaker[Session],
) -> None:
    monkeypatch.setattr(crear_admin, "SessionLocal", sesiones_locales)
    password = "Clave segura de prueba 123!"
    _preparar_entrada(monkeypatch, "  Primer.Admin ", password, password)

    assert crear_admin.main() == 0
    salida = capsys.readouterr()
    assert "primer.admin" in salida.out
    assert password not in salida.out
    assert password not in salida.err

    with sesiones_locales() as db:
        usuario = db.scalar(select(UsuarioORM))
        rol_admin = db.scalar(select(RolORM).where(RolORM.codigo == "ADMIN"))

    assert usuario is not None
    assert rol_admin is not None
    assert usuario.username == "primer.admin"
    assert usuario.rol_id == rol_admin.id
    assert verificar_password(password, usuario.password_hash)


def test_no_permite_crear_otra_cuenta_admin_por_cli(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    sesiones_locales: sessionmaker[Session],
) -> None:
    monkeypatch.setattr(crear_admin, "SessionLocal", sesiones_locales)
    password = "Clave segura de prueba 123!"
    _preparar_entrada(monkeypatch, "segundo.admin", password, password)

    with sesiones_locales.begin() as db:
        rol_admin = db.scalar(select(RolORM).where(RolORM.codigo == "ADMIN"))
        assert rol_admin is not None
        db.add(
            UsuarioORM(
                username="primer.admin",
                password_hash="hash",
                rol_id=rol_admin.id,
            )
        )

    assert crear_admin.main() == 1
    assert "Ya existe una cuenta ADMIN" in capsys.readouterr().err

    with sesiones_locales() as db:
        usuarios = db.scalars(select(UsuarioORM)).all()
    assert len(usuarios) == 1


def test_password_no_coincidente_no_crea_usuario(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    sesiones_locales: sessionmaker[Session],
) -> None:
    monkeypatch.setattr(crear_admin, "SessionLocal", sesiones_locales)
    _preparar_entrada(monkeypatch, "primer.admin", "Clave segura de prueba 123!", "otra clave")

    assert crear_admin.main() == 1
    assert "no coinciden" in capsys.readouterr().err

    with sesiones_locales() as db:
        assert db.scalar(select(UsuarioORM.id)) is None
