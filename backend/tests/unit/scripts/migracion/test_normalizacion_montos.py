"""Tests de las funciones puras de monto y capacidad (FR-013 a FR-016).

El caso central es el separador argentino: en la planilla el punto es de miles y la coma es decimal,
que es al revés de como lo lee `float()` de Python.
"""

from decimal import Decimal

import pytest

from scripts.migracion.normalizacion import (
    MONEDA_DOLAR,
    MONEDA_PESO,
    normalizar_capacidad,
    normalizar_decimal_argentino,
    normalizar_monto,
)


class TestNormalizarMonto:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("$12.500", Decimal("12500")),
            ("$ 11.000,00", Decimal("11000.00")),
            ("18.000,50", Decimal("18000.50")),
            ("$ 28.000,00", Decimal("28000.00")),
            ("450,00", Decimal("450.00")),
            ("12500", Decimal("12500")),
            ("32000", Decimal("32000")),
            ("98.500,50", Decimal("98500.50")),
            ("$ 55.000", Decimal("55000")),
        ],
    )
    def test_resuelve_el_separador_argentino(self, entrada: str, esperado: Decimal) -> None:
        monto, motivo = normalizar_monto(entrada)

        assert motivo is None
        assert monto.valor == esperado
        assert monto.moneda == MONEDA_PESO

    def test_un_punto_con_tres_digitos_despues_es_de_miles(self) -> None:
        """FR-015: `$12.500` son 12500 pesos, no 12.5."""
        assert normalizar_monto("$12.500")[0].valor == Decimal("12500")

    def test_un_punto_con_un_digito_despues_es_decimal(self) -> None:
        assert normalizar_monto("0.5")[0].valor == Decimal("0.5")

    def test_el_separador_decimal_es_el_que_mas_a_la_derecha_esta(self) -> None:
        assert normalizar_monto("1.234,56")[0].valor == Decimal("1234.56")
        assert normalizar_monto("1,234.56")[0].valor == Decimal("1234.56")

    def test_los_dolares_conservan_su_moneda_y_no_se_convierten(self) -> None:
        """FR-016: convertir sin tipo de cambio confirmado sería inventar el dato."""
        monto, motivo = normalizar_monto("U$S 15")

        assert motivo is None
        assert monto.valor == Decimal("15")
        assert monto.moneda == MONEDA_DOLAR
        assert monto.es_extranjera is True

    def test_un_decimal_en_dolares_tambien_se_detecta(self) -> None:
        monto, _ = normalizar_monto("U$S 0.5")

        assert monto.valor == Decimal("0.5")
        assert monto.moneda == MONEDA_DOLAR

    @pytest.mark.parametrize("entrada", ["USD 20", "us$ 20", "20 dolares", "20 dólares"])
    def test_reconoce_variantes_de_dolar(self, entrada: str) -> None:
        monto, motivo = normalizar_monto(entrada)

        assert motivo is None
        assert monto.moneda == MONEDA_DOLAR

    def test_un_monto_en_pesos_no_es_extranjero(self) -> None:
        assert normalizar_monto("$ 11.000,00")[0].es_extranjera is False

    def test_un_numero_de_python_se_toma_como_pesos(self) -> None:
        monto, motivo = normalizar_monto(12500)

        assert motivo is None
        assert monto.valor == Decimal("12500")
        assert monto.moneda == MONEDA_PESO

    @pytest.mark.parametrize("vacio", [None, "", "   "])
    def test_una_celda_vacia_devuelve_motivo(self, vacio) -> None:
        monto, motivo = normalizar_monto(vacio)

        assert monto is None
        assert "vacía" in motivo

    def test_un_texto_sin_numero_devuelve_motivo(self) -> None:
        monto, motivo = normalizar_monto("a consultar")

        assert monto is None
        assert "número reconocible" in motivo


class TestNormalizarDecimalArgentino:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("35,5", Decimal("35.5")),
            ("8,5", Decimal("8.5")),
            ("12", Decimal("12")),
            ("65,0", Decimal("65.0")),
            ("22", Decimal("22")),
        ],
    )
    def test_normaliza_los_kilometros(self, entrada: str, esperado: Decimal) -> None:
        numero, motivo = normalizar_decimal_argentino(entrada)

        assert motivo is None
        assert numero == esperado

    def test_tolera_una_unidad_suelta_al_final(self) -> None:
        """FR-026: `Km_Recorridos` no trae símbolo de moneda, pero a veces se le cuela una
        unidad."""
        numero, motivo = normalizar_decimal_argentino("35,5 km")

        assert motivo is None
        assert numero == Decimal("35.5")


class TestNormalizarCapacidad:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("1500 kg", Decimal("1500")),
            ("800kg", Decimal("800")),
            ("500 kgs", Decimal("500")),
            ("1200 kg", Decimal("1200")),
            ("1,5 tn", Decimal("1500")),
            ("3,5 toneladas", Decimal("3500")),
            ("1,2 tn", Decimal("1200")),
        ],
    )
    def test_normaliza_todas_las_unidades_a_kilogramos(
        self, entrada: str, esperado: Decimal
    ) -> None:
        capacidad, motivo = normalizar_capacidad(entrada)

        assert motivo is None
        assert capacidad.kilos == esperado
        assert capacidad.unidad_supuesta is False

    @pytest.mark.parametrize("entrada", ["1000", "3500", "600"])
    def test_sin_unidad_se_asume_kg_y_se_marca_el_supuesto(self, entrada: str) -> None:
        """FR-014: si la celda iba en toneladas, la capacidad quedaría 1000 veces menor."""
        capacidad, motivo = normalizar_capacidad(entrada)

        assert motivo is None
        assert capacidad.kilos == Decimal(entrada)
        assert capacidad.unidad_supuesta is True
        assert capacidad.unidad_original is None

    def test_una_unidad_desconocida_devuelve_motivo(self) -> None:
        capacidad, motivo = normalizar_capacidad("3,5 quintales")

        assert capacidad is None
        assert "no conozco" in motivo

    @pytest.mark.parametrize("vacio", [None, "", "   "])
    def test_una_celda_vacia_devuelve_motivo(self, vacio) -> None:
        capacidad, motivo = normalizar_capacidad(vacio)

        assert capacidad is None
        assert "vacía" in motivo
