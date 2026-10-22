"""Suite unificada de Gestión de Vehículos y Tipos de Vehículo (H4).

Comprimido exactamente en 3 tests de alto nivel:
1. `test_h4_dominio`: validaciones de patentes, descripciones y capacidades.
2. `test_h4_gestor_tipos_vehiculo`: ciclo de vida (alta, listar, editar, baja).
3. `test_h4_gestor_vehiculos`: ciclo de vida (alta, listar, editar, baja).
"""

from decimal import Decimal

import pytest

from app.application.tipos_vehiculo.gestor_tipos_vehiculo import GestorTiposVehiculo
from app.application.vehiculos.gestor_vehiculos import GestorVehiculos
from app.domain.errores import (
    ChoferInvalido,
    DescripcionDuplicada,
    PatenteDuplicada,
    ReglaNegocioError,
    TipoVehiculoConVehiculos,
    TipoVehiculoInvalido,
    TipoVehiculoNoEncontrado,
    VehiculoConServicios,
    VehiculoNoEncontrado,
)
from app.domain.tipo_vehiculo import TipoVehiculo, normalizar_descripcion_key
from app.domain.vehiculo import Vehiculo, es_patente_valida, normalizar_patente
from tests.unit.application.tipos_vehiculo.fakes import (
    FakeConsultaVehiculosPorTipo,
    FakeTipoVehiculoRepo,
)
from tests.unit.application.vehiculos.fakes import (
    FakeConsultaChofer,
    FakeConsultaServiciosVehiculo,
    FakeConsultaTipoVehiculo,
    FakeVehiculoRepo,
)


def test_h4_dominio() -> None:
    # --- Validaciones de Vehiculo ---
    assert es_patente_valida("AA 123 ABC")
    assert es_patente_valida("ABC 123")
    assert not es_patente_valida("ABCD 123")
    assert not es_patente_valida("123 ABC")

    assert normalizar_patente("aa 123 abc") == "AA 123 ABC"
    assert normalizar_patente("  abc 123  ") == "ABC 123"

    v = Vehiculo.crear(patente="AA 123 ABC", id_tipo_vehiculo=1, id_chofer_habitual=10)
    assert v.patente == "AA 123 ABC"
    assert v.activo is True
    assert v.id_chofer_habitual == 10

    v.actualizar(patente="XYZ 789", id_tipo_vehiculo=2, id_chofer_habitual=None)
    assert v.patente == "XYZ 789"
    assert v.id_chofer_habitual is None

    v.desactivar()
    assert v.activo is False

    with pytest.raises(ReglaNegocioError):
        Vehiculo.crear(patente="PATENTE_INVALIDA", id_tipo_vehiculo=1)

    # --- Validaciones de TipoVehiculo ---
    assert normalizar_descripcion_key("  Camioneta 1/2 Tonelada  ") == "camioneta 1/2 tonelada"

    t = TipoVehiculo.crear(
        descripcion="  Camioneta  ",
        capacidad_carga_kg=Decimal("500.00"),
        tarifa_hora_base=Decimal("3000.00"),
        tarifa_km_excedente=Decimal("150.00"),
    )
    assert t.descripcion == "Camioneta"
    assert t.activo is True

    t.actualizar(
        descripcion="Camion",
        capacidad_carga_kg=Decimal("1000"),
        tarifa_hora_base=Decimal("4000"),
        tarifa_km_excedente=Decimal("200"),
    )
    assert t.descripcion == "Camion"

    t.desactivar()
    assert t.activo is False

    with pytest.raises(ReglaNegocioError):
        TipoVehiculo.crear(
            descripcion="",
            capacidad_carga_kg=Decimal("500"),
            tarifa_hora_base=Decimal("100"),
            tarifa_km_excedente=Decimal("100"),
        )
    with pytest.raises(ReglaNegocioError):
        TipoVehiculo.crear(
            descripcion="Tipo",
            capacidad_carga_kg=Decimal("0"),
            tarifa_hora_base=Decimal("100"),
            tarifa_km_excedente=Decimal("100"),
        )
    with pytest.raises(ReglaNegocioError):
        TipoVehiculo.crear(
            descripcion="Tipo",
            capacidad_carga_kg=Decimal("100"),
            tarifa_hora_base=Decimal("-1"),
            tarifa_km_excedente=Decimal("100"),
        )


