"""Tests de las funciones puras de teléfono (FR-010, FR-011).

El caso importante es el que no es un teléfono: la planilla tiene al menos una celda donde el
administrador escribió una frase en vez de un número, y esa celda tiene que terminar en `NULL` y no
en un teléfono inventado.
"""

import pytest

from app.domain.cliente import TELEFONO_DIGITOS_MAX, TELEFONO_DIGITOS_MIN
from scripts.migracion.normalizacion import normalizar_telefono


class TestNormalizarTelefono:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("11-4455-6677", "1144556677"),
            ("+5491144556677", "5491144556677"),
            ("15-3322-9988", "1533229988"),
            ("011 5566-7788", "01155667788"),
            ("+54 9 11 2233 4455", "5491122334455"),
            ("1166778899", "1166778899"),
            ("11 2345 6789", "1123456789"),
        ],
    )
    def test_deja_solo_digitos(self, entrada: str, esperado: str) -> None:
        telefono, motivo = normalizar_telefono(entrada)

        assert motivo is None
        assert telefono.digitos == esperado

    @pytest.mark.parametrize("entrada", ["No tiene whatsapp", "sin telefono", "n/a", "-"])
    def test_una_anotacion_no_es_un_telefono(self, entrada: str) -> None:
        """FR-010: no se inventa un teléfono, se devuelve `None` con el motivo."""
        telefono, motivo = normalizar_telefono(entrada)

        assert telefono is None
        assert motivo is not None

    def test_el_mensaje_dice_que_no_es_un_telefono(self) -> None:
        telefono, motivo = normalizar_telefono("No tiene whatsapp")

        assert telefono is None
        assert "no es un teléfono" in motivo

    @pytest.mark.parametrize("vacio", [None, "", "   "])
    def test_una_celda_vacia_devuelve_motivo(self, vacio) -> None:
        telefono, motivo = normalizar_telefono(vacio)

        assert telefono is None
        assert "vacía" in motivo

    def test_un_texto_sin_digitos_devuelve_motivo(self) -> None:
        telefono, motivo = normalizar_telefono("consultar con el encargado")

        assert telefono is None
        assert "ningún dígito" in motivo

    @pytest.mark.parametrize(
        "entrada",
        ["+54 9 11 2233 4455", "+5491122334455", "54911 2233 4455"],
    )
    def test_marca_los_valores_que_traen_prefijo_internacional(self, entrada: str) -> None:
        """FR-011: se marca, no se decide. Cómo se guardan los teléfonos es regla de H1 (DD-4)."""
        telefono, _ = normalizar_telefono(entrada)

        assert telefono.digitos_con_pais is True

    def test_un_telefono_nacional_no_se_marca_con_pais(self) -> None:
        telefono, _ = normalizar_telefono("11-4455-6677")

        assert telefono.digitos_con_pais is False

    def test_la_compatibilidad_con_h1_se_mide_en_digitos(self) -> None:
        """H1 valida entre 7 y 20 dígitos (FR-005); el flag lo dice sin volver a mirar la regla."""
        valido, _ = normalizar_telefono("11-4455-6677")
        assert valido.es_valido_para_h1 is True

        corto, _ = normalizar_telefono("123")
        assert corto.es_valido_para_h1 is False

        largo, _ = normalizar_telefono("1" * (TELEFONO_DIGITOS_MAX + 1))
        assert largo.es_valido_para_h1 is False

    def test_los_limites_de_h1_son_los_que_la_migracion_usa(self) -> None:
        """Si H1 cambia el rango, esta migración lo hereda en vez de tener su propio número."""
        exacto_min, _ = normalizar_telefono("1" * TELEFONO_DIGITOS_MIN)
        exacto_max, _ = normalizar_telefono("1" * TELEFONO_DIGITOS_MAX)

        assert exacto_min.es_valido_para_h1 is True
        assert exacto_max.es_valido_para_h1 is True

    def test_un_numero_de_python_se_acepta(self) -> None:
        telefono, motivo = normalizar_telefono(1144556677)

        assert motivo is None
        assert telefono.digitos == "1144556677"
