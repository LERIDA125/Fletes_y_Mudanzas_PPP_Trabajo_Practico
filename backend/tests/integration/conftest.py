"""Infraestructura de los tests de integración contra PostgreSQL real (AGENTS.md §8).

Usa una base de datos propia (`fletes_test`) separada de la de desarrollo, así los tests
nunca tocan los datos reales.
"""

from collections.abc import Generator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.dependencias import get_historial_clientes
from app.infrastructure.db.base import Base
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.cliente_repo import ClienteRepo
from app.main import app

BASE_DATOS_TEST = "fletes_test"


def _url_de_test() -> URL:
    """Devuelve la URL de la base de test conservando la contraseña real.

    Ojo: `str(URL)` la enmascara como `***`, así que hay que pasarle el objeto `URL` entero a
    `create_engine` y nunca convertirlo a texto.
    """
    return make_url(get_settings().DATABASE_URL).set(database=BASE_DATOS_TEST)


@pytest.fixture(scope="session")
def engine_test() -> Iterator[Engine]:
    url_prueba = make_url(get_settings().DATABASE_URL)
    admin = create_engine(
        url_prueba.set(database="postgres"), isolation_level="AUTOCOMMIT", pool_pre_ping=True
    )
    with admin.connect() as conexion:
        existe = conexion.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :nombre"),
            {"nombre": BASE_DATOS_TEST},
        ).scalar()
        if not existe:
            conexion.execute(text(f'CREATE DATABASE "{BASE_DATOS_TEST}"'))
    admin.dispose()

    engine = create_engine(_url_de_test(), pool_pre_ping=True)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sesion_test(engine_test: Engine) -> Iterator[Session]:
    SessionDeTest = sessionmaker(bind=engine_test, autoflush=False, expire_on_commit=False)
    sesion = SessionDeTest()
    try:
        yield sesion
    finally:
        sesion.close()


def _vaciar_todas_las_tablas(sesion: Session) -> None:
    """Deja la base de test vacía y confirma.

    El `commit()` es obligatorio: sin él el DELETE queda en la transacción que revierte el
    `close()` de la sesión, y los datos de un test se filtran al siguiente.
    """
    for tabla in reversed(Base.metadata.sorted_tables):
        sesion.execute(tabla.delete())
    sesion.commit()


@pytest.fixture(autouse=True)
def _limpiar_tablas(sesion_test: Session) -> Iterator[None]:
    # Antes y después: así una corrida anterior que quedó a medias no deja basura que haga fallar
    # un test por un motivo que no es el suyo.
    _vaciar_todas_las_tablas(sesion_test)
    yield
    _vaciar_todas_las_tablas(sesion_test)


@pytest.fixture
def cliente(sesion_test: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: sesion_test
    with TestClient(app) as cliente_http:
        yield cliente_http
    app.dependency_overrides.clear()


@pytest.fixture
def repo_test(sesion_test: Session) -> ClienteRepo:
    return ClienteRepo(sesion_test)


class HistorialSimulado:
    """Doble del puerto `ConsultaHistorialCliente` para probar FR-015 por HTTP.

    La implementación real (`HistorialClienteRepoVacio`) responde "sin historial" para cualquier
    cliente, y la historia de Servicios todavía no existe (llega en H4), así que el `409` de
    FR-015 no se puede alcanzar por un endpoint sin reemplazar esta dependencia.
    """

    def __init__(self) -> None:
        self._clientes_con_historial: set[int] = set()
        self.consultas: list[int] = []

    def tiene_historial(self, cliente_id: int) -> bool:
        self.consultas.append(cliente_id)
        return cliente_id in self._clientes_con_historial

    def marcar_con_historial(self, cliente_id: int) -> None:
        self._clientes_con_historial.add(cliente_id)


@pytest.fixture
def historial_fake(cliente: TestClient) -> Iterator[HistorialSimulado]:
    """Sobreescribe `get_historial_clientes` con un doble mientras dura el test.

    `get_gestor_clientes` consulta el historial a través de este puerto, así que basta con
    reemplazar la dependencia más chica (el historial) y el resto del wiring real queda intacto.
    """
    historial = HistorialSimulado()
    app.dependency_overrides[get_historial_clientes] = lambda: historial
    yield historial
    app.dependency_overrides.pop(get_historial_clientes, None)


@pytest.fixture
def admin() -> dict[str, str]:
    return {"X-Rol": "admin"}


@pytest.fixture
def chofer() -> dict[str, str]:
    return {"X-Rol": "chofer"}


@pytest.fixture
def datos_cliente() -> dict[str, object]:
    return {
        "razon_social": "Distribuidora del Sur S.A.",
        "telefono": "351 555 0100",
        "direccion_habitual": "Av. Colón 1250, Córdoba",
        "tiene_cuenta_corriente": True,
    }
