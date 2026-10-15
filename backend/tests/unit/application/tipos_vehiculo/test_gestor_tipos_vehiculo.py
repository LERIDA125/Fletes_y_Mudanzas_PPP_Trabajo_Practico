from decimal import Decimal

import pytest

from app.application.tipos_vehiculo.gestor_tipos_vehiculo import GestorTiposVehiculo
from app.domain.errores import (
    DescripcionDuplicada,
    ReglaNegocioError,
    TipoVehiculoConVehiculos,
    TipoVehiculoNoEncontrado,
)
from tests.unit.application.tipos_vehiculo.fakes import (
    FakeConsultaVehiculosPorTipo,
    FakeTipoVehiculoRepo,
)

DESCRIPCION = "Camioneta 1/2 tonelada"
CAPACIDAD = 500.0
TARIFA_HORA = 3000.0
TARIFA_KM = 150.0


@pytest.fixture
def repo() -> FakeTipoVehiculoRepo:
    return FakeTipoVehiculoRepo()


@pytest.fixture
def consulta_vehiculos() -> FakeConsultaVehiculosPorTipo:
    return FakeConsultaVehiculosPorTipo()


@pytest.fixture
def gestor(
    repo: FakeTipoVehiculoRepo, consulta_vehiculos: FakeConsultaVehiculosPorTipo
) -> GestorTiposVehiculo:
    return GestorTiposVehiculo(
        repositorio_tipos=repo,
        consulta_vehiculos=consulta_vehiculos,
    )


def _registrar(
    gestor: GestorTiposVehiculo,
    descripcion: str = DESCRIPCION,
    capacidad: float = CAPACIDAD,
    tarifa_hora: float = TARIFA_HORA,
    tarifa_km: float = TARIFA_KM,
):
    return gestor.registrar(
        descripcion=descripcion,
        capacidad_carga_kg=capacidad,
        tarifa_hora_base=tarifa_hora,
        tarifa_km_excedente=tarifa_km,
    )


class TestRegistrar:
    def test_registra_con_todos_los_datos(self, gestor: GestorTiposVehiculo) -> None:
        tipo = _registrar(gestor)

        assert tipo.descripcion == DESCRIPCION
        assert tipo.capacidad_carga_kg == Decimal("500.0")
        assert tipo.tarifa_hora_base == Decimal("3000.0")
        assert tipo.tarifa_km_excedente == Decimal("150.0")

    def test_asigna_identificador_y_deja_el_tipo_activo(self, gestor: GestorTiposVehiculo) -> None:
        tipo = _registrar(gestor)

        assert tipo.id is not None
        assert tipo.activo is True

    def test_rechaza_descripcion_duplicada(self, gestor: GestorTiposVehiculo) -> None:
        _registrar(gestor)

        with pytest.raises(DescripcionDuplicada):
            _registrar(gestor)

    def test_rechaza_descripcion_duplicada_con_distinta_capitalizacion(
        self, gestor: GestorTiposVehiculo
    ) -> None:
        _registrar(gestor)

        with pytest.raises(DescripcionDuplicada):
            _registrar(gestor, "  CAMIONETA  1/2 TONELADA  ")

    def test_no_registra_un_segundo_tipo_al_rechazar_el_duplicado(
        self, gestor: GestorTiposVehiculo, repo: FakeTipoVehiculoRepo
    ) -> None:
        _registrar(gestor)

        with pytest.raises(DescripcionDuplicada):
            _registrar(gestor)

        assert repo.contar(None) == 1

    @pytest.mark.parametrize(
        ("campo", "valor"),
        [
            ("descripcion", "Ab"),
            ("descripcion", "   "),
            ("capacidad_carga_kg", 0),
            ("capacidad_carga_kg", -100),
            ("tarifa_hora_base", -1),
            ("tarifa_km_excedente", -1),
        ],
    )
    def test_rechaza_datos_invalidos(
        self, gestor: GestorTiposVehiculo, campo: str, valor: float
    ) -> None:
        datos = {
            "descripcion": DESCRIPCION,
            "capacidad_carga_kg": CAPACIDAD,
            "tarifa_hora_base": TARIFA_HORA,
            "tarifa_km_excedente": TARIFA_KM,
        }
        datos[campo] = valor

        with pytest.raises(ReglaNegocioError):
            gestor.registrar(**datos)

    def test_no_persiste_nada_ante_un_dato_invalido(
        self, gestor: GestorTiposVehiculo, repo: FakeTipoVehiculoRepo
    ) -> None:
        with pytest.raises(ReglaNegocioError):
            gestor.registrar(
                descripcion=DESCRIPCION,
                capacidad_carga_kg=0,
                tarifa_hora_base=TARIFA_HORA,
                tarifa_km_excedente=TARIFA_KM,
            )

        assert repo.contar(None) == 0

    def test_acepta_tarifa_hora_cero(self, gestor: GestorTiposVehiculo) -> None:
        tipo = _registrar(gestor, tarifa_hora=0)

        assert tipo.tarifa_hora_base == Decimal("0")

    def test_acepta_tarifa_km_cero(self, gestor: GestorTiposVehiculo) -> None:
        tipo = _registrar(gestor, tarifa_km=0)

        assert tipo.tarifa_km_excedente == Decimal("0")


