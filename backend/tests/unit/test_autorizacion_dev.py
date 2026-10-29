import pytest
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.dependencias import ROL_ADMIN, get_rol_actual


def test_asume_admin_solo_con_modo_dev_explicito(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "dev")
    monkeypatch.setenv("DEV_ASSUME_ADMIN", "true")
    get_settings.cache_clear()

    try:
        assert get_rol_actual() == ROL_ADMIN
    finally:
        get_settings.cache_clear()


@pytest.mark.parametrize(
    ("environment", "dev_assume_admin"),
    [("dev", "false"), ("production", "true"), ("production", "false")],
)
def test_falla_cerrado_fuera_del_modo_dev_explicito(
    monkeypatch: pytest.MonkeyPatch,
    environment: str,
    dev_assume_admin: str,
) -> None:
    monkeypatch.setenv("ENVIRONMENT", environment)
    monkeypatch.setenv("DEV_ASSUME_ADMIN", dev_assume_admin)
    get_settings.cache_clear()

    try:
        with pytest.raises(HTTPException) as error:
            get_rol_actual("admin")
    finally:
        get_settings.cache_clear()

    assert error.value.status_code == 401
    assert error.value.headers == {"WWW-Authenticate": "Bearer"}
