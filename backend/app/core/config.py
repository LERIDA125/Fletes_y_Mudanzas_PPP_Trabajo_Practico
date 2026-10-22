from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://fletes:fletes@localhost:5432/fletes"
    ENVIRONMENT: str = "dev"
    DEV_ASSUME_ADMIN: bool = False
    # Orígenes del navegador autorizados a llamar a la API. En desarrollo es el
    # Next.js local; en producción se setea por variable de entorno con la URL
    # real del frontend.
    ORIGENES_CORS: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
