"""Tests unitarios de aplicación de autenticación y alta de usuarios (H9)."""

import pytest

from app.application.autenticacion.gestor_autenticacion import GestorAutenticacion
from app.application.usuarios.gestor_usuarios import GestorUsuarios
from app.domain.errores import (
    ChoferInvalido,
    ChoferYaVinculado,
    CredencialesInvalidas,
    DatoInvalido,
    UsernameDuplicado,
)
from app.domain.usuario import Usuario
from tests.unit.application.usuarios.fakes import FakeUsuarioRepo

PASSWORD = "una-clave-segura-123"


def _gestor_autenticacion(repo: FakeUsuarioRepo) -> GestorAutenticacion:
    return GestorAutenticacion(
        repo,
        verificar=lambda password, hash_guardado: password == "correcta",
        emitir_token=lambda **datos: f"token-{datos['usuario_id']}",
    )


def test_autenticacion_valida_y_registra_ultimo_acceso() -> None:
    repo = FakeUsuarioRepo()
    admin = repo.agregar(Usuario.crear(username="Admin", rol="ADMIN"), password_hash="hash")
    gestor = _gestor_autenticacion(repo)

    token = gestor.autenticar(username="  ADMIN ", password="correcta")

    assert token.access_token == f"token-{admin.id}"
    assert token.expires_in > 0
    assert repo.llamadas_acceso and repo.llamadas_acceso[0][0] == admin.id


def test_login_falla_igual_para_usuario_inexistente_password_incorrecta_o_inactivo() -> None:
    repo = FakeUsuarioRepo()
    repo.agregar(Usuario.crear(username="admin", rol="ADMIN"), password_hash="hash")
    inactivo = repo.agregar(
        Usuario(username="inactivo", rol="ADMIN", activo=False),
        password_hash="hash",
    )
    gestor = _gestor_autenticacion(repo)

    for username, password in [
        ("no-existe", "correcta"),
        ("admin", "incorrecta"),
        ("inactivo", "correcta"),
    ]:
        with pytest.raises(CredencialesInvalidas) as error:
            gestor.autenticar(username=username, password=password)
        assert str(error.value) == "Credenciales inválidas o cuenta no habilitada"

    assert inactivo.id is not None
    assert not any(usuario_id == inactivo.id for usuario_id, _ in repo.llamadas_acceso)


def test_login_de_chofer_exige_chofer_activo() -> None:
    repo = FakeUsuarioRepo()
    repo.agregar(
        Usuario.crear(username="chofer1", rol="CHOFER", id_chofer=10),
        password_hash="hash",
        chofer_activo=False,
    )
    gestor = _gestor_autenticacion(repo)

    with pytest.raises(CredencialesInvalidas):
        gestor.autenticar(username="chofer1", password="correcta")


def test_alta_de_usuarios_valida_rol_chofer_duplicados_y_password() -> None:
    repo = FakeUsuarioRepo()
    repo.marcar_chofer_activo(10)
    gestor = GestorUsuarios(repo)

    admin = gestor.registrar(
        username="  Admin.Nuevo ",
        password=PASSWORD,
        rol="admin",
        id_chofer=None,
        creado_por=1,
    )
    assert admin.username == "admin.nuevo"
    assert admin.rol == "ADMIN"
    assert admin.creado_por == 1

    chofer = gestor.registrar(
        username="chofer.10",
        password=PASSWORD,
        rol="CHOFER",
        id_chofer=10,
        creado_por=admin.id,
    )
    assert chofer.rol == "CHOFER"
    assert chofer.id_chofer == 10

    with pytest.raises(UsernameDuplicado):
        gestor.registrar(
            username="ADMIN.NUEVO",
            password=PASSWORD,
            rol="ADMIN",
            id_chofer=None,
            creado_por=1,
        )

    with pytest.raises(ChoferYaVinculado):
        gestor.registrar(
            username="otro.chofer",
            password=PASSWORD,
            rol="CHOFER",
            id_chofer=10,
            creado_por=admin.id,
        )

    with pytest.raises(ChoferInvalido):
        gestor.registrar(
            username="chofer.inactivo",
            password=PASSWORD,
            rol="CHOFER",
            id_chofer=99,
            creado_por=admin.id,
        )

    with pytest.raises(DatoInvalido):
        gestor.registrar(
            username="admin.con.chofer",
            password=PASSWORD,
            rol="ADMIN",
            id_chofer=10,
            creado_por=admin.id,
        )

    with pytest.raises(DatoInvalido):
        gestor.registrar(
            username="password.corta",
            password="corta",
            rol="ADMIN",
            id_chofer=None,
            creado_por=admin.id,
        )
