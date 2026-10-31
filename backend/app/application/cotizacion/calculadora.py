"""Caso de uso para cotizar usando tarifas activas y una estrategia intercambiable."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.application.cotizacion.estrategias.por_hora_km_modificadores import (
    EstrategiaPorHoraKmModificadores,
)
from app.application.cotizacion.puertos import (
    ConsultaConfiguracionCotizacion,
    ConsultaTipoVehiculoTarifas,
)
from app.domain.configuracion_cotizacion import ConfiguracionCotizacion
from app.domain.cotizacion import CotizacionCalculada
from app.domain.errores import ConfiguracionCotizacionInvalida, TipoVehiculoInvalido


class EstrategiaCotizacion(Protocol):
    def calcular(
        self,
        *,
        horas_estimadas: Decimal,
        km_estimados: Decimal,
        tarifa_hora_base: Decimal,
        tarifa_km_excedente: Decimal,
        configuracion: ConfiguracionCotizacion,
        requiere_ayudante: bool = False,
        acceso_escalera: bool = False,
        zona_concurrida: bool = False,
        urgencia_mismo_dia: bool = False,
    ) -> CotizacionCalculada: ...


@dataclass(frozen=True)
class Cotizacion:
    id_tipo_vehiculo: int
    descripcion_tipo_vehiculo: str
    resultado: CotizacionCalculada


class CalculadoraCotizacion:
    def __init__(
        self,
        consulta_tipos: ConsultaTipoVehiculoTarifas,
        consulta_configuracion: ConsultaConfiguracionCotizacion,
        estrategia: EstrategiaCotizacion | None = None,
    ) -> None:
        self._consulta_tipos = consulta_tipos
        self._consulta_configuracion = consulta_configuracion
        self._estrategia = estrategia or EstrategiaPorHoraKmModificadores()

    def cotizar(
        self,
        *,
        id_tipo_vehiculo: int,
        horas_estimadas: Decimal,
        km_estimados: Decimal,
        requiere_ayudante: bool = False,
        acceso_escalera: bool = False,
        zona_concurrida: bool = False,
        urgencia_mismo_dia: bool = False,
    ) -> Cotizacion:
        tipo = self._consulta_tipos.obtener_por_id(id_tipo_vehiculo)
        if tipo is None or not tipo.activo:
            raise TipoVehiculoInvalido(id_tipo_vehiculo)

        configuracion = self._consulta_configuracion.obtener()
        if configuracion is None:
            raise ConfiguracionCotizacionInvalida(
                "No hay una configuración de cotización cargada en el sistema"
            )

        resultado = self._estrategia.calcular(
            horas_estimadas=horas_estimadas,
            km_estimados=km_estimados,
            tarifa_hora_base=tipo.tarifa_hora_base,
            tarifa_km_excedente=tipo.tarifa_km_excedente,
            configuracion=configuracion,
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
