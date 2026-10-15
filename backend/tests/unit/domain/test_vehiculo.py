import pytest

from app.domain.errores import ReglaNegocioError
from app.domain.vehiculo import Vehiculo, es_patente_valida, normalizar_patente


class TestPatente:
    def test_validacion_de_formatos_argentinos(self) -> None:
        validas = ["ABC 123", "ABC123", "AA 123 ABC", "AA123ABC", "abc 123", "aa 123 abc"]
        for p in validas:
            assert es_patente_valida(p) is True

        invalidas = ["", "ABC 12", "ABCD 123", "ABC 1234", "123 ABC", "AA 12 AB", "ABC 123 ABCD"]
        for p in invalidas:
            assert es_patente_valida(p) is False

    def test_normalizacion_de_patente(self) -> None:
        assert normalizar_patente("abc 123") == "ABC 123"
        assert normalizar_patente("  ABC   123  ") == "ABC 123"


class TestCrearVehiculo:
    def test_creacion_basica_y_valores_por_defecto(self) -> None:
        v = Vehiculo.crear(patente="  abc  123  ", id_tipo_vehiculo=1)
        assert v.id is None
        assert v.creado_en is None
        assert v.actualizado_en is None
        assert v.activo is True
        assert v.id_chofer_habitual is None
        assert v.patente == "ABC 123"

        v_con_chofer = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1, id_chofer_habitual=5)
        assert v_con_chofer.id_chofer_habitual == 5

    def test_crear_rechaza_patente_o_tipo_invalido(self) -> None:
        for p in ["", "   ", "ABC 12", "ABCD 123", "123 ABC", "AA 12 AB"]:
            with pytest.raises(ReglaNegocioError):
                Vehiculo.crear(patente=p, id_tipo_vehiculo=1)

        for tipo_inv in [0, -1]:
            with pytest.raises(ReglaNegocioError):
                Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=tipo_inv)

        v_mercosur = Vehiculo.crear(patente="AA 123 ABC", id_tipo_vehiculo=1)
        assert v_mercosur.patente == "AA 123 ABC"


class TestActualizarYDesactivar:
    def test_actualizar_datos_del_vehiculo(self) -> None:
        v = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1, id_chofer_habitual=5)
        v.actualizar(patente="XYZ 789", id_tipo_vehiculo=2, id_chofer_habitual=3)
        assert v.patente == "XYZ 789"
        assert v.id_tipo_vehiculo == 2
        assert v.id_chofer_habitual == 3

        v.actualizar(patente="XYZ 789", id_tipo_vehiculo=2, id_chofer_habitual=None)
        assert v.id_chofer_habitual is None

    def test_actualizar_invalido_no_deja_el_vehiculo_a_medias(self) -> None:
        v = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1)
        with pytest.raises(ReglaNegocioError):
            v.actualizar(patente="INVALID", id_tipo_vehiculo=2, id_chofer_habitual=None)
        assert v.patente == "ABC 123"
        assert v.id_tipo_vehiculo == 1

    def test_desactivar_pone_activo_en_false(self) -> None:
        v = Vehiculo.crear(patente="ABC 123", id_tipo_vehiculo=1)
        v.desactivar()
        assert v.activo is False
