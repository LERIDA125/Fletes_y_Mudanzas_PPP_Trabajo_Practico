"""Estrategia aprobada: tarifa horaria más kilómetros que exceden la franquicia."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.domain.errores import DatoInvalido

KM_FRANQUICIA = Decimal("10")
CENTAVO = Decimal("0.01")
CERO = Decimal("0.00")
RECARGO_AYUDANTE = Decimal("30000.00")
RECARGO_ESCALERA = Decimal("15000.00")
PORCENTAJE_ZONA_CONCURRIDA = Decimal("15.00")
PORCENTAJE_URGENCIA_MISMO_DIA = Decimal("20.00")


def _cuantizar(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


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
    base_horas: Decimal
    base_km: Decimal
    subtotal_base: Decimal
    requiere_ayudante: bool
    recargo_ayudante: Decimal
    acceso_escalera: bool
    recargo_escalera: Decimal
    subtotal_con_fijos: Decimal
    zona_concurrida: bool
    porcentaje_zona_concurrida: Decimal
    importe_recargo_zona_concurrida: Decimal
    urgencia_mismo_dia: bool
    porcentaje_urgencia_mismo_dia: Decimal
    importe_recargo_urgencia_mismo_dia: Decimal
    total_recargos_porcentuales: Decimal


class EstrategiaPorHoraYKm:
    """Calcula precio con tarifas suministradas desde la configuración persistida."""

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

        base_horas = _cuantizar(tarifa_hora_base * horas_estimadas)
        base_km = _cuantizar(tarifa_km_excedente * km_excedente)
        subtotal_base = _cuantizar(base_horas + base_km)

        recargo_ayudante = _cuantizar(RECARGO_AYUDANTE) if requiere_ayudante else CERO
        recargo_escalera = _cuantizar(RECARGO_ESCALERA) if acceso_escalera else CERO
        subtotal_con_fijos = _cuantizar(
            subtotal_base + recargo_ayudante + recargo_escalera
        )

        porcentaje_zona = (
            _cuantizar(PORCENTAJE_ZONA_CONCURRIDA) if zona_concurrida else CERO
        )
        importe_zona = (
            _cuantizar(subtotal_con_fijos * porcentaje_zona / Decimal("100"))
            if zona_concurrida
            else CERO
        )

        porcentaje_urgencia = (
            _cuantizar(PORCENTAJE_URGENCIA_MISMO_DIA) if urgencia_mismo_dia else CERO
        )
        importe_urgencia = (
            _cuantizar(subtotal_con_fijos * porcentaje_urgencia / Decimal("100"))
            if urgencia_mismo_dia
            else CERO
        )

        total_recargos_porcentuales = _cuantizar(importe_zona + importe_urgencia)
        precio_final = _cuantizar(subtotal_con_fijos + total_recargos_porcentuales)

        return ResultadoCotizacion(
            horas_estimadas=horas_estimadas,
            distancia_ida_km=distancia_ida_km,
            distancia_total_km=distancia_total_km,
            km_franquicia=KM_FRANQUICIA,
            km_excedente=km_excedente,
            tarifa_hora_base=tarifa_hora_base,
            tarifa_km_excedente=tarifa_km_excedente,
            precio_final=precio_final,
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
        )
