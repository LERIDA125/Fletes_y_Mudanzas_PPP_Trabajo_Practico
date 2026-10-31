from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.schemas.vehiculo import VehiculoListadoRead
from app.infrastructure.db.base import Base
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.tipo_vehiculo import TipoVehiculoORM
from app.infrastructure.models.vehiculo import VehiculoORM
from app.infrastructure.repositories.vehiculo_repo import VehiculoRepo


def test_listar_enriquece_vehiculos_y_preserva_choferes_opcionales_o_inactivos() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as sesion:
        tipo = TipoVehiculoORM(
            descripcion="Camioneta mediana",
            descripcion_key="camioneta mediana",
            capacidad_carga_kg=Decimal("1500.00"),
            tarifa_hora_base=Decimal("5000.00"),
            tarifa_km_excedente=Decimal("250.00"),
        )
        chofer_inactivo = ChoferORM(
            nombre_completo="Juan Pérez",
            telefono="351 555 0100",
            activo=False,
            saldo_a_favor=Decimal("0.00"),
        )
        sesion.add_all([tipo, chofer_inactivo])
        sesion.flush()

        asignado = VehiculoORM(
            patente="AA 123 ABC",
            id_tipo_vehiculo=tipo.id,
            id_chofer_habitual=chofer_inactivo.id,
            activo=True,
        )
        sin_chofer = VehiculoORM(
            patente="AB 456 CDE",
            id_tipo_vehiculo=tipo.id,
            id_chofer_habitual=None,
            activo=True,
        )
        inactivo = VehiculoORM(
            patente="AC 789 FGH",
            id_tipo_vehiculo=tipo.id,
            id_chofer_habitual=None,
            activo=False,
        )
        sesion.add_all([asignado, sin_chofer, inactivo])
        sesion.commit()

        repo = VehiculoRepo(sesion)
        items = repo.listar(busqueda=None, offset=0, limit=20)

        assert [item.vehiculo.patente for item in items] == ["AA 123 ABC", "AB 456 CDE"]
        assert items[0].descripcion_tipo_vehiculo == "Camioneta mediana"
        assert items[0].capacidad_carga_kg == Decimal("1500.00")
        assert items[0].nombre_chofer_habitual == "Juan Pérez"
        assert items[1].nombre_chofer_habitual is None
        respuesta = VehiculoListadoRead.de_listado(items[0]).model_dump(mode="json")
        assert respuesta["descripcion_tipo_vehiculo"] == "Camioneta mediana"
        assert respuesta["capacidad_carga_kg"] == 1500.0
        assert respuesta["nombre_chofer_habitual"] == "Juan Pérez"
        assert repo.contar(busqueda=None) == 2
        assert repo.contar(busqueda="CDE") == 1

    engine.dispose()
