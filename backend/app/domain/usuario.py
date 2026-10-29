"""Entidad de dominio `Usuario` e invariantes de identidad y rol (H9).

Reglas puras de dominio:
- `username`: normalizado con `strip().casefold()`, entre 3 y 60 caracteres, sin espacios internos.
- `rol`: `"admin"` (soporta múltiples administradores) o `"chofer"`.
- `id_chofer`: obligatorio cuando `rol == "chofer"`, prohibido (`None`) cuando `rol == "admin"`.
- Incluye campos de auditoría `creado_por_id` y `modificado_por_id`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

from app.domain.errores import DatoInvalido

LONGITUD_MIN_USERNAME: Final[int] = 3
LONGITUD_MAX_USERNAME: Final[int] = 60
LONGITUD_MIN_PASSWORD: Final[int] = 6
ROLES_VALIDOS: Final[tuple[str, ...]] = ("admin", "chofer")


def normalizar_username(username: str) -> str:
    limpio = username.strip().casefold()
    if len(limpio) < LONGITUD_MIN_USERNAME or len(limpio) > LONGITUD_MAX_USERNAME:
        raise DatoInvalido(
            f"El nombre de usuario debe tener entre {LONGITUD_MIN_USERNAME} y "
            f"{LONGITUD_MAX_USERNAME} caracteres"
        )
    if any(ch.isspace() for ch in limpio):
        raise DatoInvalido("El nombre de usuario no puede contener espacios")
    return limpio


def validar_password_en_claro(password: str) -> str:
    if len(password.strip()) < LONGITUD_MIN_PASSWORD:
        raise DatoInvalido(
            f"La contraseña debe tener al menos {LONGITUD_MIN_PASSWORD} caracteres"
        )
    return password


@dataclass
class Usuario:
    username: str
    password_hash: str
    rol: str
    id_chofer: int | None = None
    activo: bool = True
    id: int | None = None
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None
    creado_por_id: int | None = None
    modificado_por_id: int | None = None

    @classmethod
    def crear(
        cls,
        *,
        username: str,
        password_hash: str,
        rol: str,
        id_chofer: int | None = None,
        creado_por_id: int | None = None,
    ) -> Usuario:
        username_norm = normalizar_username(username)
        rol_norm = rol.strip().casefold()
        if rol_norm not in ROLES_VALIDOS:
            raise DatoInvalido(f"El rol {rol!r} no es válido; debe ser 'admin' o 'chofer'")
        if not password_hash or not password_hash.strip():
            raise DatoInvalido("El hash de contraseña no puede estar vacío")

        if rol_norm == "admin" and id_chofer is not None:
            raise DatoInvalido("Una cuenta con rol 'admin' no puede vincularse a un chofer")
        if rol_norm == "chofer" and (id_chofer is None or id_chofer <= 0):
            raise DatoInvalido(
                "Una cuenta con rol 'chofer' debe vincularse a un id_chofer válido"
            )

        return cls(
            username=username_norm,
            password_hash=password_hash,
            rol=rol_norm,
            id_chofer=id_chofer,
            activo=True,
            creado_por_id=creado_por_id,
            modificado_por_id=creado_por_id,
        )

    def desactivar(self, *, modificado_por_id: int | None = None) -> None:
        self.activo = False
        if modificado_por_id is not None:
            self.modificado_por_id = modificado_por_id
