"""Tests de las funciones puras de monto y capacidad (FR-013 a FR-016).

El caso central es el separador argentino: en la planilla el punto es de miles y la coma es decimal,
que es al revés de como lo lee `float()` de Python.
"""

from decimal import Decimal

from scripts.migracion.normalizacion import (
    MONEDA_DOLAR,
    MONEDA_PESO,
    normalizar_capacidad,
    normalizar_decimal_argentino,
    normalizar_monto,
)


class TestNormalizarMonto:
    def test_resuelve_el_separador_argentino_y_formatos_peso(self) -> None:
        casos = [
            ("$12.500", Decimal("12500")),
            ("$ 11.000,00", Decimal("11000.00")),
            ("18.000,50", Decimal("18000.50")),
            ("$ 28.000,00", Decimal("28000.00")),
            ("450,00", Decimal("450.00")),
            ("12500", Decimal("12500")),
            ("32000", Decimal("32000")),
            ("98.500,50", Decimal("98500.50")),
            ("$ 55.000", Decimal("55000")),
            ("0.5", Decimal("0.5")),
            ("1.234,56", Decimal("1234.56")),
            ("1,234.56", Decimal("1234.56")),
            (12500, Decimal("12500")),
        ]
        for entrada, esperado in casos:
            monto, motivo = normalizar_monto(entrada)
            assert motivo is None
            assert monto.valor == esperado
            assert monto.moneda == MONEDA_PESO
            assert monto.es_extranjera is False

    def test_dolares_conservan_moneda_y_variantes(self) -> None:
        """FR-016: convertir sin tipo de cambio confirmado sería inventar el dato."""
        for entrada, valor_esperado in [
            ("U$S 15", Decimal("15")),
            ("U$S 0.5", Decimal("0.5")),
            ("USD 20", Decimal("20")),
            ("us$ 20", Decimal("20")),
            ("20 dolares", Decimal("20")),
            ("20 dólares", Decimal("20")),
        ]:
            monto, motivo = normalizar_monto(entrada)
            assert motivo is None
            assert monto.valor == valor_esperado
            assert monto.moneda == MONEDA_DOLAR
            assert monto.es_extranjera is True

    def test_celdas_vacias_o_sin_numero_devuelven_motivo(self) -> None:
        for vacio in [None, "", "   ", "a consultar"]:
            monto, motivo = normalizar_monto(vacio)
            assert monto is None
            assert motivo is not None


class TestNormalizarDecimalArgentino:
    def test_normaliza_los_kilometros(self) -> None:
        casos = [
            ("35,5", Decimal("35.5")),
            ("8,5", Decimal("8.5")),
            ("12", Decimal("12")),
            ("65,0", Decimal("65.0")),
            ("22", Decimal("22")),
            ("35,5 km", Decimal("35.5")),
        ]
        for entrada, esperado in casos:
            numero, motivo = normalizar_decimal_argentino(entrada)
            assert motivo is None
            assert numero == esperado


class TestNormalizarCapacidad:
    def test_normaliza_todas_las_unidades_a_kilogramos(self) -> None:
        casos = [
            ("1500 kg", Decimal("1500")),
            ("800kg", Decimal("800")),
            ("500 kgs", Decimal("500")),
            ("1200 kg", Decimal("1200")),
            ("1,5 tn", Decimal("1500")),
            ("3,5 toneladas", Decimal("3500")),
            ("1,2 tn", Decimal("1200")),
        ]
        for entrada, esperado in casos:
            capacidad, motivo = normalizar_capacidad(entrada)
            assert motivo is None
            assert capacidad.kilos == esperado
            assert capacidad.unidad_supuesta is False

    def test_sin_unidad_se_asume_kg_y_se_marca_el_supuesto(self) -> None:
        """FR-014: si la celda iba en toneladas, la capacidad quedaría 1000 veces menor."""
        for entrada in ["1000", "3500", "600"]:
            capacidad, motivo = normalizar_capacidad(entrada)
            assert motivo is None
            assert capacidad.kilos == Decimal(entrada)
            assert capacidad.unidad_supuesta is True
            assert capacidad.unidad_original is None

    def test_unidad_desconocida_o_vacia_devuelve_motivo(self) -> None:
        for invalido in ["3,5 quintales", None, "", "   "]:
            capacidad, motivo = normalizar_capacidad(invalido)
            assert capacidad is None
            assert motivo is not None
