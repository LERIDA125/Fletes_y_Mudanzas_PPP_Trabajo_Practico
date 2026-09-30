from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.cliente import Cliente, normalizar_razon_social
from app.domain.errores import ClienteNoEncontrado, RazonSocialDuplicada
from app.infrastructure.models.cliente import ClienteORM


def a_dominio(orm: ClienteORM) -> Cliente:
    return Cliente(
        id=orm.id,
        razon_social=orm.razon_social,
        telefono=orm.telefono,
        direccion_habitual=orm.direccion_habitual,
        tiene_cuenta_corriente=orm.tiene_cuenta_corriente,
        activo=orm.activo,
        creado_en=orm.creado_en,
        actualizado_en=orm.actualizado_en,
    )


def a_orm(cliente: Cliente) -> ClienteORM:
    return ClienteORM(
        id=cliente.id,
        razon_social=cliente.razon_social,
        razon_social_key=cliente.razon_social_key,
        telefono=cliente.telefono,
        direccion_habitual=cliente.direccion_habitual,
        tiene_cuenta_corriente=cliente.tiene_cuenta_corriente,
        activo=cliente.activo,
        creado_en=cliente.creado_en,
        actualizado_en=cliente.actualizado_en,
    )


class ClienteRepo:
    """Único punto de acceso a PostgreSQL para clientes (AGENTS.md §2)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def crear(self, cliente: Cliente) -> Cliente:
        orm = a_orm(cliente)
        self._db.add(orm)
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            if "razon_social_key" in str(error.orig):
                raise RazonSocialDuplicada(cliente.razon_social) from error
            raise
        self._db.refresh(orm)
        return a_dominio(orm)

    def obtener_por_id(self, cliente_id: int) -> Cliente | None:
        orm = self._db.get(ClienteORM, cliente_id)
        return a_dominio(orm) if orm is not None else None

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[Cliente]:
        consulta = (
            self._consulta_filtrada(busqueda).order_by(ClienteORM.id).offset(offset).limit(limit)
        )
        return [a_dominio(orm) for orm in self._db.scalars(consulta)]

    def contar(self, busqueda: str | None) -> int:
        consulta = self._consulta_filtrada(busqueda).with_only_columns(func.count())
        return self._db.scalar(consulta) or 0

    def actualizar(self, cliente: Cliente) -> Cliente:
        orm = self._db.get(ClienteORM, cliente.id)
        if orm is None:
            raise ClienteNoEncontrado(cliente.id)
        orm.razon_social = cliente.razon_social
        orm.razon_social_key = cliente.razon_social_key
        orm.telefono = cliente.telefono
        orm.direccion_habitual = cliente.direccion_habitual
        orm.tiene_cuenta_corriente = cliente.tiene_cuenta_corriente
        # FR-020: guardar tiene que refrescar la fecha de última modificación aunque el cliente se
        # guarde idéntico. El `onupdate` de la columna no alcanza para eso, porque si ningún
        # atributo cambió SQLAlchemy no emite el UPDATE y el `onupdate` nunca llega a evaluarse;
        # marcar la columna como modificada a mano es lo que fuerza la escritura.
        orm.actualizado_en = func.now()
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            if "razon_social_key" in str(error.orig):
                raise RazonSocialDuplicada(cliente.razon_social) from error
            raise
        self._db.refresh(orm)
        return a_dominio(orm)

    def desactivar(self, cliente_id: int) -> None:
        self._db.execute(update(ClienteORM).where(ClienteORM.id == cliente_id).values(activo=False))
        self._db.commit()

    def existe_razon_social(self, razon_social_key: str, excluir_id: int | None = None) -> bool:
        consulta = select(ClienteORM.id).where(ClienteORM.razon_social_key == razon_social_key)
        if excluir_id is not None:
            consulta = consulta.where(ClienteORM.id != excluir_id)
        return self._db.scalar(consulta.limit(1)) is not None

    def _consulta_filtrada(self, busqueda: str | None):
        consulta = select(ClienteORM).where(ClienteORM.activo.is_(True))
        if busqueda:
            consulta = consulta.where(
                ClienteORM.razon_social_key.contains(normalizar_razon_social(busqueda))
            )
        return consulta