class TestObtener:
    def test_devuelve_el_tipo_registrado(self, gestor: GestorTiposVehiculo) -> None:
        registrado = _registrar(gestor)

        obtenido = gestor.obtener(registrado.id)

        assert obtenido.id == registrado.id
        assert obtenido.descripcion == DESCRIPCION

    def test_lanza_error_si_no_existe(self, gestor: GestorTiposVehiculo) -> None:
        with pytest.raises(TipoVehiculoNoEncontrado):
            gestor.obtener(999)

    def test_no_devuelve_tipos_dados_de_baja(self, gestor: GestorTiposVehiculo) -> None:
        registrado = _registrar(gestor)
        gestor.eliminar(registrado.id)

        with pytest.raises(TipoVehiculoNoEncontrado):
            gestor.obtener(registrado.id)


class TestListar:
    def test_lista_solo_tipos_activos(self, gestor: GestorTiposVehiculo) -> None:
        activo = _registrar(gestor, "Camioneta 1/2 tonelada")
        baja = _registrar(gestor, "Camión 1 tonelada")
        gestor.eliminar(baja.id)

        resultado, total = gestor.listar(busqueda=None, offset=0, limit=20)

        assert total == 1
        assert [tipo.id for tipo in resultado] == [activo.id]

    def test_filtra_por_parte_de_la_descripcion(self, gestor: GestorTiposVehiculo) -> None:
        _registrar(gestor, "Camioneta 1/2 tonelada")
        _registrar(gestor, "Camión 1 tonelada")
        otro = _registrar(gestor, "Furgón mediano")

        resultado, total = gestor.listar(busqueda="tonelada", offset=0, limit=20)

        assert total == 2
        assert otro.id not in [tipo.id for tipo in resultado]

    def test_el_filtro_ignora_mayusculas(self, gestor: GestorTiposVehiculo) -> None:
        _registrar(gestor, "Camioneta 1/2 tonelada")

        resultado, total = gestor.listar(busqueda="CAMIONETA", offset=0, limit=20)

        assert total == 1

    def test_sin_coincidencias_devuelve_lista_vacia_y_total_cero(
        self, gestor: GestorTiposVehiculo
    ) -> None:
        _registrar(gestor)

        resultado, total = gestor.listar(busqueda="No existe", offset=0, limit=20)

        assert resultado == []
        assert total == 0

    def test_pagina_por_offset_y_limit(self, gestor: GestorTiposVehiculo) -> None:
        for indice in range(5):
            _registrar(gestor, f"Tipo Numero {indice}")

        resultado, total = gestor.listar(busqueda=None, offset=1, limit=2)

        assert total == 5
        assert len(resultado) == 2

    def test_el_total_refleja_el_filtro_y_no_la_pagina(
        self, gestor: GestorTiposVehiculo
    ) -> None:
        for indice in range(3):
            _registrar(gestor, f"Tipo Numero {indice}")

        _, total = gestor.listar(busqueda=None, offset=0, limit=1)

        assert total == 3


