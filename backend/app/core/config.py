import os
import tempfile
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_DB_URL = "postgresql+psycopg://fletes:fletes@localhost:5432/fletes"
_DEFAULT_JWT_SECRET = "fletes-express-dev-secret-key-2026-mvp"


def _es_url_local(url: str) -> bool:
    baja = url.lower()
    return "@localhost" in baja or "@127.0.0.1" in baja


def _normalizar_esquema_postgres(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _buscar_url_postgres_entorno() -> str | None:
    claves_prioritarias = (
        "DATABASE_URL",
        "POSTGRES_URL",
        "POSTGRES_URL_NON_POOLING",
        "NEON_DATABASE_URL",
        "POSTGRES_PRISMA_URL",
        "STORAGE_URL",
        "STORAGE_DATABASE_URL",
    )
    for clave in claves_prioritarias:
        valor = (os.environ.get(clave) or "").strip()
        if valor and not _es_url_local(valor):
            return _normalizar_esquema_postgres(valor)

    for clave, valor in os.environ.items():
        limpio = (valor or "").strip()
        if (
            limpio.startswith(("postgres://", "postgresql://", "postgresql+psycopg://"))
            and not _es_url_local(limpio)
            and "TEST" not in clave.upper()
        ):
            return _normalizar_esquema_postgres(limpio)
    return None


def url_sqlite_respaldo() -> str:
    ruta = Path(tempfile.gettempdir()) / "fletes_express_mvp_v2.db"
    return f"sqlite:///{ruta.as_posix()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = _DEFAULT_DB_URL
    ENVIRONMENT: str = "dev"
    DEV_ASSUME_ADMIN: bool = False
    JWT_SECRET: str = _DEFAULT_JWT_SECRET
    JWT_TTL_SECONDS: int = 1800
    # Orígenes del navegador autorizados a llamar a la API. En desarrollo es el
    # Next.js local; en producción se setea por variable de entorno con la URL
    # real del frontend.
    ORIGENES_CORS: list[str] = ["http://localhost:3000"]

    @model_validator(mode="after")
    def _resolver_configuracion_entorno(self) -> "Settings":
        candidato = (self.DATABASE_URL or "").strip()
        if not candidato or _es_url_local(candidato):
            remota = _buscar_url_postgres_entorno()
            if remota:
                candidato = remota
            elif any(
                os.environ.get(k)
                for k in ("VERCEL", "VERCEL_ENV", "VERCEL_URL", "AWS_LAMBDA_FUNCTION_NAME")
            ):
                candidato = url_sqlite_respaldo()
        self.DATABASE_URL = _normalizar_esquema_postgres(candidato or _DEFAULT_DB_URL)

        secreto = (self.JWT_SECRET or "").strip()
        self.JWT_SECRET = secreto if secreto else _DEFAULT_JWT_SECRET
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
