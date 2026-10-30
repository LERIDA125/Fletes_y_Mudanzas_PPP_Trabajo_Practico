import os
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_DB_URL = "postgresql+psycopg://fletes:fletes@localhost:5432/fletes"
_DEFAULT_JWT_SECRET = "fletes-express-dev-secret-key-2026-mvp"


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

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalizar_database_url(cls, valor: str | None) -> str:
        candidato = (valor or "").strip()
        if not candidato or candidato == _DEFAULT_DB_URL:
            postgres_env = (
                os.environ.get("POSTGRES_URL")
                or os.environ.get("NEON_DATABASE_URL")
                or ""
            ).strip()
            if postgres_env:
                candidato = postgres_env
        if not candidato:
            candidato = _DEFAULT_DB_URL
        if candidato.startswith("postgres://"):
            return candidato.replace("postgres://", "postgresql+psycopg://", 1)
        if candidato.startswith("postgresql://"):
            return candidato.replace("postgresql://", "postgresql+psycopg://", 1)
        return candidato

    @field_validator("JWT_SECRET", mode="before")
    @classmethod
    def _asegurar_jwt_secret(cls, valor: str | None) -> str:
        limpio = (valor or "").strip()
        return limpio if limpio else _DEFAULT_JWT_SECRET


@lru_cache
def get_settings() -> Settings:
    return Settings()
