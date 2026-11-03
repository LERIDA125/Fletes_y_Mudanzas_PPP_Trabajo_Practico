"""Único punto de acceso SQLAlchemy para Rendiciones."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import and_, case, extract, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.rendiciones.puertos import (
    RendicionListadoItem,
    ResumenRendiciones,
    ServicioElegible,
    ServicioParaRendir,
)
from app.domain.errores import RendicionNoEncontrada, ServicioYaRendido
from app.domain.rendicion import ESTADOS_SERVICIO_RENDIBLES, Rendicion
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.cliente import ClienteORM
from app.infrastructure.models.rendicion import RendicionORM
from app.infrastructure.models.servicio import ServicioORM

CENTAVO = Decimal("0.01")

_EXPRESION_SALDO = (
    RendicionORM.tarifa
    - RendicionORM.adelanto
    - RendicionORM.gasto_combustible
    - RendicionORM.gasto_peajes
    - RendicionORM.gasto_otros
)
_EXPRESION_GASTOS = (
    RendicionORM.gasto_combustible
    + RendicionORM.gasto_peajes
    + RendicionORM.gasto_otros
)


def a_dominio(orm: RendicionORM) -> Rendicion:
    return Rendicion(
        id=orm.id,
        codigo=orm.codigo,
        id_servicio=orm.id_servicio,
        id_chofer=orm.id_chofer,
        fecha=orm.fecha,
        tarifa=orm.tarifa,
        adelanto=orm.adelanto,
        gasto_combustible=orm.gasto_combustible,
        gasto_peajes=orm.gasto_peajes,
        gasto_otros=orm.gasto_otros,
        estado=orm.estado,
        observaciones=orm.observaciones,
        creado_en=orm.creado_en,
        actualizado_en=orm.actualizado_en,
        creado_por_id=orm.creado_por_id,
        modificado_por_id=orm.modificado_por_id,
    )


def _a_item(fila) -> RendicionListadoItem:
    orm, nombre_chofer, razon_social_cliente = fila
    return RendicionListadoItem(
        rendicion=a_dominio(orm),
        nombre_chofer=nombre_chofer,
        razon_social_cliente=razon_social_cliente,
    )


def _a_decimal(valor: object | None) -> Decimal:
    return Decimal(str(valor or 0)).quantize(CENTAVO)


class RendicionRepo:
    def __init__(self, db: Session) -> None:
        self._db = db

    def crear(self, rendicion: Rendicion) -> RendicionListadoItem:
        orm = RendicionORM(
            id_servicio=rendicion.id_servicio,
            id_chofer=rendicion.id_chofer,
            fecha=rendicion.fecha,
            tarifa=rendicion.tarifa,
            adelanto=rendicion.adelanto,
            gasto_combustible=rendicion.gasto_combustible,
            gasto_peajes=rendicion.gasto_peajes,
            gasto_otros=rendicion.gasto_otros,
            estado=rendicion.estado,
            observaciones=rendicion.observaciones,
            creado_por_id=rendicion.creado_por_id,
            modificado_por_id=rendicion.modificado_por_id,
        )
        self._db.add(orm)
        try:
            self._db.flush()
            orm.codigo = f"REN-{orm.id:03d}"
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            raise ServicioYaRendido(rendicion.id_servicio) from error
        self._db.refresh(orm)
        return self._obtener_item(orm.id)

    def obtener_por_id(self, rendicion_id: int) -> RendicionListadoItem | None:
        fila = self._db.execute(
            self._consulta_con_nombres().where(RendicionORM.id == rendicion_id)
        ).one_or_none()
        return _a_item(fila) if fila is not None else None

    def listar(
        self, busqueda: str | None, offset: int, limit: int
    ) -> list[RendicionListadoItem]:
        consulta = (
            self._consulta_con_nombres()
            .order_by(RendicionORM.id.desc())
            .offset(offset)
            .limit(limit)
        )
        consulta = self._aplicar_busqueda(consulta, busqueda)
        return [_a_item(fila) for fila in self._db.execute(consulta)]

    def contar(self, busqueda: str | None) -> int:
        consulta = (
            select(func.count(RendicionORM.id))
            .select_from(RendicionORM)
            .join(ServicioORM, RendicionORM.id_servicio == ServicioORM.id)
            .join(ChoferORM, RendicionORM.id_chofer == ChoferORM.id)
            .join(ClienteORM, ServicioORM.id_cliente == ClienteORM.id)
        )
        consulta = self._aplicar_busqueda(consulta, busqueda)
        return self._db.scalar(consulta) or 0

    def resumen(self, *, anio: int, mes: int) -> ResumenRendiciones:
        pendientes = ("pendiente", "en revision")
        consulta = select(
            func.coalesce(
                func.sum(case((RendicionORM.estado.in_(pendientes), _EXPRESION_SALDO), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(case((RendicionORM.estado.in_(pendientes), 1), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                RendicionORM.estado == "aprobada",
                                extract("year", RendicionORM.fecha) == anio,
                                extract("month", RendicionORM.fecha) == mes,
                            ),
                            RendicionORM.tarifa,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(func.sum(_EXPRESION_GASTOS), 0),
        )
        pendiente_total, pendiente_cantidad, aprobado_mes_total, gastos_total = (
            self._db.execute(consulta).one()
        )
        return ResumenRendiciones(
            pendiente_total=_a_decimal(pendiente_total),
            pendiente_cantidad=int(pendiente_cantidad or 0),
            aprobado_mes_total=_a_decimal(aprobado_mes_total),
            gastos_total=_a_decimal(gastos_total),
        )

    def actualizar(self, rendicion: Rendicion) -> RendicionListadoItem:
        if rendicion.id is None:
            raise ValueError("No se puede actualizar una rendición sin identidad")

        orm = self._db.get(RendicionORM, rendicion.id)
        if orm is None:
            raise RendicionNoEncontrada(rendicion.id)

        orm.estado = rendicion.estado
        orm.observaciones = rendicion.observaciones
        orm.modificado_por_id = rendicion.modificado_por_id
        orm.actualizado_en = func.now()
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            raise ServicioYaRendido(rendicion.id_servicio) from error
        self._db.refresh(orm)
        return self._obtener_item(orm.id)

    def existe_para_servicio(self, servicio_id: int) -> bool:
        consulta = select(RendicionORM.id).where(RendicionORM.id_servicio == servicio_id)
        return self._db.scalar(consulta.limit(1)) is not None

    def _obtener_item(self, rendicion_id: int) -> RendicionListadoItem:
        fila = self._db.execute(
            self._consulta_con_nombres().where(RendicionORM.id == rendicion_id)
        ).one()
        return _a_item(fila)

    @staticmethod
    def _consulta_con_nombres():
        return (
            select(
                RendicionORM,
                ChoferORM.nombre_completo,
                ClienteORM.razon_social,
            )
            .join(ServicioORM, RendicionORM.id_servicio == ServicioORM.id)
            .join(ChoferORM, RendicionORM.id_chofer == ChoferORM.id)
            .join(ClienteORM, ServicioORM.id_cliente == ClienteORM.id)
        )

    @staticmethod
    def _aplicar_busqueda(consulta, busqueda: str | None):
        termino = (busqueda or "").strip()
        if not termino:
            return consulta

        patron = f"%{termino}%"
        condiciones = [
            RendicionORM.codigo.ilike(patron),
            ChoferORM.nombre_completo.ilike(patron),
            ClienteORM.razon_social.ilike(patron),
        ]
        if termino.isdigit():
            condiciones.append(ServicioORM.id == int(termino))
        return consulta.where(or_(*condiciones))


class ServicioRendibleRepo:
    """Consulta de servicios aptos para rendir; comparte la Session de la request."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def listar_elegibles(self) -> list[ServicioElegible]:
        ya_rendido = select(RendicionORM.id).where(
            RendicionORM.id_servicio == ServicioORM.id
        ).exists()
        consulta = (
            select(
                ServicioORM.id,
                ClienteORM.razon_social,
                ChoferORM.nombre_completo,
                ServicioORM.fecha,
                ServicioORM.hora_inicio,
                ServicioORM.precio_total,
            )
            .join(ClienteORM, ServicioORM.id_cliente == ClienteORM.id)
            .join(ChoferORM, ServicioORM.id_chofer == ChoferORM.id)
            .where(
                ServicioORM.id_chofer.is_not(None),
                ServicioORM.estado.in_(ESTADOS_SERVICIO_RENDIBLES),
                ~ya_rendido,
            )
            .order_by(ServicioORM.fecha.desc(), ServicioORM.id.desc())
        )
        return [
            ServicioElegible(
                id_servicio=id_servicio,
                razon_social_cliente=razon_social,
                nombre_chofer=nombre_chofer,
                fecha=fecha,
                hora_inicio=hora_inicio,
                precio_total=precio_total,
            )
            for id_servicio, razon_social, nombre_chofer, fecha, hora_inicio, precio_total in (
                self._db.execute(consulta)
            )
        ]

    def obtener_para_rendir(self, servicio_id: int) -> ServicioParaRendir | None:
        fila = self._db.execute(
            select(
                ServicioORM.id,
                ServicioORM.id_chofer,
                ServicioORM.fecha,
                ServicioORM.estado,
            ).where(ServicioORM.id == servicio_id)
        ).one_or_none()
        if fila is None:
            return None
        id_servicio, id_chofer, fecha, estado = fila
        return ServicioParaRendir(
            id_servicio=id_servicio,
            id_chofer=id_chofer,
            fecha=fecha,
            estado=estado,
        )
