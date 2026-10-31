"""Resultado inmutable de una cotización calculada."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.domain.errores import DatoInvalido

CENTAVO = Decimal("0.01")
CERO = Decimal("0.00")


def _cuantizar(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class CotizacionCalculada:
    """Desglose completo del precio sugerido, con entradas y parámetros aplicados."""

    horas_estimadas: Decimal
    km_estimados: Decimal
    tarifa_hora_base: Decimal
    tarifa_km_excedente: Decimal
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
    precio_sugerido: Decimal

    def __post_init__(self) -> None:
        self._validar()

    def _validar(self) -> None:
        for nombre in (
            "horas_estimadas",
            "km_estimados",
            "tarifa_hora_base",
            "tarifa_km_excedente",
            "base_horas",
            "base_km",
            "subtotal_base",
            "recargo_ayudante",
            "recargo_escalera",
            "subtotal_con_fijos",
            "porcentaje_zona_concurrida",
            "importe_recargo_zona_concurrida",
            "porcentaje_urgencia_mismo_dia",
            "importe_recargo_urgencia_mismo_dia",
            "total_recargos_porcentuales",
            "precio_sugerido",
        ):
            valor = getattr(self, nombre)
            if not isinstance(valor, Decimal) or not valor.is_finite():
                raise DatoInvalido(f"{nombre} debe ser un valor numérico finito")
            if valor < 0:
                raise DatoInvalido(f"{nombre} no puede ser negativo")

        if self.horas_estimadas < Decimal("1"):
            raise DatoInvalido("Las horas estimadas deben ser como mínimo 1")

        for nombre in (
            "requiere_ayudante",
            "acceso_escalera",
            "zona_concurrida",
            "urgencia_mismo_dia",
        ):
            if not isinstance(getattr(self, nombre), bool):
                raise DatoInvalido(f"{nombre} debe ser un valor booleano")

        for nombre in (
            "porcentaje_zona_concurrida",
            "porcentaje_urgencia_mismo_dia",
        ):
            if getattr(self, nombre) > Decimal("100"):
                raise DatoInvalido(f"{nombre} no puede superar 100")

        if not self.requiere_ayudante and self.recargo_ayudante != CERO:
            raise DatoInvalido("El recargo por ayudante requiere el modificador activo")
        if not self.acceso_escalera and self.recargo_escalera != CERO:
            raise DatoInvalido("El recargo por escalera requiere el modificador activo")
        if not self.zona_concurrida:
            if (
                self.porcentaje_zona_concurrida != CERO
                or self.importe_recargo_zona_concurrida != CERO
            ):
                raise DatoInvalido("El recargo por zona requiere el modificador activo")
        if not self.urgencia_mismo_dia:
            if (
                self.porcentaje_urgencia_mismo_dia != CERO
                or self.importe_recargo_urgencia_mismo_dia != CERO
            ):
                raise DatoInvalido("El recargo por urgencia requiere el modificador activo")

        if _cuantizar(self.subtotal_base) != _cuantizar(self.base_horas + self.base_km):
            raise DatoInvalido("El subtotal base no coincide con la suma de sus componentes")
        if _cuantizar(self.subtotal_con_fijos) != _cuantizar(
            self.subtotal_base + self.recargo_ayudante + self.recargo_escalera
        ):
            raise DatoInvalido("El subtotal con fijos no coincide con la suma de sus componentes")
        if _cuantizar(self.total_recargos_porcentuales) != _cuantizar(
            self.importe_recargo_zona_concurrida + self.importe_recargo_urgencia_mismo_dia
        ):
            raise DatoInvalido("El total de recargos no coincide con la suma de sus componentes")
        if _cuantizar(self.precio_sugerido) != _cuantizar(
            self.subtotal_con_fijos + self.total_recargos_porcentuales
        ):
            raise DatoInvalido("El precio sugerido no coincide con el total del desglose")
