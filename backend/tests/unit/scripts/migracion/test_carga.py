"""Tests de la carga de clientes (FR-004 a FR-007).

La carga se prueba contra un doble de `ClienteRepo`, sin PostgreSQL. Lo que importa verificar acá es
que la escritura pase por el repositorio de H1 (nunca por un `INSERT` a mano) y que correr dos
veces no duplique nada.
"""

import pytest

from app.domain.cliente import Cliente
from app.domain.errores import RazonSocialDuplicada, ReglaNegocioError
from scripts.migracion.carga import ResultadoCarga, cargar_clientes, cliente_creable
from scripts.migracion.revision import Gravedad, Motivo
from scripts.migracion.transformacion import ClienteMigrable


class ClienteRepoFalso:
    """Doble de `ClienteRepo` que registra las llamadas, para poder afirmar que se usó."""

    def __init__(self) -> None:
        self.creados: list[Cliente] = []
        self._siguiente_id = 1

    def crear(self, cliente: Cliente) -> Cliente:
        self.creados.append(cliente)
        cliente.id = self._siguiente_id
        self._siguiente_id += 1
        return cliente

    def existe_razon_social(self, razon_social_key: str, excluir_id: int | None = None) -> bool:
        return any(c.razon_social_key == razon_social_key for c in self.creados)


def migrable(nombre: str, telefono: str | None = "1122334455", **extra) -> ClienteMigrable:
    datos = {
        "nombre": nombre,
        "nombre_key": nombre.lower(),
        "telefono": telefono,
        "direccion": "Av. Cabildo 2140",
        "direccion_es_estructurada": True,
        "codigo_origen": "CLI-101",
        "localidad_barrio": None,
        "condicion_iva": None,
        "historial_pagos": None,
        "fila_origen": 2,
        "hoja_origen": "Clientes_Cotizaciones",
    }
    datos.update(extra)
    return ClienteMigrable(**datos)


@pytest.fixture
def repo() -> ClienteRepoFalso:
    return ClienteRepoFalso()


class TestClienteCreable:
    def test_se_construye_con_los_cuatro_campos_de_h1(self) -> None:
        cliente = cliente_creable(migrable("Muebles Belgrano S.R.L."))

        assert isinstance(cliente, Cliente)
        assert cliente.razon_social == "Muebles Belgrano S.R.L."
        assert cliente.telefono == "1122334455"
        assert cliente.direccion_habitual == "Av. Cabildo 2140"

    @pytest.mark.parametrize(
        "historial", ["Cuenta corriente", "Fiado de palabra", "Paga a 30 días", "Efectivo"]
    )
    def test_la_cuenta_corriente_siempre_queda_en_false(self, historial: str) -> None:
        """FR-021 / DP-06: ni siquiera un historial que dice "Cuenta corriente" lo prende."""
        cliente = cliente_creable(migrable("Panificadora Sur", historial_pagos=historial))

        assert cliente.tiene_cuenta_corriente is False


class TestCargarClientes:
    def test_carga_un_cliente_por_uno(self, repo: ClienteRepoFalso) -> None:
        resultado = cargar_clientes([migrable("Uno"), migrable("Dos")], repo)

        assert len(resultado.agregados) == 2
        assert resultado.omitidos == []
        assert resultado.ya_existentes == []

    def test_la_escritura_pasa_por_el_repositorio(self, repo: ClienteRepoFalso) -> None:
        """FR-004: se usa `ClienteRepo.crear`, no un INSERT propio."""
        cargar_clientes([migrable("Uno")], repo)

        assert len(repo.creados) == 1
        assert repo.creados[0].razon_social == "Uno"

    def test_correr_dos_veces_no_duplica_clientes(self, repo: ClienteRepoFalso) -> None:
        """FR-005: la idempotencia es lo que hace recuperable el procedimiento."""
        clientes = [migrable("Uno"), migrable("Dos")]

        primera = cargar_clientes(clientes, repo)
        segunda = cargar_clientes(clientes, repo)

        assert len(primera.agregados) == 2
        assert len(segunda.agregados) == 0
        assert sorted(segunda.ya_existentes) == ["Dos", "Uno"]
        assert len(repo.creados) == 2

    def test_reconoce_un_cliente_que_ya_estaba_cargado_a_mano(self, repo: ClienteRepoFalso) -> None:
        """El `UNIQUE` de `razon_social_key` de H1 también protege contra esto."""
        repo.creados.append(cliente_creable(migrable("Distribuidora  del sur")))

        resultado = cargar_clientes([migrable("DISTRIBUIDORA DEL SUR")], repo)

        assert resultado.agregados == []
        assert resultado.ya_existentes == ["DISTRIBUIDORA DEL SUR"]

    def test_un_cliente_sin_telefono_se_omite_y_se_reporta(self, repo: ClienteRepoFalso) -> None:
        resultado = cargar_clientes([migrable("Sin Telefono", telefono=None)], repo)

        assert resultado.agregados == []
        assert resultado.omitidos == ["Sin Telefono"]
        bloqueantes = [c for c in resultado.casos if c.gravedad is Gravedad.BLOQUEANTE]
        assert len(bloqueantes) == 1
        assert bloqueantes[0].motivo is Motivo.DATO_INCOMPLETO

    def test_una_fila_invalida_no_corta_la_carga_de_las_demas(self, repo: ClienteRepoFalso) -> None:
        """FR-007: una fila ilegible no puede abortar la migración entera."""
        resultado = cargar_clientes(
            [
                migrable("Bueno"),
                migrable("Sin Telefono", telefono=None),
                migrable("Bueno Dos"),
            ],
            repo,
        )

        assert len(resultado.agregados) == 2
        assert resultado.omitidos == ["Sin Telefono"]

    def test_un_dominio_que_rechaza_el_cliente_lo_omite(self, repo: ClienteRepoFalso) -> None:
        """Una dirección demasiado corta la rechaza `Cliente` (mínimo 5 caracteres)."""
        resultado = cargar_clientes([migrable("Corto", direccion="Av 1")], repo)

        assert resultado.agregados == []
        assert resultado.omitidos == ["Corto"]
        assert "dominio lo rechazó" in resultado.casos[0].detalle

    def test_dos_filas_con_la_misma_razon_social_no_producen_dos_clientes(
        self, repo: ClienteRepoFalso
    ) -> None:
        resultado = cargar_clientes([migrable("Igual"), migrable("Igual")], repo)

        assert len(resultado.agregados) == 1
        assert resultado.ya_existentes == ["Igual"]

    def test_simular_no_escribe_nada(self, repo: ClienteRepoFalso) -> None:
        resultado = cargar_clientes([migrable("Uno")], repo, simular=True)

        assert len(resultado.agregados) == 1
        assert repo.creados == []

    def test_el_resultado_cuenta_los_procesados(self, repo: ClienteRepoFalso) -> None:
        """FR-006: la carga informa cuántos se agregaron, cuántos ya existían y cuántos se
        omitieron."""
        resultado = cargar_clientes(
            [migrable("Uno"), migrable("Sin Telefono", telefono=None)], repo
        )

        assert resultado.total_procesados == 2


