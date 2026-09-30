import pytest


@pytest.fixture(scope="session", autouse=True)
def _limpiar_cache_de_settings() -> None:
    """Evita que una configuración cacheada contamine otros tests."""
    from app.core.config import get_settings

    get_settings.cache_clear()
