"""Repositorios en memoria para testear app/application/ sin levantar PostgreSQL.

AGENTS.md §8: los tests de la capa de Aplicación van con el repositorio mockeado.
"""

from app.application.clientes.puertos import ClienteRepository
from app.domain.cliente import Cliente


class ClienteYaExiste(Exception):
    """Simula el error de base de datos cuando se viola el UNIQUE de razon_social_key."""


class FakeClienteRepo(ClienteRepository):
    def __init__(self) -> None:
        self._por_id: dict[int, Cliente] = {}
        self._siguiente_id = 1
        self.llamadas_desactivar: list[int] = []

    def crear(self, cliente: Cliente) -> Cliente:
        self._verificar_unicidad(cliente.razon_social_key)
        cliente.id = self._siguiente_id
        self._siguiente_id += 1
        self._por_id[cliente.id] = cliente
        return cliente

    def obtener_por_id(self, cliente_id: int) -> Cliente | None:
        return self._por_id.get(cliente_id)

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[Cliente]:
        candidatos = self._filtrar(busqueda)
        return candidatos[offset : offset + limit]

    def contar(self, busqueda: str | None) -> int:
        return len(self._filtrar(busqueda))

    def actualizar(self, cliente: Cliente) -> Cliente:
        self._verificar_unicidad(cliente.razon_social_key, excluir_id=cliente.id)
        self._por_id[cliente.id] = cliente
        return cliente

    def desactivar(self, cliente_id: int) -> None:
        self.llamadas_desactivar.append(cliente_id)
        self._por_id[cliente_id].desactivar()

    def existe_razon_social(self, razon_social_key: str, excluir_id: int | None = None) -> bool:
        return any(
            cliente.razon_social_key == razon_social_key and cliente.id != excluir_id
            for cliente in self._por_id.values()
        )

    def _filtrar(self, busqueda: str | None) -> list[Cliente]:
        from app.domain.cliente import normalizar_razon_social

        activos = [cliente for cliente in self._por_id.values() if cliente.activo]
        if not busqueda:
            return sorted(activos, key=lambda cliente: cliente.id)
        clave = normalizar_razon_social(busqueda)
        return sorted(
            (cliente for cliente in activos if clave in cliente.razon_social_key),
            key=lambda cliente: cliente.id,
        )

    def _verificar_unicidad(self, razon_social_key: str, excluir_id: int | None = None) -> None:
        if self.existe_razon_social(razon_social_key, excluir_id=excluir_id):
            raise ClienteYaExiste(razon_social_key)


class FakeHistorial:
    def __init__(self) -> None:
        self.clientes_con_historial: set[int] = set()
        self.consultas: list[int] = []

    def tiene_historial(self, cliente_id: int) -> bool:
        self.consultas.append(cliente_id)
        return cliente_id in self.clientes_con_historial

    def marcar_con_historial(self, cliente_id: int) -> None:
        self.clientes_con_historial.add(cliente_id)
