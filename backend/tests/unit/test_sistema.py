from fastapi.testclient import TestClient

from app.main import app


def test_health_responde_ok() -> None:
    with TestClient(app) as cliente:
        respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_openapi_se_genera() -> None:
    with TestClient(app) as cliente:
        esquema = cliente.get("/openapi.json").json()

    assert "/health" in esquema["paths"]
