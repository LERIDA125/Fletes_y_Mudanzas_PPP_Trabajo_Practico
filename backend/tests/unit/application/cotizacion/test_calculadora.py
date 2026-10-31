from decimal import Decimal

import pytest

from app.application.cotizacion.estrategias.por_hora_km_modificadores import (
    EstrategiaPorHoraKmModificadores,
)
from app.domain.configuracion_cotizacion import ConfiguracionCotizacion
from app.domain.errores import ConfiguracionCotizacionInvalida, DatoInvalido

CONFIGURACION = ConfiguracionCotizacion(
    recargo_ayudante=Decimal("500.00"),
    recargo_escalera=Decimal("300.00"),
    porcentaje_zona_concurrida=Decimal("15.00"),
    porcentaje_urgencia_mismo_dia=Decimal("20.00"),
)


def test_precio_sugerido_con_todos_los_modificadores() -> None:
    resultado = EstrategiaPorHoraKmModificadores().calcular(
        horas_estimadas=Decimal("2"),
        km_estimados=Decimal("10"),
        tarifa_hora_base=Decimal("3000.00"),
        tarifa_km_excedente=Decimal("150.00"),
        configuracion=CONFIGURACION,
        requiere_ayudante=True,
        acceso_escalera=True,
        zona_concurrida=True,
        urgencia_mismo_dia=True,
    )

    assert resultado.base_horas == Decimal("6000.00")
    assert resultado.base_km == Decimal("1500.00")
    assert resultado.subtotal_base == Decimal("7500.00")
    assert resultado.subtotal_con_fijos == Decimal("8300.00")
    assert resultado.importe_recargo_zona_concurrida == Decimal("1245.00")
    assert resultado.importe_recargo_urgencia_mismo_dia == Decimal("1660.00")
    assert resultado.total_recargos_porcentuales == Decimal("2905.00")
    assert resultado.precio_sugerido == Decimal("11205.00")


def test_precio_sugerido_sin_modificadores_no_aplica_recargos() -> None:
    resultado = EstrategiaPorHoraKmModificadores().calcular(
        horas_estimadas=Decimal("2"),
        km_estimados=Decimal("10"),
        tarifa_hora_base=Decimal("3000.00"),
        tarifa_km_excedente=Decimal("150.00"),
        configuracion=CONFIGURACION,
    )

    assert resultado.base_horas == Decimal("6000.00")
    assert resultado.base_km == Decimal("1500.00")
    assert resultado.subtotal_base == Decimal("7500.00")
    assert resultado.subtotal_con_fijos == Decimal("7500.00")
    assert resultado.recargo_ayudante == Decimal("0.00")
    assert resultado.recargo_escalera == Decimal("0.00")
    assert resultado.importe_recargo_zona_concurrida == Decimal("0.00")
    assert resultado.importe_recargo_urgencia_mismo_dia == Decimal("0.00")
    assert resultado.total_recargos_porcentuales == Decimal("0.00")
    assert resultado.precio_sugerido == Decimal("7500.00")


def test_redondea_empate_con_half_up_por_componente() -> None:
    resultado = EstrategiaPorHoraKmModificadores().calcular(
        horas_estimadas=Decimal("1.5"),
        km_estimados=Decimal("0"),
        tarifa_hora_base=Decimal("100.01"),
        tarifa_km_excedente=Decimal("0"),
        configuracion=CONFIGURACION,
    )

    assert resultado.base_horas == Decimal("150.02")
    assert resultado.precio_sugerido == Decimal("150.02")


@pytest.mark.parametrize(
    ("horas", "kilometros"),
    [(Decimal("0.99"), Decimal("0")), (Decimal("1"), Decimal("-0.01"))],
)
def test_rechaza_duracion_o_kilometros_invalidos(horas: Decimal, kilometros: Decimal) -> None:
    with pytest.raises(DatoInvalido):
        EstrategiaPorHoraKmModificadores().calcular(
            horas_estimadas=horas,
            km_estimados=kilometros,
            tarifa_hora_base=Decimal("100"),
            tarifa_km_excedente=Decimal("10"),
            configuracion=CONFIGURACION,
        )


def test_rechaza_configuracion_invalida() -> None:
    with pytest.raises(ConfiguracionCotizacionInvalida):
        ConfiguracionCotizacion(
            recargo_ayudante=Decimal("-1"),
            recargo_escalera=Decimal("0"),
            porcentaje_zona_concurrida=Decimal("0"),
            porcentaje_urgencia_mismo_dia=Decimal("0"),
        )
