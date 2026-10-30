from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errores import DatoInvalido
from app.domain.rol import ROL_ADMIN, ROL_CHOFER, ROLES_VALIDOS, normalizar_rol

USERNAME_MIN = 3
USERNAME_MAX = 50
PASSWORD_MIN = 12
PASSWORD_MAX = 128


def normalizar_username(username: str) -> str:
    """Normaliza el nombre de usuario para almacenarlo y compararlo sin ambigüedades."""
    return username.strip().casefold()


def validar_password(password: str, username: str) -> None:
    if not PASSWORD_MIN <= len(password) <= PASSWORD_MAX:
        raise DatoInvalido(
            f"La contraseña debe tener entre {PASSWORD_MIN} y {PASSWORD_MAX} caracteres"
        )

    if password.casefold() == normalizar_username(username):
        raise DatoInvalido("La contraseña no puede ser igual al nombre de usuario")


@dataclass(frozen=True)
class Usuario:
    username: str
    rol: str
    id: int | None = None
    activo: bool = True
    id_chofer: int | None = None
    chofer_activo: bool | None = None
    creado_por: int | None = None
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None

    def __post_init__(self) -> None:
        username = normalizar_username(self.username)
        rol = normalizar_rol(self.rol)

        object.__setattr__(self, "username", username)
        object.__setattr__(self, "rol", rol)

        if not USERNAME_MIN <= len(username) <= USERNAME_MAX:
            raise DatoInvalido(
                f"El nombre de usuario debe tener entre {USERNAME_MIN} y {USERNAME_MAX} caracteres"
            )

        if rol not in ROLES_VALIDOS:
            raise DatoInvalido(f"El rol {rol!r} no es válido")

        if rol == ROL_CHOFER and self.id_chofer is None:
            raise DatoInvalido("Un usuario con rol CHOFER debe estar vinculado a un chofer")

        if rol == ROL_ADMIN and self.id_chofer is not None:
            raise DatoInvalido("Un usuario con rol ADMIN no puede estar vinculado a un chofer")

    @classmethod
    def crear(cls, *, username: str, rol: str, id_chofer: int | None = None) -> Usuario:
        return cls(username=username, rol=rol, id_chofer=id_chofer)

    @property
    def rol_minusculas(self) -> str:
        return self.rol.lower()
