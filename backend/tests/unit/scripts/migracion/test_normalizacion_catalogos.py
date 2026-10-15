"""Tests de los catálogos y de la normalización contra catálogo (FR-008, FR-012, FR-017 a FR-019,
FR-027).
"""

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
    def test_normalizacion_de_codigos_y_prefijos(self) -> None:
        for entrada in ["MOV-01", "MOV01", "mov 01", "MOV 1", "01", "1"]:
            assert codigo_de_movil(entrada).valor == "MOV-01"

        assert codigo_de_movil("03").valor == "MOV-03"
        assert codigo_de_movil("MOV-03").valor == "MOV-03"
        assert codigo_de_movil("1").valor == "MOV-01"
        assert codigo_de_viaje("2002").valor == "VJ-2002"
        assert codigo_de_cliente("102").valor == "CLI-102"
        assert codigo_de_viaje("OTRO-7").valor == "OTRO-0007"

    def test_codigos_invalidos_o_vacios_devuelven_none(self) -> None:
        for vacio in ["sin codigo", None, "", "   "]:
            assert codigo_de_movil(vacio) is None


class TestNormalizarTexto:
    def test_normalizacion_y_comparacion_de_texto(self) -> None:
        assert normalizar_texto("  Camioneta   Mediana ") == "camioneta mediana"
        assert normalizar_texto("Camión") == normalizar_texto("Camion")
        assert normalizar_texto("MARCELO RODRIGUEZ") == normalizar_texto("Marcelo Rodriguez")


class TestTipoVehiculo:
    def test_normaliza_las_variantes_de_mayusculas_y_tildes(self) -> None:
        casos = [
            ("Furgón Grande", "Furgón Grande"),
            ("Furgon Grande", "Furgón Grande"),
            ("CAMIONETA", "Camioneta"),
            ("camioneta", "Camioneta"),
            ("Camioneta Mediana", "Camioneta Mediana"),
            ("Utilitario", "Utilitario"),
            ("Camión Mudancero", "Camión Mudancero"),
        ]
        for entrada, esperado in casos:
            tipo, motivo = normalizar_tipo_vehiculo(entrada)
            assert motivo is None
            assert tipo == esperado

    def test_un_tipo_fuera_del_catalogo_devuelve_motivo(self) -> None:
        tipo, motivo = normalizar_tipo_vehiculo("Camioneta con jaula")
        assert tipo is None
        assert "no está en el catálogo" in motivo

    def test_todo_tipo_del_archivo_real_esta_en_el_catalogo(self) -> None:
        for tipo in cat.TIPOS_VEHICULO_CANONICOS:
            assert normalizar_tipo_vehiculo(tipo)[0] == tipo


class TestEstadoMovil:
    def test_normaliza_estados_directos(self) -> None:
        casos = [
            ("Disponible", cat.ESTADO_DISPONIBLE),
            ("Libre", cat.ESTADO_DISPONIBLE),
            ("En viaje", cat.ESTADO_OCUPADO),
            ("Suspendido por choque", cat.ESTADO_INACTIVO),
            ("Rompió el elástico", cat.ESTADO_INACTIVO),
        ]
        for entrada, esperado in casos:
            estado, texto_original, motivo = normalizar_estado_movil(entrada)
            assert estado == esperado
            assert texto_original == entrada
            assert motivo is None

    def test_estados_ambiguos_o_invalidos(self) -> None:
        for entrada in ["En taller hasta el martes", "De franco"]:
            estado, texto_original, motivo = normalizar_estado_movil(entrada)
            assert estado in cat.ESTADOS_CANONICOS
            assert texto_original == entrada
            assert "más de una lectura" in motivo

        estado, texto, motivo = normalizar_estado_movil("El auto está en el taller de laterminal")
        assert estado is None
        assert "no está en el catálogo" in motivo

        estado_vacio, _, motivo_vacio = normalizar_estado_movil(None)
        assert estado_vacio is None
        assert "vacía" in motivo_vacio


class TestCondicionIva:
    def test_normaliza_condicion_iva_y_rechaza_desconocidas(self) -> None:
        casos = [
            ("Responsable Inscripto", "Responsable Inscripto"),
            ("Resp. Inscripto", "Responsable Inscripto"),
            ("Consumidor Final", "Consumidor Final"),
            ("Exento", "Exento"),
        ]
        for entrada, esperado in casos:
            condicion, motivo = normalizar_condicion_iva(entrada)
            assert motivo is None
            assert condicion == esperado

        condicion, motivo = normalizar_condicion_iva("Monotributista")
        assert condicion is None
        assert "no está en el catálogo" in motivo


class TestDireccionNoEstructurada:
    def test_detecta_direcciones_no_estructuradas_y_reales(self) -> None:
        for no_estructurada in [
            "Retira en depósito",
            "retirar en deposito",
            "A retirar en depósito",
            "Consultar",
        ]:
            assert es_direccion_no_estructurada(no_estructurada) is True

        for real in ["Av. Cabildo 2140", "Cucha Cucha 1200 timbre 2", "Thames 1450", None]:
            assert es_direccion_no_estructurada(real) is False


class TestBultos:
    def test_extrae_el_numero_cuando_hay_uno_solo(self) -> None:
        casos = [
            ("6 muebles embalados", 6),
            ("30 cajas surtidas", 30),
            ("15 monitores", 15),
        ]
        for entrada, esperado in casos:
            bultos, motivo = normalizar_bultos(entrada)
            assert motivo is None
            assert bultos.cantidad == esperado
            assert bultos.es_texto_libre is False

    def test_casos_especiales_sin_cantidad_o_multiples(self) -> None:
        bultos_serv, motivo_serv = normalizar_bultos("Sonido y luces")
        assert bultos_serv.cantidad is None
        assert "describe un servicio" in motivo_serv

        bultos_sin_cant, motivo_sin_cant = normalizar_bultos("Archivadores pesados")
        assert bultos_sin_cant.cantidad is None
        assert "no dice cuántos bultos" in motivo_sin_cant

        for entrada in ["10 cajas y 1 heladera", "4 mancuernas y 2 bancos", "1 sillon 3 cuerpos"]:
            bultos, motivo = normalizar_bultos(entrada)
            assert bultos.cantidad is None
            assert "2 cantidades" in motivo

        for vacio in [None, "", "   "]:
            bultos, motivo = normalizar_bultos(vacio)
            assert bultos.cantidad is None
            assert "vacía" in motivo
