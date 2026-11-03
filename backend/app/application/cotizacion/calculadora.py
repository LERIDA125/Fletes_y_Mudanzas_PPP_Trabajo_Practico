"""Caso de uso para cotizar usando tarifas activas y una estrategia intercambiable."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.application.cotizacion.estrategias.por_hora_y_km import (
    EstrategiaPorHoraYKm,
    ResultadoCotizacion,
)
from app.application.cotizacion.puertos import ConsultaTipoVehiculoTarifas
from app.domain.errores import TipoVehiculoInvalido


class EstrategiaCotizacion(Protocol):
    def calcular(
        self,
        *,
        horas_estimadas: Decimal,
        distancia_ida_km: Decimal,
        tarifa_hora_base: Decimal,
        tarifa_km_excedente: Decimal,
        requiere_ayudante: bool = False,
        acceso_escalera: bool = False,
        zona_concurrida: bool = False,
        urgencia_mismo_dia: bool = False,
    ) -> ResultadoCotizacion: ...


@dataclass(frozen=True)
class Cotizacion:
    id_tipo_vehiculo: int
    descripcion_tipo_vehiculo: str
    resultado: ResultadoCotizacion

    @property
    def precio_final(self) -> Decimal:
        return self.resultado.precio_final


class CalculadoraCotizacion:
    def __init__(
        self,
        consulta_tipos: ConsultaTipoVehiculoTarifas,
        estrategia: EstrategiaCotizacion | None = None,
    ) -> None:
        self._consulta_tipos = consulta_tipos
        self._estrategia = estrategia or EstrategiaPorHoraYKm()

    def cotizar(
        self,
        *,
        id_tipo_vehiculo: int,
        horas_estimadas: Decimal,
        distancia_ida_km: Decimal,
        requiere_ayudante: bool = False,
        acceso_escalera: bool = False,
        zona_concurrida: bool = False,
        urgencia_mismo_dia: bool = False,
    ) -> Cotizacion:
        tipo = self._consulta_tipos.obtener_por_id(id_tipo_vehiculo)
        if tipo is None or not tipo.activo:
            raise TipoVehiculoInvalido(id_tipo_vehiculo)

        resultado = self._estrategia.calcular(
            horas_estimadas=horas_estimadas,
            distancia_ida_km=distancia_ida_km,
            tarifa_hora_base=tipo.tarifa_hora_base,
            tarifa_km_excedente=tipo.tarifa_km_excedente,
            requiere_ayudante=requiere_ayudante,
            acceso_escalera=acceso_escalera,
            zona_concurrida=zona_concurrida,
            urgencia_mismo_dia=urgencia_mismo_dia,
        )
        return Cotizacion(
            id_tipo_vehiculo=id_tipo_vehiculo,
            descripcion_tipo_vehiculo=tipo.descripcion,
            resultado=resultado,
        )
