"""Inicialización idempotente del esquema y cuentas por defecto para despliegues Serverless."""

from __future__ import annotations

import logging
from threading import Lock

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.infrastructure.db.base import Base
from app.infrastructure.models import (  # noqa: F401
     chofer,
    cliente,
    servicio,
    tipo_vehiculo,
    usuario,
    vehiculo,
)
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.usuario import UsuarioORM
from app.infrastructure.security.password_hasher import PasswordHasher

logger = logging.getLogger(__name__)

_lock = Lock()
_inicializado = False

_TABLAS_AUDITORIA = (
    "usuarios",
    "clientes",
    "choferes",
    "tipos_vehiculo",
    "vehiculos",
    "servicios",
)


def asegurar_esquema_y_usuarios(engine: Engine) -> None:
    """Garantiza tablas, columnas de auditoría y cuentas iniciales si la base está vacía."""
    global _inicializado
    if _inicializado:
        return

    with _lock:
        if _inicializado:
            return
        try:
            Base.metadata.create_all(bind=engine)
            with engine.begin() as conn:
                if conn.dialect.name == "postgresql":
                    for tabla in _TABLAS_AUDITORIA:
                        conn.execute(
                            text(
                                f"ALTER TABLE {tabla} "
                                "ADD COLUMN IF NOT EXISTS creado_por_id INTEGER "
                                "REFERENCES usuarios(id) ON DELETE SET NULL"
                            )
                        )
                        conn.execute(
                            text(
                                f"ALTER TABLE {tabla} "
                                "ADD COLUMN IF NOT EXISTS modificado_por_id INTEGER "
                                "REFERENCES usuarios(id) ON DELETE SET NULL"
                            )
                        )

            with Session(bind=engine) as db:
                total_choferes = db.query(ChoferORM).count()
                total_usuarios = db.query(UsuarioORM).count()

                if total_choferes == 0 and total_usuarios == 0:
                    from scripts.seed import run_seed

                    run_seed()
                else:
                    hasher = PasswordHasher()
                    admin = (
                        db.query(UsuarioORM)
                        .filter(UsuarioORM.username_key == "admin")
                        .one_or_none()
                    )
                    if admin is None:
                        admin = UsuarioORM(
                            username="admin",
                            username_key="admin",
                            password_hash=hasher.hashear("admin1234"),
                            rol="admin",
                            id_chofer=None,
                            activo=True,
                        )
                        db.add(admin)
                        db.commit()
                        db.refresh(admin)

                    admin2 = (
                        db.query(UsuarioORM)
                        .filter(UsuarioORM.username_key == "admin2")
                        .one_or_none()
                    )
                    if admin2 is None:
                        db.add(
                            UsuarioORM(
                                username="admin2",
                                username_key="admin2",
                                password_hash=hasher.hashear("admin1234"),
                                rol="admin",
                                id_chofer=None,
                                activo=True,
                                creado_por_id=admin.id,
                                modificado_por_id=admin.id,
                            )
                        )
                        db.commit()
        except Exception as exc:
            logger.warning("No se pudo ejecutar bootstrap automático de esquema: %s", exc)
        finally:
            _inicializado = True
