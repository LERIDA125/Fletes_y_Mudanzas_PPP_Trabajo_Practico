from decimal import Decimal

import pytest

from app.domain.errores import ReglaNegocioError
from app.domain.tipo_vehiculo import TipoVehiculo, normalizar_descripcion_key


class TestCrearTipoVehiculo:
    def test_creacion_basica_y_valores_por_defecto(self) -> None:
        tipo = TipoVehiculo.crear(
            descripcion="  Camioneta 1/2 Tonelada  ",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )
        assert tipo.id is None
        assert tipo.creado_en is None
        assert tipo.actualizado_en is None
        assert tipo.activo is True
        assert tipo.descripcion == "Camioneta 1/2 Tonelada"
        assert tipo.descripcion_key == "camioneta 1/2 tonelada"


class TestInvariantesDeCrear:
    def test_crear_rechaza_descripciones_invalidas(self) -> None:
        for desc in ["", "   ", "Ab", "A" * 81]:
            with pytest.raises(ReglaNegocioError):
                TipoVehiculo.crear(
                    descripcion=desc,
                    capacidad_carga_kg=Decimal("500.00"),
                    tarifa_hora_base=Decimal("3000.00"),
                    tarifa_km_excedente=Decimal("150.00"),
                )

    def test_crear_acepta_extremos_de_largo_validos(self) -> None:
        t1 = TipoVehiculo.crear(
            descripcion="Abc",
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )
        t2 = TipoVehiculo.crear(
            descripcion="A" * 80,
            capacidad_carga_kg=Decimal("500.00"),
            tarifa_hora_base=Decimal("3000.00"),
            tarifa_km_excedente=Decimal("150.00"),
        )
        assert t1.descripcion == "Abc"
        assert t2.descripcion == "A" * 80

    def test_validaciones_de_capacidad_y_tarifas(self) -> None:
        # Capacidad no positiva
        for cap in [Decimal("0"), Decimal("-100"), Decimal("-0.01")]:
            with pytest.raises(ReglaNegocioError):
                TipoVehiculo.crear("Tipo", cap, Decimal("100"), Decimal("100"))

        # Tarifas negativas
        for tarifa in [Decimal("-1"), Decimal("-0.01")]:
            with pytest.raises(ReglaNegocioError):
                TipoVehiculo.crear("Tipo", Decimal("100"), tarifa, Decimal("100"))
            with pytest.raises(ReglaNegocioError):
                TipoVehiculo.crear("Tipo", Decimal("100"), Decimal("100"), tarifa)

        # Valores mínimos válidos
        t = TipoVehiculo.crear("Tipo", Decimal("0.01"), Decimal("0"), Decimal("0"))
        assert t.capacidad_carga_kg == Decimal("0.01")
        assert t.tarifa_hora_base == Decimal("0")
        assert t.tarifa_km_excedente == Decimal("0")


class TestActualizarYDesactivar:
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
    def test_normalizacion_de_descripcion(self) -> None:
        assert normalizar_descripcion_key("Camioneta 1/2 Tonelada") == (
            normalizar_descripcion_key("camioneta 1/2 tonelada")
        )
        assert normalizar_descripcion_key("  Camioneta   1/2 tonelada  ") == (
            "camioneta 1/2 tonelada"
        )
