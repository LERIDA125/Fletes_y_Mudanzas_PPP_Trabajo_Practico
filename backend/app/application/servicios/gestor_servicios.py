"""Casos de uso de Servicios; las reglas se ejecutan antes de persistir."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import ROUND_CEILING, Decimal

from app.application.cotizacion.calculadora import CalculadoraCotizacion, Cotizacion
from app.application.servicios.puertos import (
    AsignacionDia,
    ConsultaChoferServicio,
    ConsultaClienteServicio,
    ConsultaTipoServicio,
    ConsultaVehiculoServicio,
    Disponibilidad,
    RegistroClienteServicio,
    ServicioListadoItem,
    ServicioRepository,
)
from app.domain.cliente import Cliente
from app.domain.errores import (
    ChoferInvalido,
    ClienteInvalido,
    DatoInvalido,
    RazonSocialDuplicada,
    ServicioNoEncontrado,
    TipoVehiculoInvalido,
    VehiculoInvalido,
    VehiculoTipoIncompatible,
)
from app.domain.servicio import Servicio


def _minutos_desde_medianoche(hora: time) -> int:
    return hora.hour * 60 + hora.minute


def _duracion_en_minutos(horas: Decimal) -> int:
    """Redondea hacia arriba para no liberar un recurso antes de que termine el servicio."""
    return int((horas * 60).to_integral_value(rounding=ROUND_CEILING))


def _hora_fin(hora_inicio: time | None, horas: Decimal) -> time | None:
    if hora_inicio is None:
        return None
    total = _minutos_desde_medianoche(hora_inicio) + _duracion_en_minutos(horas)
    if total >= 24 * 60:
        return time(23, 59, 59)
    return time(total // 60, total % 60)


def _se_solapa(
    *,
    hora_inicio: time | None,
    horas_estimadas: Decimal,
    asignacion: AsignacionDia,
) -> bool:
    """Considera ocupado el recurso ante cualquier dato horario incompleto.

    Supuesto documentado en `specs/008-frontend-gestion-servicios/spec.md`: si un
    servicio del día no tiene hora de inicio, no se puede garantizar que el recurso
    esté libre, así que se bloquea durante todo el día. Tampoco se aplica un margen
    entre servicios porque el cliente no lo confirmó (AGENTS.md §6).
    """
    if hora_inicio is None or asignacion.hora_inicio is None:
        return True

    inicio_solicitado = _minutos_desde_medianoche(hora_inicio)
    fin_solicitado = inicio_solicitado + _duracion_en_minutos(horas_estimadas)
    inicio_existente = _minutos_desde_medianoche(asignacion.hora_inicio)
    fin_existente = inicio_existente + _duracion_en_minutos(asignacion.horas_estimadas)
    return inicio_solicitado < fin_existente and inicio_existente < fin_solicitado


class GestorServicios:
    def __init__(
        self,
        *,
        repositorio: ServicioRepository,
        calculadora: CalculadoraCotizacion,
        consulta_clientes: ConsultaClienteServicio,
        consulta_choferes: ConsultaChoferServicio,
        consulta_vehiculos: ConsultaVehiculoServicio,
        consulta_tipos: ConsultaTipoServicio | None = None,
        registro_clientes: RegistroClienteServicio | None = None,
    ) -> None:
        self._repo = repositorio
        self._calculadora = calculadora
        self._clientes = consulta_clientes
        self._choferes = consulta_choferes
        self._vehiculos = consulta_vehiculos
        self._tipos = consulta_tipos
        self._registro_clientes = registro_clientes

    def cotizar(
        self,
        *,
        id_tipo_vehiculo: int,
        horas_estimadas: Decimal,
        distancia_ida_km: Decimal,
    ) -> Cotizacion:
        return self._calculadora.cotizar(
            id_tipo_vehiculo=id_tipo_vehiculo,
            horas_estimadas=horas_estimadas,
            distancia_ida_km=distancia_ida_km,
        )

    def crear(
        self,
        *,
        id_cliente: int | None,
        id_tipo_vehiculo: int,
        id_chofer: int | None,
        id_vehiculo: int | None,
        fecha: date,
        hora_inicio: time | None,
        horas_estimadas: Decimal,
        distancia_ida_km: Decimal,
        nuevo_cliente: Cliente | None = None,
    ) -> ServicioListadoItem:
        cliente_id = self._resolver_cliente(id_cliente=id_cliente, nuevo_cliente=nuevo_cliente)

        if id_chofer is not None:
            chofer = self._choferes.obtener_por_id(id_chofer)
            if chofer is None or not chofer.activo:
                raise ChoferInvalido(id_chofer)

        if id_vehiculo is not None:
            vehiculo = self._vehiculos.obtener_por_id(id_vehiculo)
            if vehiculo is None or not vehiculo.activo:
                raise VehiculoInvalido(id_vehiculo)
            if vehiculo.id_tipo_vehiculo != id_tipo_vehiculo:
                raise VehiculoTipoIncompatible(id_vehiculo, id_tipo_vehiculo)

        cotizacion = self._calculadora.cotizar(
            id_tipo_vehiculo=id_tipo_vehiculo,
            horas_estimadas=horas_estimadas,
            distancia_ida_km=distancia_ida_km,
        )
        servicio = Servicio.crear(
            id_cliente=cliente_id,
            id_tipo_vehiculo=id_tipo_vehiculo,
            id_chofer=id_chofer,
            id_vehiculo=id_vehiculo,
            fecha=fecha,
            hora_inicio=hora_inicio,
            horas_estimadas=cotizacion.resultado.horas_estimadas,
            distancia_ida_km=cotizacion.resultado.distancia_ida_km,
            distancia_total_km=cotizacion.resultado.distancia_total_km,
            km_franquicia=cotizacion.resultado.km_franquicia,
            km_excedente=cotizacion.resultado.km_excedente,
            tarifa_hora_aplicada=cotizacion.resultado.tarifa_hora_base,
            tarifa_km_aplicada=cotizacion.resultado.tarifa_km_excedente,
            precio_total=cotizacion.resultado.precio_final,
        )
        return self._repo.crear(servicio)

    def disponibilidad(
        self,
        *,
        fecha: date,
        id_tipo_vehiculo: int,
        hora_inicio: time | None,
        horas_estimadas: Decimal,
    ) -> Disponibilidad:
        if self._tipos is None:
            raise RuntimeError("El gestor de servicios no tiene configurada la consulta de tipos")

        tipo = self._tipos.obtener_por_id(id_tipo_vehiculo)
        if tipo is None or not tipo.activo:
            raise TipoVehiculoInvalido(id_tipo_vehiculo)

        asignaciones = self._repo.listar_asignaciones_del_dia(fecha)
        choferes_ocupados: set[int] = set()
        vehiculos_ocupados: set[int] = set()
        for asignacion in asignaciones:
            if not _se_solapa(
                hora_inicio=hora_inicio,
                horas_estimadas=horas_estimadas,
                asignacion=asignacion,
            ):
                continue
            if asignacion.id_chofer is not None:
                choferes_ocupados.add(asignacion.id_chofer)
            if asignacion.id_vehiculo is not None:
                vehiculos_ocupados.add(asignacion.id_vehiculo)

        choferes = [
            chofer
            for chofer in self._choferes.listar_activos()
            if chofer.id is not None and chofer.id not in choferes_ocupados
        ]
        vehiculos = [
            vehiculo
            for vehiculo in self._vehiculos.listar_activos_por_tipo(id_tipo_vehiculo)
            if vehiculo.vehiculo.id is not None
            and vehiculo.vehiculo.id not in vehiculos_ocupados
        ]
        return Disponibilidad(
            hora_fin=_hora_fin(hora_inicio, horas_estimadas),
            choferes=choferes,
            vehiculos=vehiculos,
        )

    def cancelar(
        self,
        *,
        id_servicio: int,
        motivo: str,
        ahora: datetime | None = None,
    ) -> ServicioListadoItem:
        actual = self._repo.obtener_por_id(id_servicio)
        if actual is None:
            raise ServicioNoEncontrado(id_servicio)

        hora_fin = (ahora or datetime.now()).time().replace(microsecond=0)
        actual.servicio.cancelar(motivo=motivo, hora_fin=hora_fin)
        return self._repo.actualizar(actual.servicio)

    def listar(self, *, offset: int, limit: int) -> tuple[list[ServicioListadoItem], int]:
        total = self._repo.contar()
        return self._repo.listar(offset=offset, limit=limit), total

    def _resolver_cliente(
        self,
        *,
        id_cliente: int | None,
        nuevo_cliente: Cliente | None,
    ) -> int:
        if id_cliente is not None and nuevo_cliente is not None:
            raise DatoInvalido("Indicá un cliente existente o uno nuevo, pero no ambos")
        if id_cliente is None and nuevo_cliente is None:
            raise DatoInvalido("El servicio necesita un cliente existente o los datos de uno nuevo")

        if id_cliente is not None:
            cliente = self._clientes.obtener_por_id(id_cliente)
            if cliente is None or not cliente.activo:
                raise ClienteInvalido(id_cliente)
            return id_cliente

        if self._registro_clientes is None:
            raise RuntimeError(
                "El gestor de servicios no tiene configurado el alta implícita de clientes"
            )
        assert nuevo_cliente is not None

        existente = self._registro_clientes.obtener_por_razon_social(
            nuevo_cliente.razon_social_key
        )
        if existente is not None:
            if not existente.activo:
                raise RazonSocialDuplicada(nuevo_cliente.razon_social)
            if existente.id is None:
                raise RuntimeError("El repositorio devolvió un cliente sin identidad")
            return existente.id

        creado = self._registro_clientes.crear(nuevo_cliente)
        if creado.id is None:
            raise RuntimeError("El repositorio devolvió un cliente recién creado sin identidad")
        return creado.id
