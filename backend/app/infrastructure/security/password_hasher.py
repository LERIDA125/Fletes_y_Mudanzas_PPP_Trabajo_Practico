"""Hashing y verificación de contraseñas resistente a ataques de timing (H9).

Utiliza `hashlib.scrypt` con sal criptográfica aleatoria de 16 bytes (`secrets.token_bytes`) y
comparación en tiempo constante mediante `hmac.compare_digest`.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

_SCRYPT_N = 16384
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_DKLEN = 32


class PasswordHasher:
    def hashear(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        derivada = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=_SCRYPT_N,
            r=_SCRYPT_R,
            p=_SCRYPT_P,
            dklen=_SCRYPT_DKLEN,
        )
        salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
        hash_b64 = base64.urlsafe_b64encode(derivada).decode("ascii")
        return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt_b64}${hash_b64}"

    def verificar(self, password: str, password_hash: str) -> bool:
        try:
            if password_hash.startswith("$argon2"):
                from pwdlib import PasswordHash
                from pwdlib.hashers.argon2 import Argon2Hasher

                return PasswordHash((Argon2Hasher(),)).verify(password, password_hash)

            esquema, n_str, r_str, p_str, salt_b64, hash_b64 = password_hash.split("$")
            if esquema != "scrypt":
                return False
            salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
            esperado = base64.urlsafe_b64decode(hash_b64.encode("ascii"))
            calculado = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt,
                n=int(n_str),
                r=int(r_str),
                p=int(p_str),
                dklen=len(esperado),
            )
            return hmac.compare_digest(calculado, esperado)
        except Exception:
            return False
