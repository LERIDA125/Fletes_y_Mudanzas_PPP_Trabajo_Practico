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

_USUARIOS_CHOFER_POR_NOMBRE = {
    "marcelo rodriguez": "marcelo",
    "el ruso": "ruso",
    "cacho benitez": "cacho",
    "hernan perez": "hernan",
    "sergio gomez": "sergio",
    "daniel silva": "daniel",
    "jorge medina": "jorge",
    "carlos garcia": "carlos",
    "matias fernandez": "matias",
    "lucas ramirez": "lucas",
}


def asegurar_esquema_y_usuarios(engine: Engine) -> None:
    """Garantiza tablas, migración de esquema legado en Neon y cuentas iniciales."""
    global _inicializado
    if _inicializado:
        return

    with _lock:
        if _inicializado:
            return
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as exc:
            logger.warning("No se pudo ejecutar create_all en bootstrap: %s", exc)

        try:
            with engine.begin() as conn:
                if conn.dialect.name == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE usuarios "
                            "ADD COLUMN IF NOT EXISTS rol VARCHAR(20) NOT NULL DEFAULT 'admin'"
                        )
                    )
                    conn.execute(
                        text(
                            """
                            DO $$
                            BEGIN
                                IF EXISTS (
                                    SELECT 1 FROM information_schema.columns
                                    WHERE table_name = 'usuarios' AND column_name = 'rol_id'
                                ) THEN
                                    IF EXISTS (
                                        SELECT 1 FROM information_schema.tables
                                        WHERE table_name = 'roles'
                                    ) THEN
                                        UPDATE usuarios u
                                        SET rol = LOWER(r.codigo)
                                        FROM roles r
                                        WHERE u.rol_id = r.id;
                                    END IF;
                                    ALTER TABLE usuarios ALTER COLUMN rol_id DROP NOT NULL;
                                END IF;
                            END $$;
                            """
                        )
                    )
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
                    conn.execute(
                        text(
                            """
                            DO $$
                            BEGIN
                                IF EXISTS (
                                    SELECT 1 FROM information_schema.columns
                                    WHERE table_name = 'usuarios' AND column_name = 'creado_por'
                                ) THEN
                                    UPDATE usuarios
                                    SET creado_por_id = creado_por
                                    WHERE creado_por_id IS NULL AND creado_por IS NOT NULL;
                                END IF;
                            END $$;
                            """
                        )
                    )
        except Exception as exc:
            logger.warning("No se pudo migrar columnas en bootstrap: %s", exc)

        try:
            with Session(bind=engine) as db:
                hasher = PasswordHasher()
                admin = (
                    db.query(UsuarioORM)
                    .filter(UsuarioORM.username == "admin")
                    .one_or_none()
                )
                if admin is None:
                    admin = UsuarioORM(
                        username="admin",
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
                    .filter(UsuarioORM.username == "admin2")
                    .one_or_none()
                )
                if admin2 is None:
                    db.add(
                        UsuarioORM(
                            username="admin2",
                            password_hash=hasher.hashear("admin1234"),
                            rol="admin",
                            id_chofer=None,
                            activo=True,
                            creado_por_id=admin.id,
                            modificado_por_id=admin.id,
                        )
                    )
                    db.commit()

                choferes_activos = (
                    db.query(ChoferORM).filter(ChoferORM.activo.is_(True)).all()
                )
                hash_chofer = hasher.hashear("chofer1234")
                for chofer_orm in choferes_activos:
                    clave = " ".join(chofer_orm.nombre_completo.lower().split())
                    username_chofer = _USUARIOS_CHOFER_POR_NOMBRE.get(clave)
                    if not username_chofer:
                        continue
                    existe_usuario = (
                        db.query(UsuarioORM)
                        .filter(
                            (UsuarioORM.username == username_chofer)
                            | (UsuarioORM.id_chofer == chofer_orm.id)
                        )
                        .first()
                    )
                    if existe_usuario is None:
                        db.add(
                            UsuarioORM(
                                username=username_chofer,
                                password_hash=hash_chofer,
                                rol="chofer",
                                id_chofer=chofer_orm.id,
                                activo=True,
                                creado_por_id=admin.id,
                                modificado_por_id=admin.id,
                            )
                        )
                db.commit()
                _inicializado = True
        except Exception as exc:
            logger.warning("No se pudo inicializar usuarios por defecto: %s", exc)
