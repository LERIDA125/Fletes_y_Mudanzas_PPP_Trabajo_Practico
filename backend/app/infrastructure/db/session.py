from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.infrastructure.db.bootstrap import asegurar_esquema_y_usuarios

engine = create_engine(get_settings().DATABASE_URL, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    asegurar_esquema_y_usuarios(engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
