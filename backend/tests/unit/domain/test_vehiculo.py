import pytest

from app.domain.errores import ReglaNegocioError
from app.domain.vehiculo import Vehiculo, es_patente_valida, normalizar_patente


class TestPatente:
    @pytest.mark.parametrize(
        "patente",
        ["ABC 123", "ABC123", "AA 123 ABC", "AA123ABC", "abc 123", "aa 123 abc"],
    )
    def test_es_patente_valida_acepta_formatos_argentinos(self, patente: str) -> None:
        assert es_patente_valida(patente) is True

    @pytest.mark.parametrize(
        "patente",
        ["", "ABC 12", "ABCD 123", "ABC 1234", "123 ABC", "AA 12 AB", "ABC 123 ABCD"],
    )
    def test_es_patente_valida_rechaza_formatos_invalidos(self, patente: str) -> None:
        assert es_patente_valida(patente) is False

    def test_normalizar_patente_pone_en_mayusculas(self) -> None:
        assert normalizar_patente("abc 123") == "ABC 123"

    def test_normalizar_patente_colapsa_espacios(self) -> None:
        assert normalizar_patente("  ABC   123  ") == "ABC 123"


class TestCrearVehiculo:
    def test_crear_deja_el_id_y_las_fechas_a_cargo_del_sistema(self) -> None:
        vehiculo = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1)

        assert vehiculo.id is None
        assert vehiculo.creado_en is None
        assert vehiculo.actualizado_en is None

    def test_crear_activo_por_defecto(self) -> None:
        vehiculo = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1)

        assert vehiculo.activo is True

    def test_crear_sin_chofer_habitual(self) -> None:
        vehiculo = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1)

        assert vehiculo.id_chofer_habitual is None

    def test_crear_con_chofer_habitual(self) -> None:
        vehiculo = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1, id_chofer_habitual=5)

        assert vehiculo.id_chofer_habitual == 5

    def test_crear_normaliza_la_patente(self) -> None:
        vehiculo = Vehiculo.crear(patente="  abc  123  ", id_tipo_vehiculo=1)

        assert vehiculo.patente == "ABC 123"


class TestInvariantesDeCrear:
    @pytest.mark.parametrize(
        "patente",
        ["", "   ", "ABC 12", "ABCD 123", "123 ABC", "AA 12 AB"],
    )
    def test_crear_rechaza_patente_invalida(self, patente: str) -> None:
        with pytest.raises(ReglaNegocioError):
            Vehiculo.crear(patente=patente, id_tipo_vehiculo=1)

    def test_crear_rechaza_tipo_vehiculo_cero(self) -> None:
        with pytest.raises(ReglaNegocioError):
            Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=0)

    def test_crear_rechaza_tipo_vehiculo_negativo(self) -> None:
        with pytest.raises(ReglaNegocioError):
            Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=-1)

    def test_crear_acepta_formato_mercosur(self) -> None:
        vehiculo = Vehiculo.crear(patente="AA 123 ABC", id_tipo_vehiculo=1)

        assert vehiculo.patente == "AA 123 ABC"


class TestActualizar:
    def test_actualizar_cambia_los_datos_editables(self) -> None:
        vehiculo = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1)

        vehiculo.actualizar(patente="XYZ 789", id_tipo_vehiculo=2, id_chofer_habitual=3)

        assert vehiculo.patente == "XYZ 789"
        assert vehiculo.id_tipo_vehiculo == 2
        assert vehiculo.id_chofer_habitual == 3

    def test_actualizar_invalido_no_deja_el_vehiculo_a_medias(self) -> None:
        vehiculo = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1)

        with pytest.raises(ReglaNegocioError):
            vehiculo.actualizar(patente="INVALID", id_tipo_vehiculo=2, id_chofer_habitual=None)

        assert vehiculo.patente == "ABC 123"
        assert vehiculo.id_tipo_vehiculo == 1

    def test_actualizar_puede_quitar_chofer_habitual(self) -> None:
        vehiculo = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1, id_chofer_habitual=5)

        vehiculo.actualizar(patente="ABC 123", id_tipo_vehiculo=1, id_chofer_habitual=None)

        assert vehiculo.id_chofer_habitual is None


class TestDesactivar:
    def test_desactivar_pone_activo_en_false(self) -> None:
        vehiculo = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1)

        vehiculo.desactivar()

        assert vehiculo.activo is False
