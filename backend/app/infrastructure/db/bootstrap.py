"""Inicialización idempotente del esquema y cuentas por defecto para despliegues Serverless."""

from __future__ import annotations

import logging
import random
import unicodedata
from datetime import date, datetime, time, timedelta
from decimal import Decimal
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
from app.infrastructure.models.cliente import ClienteORM
from app.infrastructure.models.servicio import ServicioORM
from app.infrastructure.models.tipo_vehiculo import TipoVehiculoORM
from app.infrastructure.models.usuario import UsuarioORM
from app.infrastructure.models.vehiculo import VehiculoORM
from app.infrastructure.security.password_hasher import PasswordHasher

logger = logging.getLogger(__name__)

_lock = Lock()
_engines_inicializados: set[int] = set()

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


def _normalizar_texto(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
    return " ".join(sin_acentos.lower().split())


def _poblar_catalogo_inicial_si_vacio(db: Session, admin_id: int | None) -> None:
    if db.query(ChoferORM).count() > 0 or db.query(ClienteORM).count() > 0:
        return

    rng = random.Random(2026)
    tipos_data = [
        ("Furgón Grande", Decimal("25000.00"), Decimal("850.00")),
        ("Camioneta Mediana", Decimal("18000.00"), Decimal("650.00")),
        ("Furgón Chico", Decimal("15000.00"), Decimal("550.00")),
    ]
    db_tipos = [
        TipoVehiculoORM(
            descripcion=desc,
            descripcion_key=_normalizar_texto(desc),
            capacidad_carga_kg=Decimal("1000.00"),
            tarifa_hora_base=tarifa_hora,
            tarifa_km_excedente=tarifa_km,
            activo=True,
            creado_por_id=admin_id,
            modificado_por_id=admin_id,
        )
        for desc, tarifa_hora, tarifa_km in tipos_data
    ]
    db.add_all(db_tipos)
    db.commit()
    for t in db_tipos:
        db.refresh(t)

    nombres_choferes = [
        "Marcelo Rodriguez",
        "El Ruso",
        "Cacho Benitez",
        "Hernan Perez",
        "Sergio Gomez",
        "Daniel Silva",
        "Jorge Medina",
        "Carlos Garcia",
        "Matias Fernandez",
        "Lucas Ramirez",
    ]
    db_choferes = [
        ChoferORM(
            nombre_completo=nombre,
            telefono=f"11-{rng.randint(2000, 7999)}-{rng.randint(1000, 9999)}",
            activo=True,
            creado_por_id=admin_id,
            modificado_por_id=admin_id,
        )
        for nombre in nombres_choferes
    ]
    db.add_all(db_choferes)
    db.commit()
    for c in db_choferes:
        db.refresh(c)

    patentes = ["ABC 123", "DEF 456", "GHI 789", "JKL 321", "MNO 654"]
    db_vehiculos = [
        VehiculoORM(
            patente=patentes[i],
            id_tipo_vehiculo=db_tipos[i % 3].id,
            id_chofer_habitual=db_choferes[i].id,
            activo=True,
            creado_por_id=admin_id,
            modificado_por_id=admin_id,
        )
        for i in range(5)
    ]
    db.add_all(db_vehiculos)
    db.commit()
    for v in db_vehiculos:
        db.refresh(v)

    nombres_clientes = [
        "Muebles Belgrano S.R.L.",
        "Lucia Mendez",
        "Estudio Jurídico Perez & Asoc",
        "Gimnasio Iron",
        "Juan Carlos Gomez",
        "Librería Ateneo",
        "Mecánica Los Hermanos",
        "Verdulería Don José",
        "Ferretería El Tuerca",
        "Bazar Oriental",
    ]
    ahora = datetime.now()
    db_clientes = [
        ClienteORM(
            razon_social=nombre,
            razon_social_key=_normalizar_texto(nombre),
            telefono=f"11-{rng.randint(4000, 6999)}-1111",
            direccion_habitual="Capital Federal",
            tiene_cuenta_corriente=False,
            activo=True,
            creado_por_id=admin_id,
            modificado_por_id=admin_id,
            creado_en=ahora,
            actualizado_en=ahora,
        )
        for nombre in nombres_clientes
    ]
    db.add_all(db_clientes)
    db.commit()
    for cl in db_clientes:
        db.refresh(cl)

    hoy = date.today()
    fechas = [hoy - timedelta(days=1), hoy, hoy, hoy + timedelta(days=1), hoy + timedelta(days=2)]
    horas = [time(8, 0), time(9, 30), time(11, 0), time(14, 0), time(16, 30)]
    for i in range(5):
        veh = db_vehiculos[i]
        db.add(
            ServicioORM(
                id_cliente=db_clientes[i].id,
                id_tipo_vehiculo=veh.id_tipo_vehiculo,
                fecha=fechas[i],
                hora_inicio=horas[i],
                estado="confirmado" if fechas[i] >= hoy else "finalizado",
                id_chofer=veh.id_chofer_habitual,
                id_vehiculo=veh.id,
                horas_estimadas=Decimal("2.50"),
                distancia_ida_km=Decimal("15.00"),
                distancia_total_km=Decimal("30.00"),
                km_franquicia=Decimal("10.00"),
                km_excedente=Decimal("20.00"),
                tarifa_hora_aplicada=Decimal("18000.00"),
                tarifa_km_aplicada=Decimal("650.00"),
                precio_total=Decimal("58000.00"),
                creado_por_id=admin_id,
                modificado_por_id=admin_id,
            )
        )
    db.commit()


def asegurar_esquema_y_usuarios(engine: Engine) -> None:
    """Garantiza tablas, migración de esquema legado en Neon y cuentas iniciales."""
    engine_id = id(engine)
    if engine_id in _engines_inicializados:
        return

    with _lock:
        if engine_id in _engines_inicializados:
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

                _poblar_catalogo_inicial_si_vacio(db, admin.id)

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
                _engines_inicializados.add(engine_id)
        except Exception as exc:
            logger.warning("No se pudo inicializar usuarios por defecto: %s", exc)
            raise
