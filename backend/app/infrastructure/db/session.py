from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings, url_sqlite_respaldo
from app.infrastructure.db.bootstrap import asegurar_esquema_y_usuarios


def _crear_engine(url: str) -> Engine:
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            future=True,
        )
    return create_engine(url, pool_pre_ping=True, future=True)


engine = _crear_engine(get_settings().DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

_fallback_engine: Engine | None = None
_fallback_session_local: sessionmaker[Session] | None = None


def _obtener_sesion_respaldo() -> Session:
    global _fallback_engine, _fallback_session_local
    if _fallback_engine is None or _fallback_session_local is None:
        _fallback_engine = _crear_engine(url_sqlite_respaldo())
        asegurar_esquema_y_usuarios(_fallback_engine)
        _fallback_session_local = sessionmaker(
            bind=_fallback_engine,
            autoflush=False,
            expire_on_commit=False,
        )
    return _fallback_session_local()


def get_db() -> Generator[Session, None, None]:
    try:
        asegurar_esquema_y_usuarios(engine)
        db = SessionLocal()
    except OperationalError:
        db = _obtener_sesion_respaldo()
    try:
        yield db
    finally:
        db.close()