class TestActualizar:
    def test_cambia_la_tarifa_hora(self, gestor: GestorTiposVehiculo) -> None:
        tipo = _registrar(gestor)

        actualizado = gestor.actualizar(
            tipo.id,
            descripcion=DESCRIPCION,
            capacidad_carga_kg=CAPACIDAD,
            tarifa_hora_base=3500.0,
            tarifa_km_excedente=TARIFA_KM,
        )

        assert actualizado.tarifa_hora_base == Decimal("3500.0")

    def test_cambia_la_descripcion(self, gestor: GestorTiposVehiculo) -> None:
        tipo = _registrar(gestor)

        actualizado = gestor.actualizar(
            tipo.id,
            descripcion="Camión 1 tonelada",
            capacidad_carga_kg=1000.0,
            tarifa_hora_base=TARIFA_HORA,
            tarifa_km_excedente=TARIFA_KM,
        )

        assert actualizado.descripcion == "Camión 1 tonelada"

    def test_conserva_el_id(self, gestor: GestorTiposVehiculo) -> None:
        tipo = _registrar(gestor)

        actualizado = gestor.actualizar(
            tipo.id,
            descripcion=DESCRIPCION,
            capacidad_carga_kg=CAPACIDAD,
            tarifa_hora_base=TARIFA_HORA,
            tarifa_km_excedente=TARIFA_KM,
        )

        assert actualizado.id == tipo.id

    def test_rechaza_tomar_la_descripcion_de_otro_tipo(
        self, gestor: GestorTiposVehiculo
    ) -> None:
        primero = _registrar(gestor, "Camioneta 1/2 tonelada")
        segundo = _registrar(gestor, "Camión 1 tonelada")

        with pytest.raises(DescripcionDuplicada):
            gestor.actualizar(
                segundo.id,
                descripcion="Camioneta 1/2 tonelada",
                capacidad_carga_kg=CAPACIDAD,
                tarifa_hora_base=TARIFA_HORA,
                tarifa_km_excedente=TARIFA_KM,
            )

        assert gestor.obtener(primero.id).descripcion == "Camioneta 1/2 tonelada"
        assert gestor.obtener(segundo.id).descripcion == "Camión 1 tonelada"

    def test_guardar_los_mismos_datos_no_choca_consigo_mismo(
        self, gestor: GestorTiposVehiculo
    ) -> None:
        tipo = _registrar(gestor, "Camioneta 1/2 tonelada")

        actualizado = gestor.actualizar(
            tipo.id,
            descripcion="CAMIONETA 1/2 TONELADA",
            capacidad_carga_kg=CAPACIDAD,
            tarifa_hora_base=TARIFA_HORA,
            tarifa_km_excedente=TARIFA_KM,
        )

        assert actualizado.descripcion == "CAMIONETA 1/2 TONELADA"

    @pytest.mark.parametrize(
        ("campo", "valor"),
        [
            ("descripcion", "Ab"),
            ("capacidad_carga_kg", 0),
            ("tarifa_hora_base", -1),
            ("tarifa_km_excedente", -1),
        ],
    )
    def test_rechaza_datos_invalidos(
        self, gestor: GestorTiposVehiculo, campo: str, valor: float
    ) -> None:
        tipo = _registrar(gestor)
        datos = {
            "descripcion": DESCRIPCION,
            "capacidad_carga_kg": CAPACIDAD,
            "tarifa_hora_base": TARIFA_HORA,
            "tarifa_km_excedente": TARIFA_KM,
        }
        datos[campo] = valor

        with pytest.raises(ReglaNegocioError):
            gestor.actualizar(tipo.id, **datos)

    def test_no_altera_el_tipo_ante_un_dato_invalido(
        self, gestor: GestorTiposVehiculo
    ) -> None:
        tipo = _registrar(gestor)

        with pytest.raises(ReglaNegocioError):
            gestor.actualizar(
                tipo.id,
                descripcion=DESCRIPCION,
                capacidad_carga_kg=0,
                tarifa_hora_base=TARIFA_HORA,
                tarifa_km_excedente=TARIFA_KM,
            )

        assert gestor.obtener(tipo.id).capacidad_carga_kg == Decimal("500.0")

    def test_lanza_error_si_el_tipo_no_existe(self, gestor: GestorTiposVehiculo) -> None:
        with pytest.raises(TipoVehiculoNoEncontrado):
            gestor.actualizar(
                999,
                descripcion=DESCRIPCION,
                capacidad_carga_kg=CAPACIDAD,
                tarifa_hora_base=TARIFA_HORA,
                tarifa_km_excedente=TARIFA_KM,
            )

    def test_no_crea_registros_al_actualizar_un_id_inexistente(
        self, gestor: GestorTiposVehiculo, repo: FakeTipoVehiculoRepo
    ) -> None:
        with pytest.raises(TipoVehiculoNoEncontrado):
            gestor.actualizar(
                999,
                descripcion=DESCRIPCION,
                capacidad_carga_kg=CAPACIDAD,
                tarifa_hora_base=TARIFA_HORA,
                tarifa_km_excedente=TARIFA_KM,
            )

        assert repo.contar(None) == 0


