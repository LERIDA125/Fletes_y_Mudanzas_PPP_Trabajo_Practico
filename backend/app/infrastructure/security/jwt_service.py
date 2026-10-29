"""Emisión y verificación de tokens JWT RFC 7519 con algoritmo fijo HS256 (H9).

Valida firma con `hmac.compare_digest`, rechaza algoritmos distintos a `HS256` y verifica los
claims obligatorios `sub`, `rol` y `exp`.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from app.domain.errores import CredencialesInvalidas


def _b64url_encode(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode("ascii")


def _b64url_decode(texto: str) -> bytes:
    relleno = "=" * (-len(texto) % 4)
    return base64.urlsafe_b64decode((texto + relleno).encode("ascii"))


@dataclass(frozen=True)
class PayloadToken:
    usuario_id: int
    username: str
    rol: str
    id_chofer: int | None
    exp: int


class JWTService:
    ALGORITMO = "HS256"

    def __init__(self, *, secret_key: str, ttl_segundos: int = 1800) -> None:
        if not secret_key or len(secret_key.strip()) < 16:
            raise ValueError("JWT_SECRET debe tener al menos 16 caracteres")
        self._secret = secret_key.encode("utf-8")
        self._ttl_segundos = ttl_segundos

    @property
    def ttl_segundos(self) -> int:
        return self._ttl_segundos

    def emitir(
        self,
        *,
        usuario_id: int,
        username: str,
        rol: str,
        id_chofer: int | None = None,
        ahora: int | None = None,
    ) -> str:
        instante = ahora if ahora is not None else int(time.time())
        header = {"alg": self.ALGORITMO, "typ": "JWT"}
        payload = {
            "sub": str(usuario_id),
            "username": username,
            "rol": rol,
            "id_chofer": id_chofer,
            "iat": instante,
            "exp": instante + self._ttl_segundos,
        }
        segmento_header = _b64url_encode(
            json.dumps(header, separators=(",", ":")).encode("utf-8")
        )
        segmento_payload = _b64url_encode(
            json.dumps(payload, separators=(",", ":")).encode("utf-8")
        )
        mensaje = f"{segmento_header}.{segmento_payload}".encode("ascii")
        firma = hmac.new(self._secret, mensaje, hashlib.sha256).digest()
        return f"{segmento_header}.{segmento_payload}.{_b64url_encode(firma)}"

    def verificar(self, token: str, *, ahora: int | None = None) -> PayloadToken:
        partes = token.strip().split(".")
        if len(partes) != 3:
            raise CredencialesInvalidas("Token de acceso malformado")

        segmento_header, segmento_payload, segmento_firma = partes
        try:
            header = json.loads(_b64url_decode(segmento_header).decode("utf-8"))
            payload = json.loads(_b64url_decode(segmento_payload).decode("utf-8"))
            firma_recibida = _b64url_decode(segmento_firma)
        except Exception as error:
            raise CredencialesInvalidas("Token de acceso inválido") from error

        if not isinstance(header, dict) or header.get("alg") != self.ALGORITMO:
            raise CredencialesInvalidas("Algoritmo de token no permitido")

        mensaje = f"{segmento_header}.{segmento_payload}".encode("ascii")
        firma_esperada = hmac.new(self._secret, mensaje, hashlib.sha256).digest()
        if not hmac.compare_digest(firma_recibida, firma_esperada):
            raise CredencialesInvalidas("Firma de token inválida")

        if not isinstance(payload, dict):
            raise CredencialesInvalidas("Payload de token inválido")

        instante = ahora if ahora is not None else int(time.time())
        exp = payload.get("exp")
        if not isinstance(exp, int) or exp <= instante:
            raise CredencialesInvalidas("El token de acceso ha expirado")

        sub = payload.get("sub")
        rol = payload.get("rol")
        username = payload.get("username", "")
        id_chofer = payload.get("id_chofer")
        if not isinstance(sub, str) or not sub.isdigit() or not isinstance(rol, str):
            raise CredencialesInvalidas("Claims de token inválidos")
        if id_chofer is not None and not isinstance(id_chofer, int):
            raise CredencialesInvalidas("Claim id_chofer inválido")

        return PayloadToken(
            usuario_id=int(sub),
            username=str(username),
            rol=rol,
            id_chofer=id_chofer,
            exp=exp,
        )
