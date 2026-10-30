from __future__ import annotations

ROL_ADMIN = "ADMIN"
ROL_CHOFER = "CHOFER"
ROLES_VALIDOS = frozenset({ROL_ADMIN, ROL_CHOFER})


def normalizar_rol(codigo: str) -> str:
    """Normaliza el código de rol al formato canónico persistido y expuesto por la API."""
    return codigo.strip().upper()
