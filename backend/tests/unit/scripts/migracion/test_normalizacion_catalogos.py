"""Tests de los catálogos y de la normalización contra catálogo (FR-008, FR-012, FR-017 a FR-019,
FR-027).

El criterio de todos estos tests es el mismo: cuando el valor no está en el catálogo, la función
devuelve `None` con un motivo. No devuelve "el más parecido", porque eso sería decidir por la
persona que va a tener que corregirlo después.
"""

import pytest

from scripts.migracion import catalogos as cat
from scripts.migracion.normalizacion import (
    codigo_de_cliente,
    codigo_de_movil,
    codigo_de_viaje,
    es_direccion_no_estructurada,
    normalizar_bultos,
    normalizar_condicion_iva,
    normalizar_estado_movil,
    normalizar_texto,
    normalizar_tipo_vehiculo,
)


class TestCodigos:
    @pytest.mark.parametrize("entrada", ["MOV-01", "MOV01", "mov 01", "MOV 1", "01", "1"])
    def test_el_mismo_movil_escrito_de_varias_formas(self, entrada: str) -> None:
        codigo = codigo_de_movil(entrada)

        assert codigo is not None
        assert codigo.valor == "MOV-01"

    def test_el_prefijo_falta_o_sobra_se_normaliza_igual(self) -> None:
        """`03` y `MOV-03` tienen que ser el mismo código, si no el duplicado no se detecta."""
        assert codigo_de_movil("03").valor == "MOV-03"
        assert codigo_de_movil("MOV-03").valor == "MOV-03"

    def test_el_ancho_de_ceros_deja_según_la_columna(self) -> None:
        assert codigo_de_movil("1").valor == "MOV-01"
        assert codigo_de_viaje("2002").valor == "VJ-2002"
        assert codigo_de_cliente("102").valor == "CLI-102"

    def test_un_codigo_sin_numero_devuelve_none(self) -> None:
        assert codigo_de_movil("sin codigo") is None

    @pytest.mark.parametrize("vacio", [None, "", "   "])
    def test_una_celda_vacia_devuelve_none(self, vacio) -> None:
        assert codigo_de_movil(vacio) is None

    def test_el_prefijo_se_conserva_cuando_esta_escrito(self) -> None:
        """Un prefijo distinto del esperado no se pisa en silencio: queda visible."""
        assert codigo_de_viaje("OTRO-7").valor == "OTRO-0007"


class TestNormalizarTexto:
    def test_ignora_mayusculas_acentos_y_espacios_sobrantes(self) -> None:
        assert normalizar_texto("  Camioneta   Mediana ") == "camioneta mediana"

    def test_compara_igual_con_y_sin_tilde(self) -> None:
        """Es lo que hace que el cruce de nombres del Excel funcione (FR-032)."""
        assert normalizar_texto("Camión") == normalizar_texto("Camion")
        assert normalizar_texto("MARCELO RODRIGUEZ") == normalizar_texto("Marcelo Rodriguez")


class TestTipoVehiculo:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("Furgón Grande", "Furgón Grande"),
            ("Furgon Grande", "Furgón Grande"),
            ("CAMIONETA", "Camioneta"),
            ("camioneta", "Camioneta"),
            ("Camioneta Mediana", "Camioneta Mediana"),
            ("Utilitario", "Utilitario"),
            ("Camión Mudancero", "Camión Mudancero"),
        ],
    )
    def test_normaliza_las_variantes_de_mayusculas_y_tildes(
        self, entrada: str, esperado: str
    ) -> None:
        tipo, motivo = normalizar_tipo_vehiculo(entrada)

        assert motivo is None
        assert tipo == esperado

    def test_un_tipo_fuera_del_catalogo_no_se_fuerza_al_mas_parecido(self) -> None:
        """FR-012: forzar el más parecido es inventar un dato que alguien va a corregir después."""
        tipo, motivo = normalizar_tipo_vehiculo("Camioneta con jaula")

        assert tipo is None
        assert "no está en el catálogo" in motivo

    def test_todo_tipo_del_archivo_real_esta_en_el_catalogo(self) -> None:
        for tipo in cat.TIPOS_VEHICULO_CANONICOS:
            assert normalizar_tipo_vehiculo(tipo)[0] == tipo


