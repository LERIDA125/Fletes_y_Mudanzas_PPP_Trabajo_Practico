from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.domain.chofer import Chofer
from app.domain.errores import ChoferNoEncontrado
from app.infrastructure.models.chofer import ChoferORM


def a_dominio(orm: ChoferORM) -> Chofer:
    return Chofer(
        id=orm.id,
        nombre_completo=orm.nombre_completo,
        telefono=orm.telefono,
        activo=orm.activo,
        saldo_a_favor=float(orm.saldo_a_favor),
        creado_en=orm.creado_en,
        actualizado_en=orm.actualizado_en,
    )


def a_orm(chofer: Chofer) -> ChoferORM:
    return ChoferORM(
        id=chofer.id,
        nombre_completo=chofer.nombre_completo,
        telefono=chofer.telefono,
        activo=chofer.activo,
        saldo_a_favor=chofer.saldo_a_favor,
        creado_en=chofer.creado_en,
        actualizado_en=chofer.actualizado_en,
    )


class ChoferRepo:
    """Único punto de acceso a PostgreSQL para choferes."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def crear(self, chofer: Chofer) -> Chofer:
        orm = a_orm(chofer)
        self._db.add(orm)
        self._db.commit()
        self._db.refresh(orm)
        return a_dominio(orm)

    def obtener_por_id(self, chofer_id: int) -> Chofer | None:
        orm = self._db.get(ChoferORM, chofer_id)
        return a_dominio(orm) if orm is not None else None

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[Chofer]:
        consulta = (
            self._consulta_filtrada(busqueda).order_by(ChoferORM.id).offset(offset).limit(limit)
        )
        return [a_dominio(orm) for orm in self._db.scalars(consulta)]

    def contar(self, busqueda: str | None) -> int:
        consulta = self._consulta_filtrada(busqueda).with_only_columns(func.count())
        return self._db.scalar(consulta) or 0

    def actualizar(self, chofer: Chofer) -> Chofer:
        orm = self._db.get(ChoferORM, chofer.id)
        if orm is None:
            raise ChoferNoEncontrado(chofer.id)
        orm.nombre_completo = chofer.nombre_completo
        orm.telefono = chofer.telefono
        # Forzado a mano: `onupdate` no dispara si ningún atributo cambia (lección H1/T047).
        orm.actualizado_en = func.now()
        self._db.commit()
        self._db.refresh(orm)
        return a_dominio(orm)

    def desactivar(self, chofer_id: int) -> None:
        self._db.execute(update(ChoferORM).where(ChoferORM.id == chofer_id).values(activo=False))
        self._db.commit()

    def existe_activo(self, chofer_id: int) -> bool:
        """Implementa el puerto `ConsultaChofer` de H4 (chofer habitual)."""
        consulta = select(ChoferORM.id).where(ChoferORM.id == chofer_id, ChoferORM.activo.is_(True))
        return self._db.scalar(consulta.limit(1)) is not None

    def _consulta_filtrada(self, busqueda: str | None):
        consulta = select(ChoferORM).where(ChoferORM.activo.is_(True))
        if busqueda:
            consulta = consulta.where(ChoferORM.nombre_completo.ilike(f"%{busqueda.strip()}%"))
        return consulta
