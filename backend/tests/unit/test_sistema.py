from fastapi.testclient import TestClient

from app.main import app


def test_sistema_health_y_openapi() -> None:
    with TestClient(app) as cliente:
        respuesta = cliente.get("/health")
        assert respuesta.status_code == 200
        assert respuesta.json() == {"estado": "ok"}

        esquema = cliente.get("/openapi.json").json()
        assert "/health" in esquema["paths"]
