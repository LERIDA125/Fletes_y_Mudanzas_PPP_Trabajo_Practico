from decimal import Decimal

import pytest

from app.domain.errores import ReglaNegocioError
from app.domain.tipo_vehiculo import TipoVehiculo, normalizar_descripcion_key


class TestCrearTipoVehiculo:
    def test_crear_deja_el_id_y_las_fechas_a_cargo_del_sistema(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 tonelada",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )

        assert tipo.id is None
        assert tipo.creado_en is None
        assert tipo.actualizado_en is None

    def test_crear_activo_por_defecto(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 tonelada",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )

        assert tipo.activo is True

    def test_crear_normaliza_los_espacios(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="  Camioneta  1/2 tonelada  ",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )

        assert tipo.descripcion == "Camioneta 1/2 tonelada"

    def test_descripcion_key_esta_en_minusculas(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 Tonelada",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )

        assert tipo.descripcion_key == "camioneta 1/2 tonelada"


class TestInvariantesDeCrear:
    @pytest.mark.parametrize("descripcion", ["", "   ", "Ab", "A" * 81])
    def test_crear_rechaza_descripcion_invalida(self, descripcion: str) -> None:
        with pytest.raises(ReglaNegocioError):
            TipoVehiculo.crear(
                descripcion=descripcion,
                capacidad_carga_kg=Decimal("500.00"),
                tarifa_hora_base=Decimal("3000.00"),
                tarifa_km_excedente=Decimal("150.00"),
            )

    def test_crear_acepta_los_extremos_de_largo_validos(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Abc",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )
        assert tipo.descripcion == "Abc"

        tipo2 = TipoVehiculo.crear(
            descripcion="A" * 80,
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )
        assert tipo2.descripcion == "A" * 80

    @pytest.mark.parametrize("capacidad", [Decimal("0"), Decimal("-100"), Decimal("-0.01")])
    def test_crear_rechaza_capacidad_no_positiva(self, capacidad: Decimal) -> None:
        with pytest.raises(ReglaNegocioError):
            TipoVehiculo.crear(
                descripcion="Camioneta 1/2 tonelada",
                capacidad_carga_kg=capacidad,
                tarifa_hora_base=Decimal("3000.00"),
                tarifa_km_excedente=Decimal("150.00"),
            )

    def test_crear_acepta_capacidad_positiva(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 tonelada",
            capacidad_carga_kg=Decimal("0.01"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )
        assert tipo.capacidad_carga_kg == Decimal("0.01")

    @pytest.mark.parametrize("tarifa", [Decimal("-1"), Decimal("-0.01")])
    def test_crear_rechaza_tarifa_hora_negativa(self, tarifa: Decimal) -> None:
        with pytest.raises(ReglaNegocioError):
            TipoVehiculo.crear(
                descripcion="Camioneta 1/2 tonelada",
                capacidad_carga_kg=Decimal("500.00"),
                tarifa_hora_base=tarifa,
                tarifa_km_excedente=Decimal("150.00"),
            )

    def test_crear_acepta_tarifa_hora_cero(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 tonelada",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("0"),
            tarifa_km_excedente=Decimal("150.00"),
        )
        assert tipo.tarifa_hora_base == Decimal("0")

    @pytest.mark.parametrize("tarifa", [Decimal("-1"), Decimal("-0.01")])
    def test_crear_rechaza_tarifa_km_negativa(self, tarifa: Decimal) -> None:
        with pytest.raises(ReglaNegocioError):
            TipoVehiculo.crear(
                descripcion="Camioneta 1/2 tonelada",
                capacidad_carga_kg=Decimal("500.00"),
                tarifa_hora_base=Decimal("3000.00"),
                tarifa_km_excedente=tarifa,
            )

    def test_crear_acepta_tarifa_km_cero(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 tonelada",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("0"),
        )
        assert tipo.tarifa_km_excedente == Decimal("0")


class TestActualizar:
    def test_actualizar_cambia_los_datos_editables(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 tonelada",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )

        tipo.actualizar(
            descripcion="Camión 1 tonelada",
            capacidad_carga_kg=Decimal("1000.00"),
            tarifa_hora_base=Decimal("3500.00"),
            tarifa_km_excedente=Decimal("200.00"),
        )

        assert tipo.descripcion == "Camión 1 tonelada"
        assert tipo.capacidad_carga_kg == Decimal("1000.00")
        assert tipo.tarifa_hora_base == Decimal("3500.00")
        assert tipo.tarifa_km_excedente == Decimal("200.00")

    def test_actualizar_invalido_no_deja_el_tipo_a_medias(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 tonelada",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )

        with pytest.raises(ReglaNegocioError):
            tipo.actualizar(
                descripcion="Camioneta 1/2 tonelada",
                capacidad_carga_kg=Decimal("500.00"),
                tarifa_hora_base=Decimal("-100"),
                tarifa_km_excedente=Decimal("150.00"),
            )

        assert tipo.tarifa_hora_base == Decimal("3000.00")


class TestDesactivar:
    def test_desactivar_pone_activo_en_false(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="Camioneta 1/2 tonelada",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )

        tipo.desactivar()

        assert tipo.activo is False


class TestNormalizacionDescripcion:
    def test_descripcion_key_ignora_mayusculas(self) -> None:
        assert normalizar_descripcion_key(
            "Camioneta 1/2 Tonelada"
        ) == normalizar_descripcion_key("camioneta 1/2 tonelada")

    def test_descripcion_key_colapsa_espacios(self) -> None:
        assert normalizar_descripcion_key("  Camioneta   1/2 tonelada  ") == (
            "camioneta 1/2 tonelada"
        )
