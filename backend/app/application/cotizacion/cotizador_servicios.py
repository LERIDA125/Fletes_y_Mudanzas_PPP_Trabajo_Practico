"""Caso de uso que cotiza a partir de un tipo de vehículo activo."""

from decimal import Decimal

from app.application.cotizacion.calculadora import CalculadoraCotizacion, Cotizacion


class CotizadorServicios:
    def __init__(
        self,
        *,
        calculadora: CalculadoraCotizacion,
    ) -> None:
        self._calculadora = calculadora

    def cotizar_por_tipo(
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
        return self._calculadora.cotizar(
            id_tipo_vehiculo=id_tipo_vehiculo,
            horas_estimadas=horas_estimadas,
            km_estimados=km_estimados,
            requiere_ayudante=requiere_ayudante,
            acceso_escalera=acceso_escalera,
            zona_concurrida=zona_concurrida,
            urgencia_mismo_dia=urgencia_mismo_dia,
        )
