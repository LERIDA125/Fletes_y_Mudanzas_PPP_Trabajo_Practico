import pytest

from app.application.vehiculos.gestor_vehiculos import GestorVehiculos
from app.domain.errores import (
    ChoferInvalido,
    PatenteDuplicada,
    ReglaNegocioError,
    TipoVehiculoInvalido,
    VehiculoConServicios,
    VehiculoNoEncontrado,
)
from tests.unit.application.vehiculos.fakes import (
    FakeConsultaChofer,
    FakeConsultaServiciosVehiculo,
    FakeConsultaTipoVehiculo,
    FakeVehiculoRepo,
)

PATENTE = "ABC 123"
ID_TIPO = 1
ID_CHOFER = 5


@pytest.fixture
def repo() -> FakeVehiculoRepo:
    return FakeVehiculoRepo()


@pytest.fixture
def consulta_tipos() -> FakeConsultaTipoVehiculo:
    fake = FakeConsultaTipoVehiculo()
    fake.marcar_activo(ID_TIPO)
    fake.marcar_activo(2)
    return fake


@pytest.fixture
def consulta_choferes() -> FakeConsultaChofer:
    fake = FakeConsultaChofer()
    fake.marcar_activo(ID_CHOFER)
    return fake


@pytest.fixture
def consulta_servicios() -> FakeConsultaServiciosVehiculo:
    return FakeConsultaServiciosVehiculo()


@pytest.fixture
def gestor(
    repo: FakeVehiculoRepo,
    consulta_tipos: FakeConsultaTipoVehiculo,
    consulta_choferes: FakeConsultaChofer,
    consulta_servicios: FakeConsultaServiciosVehiculo,
) -> GestorVehiculos:
    return GestorVehiculos(
        repositorio_vehiculos=repo,
        consulta_tipos=consulta_tipos,
        consulta_choferes=consulta_choferes,
        consulta_servicios=consulta_servicios,
    )


def _registrar(
    gestor: GestorVehiculos,
    patente: str = PATENTE,
    id_tipo: int = ID_TIPO,
    id_chofer: int | None = None,
):
    return gestor.registrar(
        patente=patente,
        id_tipo_vehiculo=id_tipo,
        id_chofer_habitual=id_chofer,
    )


