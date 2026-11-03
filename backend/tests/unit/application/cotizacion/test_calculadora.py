from decimal import Decimal

import pytest

from app.application.cotizacion.estrategias.por_hora_y_km import EstrategiaPorHoraYKm
from app.domain.errores import DatoInvalido


def test_calcula_total_y_kilometros_excedentes() -> None:
    resultado = EstrategiaPorHoraYKm().calcular(
        horas_estimadas=Decimal("2"),
        distancia_ida_km=Decimal("15"),
        tarifa_hora_base=Decimal("3000.00"),
        tarifa_km_excedente=Decimal("150.00"),
    )

    assert resultado.distancia_total_km == Decimal("30")
    assert resultado.km_excedente == Decimal("20")
    assert resultado.precio_final == Decimal("9000.00")


def test_no_cobra_kilometros_dentro_de_la_franquicia() -> None:
    resultado = EstrategiaPorHoraYKm().calcular(
        horas_estimadas=Decimal("4"),
        distancia_ida_km=Decimal("4"),
        tarifa_hora_base=Decimal("1000.00"),
        tarifa_km_excedente=Decimal("250.00"),
    )

    assert resultado.distancia_total_km == Decimal("8")
    assert resultado.km_excedente == Decimal("0")
    assert resultado.precio_final == Decimal("4000.00")


def test_redondea_empate_con_half_up() -> None:
    resultado = EstrategiaPorHoraYKm().calcular(
        horas_estimadas=Decimal("1.5"),
        distancia_ida_km=Decimal("0"),
        tarifa_hora_base=Decimal("100.01"),
        tarifa_km_excedente=Decimal("0"),
    )

    assert resultado.precio_final == Decimal("150.02")


def test_aplica_recargos_fijos_de_ayudante_y_escalera() -> None:
    resultado = EstrategiaPorHoraYKm().calcular(
        horas_estimadas=Decimal("2"),
        distancia_ida_km=Decimal("15"),
        tarifa_hora_base=Decimal("3000.00"),
        tarifa_km_excedente=Decimal("150.00"),
        requiere_ayudante=True,
        acceso_escalera=True,
    )

    assert resultado.subtotal_base == Decimal("9000.00")
    assert resultado.recargo_ayudante == Decimal("30000.00")
    assert resultado.recargo_escalera == Decimal("15000.00")
    assert resultado.subtotal_con_fijos == Decimal("54000.00")
    assert resultado.precio_final == Decimal("54000.00")


def test_aplica_recargos_porcentuales_sobre_el_subtotal_con_fijos() -> None:
    resultado = EstrategiaPorHoraYKm().calcular(
        horas_estimadas=Decimal("2"),
        distancia_ida_km=Decimal("15"),
        tarifa_hora_base=Decimal("3000.00"),
        tarifa_km_excedente=Decimal("150.00"),
        zona_concurrida=True,
        urgencia_mismo_dia=True,
    )

    assert resultado.porcentaje_zona_concurrida == Decimal("15.00")
    assert resultado.importe_recargo_zona_concurrida == Decimal("1350.00")
    assert resultado.porcentaje_urgencia_mismo_dia == Decimal("20.00")
    assert resultado.importe_recargo_urgencia_mismo_dia == Decimal("1800.00")
    assert resultado.total_recargos_porcentuales == Decimal("3150.00")
    assert resultado.precio_final == Decimal("12150.00")


def test_combina_recargos_fijos_y_porcentuales() -> None:
    resultado = EstrategiaPorHoraYKm().calcular(
        horas_estimadas=Decimal("2"),
        distancia_ida_km=Decimal("15"),
        tarifa_hora_base=Decimal("3000.00"),
        tarifa_km_excedente=Decimal("150.00"),
        requiere_ayudante=True,
        zona_concurrida=True,
        urgencia_mismo_dia=True,
    )

    assert resultado.subtotal_con_fijos == Decimal("39000.00")
    assert resultado.importe_recargo_zona_concurrida == Decimal("5850.00")
    assert resultado.importe_recargo_urgencia_mismo_dia == Decimal("7800.00")
    assert resultado.precio_final == Decimal("52650.00")


@pytest.mark.parametrize(
    ("horas", "distancia"),
    [(Decimal("0.99"), Decimal("0")), (Decimal("1"), Decimal("-0.01"))],
)
def test_rechaza_duracion_o_distancia_invalida(horas: Decimal, distancia: Decimal) -> None:
    with pytest.raises(DatoInvalido):
        EstrategiaPorHoraYKm().calcular(
            horas_estimadas=horas,
            distancia_ida_km=distancia,
            tarifa_hora_base=Decimal("100"),
            tarifa_km_excedente=Decimal("10"),
        )