class TestRobustezAnteColisionDeLaBase:
    """`existe_razon_social` y el `UNIQUE` de la base son dos chequeos distintos.

    El primero se puede ir al aire: si otra corrida del script —o alguien a mano— inserta la misma
    razón social entre el chequeo y el `INSERT`, el `UNIQUE` salta después. Estos tests fuerzan
    justo esa carrera, con un repositorio que miente en el chequeo previo.
    """

    class RepoQueMienteEnElChequeo(ClienteRepoFalso):
        def existe_razon_social(self, razon_social_key: str, excluir_id: int | None = None) -> bool:
            return False  # el chequeo previo no ve nada

    class RepoQueRechazaLaSegunda(RepoQueMienteEnElChequeo):
        def crear(self, cliente: Cliente) -> Cliente:
            if cliente.razon_social == "Choca":
                raise RazonSocialDuplicada(cliente.razon_social)
            return super().crear(cliente)

    def test_el_choque_no_rompe_la_carga(self) -> None:
        resultado = cargar_clientes(
            [migrable("Uno"), migrable("Choca"), migrable("Dos")], self.RepoQueRechazaLaSegunda()
        )

        assert [c.razon_social for c in resultado.agregados] == ["Uno", "Dos"]
        assert resultado.ya_existentes == ["Choca"]

    def test_un_cliente_ya_cargado_no_se_pierde_por_un_choque_posterior(self) -> None:
        """Regresión: el `except` no puede borrar lo que ya se había agregado.

        El `append` ocurre después de `repo.crear(...)`, así que cuando `crear` levanta, el cliente
        que falló nunca llegó a la lista y no hay nada que deshacer. Deshacer el `pop()` de todas
        formas se comía el alta anterior y el reporte daba un número de cargados más chico que el
        real.
        """
        resultado = cargar_clientes(
            [migrable("Primero"), migrable("Choca"), migrable("Tercero")],
            self.RepoQueRechazaLaSegunda(),
        )

        assert [c.razon_social for c in resultado.agregados] == ["Primero", "Tercero"]

    def test_el_choque_queda_reportado_para_que_lo_revise_una_persona(self) -> None:
        """No se corta en silencio: queda el caso en la cola de revisión humana."""
        resultado = cargar_clientes([migrable("Choca")], self.RepoQueRechazaLaSegunda())

        assert resultado.casos[0].motivo is Motivo.DUPLICADO
        assert resultado.casos[0].gravedad is Gravedad.A_CONFIRMAR

    def test_sin_choque_todo_entra_normal(self) -> None:
        """Control: el mismo falso, sin choque, carga todo."""
        resultado = cargar_clientes(
            [migrable("Uno"), migrable("Dos")], self.RepoQueRechazaLaSegunda()
        )

        assert [c.razon_social for c in resultado.agregados] == ["Uno", "Dos"]
        assert resultado.casos == []


class TestResultadoCarga:
    def test_una_carga_vacia_no_escribio(self) -> None:
        resultado = ResultadoCarga()

        assert resultado.escribio is False

    def test_una_carga_con_algo_escribio(self, repo: ClienteRepoFalso) -> None:
        resultado = cargar_clientes([migrable("Uno")], repo)

        assert resultado.escribio is True


class TestClienteInvalidoPorDominio:
    def test_el_dominio_sigue_siendo_el_que_rechaza(self) -> None:
        """La migración no reimplementa las reglas de H1: las usa tal como están."""
        with pytest.raises(ReglaNegocioError):
            Cliente.crear(razon_social="Ab", telefono="1122334455", direccion_habitual="Av. X 123")
