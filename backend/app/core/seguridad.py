from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import get_settings

ALGORITMO_JWT = "HS256"
DURACION_TOKEN_MINUTOS = 30
DURACION_TOKEN_SEGUNDOS = DURACION_TOKEN_MINUTOS * 60

_password_hash = PasswordHash((Argon2Hasher(),))


class TokenInvalido(Exception):
    """El token no tiene firma válida, expiró o no cumple el contrato esperado."""


class ConfiguracionSeguridadError(RuntimeError):
    """Falta configuración obligatoria para emitir o validar credenciales."""


def hashear_password(password: str) -> str:
    return _password_hash.hash(password)


def verificar_password(password: str, hash_guardado: str) -> bool:
    try:
        return _password_hash.verify(password, hash_guardado)
    except Exception:
        return False


def crear_token_acceso(*, usuario_id: int, username: str, rol: str) -> str:
    ahora = datetime.now(UTC)
    payload = {
        "sub": str(usuario_id),
        "username": username,
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=DURACION_TOKEN_MINUTOS),
        "iss": get_settings().JWT_ISSUER,
    }
    return jwt.encode(payload, _secreto_jwt(), algorithm=ALGORITMO_JWT)


def decodificar_token(token: str) -> dict[str, object]:
    try:
        return jwt.decode(
            token,
            _secreto_jwt(),
            algorithms=[ALGORITMO_JWT],
            issuer=get_settings().JWT_ISSUER,
            options={"require": ["sub", "iat", "exp", "iss"]},
        )
    except ExpiredSignatureError as exc:
        raise TokenInvalido("El token expiró") from exc
    except InvalidTokenError as exc:
        raise TokenInvalido("El token no es válido") from exc


def _secreto_jwt() -> str:
    secreto = get_settings().JWT_SECRET.get_secret_value()
    if not secreto:
        raise ConfiguracionSeguridadError("JWT_SECRET no está configurado")
    return secreto
