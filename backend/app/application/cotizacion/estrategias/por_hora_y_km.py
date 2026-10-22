"""Estrategia aprobada: tarifa horaria más kilómetros que exceden la franquicia."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.domain.errores import DatoInvalido

KM_FRANQUICIA = Decimal("10")
CENTAVO = Decimal("0.01")


@dataclass(frozen=True)
class ResultadoCotizacion:
    horas_estimadas: Decimal
    distancia_ida_km: Decimal
    distancia_total_km: Decimal
    km_franquicia: Decimal
    km_excedente: Decimal
    tarifa_hora_base: Decimal
    tarifa_km_excedente: Decimal
    precio_final: Decimal


class EstrategiaPorHoraYKm:
    """Calcula precio con tarifas suministradas desde la configuración persistida."""

    def calcular(
        self,
        *,
        horas_estimadas: Decimal,
        distancia_ida_km: Decimal,
        tarifa_hora_base: Decimal,
        tarifa_km_excedente: Decimal,
    ) -> ResultadoCotizacion:
        valores = (
            horas_estimadas,
            distancia_ida_km,
            tarifa_hora_base,
            tarifa_km_excedente,
        )
        if any(not valor.is_finite() for valor in valores):
            raise DatoInvalido("Los valores de la cotización deben ser números finitos")
        if horas_estimadas < Decimal("1"):
            raise DatoInvalido("Las horas estimadas deben ser como mínimo 1")
        if distancia_ida_km < 0:
            raise DatoInvalido("La distancia de ida no puede ser negativa")
        if tarifa_hora_base < 0 or tarifa_km_excedente < 0:
            raise DatoInvalido("Las tarifas no pueden ser negativas")

        distancia_total_km = distancia_ida_km * Decimal("2")
        km_excedente = max(Decimal("0"), distancia_total_km - KM_FRANQUICIA)
        precio_sin_redondear = (
            tarifa_hora_base * horas_estimadas + tarifa_km_excedente * km_excedente
        )
        precio_final = precio_sin_redondear.quantize(CENTAVO, rounding=ROUND_HALF_UP)

        return ResultadoCotizacion(
            horas_estimadas=horas_estimadas,
            distancia_ida_km=distancia_ida_km,
            distancia_total_km=distancia_total_km,
            km_franquicia=KM_FRANQUICIA,
            km_excedente=km_excedente,
            tarifa_hora_base=tarifa_hora_base,
            tarifa_km_excedente=tarifa_km_excedente,
            precio_final=precio_final,
        )
