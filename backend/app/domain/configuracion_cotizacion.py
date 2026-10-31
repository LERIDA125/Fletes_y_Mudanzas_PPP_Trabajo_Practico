"""Configuración de negocio para el cálculo de cotizaciones."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.errores import ConfiguracionCotizacionInvalida


@dataclass(frozen=True)
class ConfiguracionCotizacion:
    recargo_ayudante: Decimal
    recargo_escalera: Decimal
    porcentaje_zona_concurrida: Decimal
    porcentaje_urgencia_mismo_dia: Decimal

    def __post_init__(self) -> None:
        for nombre in (
            "recargo_ayudante",
            "recargo_escalera",
            "porcentaje_zona_concurrida",
            "porcentaje_urgencia_mismo_dia",
        ):
            valor = getattr(self, nombre)
            if not isinstance(valor, Decimal) or not valor.is_finite():
                raise ConfiguracionCotizacionInvalida(
                    f"{nombre} debe ser un valor numérico finito"
                )
            if valor < 0:
                raise ConfiguracionCotizacionInvalida(f"{nombre} no puede ser negativo")

        for nombre in ("porcentaje_zona_concurrida", "porcentaje_urgencia_mismo_dia"):
            if getattr(self, nombre) > Decimal("100"):
                raise ConfiguracionCotizacionInvalida(f"{nombre} no puede superar 100")
