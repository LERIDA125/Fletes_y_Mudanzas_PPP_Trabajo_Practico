"""Pruebas de Dominio de rendiciones: saldo, gastos y estados."""

from datetime import date
from decimal import Decimal

import pytest

from app.domain.errores import DatoInvalido, EstadoRendicionInvalido
from app.domain.rendicion import Rendicion


def _rendicion(**overrides) -> Rendicion:
    datos = {
        "id_servicio": 10,
        "id_chofer": 3,
        "fecha": date(2026, 11, 3),
        "tarifa": Decimal("18500.00"),
        "adelanto": Decimal("12000.00"),
        "gasto_combustible": Decimal("2000.00"),
        "gasto_peajes": Decimal("300.00"),
        "gasto_otros": Decimal("200.00"),
    }
    datos.update(overrides)
    return Rendicion.crear(**datos)


def test_calcula_gastos_totales_y_saldo() -> None:
    rendicion = _rendicion()

    assert rendicion.gastos_total == Decimal("2500.00")
    assert rendicion.saldo == Decimal("4000.00")
    assert rendicion.estado == "pendiente"
    assert rendicion.codigo is None


def test_permite_saldo_negativo() -> None:
    rendicion = _rendicion(
        tarifa=Decimal("1000.00"),
        adelanto=Decimal("900.00"),
        gasto_combustible=Decimal("500.00"),
        gasto_peajes=Decimal("0.00"),
        gasto_otros=Decimal("0.00"),
    )

    assert rendicion.saldo == Decimal("-400.00")


def test_redondea_a_dos_decimales_con_half_up() -> None:
    rendicion = _rendicion(
        tarifa=Decimal("10.005"),
        adelanto=Decimal("0.00"),
        gasto_combustible=Decimal("0.00"),
        gasto_peajes=Decimal("0.00"),
        gasto_otros=Decimal("0.00"),
    )

    assert rendicion.saldo == Decimal("10.01")


def test_rechaza_importes_negativos() -> None:
    with pytest.raises(DatoInvalido, match="no puede ser negativo"):
        _rendicion(gasto_peajes=Decimal("-1.00"))


def test_normaliza_observaciones_y_valida_longitud() -> None:
    rendicion = _rendicion(observaciones="  Comprobantes entregados  ")
    assert rendicion.observaciones == "Comprobantes entregados"

    vacia = _rendicion(observaciones="   ")
    assert vacia.observaciones is None

    with pytest.raises(DatoInvalido, match="500"):
        _rendicion(observaciones="x" * 501)


def test_cambia_estado_solo_a_valores_validos() -> None:
    rendicion = _rendicion()

    rendicion.cambiar_estado("en revision", modificado_por_id=7)
    assert rendicion.estado == "en revision"
    assert rendicion.modificado_por_id == 7

    with pytest.raises(EstadoRendicionInvalido):
        rendicion.cambiar_estado("cerrada")


def test_exige_servicio_y_chofer() -> None:
    with pytest.raises(DatoInvalido, match="servicio"):
        _rendicion(id_servicio=0)

    with pytest.raises(DatoInvalido, match="chofer"):
        _rendicion(id_chofer=0)
