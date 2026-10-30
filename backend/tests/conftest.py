import os

import pytest

os.environ["ENVIRONMENT"] = "dev"
os.environ["DEV_ASSUME_ADMIN"] = "true"
os.environ["JWT_SECRET"] = "test-only-secret-change-me-32-bytes-min"


@pytest.fixture(scope="session", autouse=True)
def _limpiar_cache_de_settings() -> None:
    """Evita que una configuración cacheada contamine otros tests."""
    from app.core.config import get_settings

    get_settings.cache_clear()