class TestEstadoMovil:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("Disponible", cat.ESTADO_DISPONIBLE),
            ("Libre", cat.ESTADO_DISPONIBLE),
            ("En viaje", cat.ESTADO_OCUPADO),
            ("Suspendido por choque", cat.ESTADO_INACTIVO),
            ("Rompió el elástico", cat.ESTADO_INACTIVO),
        ],
    )
    def test_normaliza_los_estados_directos(self, entrada: str, esperado: str) -> None:
        estado, texto_original, motivo = normalizar_estado_movil(entrada)

        assert estado == esperado
        # El texto original nunca se descarta, ni siquiera cuando el mapeo es directo.
        assert texto_original == entrada
        assert motivo is None

    @pytest.mark.parametrize("entrada", ["En taller hasta el martes", "De franco"])
    def test_un_estado_ambiguo_se_mapea_pero_se_reporta(self, entrada: str) -> None:
        """FR-018 / DP-02: se mapea al estado provisional y se avisa, porque la elección importa."""
        estado, texto_original, motivo = normalizar_estado_movil(entrada)

        assert estado in cat.ESTADOS_CANONICOS
        assert texto_original == entrada
        assert motivo is not None
        assert "más de una lectura" in motivo

    def test_el_texto_libre_siempre_queda_como_observacion(self) -> None:
        _, texto_original, _ = normalizar_estado_movil("Rompió el elástico")

        assert texto_original == "Rompió el elástico"

    def test_un_estado_fuera_del_catalogo_no_se_fuerza(self) -> None:
        estado, texto_original, motivo = normalizar_estado_movil(
            "El auto está en el taller de laterminal"
        )

        assert estado is None
        assert texto_original is not None
        assert "no está en el catálogo" in motivo

    def test_una_celda_vacia_devuelve_motivo(self) -> None:
        estado, _, motivo = normalizar_estado_movil(None)

        assert estado is None
        assert "vacía" in motivo


class TestCondicionIva:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("Responsable Inscripto", "Responsable Inscripto"),
            ("Resp. Inscripto", "Responsable Inscripto"),
            ("Consumidor Final", "Consumidor Final"),
            ("Exento", "Exento"),
        ],
    )
    def test_normaliza_las_abreviaturas(self, entrada: str, esperado: str) -> None:
        condicion, motivo = normalizar_condicion_iva(entrada)

        assert motivo is None
        assert condicion == esperado

    def test_una_condicion_fuera_del_catalogo_devuelve_motivo(self) -> None:
        condicion, motivo = normalizar_condicion_iva("Monotributista")

        assert condicion is None
        assert "no está en el catálogo" in motivo


class TestDireccionNoEstructurada:
    @pytest.mark.parametrize(
        "entrada",
        ["Retira en depósito", "retirar en deposito", "A retirar en depósito", "Consultar"],
    )
    def test_detecta_lo_que_no_es_una_direccion_postal(self, entrada: str) -> None:
        assert es_direccion_no_estructurada(entrada) is True

    @pytest.mark.parametrize(
        "entrada",
        ["Av. Cabildo 2140", "Cucha Cucha 1200 timbre 2", "Thames 1450"],
    )
    def test_una_direccion_de_verdad_no_se_marca(self, entrada: str) -> None:
        assert es_direccion_no_estructurada(entrada) is False

    def test_una_celda_vacia_no_se_marca(self) -> None:
        assert es_direccion_no_estructurada(None) is False


class TestBultos:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("6 muebles embalados", 6),
            ("30 cajas surtidas", 30),
            ("15 monitores", 15),
        ],
    )
    def test_extrae_el_numero_cuando_hay_uno_solo(self, entrada: str, esperado: int) -> None:
        bultos, motivo = normalizar_bultos(entrada)

        assert motivo is None
        assert bultos.cantidad == esperado
        assert bultos.es_texto_libre is False

    def test_no_extrae_numero_de_una_celda_que_describe_un_servicio(self) -> None:
        """`Sonido y luces` no es una cantidad de bultos: es ni siquiera un dato de ese tipo."""
        bultos, motivo = normalizar_bultos("Sonido y luces")

        assert bultos.cantidad is None
        assert bultos.es_texto_libre is True
        assert "describe un servicio" in motivo

    def test_no_extrae_numero_de_una_celda_sin_cantidad(self) -> None:
        bultos, motivo = normalizar_bultos("Archivadores pesados")

        assert bultos.cantidad is None
        assert "no dice cuántos bultos" in motivo

    @pytest.mark.parametrize(
        "entrada", ["10 cajas y 1 heladera", "4 mancuernas y 2 bancos", "1 sillon 3 cuerpos"]
    )
    def test_con_dos_numeros_no_elige_ni_suma(self, entrada: str) -> None:
        """Se podría sumar o elegir el primero: ninguna de las dos es lo que dice la celda."""
        bultos, motivo = normalizar_bultos(entrada)

        assert bultos.cantidad is None
        assert "2 cantidades" in motivo

    @pytest.mark.parametrize("vacio", [None, "", "   "])
    def test_una_celda_vacia_devuelve_motivo(self, vacio) -> None:
        bultos, motivo = normalizar_bultos(vacio)

        assert bultos.cantidad is None
        assert "vacía" in motivo
