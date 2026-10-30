from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://fletes:fletes@localhost:5432/fletes"
    ENVIRONMENT: str = "dev"
    DEV_ASSUME_ADMIN: bool = False
    JWT_SECRET: SecretStr = SecretStr("")
    JWT_ISSUER: str = "fletes-mudanzas-express"
    # Orígenes del navegador autorizados a llamar a la API. En desarrollo es el
    # Next.js local; en producción se setea por variable de entorno con la URL
    # real del frontend.
    ORIGENES_CORS: list[str] = ["http://localhost:3000"]

    @field_validator("DATABASE_URL")
    @classmethod
    def _usar_driver_psycopg(cls, valor: str) -> str:
        if valor.startswith("postgresql://"):
            return valor.replace("postgresql://", "postgresql+psycopg://", 1)
        return valor

    @model_validator(mode="after")
    def _validar_secreto_jwt(self) -> Settings:
        if self.ENVIRONMENT.strip().lower() not in {"dev", "test", "local"}:
            if not self.JWT_SECRET.get_secret_value():
                raise ValueError("JWT_SECRET es obligatorio fuera de un entorno de desarrollo")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