def test_h4_gestor_tipos_vehiculo() -> None:
    repo = FakeTipoVehiculoRepo()
    consulta_vehiculos = FakeConsultaVehiculosPorTipo()
    gestor = GestorTiposVehiculo(repositorio_tipos=repo, consulta_vehiculos=consulta_vehiculos)

    # 1. Alta
    t = gestor.registrar(
        descripcion="Utilitario Chico",
        capacidad_carga_kg=500.0,
        tarifa_hora_base=3000.0,
        tarifa_km_excedente=150.0,
    )
    assert t.id == 1 and t.activo is True

    # Duplicado
    with pytest.raises(DescripcionDuplicada):
        gestor.registrar(
            descripcion="utilitario chico",
            capacidad_carga_kg=600.0,
            tarifa_hora_base=3000.0,
            tarifa_km_excedente=150.0,
        )

    # 2. Listar y buscar
    tipos, total = gestor.listar(busqueda="utilitario", offset=0, limit=10)
    assert total == 1 and tipos[0].id == 1

    assert gestor.obtener(1).descripcion == "Utilitario Chico"
    with pytest.raises(TipoVehiculoNoEncontrado):
        gestor.obtener(999)

    # 3. Modificación
    mod = gestor.actualizar(
        1,
        descripcion="Utilitario Grande",
        capacidad_carga_kg=800.0,
        tarifa_hora_base=3500.0,
        tarifa_km_excedente=180.0,
    )
    assert mod.descripcion == "Utilitario Grande"

    # 4. Baja (con y sin vehiculos asociados)
    consulta_vehiculos.marcar_con_vehiculos(1)
    with pytest.raises(TipoVehiculoConVehiculos):
        gestor.eliminar(1)

    consulta_vehiculos._tipos_con_vehiculos.clear()
    gestor.eliminar(1)
    assert repo.obtener_por_id(1).activo is False


def test_h4_gestor_vehiculos() -> None:
    repo = FakeVehiculoRepo()
    consulta_tipo = FakeConsultaTipoVehiculo()
    consulta_chofer = FakeConsultaChofer()
    consulta_servicios = FakeConsultaServiciosVehiculo()
    gestor = GestorVehiculos(
        repositorio_vehiculos=repo,
        consulta_tipos=consulta_tipo,
        consulta_choferes=consulta_chofer,
        consulta_servicios=consulta_servicios,
    )

    consulta_tipo.marcar_activo(1)
    consulta_chofer.marcar_activo(10)

    # 1. Alta con y sin chofer
    v = gestor.registrar(patente="ABC 123", id_tipo_vehiculo=1, id_chofer_habitual=10)
    assert v.id == 1 and v.activo is True and v.id_chofer_habitual == 10

    # Duplicado
    with pytest.raises(PatenteDuplicada):
        gestor.registrar(patente="abc 123", id_tipo_vehiculo=1)

    # Validaciones foráneas
    with pytest.raises(TipoVehiculoInvalido):
        gestor.registrar(patente="XYZ 123", id_tipo_vehiculo=999)
    with pytest.raises(ChoferInvalido):
        gestor.registrar(patente="XYZ 123", id_tipo_vehiculo=1, id_chofer_habitual=20)

    # 2. Listado y búsqueda
    vehiculos, total = gestor.listar(busqueda="ABC", offset=0, limit=10)
    assert total == 1 and vehiculos[0].vehiculo.patente == "ABC 123"

    assert gestor.obtener(1).patente == "ABC 123"
    with pytest.raises(VehiculoNoEncontrado):
        gestor.obtener(999)

    # 3. Modificación
    v_mod = gestor.actualizar(
        1,
        patente="XYZ 999",
        id_tipo_vehiculo=1,
        id_chofer_habitual=None,
    )
    assert v_mod.patente == "XYZ 999" and v_mod.id_chofer_habitual is None

    # 4. Baja lógica
    consulta_servicios.marcar_con_servicios(1)
    with pytest.raises(VehiculoConServicios):
        gestor.eliminar(1)

    consulta_servicios._vehiculos_con_servicios.clear()
    gestor.eliminar(1)
    assert repo.obtener_por_id(1).activo is False
