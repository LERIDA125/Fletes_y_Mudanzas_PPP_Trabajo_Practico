"""Tests de las funciones puras de fecha y hora (FR-022 a FR-025).

No usan fixtures ni leen archivos: `normalizar_fecha` y `normalizar_hora` solo dependen del
texto que les pasan (FR-037).
"""

from datetime import date, time

from scripts.migracion.normalizacion import (
    ANIO_PIVOTE,
    normalizar_fecha,
    normalizar_hora,
)


class TestNormalizarFecha:
    def test_reconoce_formatos_validos_y_variantes(self) -> None:
        casos = [
            ("15/05/2026", date(2026, 5, 15)),
            ("2026-05-15", date(2026, 5, 15)),
            ("16 de Mayo 2026", date(2026, 5, 16)),
            ("16 de mayo 2026", date(2026, 5, 16)),
            ("01 de Setiembre 2026", date(2026, 9, 1)),
            ("16/05/26", date(2026, 5, 16)),
            (date(2026, 5, 15), date(2026, 5, 15)),
        ]
        for entrada, esperado in casos:
            fecha, motivo = normalizar_fecha(entrada)
            assert motivo is None
            assert fecha is not None
            assert fecha.valor == esperado

    def test_proyeccion_de_anio_y_supuestos(self) -> None:
        """FR-023: dos dígitos se proyectan con pivote y se reportan."""
        assert ANIO_PIVOTE == 50
        fecha_26, _ = normalizar_fecha("16/05/26")
        assert fecha_26.valor == date(2026, 5, 16)
        assert fecha_26.anio_supuesto is True

        fecha_75, _ = normalizar_fecha("16/05/75")
        assert fecha_75.valor.year == 1975

        fecha_completa, _ = normalizar_fecha("15/05/2026")
        assert fecha_completa.anio_supuesto is False

    def test_fechas_invalidas_o_vacias_devuelven_motivo(self) -> None:
        """FR-024: una fecha que no existe se rechaza."""
        invalidos = ["31/02/2026", "15/13/2026", "16 de Smarch 2026", None, "", "   ", "el jueves"]
        for entrada in invalidos:
            fecha, motivo = normalizar_fecha(entrada)
            assert fecha is None
            assert motivo is not None

    def test_el_formato_de_origen_queda_registrado(self) -> None:
        assert normalizar_fecha("15/05/2026")[0].formato_origen == "dd/mm/aaaa"
        assert normalizar_fecha("2026-05-15")[0].formato_origen == "aaaa-mm-dd"
        assert normalizar_fecha("16/05/26")[0].formato_origen == "dd/mm/aa"


class TestNormalizarHora:
    def test_normaliza_veinticuatro_y_doce_horas_con_variantes(self) -> None:
        casos = [
            ("08:30", time(8, 30)),
            ("08.30", time(8, 30)),
            ("12:00", time(12, 0)),
            ("21:00", time(21, 0)),
            ("2:30 PM", time(14, 30)),
            ("2:30 p.m.", time(14, 30)),
            ("5:00 PM", time(17, 0)),
            ("03:00 PM", time(15, 0)),
            ("08:00 AM", time(8, 0)),
            ("11:30 AM", time(11, 30)),
            ("12:00 AM", time(0, 0)),
            ("12:00 PM", time(12, 0)),
            (time(8, 30), time(8, 30)),
        ]
        for entrada, esperado in casos:
            hora, motivo = normalizar_hora(entrada)
            assert motivo is None
            assert hora == esperado

    def test_horas_invalidas_o_vacias_devuelven_motivo(self) -> None:
        invalidos = ["13:00 PM", "08:75", "a la mañana", date(2026, 5, 15), None, "", "   "]
        for entrada in invalidos:
            hora, motivo = normalizar_hora(entrada)
            assert hora is None
            assert motivo is not None
