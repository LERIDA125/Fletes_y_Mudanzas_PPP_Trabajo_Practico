"""Único punto de acceso SQLAlchemy para Servicios."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.servicios.puertos import AsignacionDia, ServicioListadoItem
from app.domain.errores import (
    ReferenciasServicioInvalidas,
    ServicioConDependencias,
    ServicioNoEncontrado,
)
from app.domain.servicio import Servicio
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.cliente import ClienteORM
from app.infrastructure.models.servicio import ServicioORM
from app.infrastructure.models.tipo_vehiculo import TipoVehiculoORM
from app.infrastructure.models.vehiculo import VehiculoORM


def a_dominio(orm: ServicioORM) -> Servicio:
    return Servicio(
        id=orm.id,
        id_cliente=orm.id_cliente,
        id_tipo_vehiculo=orm.id_tipo_vehiculo,
        id_chofer=orm.id_chofer,
        id_vehiculo=orm.id_vehiculo,
        fecha=orm.fecha,
        hora_inicio=orm.hora_inicio,
        hora_fin=orm.hora_fin,
        horas_estimadas=orm.horas_estimadas,
        distancia_ida_km=orm.distancia_ida_km,
        distancia_total_km=orm.distancia_total_km,
        km_franquicia=orm.km_franquicia,
        km_excedente=orm.km_excedente,
        tarifa_hora_aplicada=orm.tarifa_hora_aplicada,
        tarifa_km_aplicada=orm.tarifa_km_aplicada,
        precio_total=orm.precio_total,
        estado=orm.estado,
        motivo_cancelacion=orm.motivo_cancelacion,
        creado_en=orm.creado_en,
        actualizado_en=orm.actualizado_en,
        creado_por_id=orm.creado_por_id,
        modificado_por_id=orm.modificado_por_id,
    )


def a_orm(servicio: Servicio) -> ServicioORM:
    return ServicioORM(
        id=servicio.id,
        id_cliente=servicio.id_cliente,
        id_tipo_vehiculo=servicio.id_tipo_vehiculo,
        id_chofer=servicio.id_chofer,
        id_vehiculo=servicio.id_vehiculo,
        fecha=servicio.fecha,
        hora_inicio=servicio.hora_inicio,
        hora_fin=servicio.hora_fin,
        horas_estimadas=servicio.horas_estimadas,
        distancia_ida_km=servicio.distancia_ida_km,
        distancia_total_km=servicio.distancia_total_km,
        km_franquicia=servicio.km_franquicia,
        km_excedente=servicio.km_excedente,
        tarifa_hora_aplicada=servicio.tarifa_hora_aplicada,
        tarifa_km_aplicada=servicio.tarifa_km_aplicada,
        precio_total=servicio.precio_total,
        estado=servicio.estado,
        motivo_cancelacion=servicio.motivo_cancelacion,
        creado_en=servicio.creado_en,
        actualizado_en=servicio.actualizado_en,
        creado_por_id=servicio.creado_por_id,
        modificado_por_id=servicio.modificado_por_id,
    )


class ServicioRepo:
    def __init__(self, db: Session) -> None:
        self._db = db

    def crear(self, servicio: Servicio) -> ServicioListadoItem:
        orm = a_orm(servicio)
        self._db.add(orm)
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            raise ReferenciasServicioInvalidas() from error
        self._db.refresh(orm)
        fila = self._db.execute(self._consulta_con_nombres().where(ServicioORM.id == orm.id)).one()
        return self._a_item(fila)

    def obtener_por_id(self, servicio_id: int) -> ServicioListadoItem | None:
        consulta = self._consulta_con_nombres().where(ServicioORM.id == servicio_id)
        fila = self._db.execute(consulta).one_or_none()
        return self._a_item(fila) if fila is not None else None

    def actualizar(self, servicio: Servicio) -> ServicioListadoItem:
        if servicio.id is None:
            raise ValueError("No se puede actualizar un servicio sin identidad")

        orm = self._db.get(ServicioORM, servicio.id)
        if orm is None:
            raise ServicioNoEncontrado(servicio.id)

        orm.id_cliente = servicio.id_cliente
        orm.id_tipo_vehiculo = servicio.id_tipo_vehiculo
        orm.id_chofer = servicio.id_chofer
        orm.id_vehiculo = servicio.id_vehiculo
        orm.fecha = servicio.fecha
        orm.hora_inicio = servicio.hora_inicio
        orm.hora_fin = servicio.hora_fin
        orm.horas_estimadas = servicio.horas_estimadas
        orm.distancia_ida_km = servicio.distancia_ida_km
        orm.distancia_total_km = servicio.distancia_total_km
        orm.km_franquicia = servicio.km_franquicia
        orm.km_excedente = servicio.km_excedente
        orm.tarifa_hora_aplicada = servicio.tarifa_hora_aplicada
        orm.tarifa_km_aplicada = servicio.tarifa_km_aplicada
        orm.precio_total = servicio.precio_total
        orm.estado = servicio.estado
        orm.motivo_cancelacion = servicio.motivo_cancelacion
        orm.modificado_por_id = servicio.modificado_por_id
        orm.actualizado_en = func.now()

        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            raise ReferenciasServicioInvalidas() from error
        self._db.refresh(orm)
        fila = self._db.execute(self._consulta_con_nombres().where(ServicioORM.id == orm.id)).one()
        return self._a_item(fila)

    def listar(
        self, offset: int, limit: int, id_chofer: int | None = None
    ) -> list[ServicioListadoItem]:
        consulta = self._consulta_con_nombres()
        if id_chofer is not None:
            consulta = consulta.where(ServicioORM.id_chofer == id_chofer)
        consulta = consulta.order_by(ServicioORM.id).offset(offset).limit(limit)
        return [self._a_item(fila) for fila in self._db.execute(consulta)]

    def contar(self, id_chofer: int | None = None) -> int:
        consulta = select(func.count()).select_from(ServicioORM)
        if id_chofer is not None:
            consulta = consulta.where(ServicioORM.id_chofer == id_chofer)
        return self._db.scalar(consulta) or 0

    def tiene_historial(self, cliente_id: int) -> bool:
        consulta = select(ServicioORM.id).where(ServicioORM.id_cliente == cliente_id)
        return self._db.scalar(consulta.limit(1)) is not None

    def tiene_servicios(self, vehiculo_id: int) -> bool:
        consulta = select(ServicioORM.id).where(ServicioORM.id_vehiculo == vehiculo_id)
        return self._db.scalar(consulta.limit(1)) is not None

    def listar_asignaciones_del_dia(self, fecha: date) -> list[AsignacionDia]:
        """Servicios no cancelados de una fecha, para detectar recursos ocupados.

        No se filtra por estado finalizado/cobrado porque un servicio de ese día
        puede seguir consumiendo la franja estimada; la regla se documenta en la
        spec 008. Los cancelados no bloquean recursos.
        """
        consulta = select(
            ServicioORM.id_chofer,
            ServicioORM.id_vehiculo,
            ServicioORM.hora_inicio,
            ServicioORM.horas_estimadas,
        ).where(
            ServicioORM.fecha == fecha,
            ServicioORM.estado != "cancelado",
        )
        return [
            AsignacionDia(
                id_chofer=id_chofer,
                id_vehiculo=id_vehiculo,
                hora_inicio=hora_inicio,
                horas_estimadas=horas_estimadas,
            )
            for id_chofer, id_vehiculo, hora_inicio, horas_estimadas in self._db.execute(consulta)
        ]

    @staticmethod
    def _consulta_con_nombres():
        return (
            select(
                ServicioORM,
                ClienteORM.razon_social,
                TipoVehiculoORM.descripcion,
                ChoferORM.nombre_completo,
                VehiculoORM.patente,
            )
            .join(ClienteORM, ServicioORM.id_cliente == ClienteORM.id)
            .join(TipoVehiculoORM, ServicioORM.id_tipo_vehiculo == TipoVehiculoORM.id)
            .outerjoin(ChoferORM, ServicioORM.id_chofer == ChoferORM.id)
            .outerjoin(VehiculoORM, ServicioORM.id_vehiculo == VehiculoORM.id)
        )

    @staticmethod
    def _a_item(fila) -> ServicioListadoItem:
        orm, razon_social, descripcion_tipo, nombre_chofer, patente = fila
        return ServicioListadoItem(
            servicio=a_dominio(orm),
            razon_social_cliente=razon_social,
            descripcion_tipo_vehiculo=descripcion_tipo,
            nombre_chofer=nombre_chofer,
            patente_vehiculo=patente,
        )

    def eliminar(self, servicio_id: int) -> None:
        orm = self._db.get(ServicioORM, servicio_id)
        if orm is None:
            raise ServicioNoEncontrado(servicio_id)
        self._db.delete(orm)
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            raise ServicioConDependencias(servicio_id) from error
