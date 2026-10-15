"""Tests de las funciones puras de fecha y hora (FR-022 a FR-025).

No usan fixtures ni leen archivos: `normalizar_fecha` y `normalizar_hora` solo dependen del
texto que les pasan (FR-037). Si alguno de estos tests necesitara un archivo, es que se coló
una regla de negocio adentro de una función que debía ser pura.
"""

from datetime import date, time

import pytest

from scripts.migracion.normalizacion import (
    ANIO_PIVOTE,
    normalizar_fecha,
    normalizar_hora,
)

# Los cuatro formatos que conviven en la misma columna de la planilla.
LOS_CUATRO_FORMATOS = (
    ("15/05/2026", date(2026, 5, 15)),
    ("2026-05-15", date(2026, 5, 15)),
    ("16 de Mayo 2026", date(2026, 5, 16)),
    ("16/05/26", date(2026, 5, 16)),
)


class TestNormalizarFecha:
    @pytest.mark.parametrize(("entrada", "esperado"), LOS_CUATRO_FORMATOS)
    def test_reconoce_los_cuatro_formatos(self, entrada: str, esperado: date) -> None:
        fecha, motivo = normalizar_fecha(entrada)

        assert motivo is None
        assert fecha is not None
        assert fecha.valor == esperado

    def test_no_asume_el_formato_por_la_posicion_de_la_columna(self) -> None:
        """El mismo texto se interpreta igual en cualquier columna: se detecta por contenido."""
        assert normalizar_fecha("2026-05-15")[0].valor == date(2026, 5, 15)
        assert normalizar_fecha("15/05/2026")[0].valor == date(2026, 5, 15)
        # Y una celda que ya viene como fecha de Excel se acepta tal cual.
        assert normalizar_fecha(date(2026, 5, 15))[0].valor == date(2026, 5, 15)

    def test_acepta_el_mes_en_palabras_sin_tilde(self) -> None:
        fecha, motivo = normalizar_fecha("16 de mayo 2026")

        assert motivo is None
        assert fecha.valor == date(2026, 5, 16)

    def test_acepta_setiembre_como_alias_de_septiembre(self) -> None:
        assert normalizar_fecha("01 de Setiembre 2026")[0].valor == date(2026, 9, 1)

    def test_el_ano_de_dos_digitos_se_proyecta_al_siglo_veintiuno(self) -> None:
        """FR-023: `26` se proyecta con el criterio de `strptime("%y")`, y el caso se reporta."""
        fecha, motivo = normalizar_fecha("16/05/26")

        assert motivo is None
        assert fecha.valor == date(2026, 5, 16)
        # Y queda marcado como supuesto, porque el dato no lo confirma.
        assert fecha.anio_supuesto is True

    def test_un_ano_de_cuatro_digitos_no_se_marca_como_supuesto(self) -> None:
        fecha, _ = normalizar_fecha("15/05/2026")

        assert fecha.anio_supuesto is False

    def test_el_rango_del_pivote_se_proyecta_al_siglo_xx(self) -> None:
        """El mismo criterio de `strptime('%y')`: los años chicos al XXI, los grandes al XX."""
        assert ANIO_PIVOTE == 50
        assert normalizar_fecha("16/05/26")[0].valor.year == 2026
        assert normalizar_fecha("16/05/75")[0].valor.year == 1975

    def test_rechaza_una_fecha_que_no_existe_en_el_calendario(self) -> None:
        """FR-024: un 31 de febrero se rechaza en vez de 'corregirse' a marzo."""
        fecha, motivo = normalizar_fecha("31/02/2026")

        assert fecha is None
        assert "calendario" in motivo

    def test_rechaza_un_mes_que_no_existe(self) -> None:
        fecha, motivo = normalizar_fecha("15/13/2026")

        assert fecha is None
        assert motivo is not None

    def test_rechaza_un_mes_en_palabras_desconocido(self) -> None:
        fecha, motivo = normalizar_fecha("16 de Smarch 2026")

        assert fecha is None
        assert "palabras" in motivo

    @pytest.mark.parametrize("vacio", [None, "", "   "])
    def test_una_celda_vacia_devuelve_motivo(self, vacio) -> None:
        fecha, motivo = normalizar_fecha(vacio)

        assert fecha is None
        assert "vacía" in motivo

    def test_un_texto_que_no_es_fecha_devuelve_motivo(self) -> None:
        fecha, motivo = normalizar_fecha("el jueves que viene")

        assert fecha is None
        assert "ninguno de los formatos" in motivo

    def test_el_formato_de_origen_queda_registrado(self) -> None:
        assert normalizar_fecha("15/05/2026")[0].formato_origen == "dd/mm/aaaa"
        assert normalizar_fecha("2026-05-15")[0].formato_origen == "aaaa-mm-dd"
        assert normalizar_fecha("16/05/26")[0].formato_origen == "dd/mm/aa"


class TestNormalizarHora:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("08:30", time(8, 30)),
            ("12:00", time(12, 0)),
            ("21:00", time(21, 0)),
            ("2:30 PM", time(14, 30)),
            ("5:00 PM", time(17, 0)),
            ("03:00 PM", time(15, 0)),
            ("08:00 AM", time(8, 0)),
            ("11:30 AM", time(11, 30)),
            ("12:00 AM", time(0, 0)),
            ("12:00 PM", time(12, 0)),
        ],
    )
    def test_normaliza_veinticuatro_y_doce_horas(self, entrada: str, esperado: time) -> None:
        hora, motivo = normalizar_hora(entrada)

        assert motivo is None
        assert hora == esperado

    def test_acepta_punto_como_separador(self) -> None:
        assert normalizar_hora("08.30")[0] == time(8, 30)

    def test_acepta_el_meridiano_con_punto(self) -> None:
        assert normalizar_hora("2:30 p.m.")[0] == time(14, 30)

    def test_rechaza_una_hora_con_meridiano_fuera_de_rango(self) -> None:
        """Un 13 PM no se convierte a 25:00: se rechaza."""
        hora, motivo = normalizar_hora("13:00 PM")

        assert hora is None
        assert "1 y 12" in motivo

    def test_rechaza_un_minuto_invalido(self) -> None:
        hora, motivo = normalizar_hora("08:75")

        assert hora is None
        assert "hora del día" in motivo

    def test_rechaza_una_hora_que_no_es_hora(self) -> None:
        hora, motivo = normalizar_hora("a la mañana")

        assert hora is None
        assert "no parece una hora" in motivo

    def test_rechaza_una_fecha_donde_deberia_haber_una_hora(self) -> None:
        hora, motivo = normalizar_hora(date(2026, 5, 15))

        assert hora is None
        assert "fecha" in motivo

    def test_acepta_un_time_de_python(self) -> None:
        assert normalizar_hora(time(8, 30))[0] == time(8, 30)

    @pytest.mark.parametrize("vacio", [None, "", "   "])
    def test_una_celda_vacia_devuelve_motivo(self, vacio) -> None:
        hora, motivo = normalizar_hora(vacio)

        assert hora is None
        assert "vacía" in motivo