class TestEliminar:
    def test_da_de_baja_un_tipo_sin_vehiculos(
        self,
        gestor: GestorTiposVehiculo,
        consulta_vehiculos: FakeConsultaVehiculosPorTipo,
    ) -> None:
        tipo = _registrar(gestor)

        gestor.eliminar(tipo.id)

        with pytest.raises(TipoVehiculoNoEncontrado):
            gestor.obtener(tipo.id)
        assert consulta_vehiculos.consultas == [tipo.id]

    def test_el_tipo_dado_de_baja_desaparece_del_listado(
        self, gestor: GestorTiposVehiculo
    ) -> None:
        tipo = _registrar(gestor)

        gestor.eliminar(tipo.id)
        resultado, total = gestor.listar(busqueda=None, offset=0, limit=20)

        assert resultado == []
        assert total == 0

    def test_rechaza_dar_de_baja_un_tipo_con_vehiculos(
        self,
        gestor: GestorTiposVehiculo,
        consulta_vehiculos: FakeConsultaVehiculosPorTipo,
    ) -> None:
        tipo = _registrar(gestor)
        consulta_vehiculos.marcar_con_vehiculos(tipo.id)

        with pytest.raises(TipoVehiculoConVehiculos):
            gestor.eliminar(tipo.id)

    def test_no_desactiva_un_tipo_con_vehiculos(
        self,
        gestor: GestorTiposVehiculo,
        consulta_vehiculos: FakeConsultaVehiculosPorTipo,
        repo: FakeTipoVehiculoRepo,
    ) -> None:
        tipo = _registrar(gestor)
        consulta_vehiculos.marcar_con_vehiculos(tipo.id)

        with pytest.raises(TipoVehiculoConVehiculos):
            gestor.eliminar(tipo.id)

        assert repo.llamadas_desactivar == []
        assert gestor.obtener(tipo.id).activo is True

    def test_eliminar_dos_veces_es_idempotente(self, gestor: GestorTiposVehiculo) -> None:
        tipo = _registrar(gestor)

        gestor.eliminar(tipo.id)
        gestor.eliminar(tipo.id)

        with pytest.raises(TipoVehiculoNoEncontrado):
            gestor.obtener(tipo.id)

    def test_lanza_error_si_el_tipo_no_existe(self, gestor: GestorTiposVehiculo) -> None:
        with pytest.raises(TipoVehiculoNoEncontrado):
            gestor.eliminar(999)
