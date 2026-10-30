import pytest

from app.domain.errores import DatoInvalido
from app.domain.usuario import Usuario, validar_password


def test_usuario_normaliza_username_y_rol() -> None:
    usuario = Usuario(id=1, username="  Admin ", rol="admin")

    assert usuario.username == "admin"
    assert usuario.rol == "ADMIN"
    assert usuario.rol_minusculas == "admin"


def test_usuario_chofer_requiere_chofer() -> None:
    with pytest.raises(DatoInvalido):
        Usuario(id=1, username="chofer1", rol="CHOFER")


def test_usuario_admin_no_puede_tener_chofer() -> None:
    with pytest.raises(DatoInvalido):
        Usuario(id=1, username="admin", rol="ADMIN", id_chofer=5)


def test_usuario_rechaza_rol_desconocido() -> None:
    with pytest.raises(DatoInvalido):
        Usuario(id=1, username="usuario", rol="SUPERVISOR")


def test_password_respeta_politica_minima() -> None:
    validar_password("una-clave-segura-123", "admin")

    with pytest.raises(DatoInvalido):
        validar_password("corta", "admin")

    with pytest.raises(DatoInvalido):
        validar_password("ADMINISTRADOR", "administrador")
