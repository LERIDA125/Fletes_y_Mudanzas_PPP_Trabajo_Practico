import pytest

from app.application.clientes.gestor_clientes import GestorClientes
from app.domain.errores import (
    ClienteConHistorial,
    ClienteNoEncontrado,
    RazonSocialDuplicada,
    ReglaNegocioError,
)
from tests.unit.application.clientes.fakes import FakeClienteRepo, FakeHistorial

RAZON_SOCIAL = "Distribuidora del Sur S.A."
TELEFONO = "351 555 0100"
DIRECCION = "Av. Colón 1250"


@pytest.fixture
def repo() -> FakeClienteRepo:
    return FakeClienteRepo()


@pytest.fixture
def historial() -> FakeHistorial:
    return FakeHistorial()


@pytest.fixture
def gestor(repo: FakeClienteRepo, historial: FakeHistorial) -> GestorClientes:
    return GestorClientes(repositorio_clientes=repo, consulta_historial=historial)


def _registrar(gestor: GestorClientes, razon_social: str = RAZON_SOCIAL, **kwargs):
    return gestor.registrar(
        razon_social=razon_social,
        telefono=kwargs.get("telefono", TELEFONO),
        direccion_habitual=kwargs.get("direccion_habitual", DIRECCION),
        tiene_cuenta_corriente=kwargs.get("tiene_cuenta_corriente", False),
    )


