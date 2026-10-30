from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.core.seguridad import (
    ALGORITMO_JWT,
    TokenInvalido,
    crear_token_acceso,
    decodificar_token,
    hashear_password,
    verificar_password,
)


def test_hash_usa_argon2id_y_verifica_password() -> None:
    hash_guardado = hashear_password("una-clave-segura-123")

    assert hash_guardado.startswith("$argon2id$")
    assert verificar_password("una-clave-segura-123", hash_guardado) is True
    assert verificar_password("otra-clave", hash_guardado) is False


def test_hash_invalido_falla_cerrado() -> None:
    assert verificar_password("una-clave-segura-123", "no-es-un-hash") is False


def test_token_redondea_identidad_y_rol() -> None:
    token = crear_token_acceso(usuario_id=7, username="admin", rol="ADMIN")

    payload = decodificar_token(token)

    assert payload["sub"] == "7"
    assert payload["username"] == "admin"
    assert payload["rol"] == "ADMIN"
    assert payload["iss"] == get_settings().JWT_ISSUER


def test_token_expirado_es_invalido() -> None:
    settings = get_settings()
    ahora = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "7",
            "username": "admin",
            "rol": "ADMIN",
            "iat": ahora - timedelta(minutes=31),
            "exp": ahora - timedelta(minutes=1),
            "iss": settings.JWT_ISSUER,
        },
        settings.JWT_SECRET.get_secret_value(),
        algorithm=ALGORITMO_JWT,
    )

    with pytest.raises(TokenInvalido):
        decodificar_token(token)


def test_token_con_emisor_incorrecto_es_invalido() -> None:
    settings = get_settings()
    ahora = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "7",
            "username": "admin",
            "rol": "ADMIN",
            "iat": ahora,
            "exp": ahora + timedelta(minutes=30),
            "iss": "otro-emisor",
        },
        settings.JWT_SECRET.get_secret_value(),
        algorithm=ALGORITMO_JWT,
    )

    with pytest.raises(TokenInvalido):
        decodificar_token(token)
