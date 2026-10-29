from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.vehiculos.puertos import VehiculoListadoItem
from app.domain.errores import PatenteDuplicada, VehiculoNoEncontrado
from app.domain.vehiculo import Vehiculo
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.tipo_vehiculo import TipoVehiculoORM
from app.infrastructure.models.vehiculo import VehiculoORM


def a_dominio(orm: VehiculoORM) -> Vehiculo:
    return Vehiculo(
        id=orm.id,
        patente=orm.patente,
        id_tipo_vehiculo=orm.id_tipo_vehiculo,
        id_chofer_habitual=orm.id_chofer_habitual,
        activo=orm.activo,
        creado_en=orm.creado_en,
        actualizado_en=orm.actualizado_en,
    )


def a_orm(vehiculo: Vehiculo) -> VehiculoORM:
    return VehiculoORM(
        id=vehiculo.id,
        patente=vehiculo.patente,
        id_tipo_vehiculo=vehiculo.id_tipo_vehiculo,
        id_chofer_habitual=vehiculo.id_chofer_habitual,
        activo=vehiculo.activo,
        creado_en=vehiculo.creado_en,
        actualizado_en=vehiculo.actualizado_en,
    )


class VehiculoRepo:
    """Único punto de acceso a PostgreSQL para vehículos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def crear(self, vehiculo: Vehiculo) -> Vehiculo:
        orm = a_orm(vehiculo)
        self._db.add(orm)
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            if "patente" in str(error.orig):
                raise PatenteDuplicada(vehiculo.patente) from error
            raise
        self._db.refresh(orm)
        return a_dominio(orm)

    def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None:
        orm = self._db.get(VehiculoORM, vehiculo_id)
        return a_dominio(orm) if orm is not None else None

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[VehiculoListadoItem]:
        consulta = (
            select(
                VehiculoORM,
                TipoVehiculoORM.descripcion,
                TipoVehiculoORM.capacidad_carga_kg,
                ChoferORM.nombre_completo,
            )
            .join(TipoVehiculoORM, VehiculoORM.id_tipo_vehiculo == TipoVehiculoORM.id)
            .outerjoin(ChoferORM, VehiculoORM.id_chofer_habitual == ChoferORM.id)
            .where(VehiculoORM.activo.is_(True))
        )
        if busqueda:
            consulta = consulta.where(VehiculoORM.patente.contains(busqueda.upper()))
        consulta = consulta.order_by(VehiculoORM.id).offset(offset).limit(limit)

        return [
            VehiculoListadoItem(
                vehiculo=a_dominio(vehiculo),
                descripcion_tipo_vehiculo=descripcion,
                capacidad_carga_kg=capacidad,
                nombre_chofer_habitual=nombre_chofer,
            )
            for vehiculo, descripcion, capacidad, nombre_chofer in self._db.execute(consulta)
        ]

    def contar(self, busqueda: str | None) -> int:
        consulta = self._consulta_filtrada(busqueda).with_only_columns(func.count())
        return self._db.scalar(consulta) or 0

    def listar_activos_por_tipo(self, tipo_vehiculo_id: int) -> list[VehiculoListadoItem]:
        """Catálogo de vehículos activos de un tipo, para la pantalla de Servicios."""
        consulta = (
            select(
                VehiculoORM,
                TipoVehiculoORM.descripcion,
                TipoVehiculoORM.capacidad_carga_kg,
                ChoferORM.nombre_completo,
            )
            .join(TipoVehiculoORM, VehiculoORM.id_tipo_vehiculo == TipoVehiculoORM.id)
            .outerjoin(ChoferORM, VehiculoORM.id_chofer_habitual == ChoferORM.id)
            .where(
                VehiculoORM.activo.is_(True),
                VehiculoORM.id_tipo_vehiculo == tipo_vehiculo_id,
            )
            .order_by(VehiculoORM.patente, VehiculoORM.id)
        )
        return [
            VehiculoListadoItem(
                vehiculo=a_dominio(vehiculo),
                descripcion_tipo_vehiculo=descripcion,
                capacidad_carga_kg=capacidad,
                nombre_chofer_habitual=nombre_chofer,
            )
            for vehiculo, descripcion, capacidad, nombre_chofer in self._db.execute(consulta)
        ]

    def actualizar(self, vehiculo: Vehiculo) -> Vehiculo:
        orm = self._db.get(VehiculoORM, vehiculo.id)
        if orm is None:
            raise VehiculoNoEncontrado(vehiculo.id)
        orm.patente = vehiculo.patente
        orm.id_tipo_vehiculo = vehiculo.id_tipo_vehiculo
        orm.id_chofer_habitual = vehiculo.id_chofer_habitual
        orm.actualizado_en = func.now()
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            if "patente" in str(error.orig):
                raise PatenteDuplicada(vehiculo.patente) from error
            raise
        self._db.refresh(orm)
        return a_dominio(orm)

    def desactivar(self, vehiculo_id: int) -> None:
        self._db.execute(
            update(VehiculoORM).where(VehiculoORM.id == vehiculo_id).values(activo=False)
        )
        self._db.commit()

    def existe_patente(self, patente: str, excluir_id: int | None = None) -> bool:
        consulta = select(VehiculoORM.id).where(VehiculoORM.patente == patente)
        if excluir_id is not None:
            consulta = consulta.where(VehiculoORM.id != excluir_id)
        return self._db.scalar(consulta.limit(1)) is not None

    def tiene_vehiculos(self, tipo_id: int) -> bool:
        consulta = select(VehiculoORM.id).where(
            VehiculoORM.id_tipo_vehiculo == tipo_id,
            VehiculoORM.activo.is_(True),
        )
        return self._db.scalar(consulta.limit(1)) is not None

    def _consulta_filtrada(self, busqueda: str | None):
        consulta = select(VehiculoORM).where(VehiculoORM.activo.is_(True))
        if busqueda:
            consulta = consulta.where(VehiculoORM.patente.contains(busqueda.upper()))
        return consulta
