"""Estrategia de cotización por horas, kilómetros estimados y modificadores."""

from decimal import ROUND_HALF_UP, Decimal

from app.domain.configuracion_cotizacion import ConfiguracionCotizacion
from app.domain.cotizacion import CotizacionCalculada
from app.domain.errores import DatoInvalido

CENTAVO = Decimal("0.01")
CERO = Decimal("0.00")


def _cuantizar(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


class EstrategiaPorHoraKmModificadores:
    """Calcula el precio sugerido con tarifas y configuración provistas por la empresa."""

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
    ) -> CotizacionCalculada:
        valores = (
            horas_estimadas,
            km_estimados,
            tarifa_hora_base,
            tarifa_km_excedente,
        )
        if any(not valor.is_finite() for valor in valores):
            raise DatoInvalido("Los valores de la cotización deben ser números finitos")
        if horas_estimadas < Decimal("1"):
            raise DatoInvalido("Las horas estimadas deben ser como mínimo 1")
        if km_estimados < 0:
            raise DatoInvalido("Los kilómetros estimados no pueden ser negativos")
        if tarifa_hora_base < 0 or tarifa_km_excedente < 0:
            raise DatoInvalido("Las tarifas no pueden ser negativas")

        base_horas = _cuantizar(tarifa_hora_base * horas_estimadas)
        base_km = _cuantizar(tarifa_km_excedente * km_estimados)
        subtotal_base = _cuantizar(base_horas + base_km)

        recargo_ayudante = (
            _cuantizar(configuracion.recargo_ayudante) if requiere_ayudante else CERO
        )
        recargo_escalera = (
            _cuantizar(configuracion.recargo_escalera) if acceso_escalera else CERO
        )
        subtotal_con_fijos = _cuantizar(subtotal_base + recargo_ayudante + recargo_escalera)

        porcentaje_zona = (
            _cuantizar(configuracion.porcentaje_zona_concurrida) if zona_concurrida else CERO
        )
        importe_zona = (
            _cuantizar(subtotal_con_fijos * porcentaje_zona / Decimal("100"))
            if zona_concurrida
            else CERO
        )

        porcentaje_urgencia = (
            _cuantizar(configuracion.porcentaje_urgencia_mismo_dia)
            if urgencia_mismo_dia
            else CERO
        )
        importe_urgencia = (
            _cuantizar(subtotal_con_fijos * porcentaje_urgencia / Decimal("100"))
            if urgencia_mismo_dia
            else CERO
        )

        total_recargos_porcentuales = _cuantizar(importe_zona + importe_urgencia)
        precio_sugerido = _cuantizar(subtotal_con_fijos + total_recargos_porcentuales)

        return CotizacionCalculada(
            horas_estimadas=horas_estimadas,
            km_estimados=km_estimados,
            tarifa_hora_base=tarifa_hora_base,
            tarifa_km_excedente=tarifa_km_excedente,
            base_horas=base_horas,
            base_km=base_km,
            subtotal_base=subtotal_base,
            requiere_ayudante=requiere_ayudante,
            recargo_ayudante=recargo_ayudante,
            acceso_escalera=acceso_escalera,
            recargo_escalera=recargo_escalera,
            subtotal_con_fijos=subtotal_con_fijos,
            zona_concurrida=zona_concurrida,
            porcentaje_zona_concurrida=porcentaje_zona,
            importe_recargo_zona_concurrida=importe_zona,
            urgencia_mismo_dia=urgencia_mismo_dia,
            porcentaje_urgencia_mismo_dia=porcentaje_urgencia,
            importe_recargo_urgencia_mismo_dia=importe_urgencia,
            total_recargos_porcentuales=total_recargos_porcentuales,
            precio_sugerido=precio_sugerido,
        )
