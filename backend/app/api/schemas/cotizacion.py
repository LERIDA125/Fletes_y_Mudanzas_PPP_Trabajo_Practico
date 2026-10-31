"""Contratos Pydantic del cálculo de cotizaciones."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.application.cotizacion.calculadora import Cotizacion


class CotizacionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_tipo_vehiculo: int = Field(
        gt=0,
        description="Tipo de vehículo activo que define las tarifas.",
    )
    horas_estimadas: Decimal = Field(
        ge=1,
        max_digits=10,
        decimal_places=2,
        allow_inf_nan=False,
        description="Duración estimada ingresada por el operador; mínimo 1 hora.",
    )
    km_estimados: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
        allow_inf_nan=False,
        description="Kilómetros estimados del recorrido, sin duplicación ni franquicia.",
    )
    requiere_ayudante: bool = Field(
        default=False,
        description="Aplica el recargo fijo por ayudante configurado por la empresa.",
    )
    acceso_escalera: bool = Field(
        default=False,
        description="Aplica el recargo fijo por acceso con escalera configurado por la empresa.",
    )
    zona_concurrida: bool = Field(
        default=False,
        description="Aplica el porcentaje de recargo por zona concurrida.",
    )
    urgencia_mismo_dia: bool = Field(
        default=False,
        description="Aplica el porcentaje de recargo por urgencia para el mismo día.",
    )


class CotizacionRead(BaseModel):
    id_tipo_vehiculo: int
    descripcion_tipo_vehiculo: str
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
    moneda: Literal["ARS"] = "ARS"

    @classmethod
    def de_cotizacion(cls, cotizacion: Cotizacion) -> CotizacionRead:
        resultado = cotizacion.resultado
        return cls(
            id_tipo_vehiculo=cotizacion.id_tipo_vehiculo,
            descripcion_tipo_vehiculo=cotizacion.descripcion_tipo_vehiculo,
            horas_estimadas=resultado.horas_estimadas,
            km_estimados=resultado.km_estimados,
            tarifa_hora_base=resultado.tarifa_hora_base,
            tarifa_km_excedente=resultado.tarifa_km_excedente,
            base_horas=resultado.base_horas,
            base_km=resultado.base_km,
            subtotal_base=resultado.subtotal_base,
            requiere_ayudante=resultado.requiere_ayudante,
            recargo_ayudante=resultado.recargo_ayudante,
            acceso_escalera=resultado.acceso_escalera,
            recargo_escalera=resultado.recargo_escalera,
            subtotal_con_fijos=resultado.subtotal_con_fijos,
            zona_concurrida=resultado.zona_concurrida,
            porcentaje_zona_concurrida=resultado.porcentaje_zona_concurrida,
            importe_recargo_zona_concurrida=resultado.importe_recargo_zona_concurrida,
            urgencia_mismo_dia=resultado.urgencia_mismo_dia,
            porcentaje_urgencia_mismo_dia=resultado.porcentaje_urgencia_mismo_dia,
            importe_recargo_urgencia_mismo_dia=(
                resultado.importe_recargo_urgencia_mismo_dia
            ),
            total_recargos_porcentuales=resultado.total_recargos_porcentuales,
            precio_sugerido=resultado.precio_sugerido,
        )