class TestRegistrar:
    def test_registra_con_los_cuatro_datos_pedidos(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        assert cliente.razon_social == RAZON_SOCIAL
        assert cliente.telefono == TELEFONO
        assert cliente.direccion_habitual == DIRECCION
        assert cliente.tiene_cuenta_corriente is False

    def test_asigna_identificador_y_deja_el_cliente_activo(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        assert cliente.id is not None
        assert cliente.activo is True

    def test_registra_con_cuenta_corriente(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor, tiene_cuenta_corriente=True)

        assert cliente.tiene_cuenta_corriente is True

    def test_rechaza_razon_social_ya_registrada(self, gestor: GestorClientes) -> None:
        _registrar(gestor)

        with pytest.raises(RazonSocialDuplicada):
            _registrar(gestor)

    def test_rechaza_razon_social_duplicada_con_distinta_capitalizacion(
        self, gestor: GestorClientes
    ) -> None:
        _registrar(gestor)

        with pytest.raises(RazonSocialDuplicada):
            _registrar(gestor, "  DISTRIBUIDORA  DEL SUR S.A. ")

    def test_rechaza_razon_social_duplicada_sin_acentos(self, gestor: GestorClientes) -> None:
        _registrar(gestor, "Almacén Central S.A.")

        with pytest.raises(RazonSocialDuplicada):
            _registrar(gestor, "Almacen Central S.A.")

    def test_no_registra_un_segundo_cliente_al_rechazar_el_duplicado(
        self, gestor: GestorClientes, repo: FakeClienteRepo
    ) -> None:
        _registrar(gestor)

        with pytest.raises(RazonSocialDuplicada):
            _registrar(gestor, "Distribuidora del Sur S.A.")

        assert repo.contar(None) == 1

    @pytest.mark.parametrize(
        ("campo", "valor"),
        [
            ("razon_social", "Ab"),
            ("razon_social", "   "),
            ("telefono", "123"),
            ("direccion_habitual", "Av 1"),
        ],
    )
    def test_rechaza_datos_invalidos(self, gestor: GestorClientes, campo: str, valor: str) -> None:
        datos = {
            "razon_social": RAZON_SOCIAL,
            "telefono": TELEFONO,
            "direccion_habitual": DIRECCION,
            "tiene_cuenta_corriente": False,
        }
        datos[campo] = valor

        with pytest.raises(ReglaNegocioError):
            gestor.registrar(**datos)

    def test_no_persiste_nada_ante_un_dato_invalido(
        self, gestor: GestorClientes, repo: FakeClienteRepo
    ) -> None:
        with pytest.raises(ReglaNegocioError):
            gestor.registrar(
                razon_social=RAZON_SOCIAL,
                telefono="1",
                direccion_habitual=DIRECCION,
                tiene_cuenta_corriente=False,
            )

        assert repo.contar(None) == 0


class TestObtener:
    def test_devuelve_el_cliente_registrado(self, gestor: GestorClientes) -> None:
        registrado = _registrar(gestor)

        obtener = gestor.obtener(registrado.id)

        assert obtener.id == registrado.id
        assert obtener.razon_social == RAZON_SOCIAL

    def test_lanza_error_si_no_existe(self, gestor: GestorClientes) -> None:
        with pytest.raises(ClienteNoEncontrado):
            gestor.obtener(999)

    def test_no_devuelve_clientes_dados_de_baja(self, gestor: GestorClientes) -> None:
        registrado = _registrar(gestor)
        gestor.eliminar(registrado.id)

        with pytest.raises(ClienteNoEncontrado):
            gestor.obtener(registrado.id)


class TestListar:
    def test_lista_solo_clientes_activos(self, gestor: GestorClientes) -> None:
        activo = _registrar(gestor, "Almacén Central S.A.")
        baja = _registrar(gestor, "Distribuidora del Norte S.A.")
        gestor.eliminar(baja.id)

        resultado, total = gestor.listar(busqueda=None, offset=0, limit=20)

        assert total == 1
        assert [cliente.id for cliente in resultado] == [activo.id]

    def test_filtra_por_parte_de_la_razon_social(self, gestor: GestorClientes) -> None:
        _registrar(gestor, "Distribuidora del Sur S.A.")
        _registrar(gestor, "Distribuidora del Norte S.A.")
        otro = _registrar(gestor, "Almacén Central S.A.")

        resultado, total = gestor.listar(busqueda="Distribuidora", offset=0, limit=20)

        assert total == 2
        assert otro.id not in [cliente.id for cliente in resultado]

    def test_el_filtro_ignora_mayusculas_y_acentos(self, gestor: GestorClientes) -> None:
        almacen = _registrar(gestor, "Almacén Central S.A.")

        resultado, total = gestor.listar(busqueda="ALMACEN", offset=0, limit=20)

        assert total == 1
        assert [cliente.id for cliente in resultado] == [almacen.id]

    def test_sin_coincidencias_devuelve_lista_vacia_y_total_cero(
        self, gestor: GestorClientes
    ) -> None:
        _registrar(gestor)

        resultado, total = gestor.listar(busqueda="No existe", offset=0, limit=20)

        assert resultado == []
        assert total == 0

    def test_pagina_por_offset_y_limit(self, gestor: GestorClientes) -> None:
        for indice in range(5):
            _registrar(gestor, f"Cliente Numero {indice}")

        resultado, total = gestor.listar(busqueda=None, offset=1, limit=2)

        assert total == 5
        assert len(resultado) == 2

    def test_el_total_refleja_el_filtro_y_no_la_pagina(self, gestor: GestorClientes) -> None:
        for indice in range(3):
            _registrar(gestor, f"Cliente Numero {indice}")

        _, total = gestor.listar(busqueda=None, offset=0, limit=1)

        assert total == 3


class TestActualizar:
    def test_cambia_el_telefono(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        actualizado = gestor.actualizar(
            cliente.id,
            razon_social=RAZON_SOCIAL,
            telefono="351 555 0199",
            direccion_habitual=DIRECCION,
            tiene_cuenta_corriente=False,
        )

        assert actualizado.telefono == "351 555 0199"

    def test_habilita_la_cuenta_corriente(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        actualizado = gestor.actualizar(
            cliente.id,
            razon_social=RAZON_SOCIAL,
            telefono=TELEFONO,
            direccion_habitual=DIRECCION,
            tiene_cuenta_corriente=True,
        )

        assert actualizado.tiene_cuenta_corriente is True

    def test_conserva_el_id_y_la_fecha_de_creacion(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        actualizado = gestor.actualizar(
            cliente.id,
            razon_social=RAZON_SOCIAL,
            telefono=TELEFONO,
            direccion_habitual=DIRECCION,
            tiene_cuenta_corriente=False,
        )

        assert actualizado.id == cliente.id
        assert actualizado.creado_en == cliente.creado_en

    def test_guardar_sin_cambios_no_altera_los_datos(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor, tiene_cuenta_corriente=True)

        actualizado = gestor.actualizar(
            cliente.id,
            razon_social=RAZON_SOCIAL,
            telefono=TELEFONO,
            direccion_habitual=DIRECCION,
            tiene_cuenta_corriente=True,
        )

        assert actualizado.razon_social == cliente.razon_social
        assert actualizado.tiene_cuenta_corriente is True

    def test_rechaza_tomar_la_razon_social_de_otro_cliente(self, gestor: GestorClientes) -> None:
        primero = _registrar(gestor, "Distribuidora del Sur S.A.")
        segundo = _registrar(gestor, "Distribuidora del Norte S.A.")

        with pytest.raises(RazonSocialDuplicada):
            gestor.actualizar(
                segundo.id,
                razon_social="Distribuidora del Sur S.A.",
                telefono=TELEFONO,
                direccion_habitual=DIRECCION,
                tiene_cuenta_corriente=False,
            )

        intacto = gestor.obtener(primero.id)
        assert intacto.razon_social == "Distribuidora del Sur S.A."
        assert gestor.obtener(segundo.id).razon_social == "Distribuidora del Norte S.A."

    def test_guardar_los_mismos_datos_no_choca_consigo_mismo(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor, "Almacén Central S.A.")

        actualizado = gestor.actualizar(
            cliente.id,
            razon_social="ALMACEN central S.A.",
            telefono=TELEFONO,
            direccion_habitual=DIRECCION,
            tiene_cuenta_corriente=False,
        )

        assert actualizado.razon_social == "ALMACEN central S.A."

    def test_una_razon_social_que_solo_cambia_de_forma_no_choca_consigo_mismo(
        self, gestor: GestorClientes
    ) -> None:
        """La clave normalizada no cambia, pero el texto guardado sí: no debe rechazarse."""
        cliente = _registrar(gestor, "Almacén  Central S.A.")

        actualizado = gestor.actualizar(
            cliente.id,
            razon_social="  ALMACEN central   S.A. ",
            telefono=TELEFONO,
            direccion_habitual=DIRECCION,
            tiene_cuenta_corriente=False,
        )

        assert actualizado.razon_social == "ALMACEN central S.A."
        assert actualizado.razon_social_key == cliente.razon_social_key

    def test_una_razon_social_que_choca_consigo_mismo_no_choca_con_otro_cliente(
        self, gestor: GestorClientes
    ) -> None:
        """Con otro cliente cargado, la comprobación de duplicados tiene que excluirse a sí misma.

        Es el caso que solo se ve con el fake: contra PostgreSQL el UNIQUE de `razon_social_key`
        taparía el error, pero acá el chequeo es el del gestor.
        """
        otro = _registrar(gestor, "Transportes del Norte S.A.")
        cliente = _registrar(gestor, "Transportes del Sur S.A.")

        actualizado = gestor.actualizar(
            cliente.id,
            razon_social="TRANSPORTES DEL SUR S.A.",
            telefono=TELEFONO,
            direccion_habitual=DIRECCION,
            tiene_cuenta_corriente=False,
        )

        assert actualizado.razon_social == "TRANSPORTES DEL SUR S.A."
        assert actualizado.razon_social_key == cliente.razon_social_key
        assert gestor.obtener(otro.id).razon_social == "Transportes del Norte S.A."

    @pytest.mark.parametrize(
        ("campo", "valor"),
        [
            ("razon_social", "Ab"),
            ("telefono", "1"),
            ("direccion_habitual", "Av 1"),
        ],
    )
    def test_rechaza_datos_invalidos(self, gestor: GestorClientes, campo: str, valor: str) -> None:
        cliente = _registrar(gestor)
        datos = {
            "razon_social": RAZON_SOCIAL,
            "telefono": TELEFONO,
            "direccion_habitual": DIRECCION,
            "tiene_cuenta_corriente": False,
        }
        datos[campo] = valor

        with pytest.raises(ReglaNegocioError):
            gestor.actualizar(cliente.id, **datos)

    def test_no_altera_el_cliente_ante_un_dato_invalido(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        with pytest.raises(ReglaNegocioError):
            gestor.actualizar(
                cliente.id,
                razon_social=RAZON_SOCIAL,
                telefono=TELEFONO,
                direccion_habitual="Av 1",
                tiene_cuenta_corriente=False,
            )

        assert gestor.obtener(cliente.id).direccion_habitual == DIRECCION

    def test_lanza_error_si_el_cliente_no_existe(self, gestor: GestorClientes) -> None:
        with pytest.raises(ClienteNoEncontrado):
            gestor.actualizar(
                999,
                razon_social=RAZON_SOCIAL,
                telefono=TELEFONO,
                direccion_habitual=DIRECCION,
                tiene_cuenta_corriente=False,
            )

    def test_no_crea_registros_al_actualizar_un_id_inexistente(
        self, gestor: GestorClientes, repo: FakeClienteRepo
    ) -> None:
        with pytest.raises(ClienteNoEncontrado):
            gestor.actualizar(
                999,
                razon_social=RAZON_SOCIAL,
                telefono=TELEFONO,
                direccion_habitual=DIRECCION,
                tiene_cuenta_corriente=False,
            )

        assert repo.contar(None) == 0


class TestEliminar:
    def test_da_de_baja_un_cliente_sin_historial(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        gestor.eliminar(cliente.id)

        with pytest.raises(ClienteNoEncontrado):
            gestor.obtener(cliente.id)

    def test_el_cliente_dado_de_baja_desaparece_del_listado(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        gestor.eliminar(cliente.id)
        resultado, total = gestor.listar(busqueda=None, offset=0, limit=20)

        assert resultado == []
        assert total == 0

    def test_rechaza_dar_de_baja_un_cliente_con_historial(
        self, gestor: GestorClientes, historial: FakeHistorial
    ) -> None:
        cliente = _registrar(gestor)
        historial.marcar_con_historial(cliente.id)

        with pytest.raises(ClienteConHistorial):
            gestor.eliminar(cliente.id)

    def test_no_desactiva_un_cliente_con_historial(
        self, gestor: GestorClientes, historial: FakeHistorial, repo: FakeClienteRepo
    ) -> None:
        cliente = _registrar(gestor)
        historial.marcar_con_historial(cliente.id)

        with pytest.raises(ClienteConHistorial):
            gestor.eliminar(cliente.id)

        assert repo.llamadas_desactivar == []
        assert gestor.obtener(cliente.id).activo is True

    def test_un_cliente_con_historial_sigue_disponible_en_el_sistema(
        self, gestor: GestorClientes, historial: FakeHistorial
    ) -> None:
        cliente = _registrar(gestor)
        historial.marcar_con_historial(cliente.id)

        with pytest.raises(ClienteConHistorial):
            gestor.eliminar(cliente.id)

        listado, total = gestor.listar(busqueda=None, offset=0, limit=20)
        assert [cliente.id for cliente in listado] == [cliente.id]
        assert total == 1

    def test_consulta_el_historial_una_sola_vez_y_del_cliente_indicado(
        self, gestor: GestorClientes, historial: FakeHistorial
    ) -> None:
        cliente = _registrar(gestor)
        otro = _registrar(gestor, "Transportes del Norte S.A.")
        historial.marcar_con_historial(cliente.id)

        with pytest.raises(ClienteConHistorial):
            gestor.eliminar(cliente.id)

        assert historial.consultas == [cliente.id]
        assert otro.id not in historial.consultas

    def test_eliminar_dos_veces_es_idempotente(self, gestor: GestorClientes) -> None:
        cliente = _registrar(gestor)

        gestor.eliminar(cliente.id)
        gestor.eliminar(cliente.id)

        with pytest.raises(ClienteNoEncontrado):
            gestor.obtener(cliente.id)

    def test_lanza_error_si_el_cliente_no_existe(self, gestor: GestorClientes) -> None:
        with pytest.raises(ClienteNoEncontrado):
            gestor.eliminar(999)
