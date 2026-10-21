"""Casos de uso de Servicios; las reglas se ejecutan antes de persistir."""

from datetime import date, time
from decimal import Decimal

from app.application.cotizacion.calculadora import CalculadoraCotizacion, Cotizacion
from app.application.servicios.puertos import (
    ConsultaChoferServicio,
    ConsultaClienteServicio,
    ConsultaVehiculoServicio,
    ServicioListadoItem,
    ServicioRepository,
)
from app.domain.errores import (
    ChoferInvalido,
    ClienteInvalido,
    VehiculoInvalido,
    VehiculoTipoIncompatible,
)
from app.domain.servicio import Servicio


class GestorServicios:
    def __init__(
        self,
        *,
        repositorio: ServicioRepository,
        calculadora: CalculadoraCotizacion,
        consulta_clientes: ConsultaClienteServicio,
        consulta_choferes: ConsultaChoferServicio,
        consulta_vehiculos: ConsultaVehiculoServicio,
    ) -> None:
        self._repo = repositorio
        self._calculadora = calculadora
        self._clientes = consulta_clientes
        self._choferes = consulta_choferes
        self._vehiculos = consulta_vehiculos

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
        id_cliente: int,
        id_tipo_vehiculo: int,
        id_chofer: int | None,
        id_vehiculo: int | None,
        fecha: date,
        hora_inicio: time | None,
        horas_estimadas: Decimal,
        distancia_ida_km: Decimal,
    ) -> ServicioListadoItem:
        cliente = self._clientes.obtener_por_id(id_cliente)
        if cliente is None or not cliente.activo:
            raise ClienteInvalido(id_cliente)

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
            id_cliente=id_cliente,
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

    def listar(self, *, offset: int, limit: int) -> tuple[list[ServicioListadoItem], int]:
        total = self._repo.contar()
        return self._repo.listar(offset=offset, limit=limit), total