class TestRegistrar:
    def test_registra_con_patente_y_tipo(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        assert vehiculo.patente == PATENTE
        assert vehiculo.id_tipo_vehiculo == ID_TIPO
        assert vehiculo.id_chofer_habitual is None

    def test_registra_con_chofer_habitual(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor, id_chofer=ID_CHOFER)

        assert vehiculo.id_chofer_habitual == ID_CHOFER

    def test_asigna_identificador_y_deja_el_vehiculo_activo(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        assert vehiculo.id is not None
        assert vehiculo.activo is True

    def test_rechaza_patente_duplicada(self, gestor: GestorVehiculos) -> None:
        _registrar(gestor)

        with pytest.raises(PatenteDuplicada):
            _registrar(gestor)

    def test_rechaza_patente_duplicada_con_distinta_capitalizacion(
        self, gestor: GestorVehiculos
    ) -> None:
        _registrar(gestor)

        with pytest.raises(PatenteDuplicada):
            _registrar(gestor, "abc 123")

    def test_no_registra_un_segundo_vehiculo_al_rechazar_el_duplicado(
        self, gestor: GestorVehiculos, repo: FakeVehiculoRepo
    ) -> None:
        _registrar(gestor)

        with pytest.raises(PatenteDuplicada):
            _registrar(gestor)

        assert repo.contar(None) == 1

    def test_rechaza_tipo_vehiculo_inexistente(self, gestor: GestorVehiculos) -> None:
        with pytest.raises(TipoVehiculoInvalido):
            _registrar(gestor, id_tipo=999)

    def test_rechaza_chofer_inexistente(self, gestor: GestorVehiculos) -> None:
        with pytest.raises(ChoferInvalido):
            _registrar(gestor, id_chofer=999)

    @pytest.mark.parametrize(
        "patente",
        ["", "   ", "ABC 12", "ABCD 123", "123 ABC"],
    )
    def test_rechaza_patente_invalida(self, gestor: GestorVehiculos, patente: str) -> None:
        with pytest.raises(ReglaNegocioError):
            _registrar(gestor, patente)

    def test_no_persiste_nada_ante_un_dato_invalido(
        self, gestor: GestorVehiculos, repo: FakeVehiculoRepo
    ) -> None:
        with pytest.raises(ReglaNegocioError):
            gestor.registrar(patente="ABC 123", id_tipo_vehiculo=0)

        assert repo.contar(None) == 0

    def test_acepta_formato_mercosur(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor, patente="AA 123 ABC")

        assert vehiculo.patente == "AA 123 ABC"


class TestObtener:
    def test_devuelve_el_vehiculo_registrado(self, gestor: GestorVehiculos) -> None:
        registrado = _registrar(gestor)

        obtenido = gestor.obtener(registrado.id)

        assert obtenido.id == registrado.id
        assert obtenido.patente == PATENTE

    def test_lanza_error_si_no_existe(self, gestor: GestorVehiculos) -> None:
        with pytest.raises(VehiculoNoEncontrado):
            gestor.obtener(999)

    def test_no_devuelve_vehiculos_dados_de_baja(self, gestor: GestorVehiculos) -> None:
        registrado = _registrar(gestor)
        gestor.eliminar(registrado.id)

        with pytest.raises(VehiculoNoEncontrado):
            gestor.obtener(registrado.id)


class TestListar:
    def test_lista_solo_vehiculos_activos(self, gestor: GestorVehiculos) -> None:
        activo = _registrar(gestor, "ABC 123")
        baja = _registrar(gestor, "XYZ 789")
        gestor.eliminar(baja.id)

        resultado, total = gestor.listar(busqueda=None, offset=0, limit=20)

        assert total == 1
        assert [v.id for v in resultado] == [activo.id]

    def test_filtra_por_patente(self, gestor: GestorVehiculos) -> None:
        _registrar(gestor, "ABC 123")
        _registrar(gestor, "XYZ 789")
        _registrar(gestor, "AA 123 ABC")

        resultado, total = gestor.listar(busqueda="ABC 12", offset=0, limit=20)

        assert total == 1
        assert resultado[0].patente == "ABC 123"

    def test_el_filtro_ignora_mayusculas(self, gestor: GestorVehiculos) -> None:
        _registrar(gestor, "ABC 123")

        resultado, total = gestor.listar(busqueda="abc", offset=0, limit=20)

        assert total == 1

    def test_sin_coincidencias_devuelve_lista_vacia_y_total_cero(
        self, gestor: GestorVehiculos
    ) -> None:
        _registrar(gestor)

        resultado, total = gestor.listar(busqueda="ZZZ", offset=0, limit=20)

        assert resultado == []
        assert total == 0

    def test_pagina_por_offset_y_limit(self, gestor: GestorVehiculos) -> None:
        for indice in range(5):
            _registrar(gestor, f"ABC 1{indice}0")

        resultado, total = gestor.listar(busqueda=None, offset=1, limit=2)

        assert total == 5
        assert len(resultado) == 2

    def test_el_total_refleja_el_filtro_y_no_la_pagina(self, gestor: GestorVehiculos) -> None:
        for indice in range(3):
            _registrar(gestor, f"ABC 1{indice}0")

        _, total = gestor.listar(busqueda=None, offset=0, limit=1)

        assert total == 3


class TestActualizar:
    def test_cambia_el_tipo_vehiculo(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        actualizado = gestor.actualizar(
            vehiculo.id, patente=PATENTE, id_tipo_vehiculo=2, id_chofer_habitual=None
        )

        assert actualizado.id_tipo_vehiculo == 2

    def test_asigna_chofer_habitual(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        actualizado = gestor.actualizar(
            vehiculo.id, patente=PATENTE, id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=ID_CHOFER
        )

        assert actualizado.id_chofer_habitual == ID_CHOFER

    def test_puede_quitar_chofer_habitual(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor, id_chofer=ID_CHOFER)

        actualizado = gestor.actualizar(
            vehiculo.id, patente=PATENTE, id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=None
        )

        assert actualizado.id_chofer_habitual is None

    def test_conserva_el_id(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        actualizado = gestor.actualizar(
            vehiculo.id, patente=PATENTE, id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=None
        )

        assert actualizado.id == vehiculo.id

    def test_rechaza_tomar_la_patente_de_otro_vehiculo(self, gestor: GestorVehiculos) -> None:
        primero = _registrar(gestor, "ABC 123")
        segundo = _registrar(gestor, "XYZ 789")

        with pytest.raises(PatenteDuplicada):
            gestor.actualizar(
                segundo.id, patente="ABC 123", id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=None
            )

        assert gestor.obtener(primero.id).patente == "ABC 123"
        assert gestor.obtener(segundo.id).patente == "XYZ 789"

    def test_guardar_los_mismos_datos_no_choca_consigo_mismo(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor, "ABC 123")

        actualizado = gestor.actualizar(
            vehiculo.id, patente="abc 123", id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=None
        )

        assert actualizado.patente == "ABC 123"

    def test_rechaza_tipo_vehiculo_inexistente(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        with pytest.raises(TipoVehiculoInvalido):
            gestor.actualizar(
                vehiculo.id, patente=PATENTE, id_tipo_vehiculo=999, id_chofer_habitual=None
            )

    def test_rechaza_chofer_inexistente(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        with pytest.raises(ChoferInvalido):
            gestor.actualizar(
                vehiculo.id, patente=PATENTE, id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=999
            )

    @pytest.mark.parametrize("patente", ["", "ABC 12", "ABCD 123"])
    def test_rechaza_patente_invalida(self, gestor: GestorVehiculos, patente: str) -> None:
        vehiculo = _registrar(gestor)

        with pytest.raises(ReglaNegocioError):
            gestor.actualizar(
                vehiculo.id, patente=patente, id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=None
            )

    def test_no_altera_el_vehiculo_ante_un_dato_invalido(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        with pytest.raises(ReglaNegocioError):
            gestor.actualizar(
                vehiculo.id, patente="INVALID", id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=None
            )

        assert gestor.obtener(vehiculo.id).patente == PATENTE

    def test_lanza_error_si_el_vehiculo_no_existe(self, gestor: GestorVehiculos) -> None:
        with pytest.raises(VehiculoNoEncontrado):
            gestor.actualizar(
                999, patente=PATENTE, id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=None
            )

    def test_no_crea_registros_al_actualizar_un_id_inexistente(
        self, gestor: GestorVehiculos, repo: FakeVehiculoRepo
    ) -> None:
        with pytest.raises(VehiculoNoEncontrado):
            gestor.actualizar(
                999, patente=PATENTE, id_tipo_vehiculo=ID_TIPO, id_chofer_habitual=None
            )

        assert repo.contar(None) == 0


class TestEliminar:
    def test_da_de_baja_un_vehiculo_sin_servicios(
        self, gestor: GestorVehiculos, consulta_servicios: FakeConsultaServiciosVehiculo
    ) -> None:
        vehiculo = _registrar(gestor)

        gestor.eliminar(vehiculo.id)

        with pytest.raises(VehiculoNoEncontrado):
            gestor.obtener(vehiculo.id)
        assert consulta_servicios.consultas == [vehiculo.id]

    def test_el_vehiculo_dado_de_baja_desaparece_del_listado(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        gestor.eliminar(vehiculo.id)
        resultado, total = gestor.listar(busqueda=None, offset=0, limit=20)

        assert resultado == []
        assert total == 0

    def test_rechaza_dar_de_baja_un_vehiculo_con_servicios(
        self, gestor: GestorVehiculos, consulta_servicios: FakeConsultaServiciosVehiculo
    ) -> None:
        vehiculo = _registrar(gestor)
        consulta_servicios.marcar_con_servicios(vehiculo.id)

        with pytest.raises(VehiculoConServicios):
            gestor.eliminar(vehiculo.id)

    def test_no_desactiva_un_vehiculo_con_servicios(
        self,
        gestor: GestorVehiculos,
        consulta_servicios: FakeConsultaServiciosVehiculo,
        repo: FakeVehiculoRepo,
    ) -> None:
        vehiculo = _registrar(gestor)
        consulta_servicios.marcar_con_servicios( vehiculo.id)

        with pytest.raises(VehiculoConServicios):
            gestor.eliminar(vehiculo.id)

        assert repo.llamadas_desactivar == []
        assert gestor.obtener(vehiculo.id).activo is True

    def test_eliminar_dos_veces_es_idempotente(self, gestor: GestorVehiculos) -> None:
        vehiculo = _registrar(gestor)

        gestor.eliminar(vehiculo.id)
        gestor.eliminar(vehiculo.id)

        with pytest.raises(VehiculoNoEncontrado):
            gestor.obtener(vehiculo.id)

    def test_lanza_error_si_el_vehiculo_no_existe(self, gestor: GestorVehiculos) -> None:
        with pytest.raises(VehiculoNoEncontrado):
            gestor.eliminar(999)
