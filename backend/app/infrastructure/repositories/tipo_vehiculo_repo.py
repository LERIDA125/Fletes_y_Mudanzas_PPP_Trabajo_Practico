from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.errores import DescripcionDuplicada, TipoVehiculoNoEncontrado
from app.domain.tipo_vehiculo import TipoVehiculo, normalizar_descripcion_key
from app.infrastructure.models.tipo_vehiculo import TipoVehiculoORM


def a_dominio(orm: TipoVehiculoORM) -> TipoVehiculo:
    return TipoVehiculo(
        id=orm.id,
        descripcion=orm.descripcion,
        capacidad_carga_kg=orm.capacidad_carga_kg,
        tarifa_hora_base=orm.tarifa_hora_base,
        tarifa_km_excedente=orm.tarifa_km_excedente,
        activo=orm.activo,
        creado_en=orm.creado_en,
        actualizado_en=orm.actualizado_en,
    )


def a_orm(tipo: TipoVehiculo) -> TipoVehiculoORM:
    return TipoVehiculoORM(
        id=tipo.id,
        descripcion=tipo.descripcion,
        descripcion_key=tipo.descripcion_key,
        capacidad_carga_kg=tipo.capacidad_carga_kg,
        tarifa_hora_base=tipo.tarifa_hora_base,
        tarifa_km_excedente=tipo.tarifa_km_excedente,
        activo=tipo.activo,
        creado_en=tipo.creado_en,
        actualizado_en=tipo.actualizado_en,
    )


class TipoVehiculoRepo:
    """Único punto de acceso a PostgreSQL para tipos de vehículo."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def crear(self, tipo: TipoVehiculo) -> TipoVehiculo:
        orm = a_orm(tipo)
        self._db.add(orm)
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            if "descripcion_key" in str(error.orig):
                raise DescripcionDuplicada(tipo.descripcion) from error
            raise
        self._db.refresh(orm)
        return a_dominio(orm)

    def obtener_por_id(self, tipo_id: int) -> TipoVehiculo | None:
        orm = self._db.get(TipoVehiculoORM, tipo_id)
        return a_dominio(orm) if orm is not None else None

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[TipoVehiculo]:
        consulta = (
            self._consulta_filtrada(busqueda)
            .order_by(TipoVehiculoORM.id)
            .offset(offset)
            .limit(limit)
        )
        return [a_dominio(orm) for orm in self._db.scalars(consulta)]

    def contar(self, busqueda: str | None) -> int:
        consulta = self._consulta_filtrada(busqueda).with_only_columns(func.count())
        return self._db.scalar(consulta) or 0

    def actualizar(self, tipo: TipoVehiculo) -> TipoVehiculo:
        orm = self._db.get(TipoVehiculoORM, tipo.id)
        if orm is None:
            raise TipoVehiculoNoEncontrado(tipo.id)
        orm.descripcion = tipo.descripcion
        orm.descripcion_key = tipo.descripcion_key
        orm.capacidad_carga_kg = tipo.capacidad_carga_kg
        orm.tarifa_hora_base = tipo.tarifa_hora_base
        orm.tarifa_km_excedente = tipo.tarifa_km_excedente
        orm.actualizado_en = func.now()
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            if "descripcion_key" in str(error.orig):
                raise DescripcionDuplicada(tipo.descripcion) from error
            raise
        self._db.refresh(orm)
        return a_dominio(orm)

    def desactivar(self, tipo_id: int) -> None:
        self._db.execute(
            update(TipoVehiculoORM).where(TipoVehiculoORM.id == tipo_id).values(activo=False)
        )
        self._db.commit()

    def existe_descripcion(self, descripcion_key: str, excluir_id: int | None = None) -> bool:
        consulta = select(TipoVehiculoORM.id).where(
            TipoVehiculoORM.descripcion_key == descripcion_key
        )
        if excluir_id is not None:
            consulta = consulta.where(TipoVehiculoORM.id != excluir_id)
        return self._db.scalar(consulta.limit(1)) is not None

    def existe_activo(self, tipo_id: int) -> bool:
        consulta = select(TipoVehiculoORM.id).where(
            TipoVehiculoORM.id == tipo_id,
            TipoVehiculoORM.activo.is_(True),
        )
        return self._db.scalar(consulta.limit(1)) is not None

    def _consulta_filtrada(self, busqueda: str | None):
        consulta = select(TipoVehiculoORM).where(TipoVehiculoORM.activo.is_(True))
        if busqueda:
            consulta = consulta.where(
                TipoVehiculoORM.descripcion_key.contains(normalizar_descripcion_key(busqueda))
            )
        return consulta
