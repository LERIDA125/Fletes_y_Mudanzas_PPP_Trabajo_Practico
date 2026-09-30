from typing import Protocol, runtime_checkable

from app.domain.cliente import Cliente


@runtime_checkable
class ClienteRepository(Protocol):
    """Puerto de persistencia de clientes. Lo implementa app/infrastructure/."""

    def crear(self, cliente: Cliente) -> Cliente: ...

    def obtener_por_id(self, cliente_id: int) -> Cliente | None: ...

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[Cliente]: ...

    def contar(self, busqueda: str | None) -> int: ...

    def actualizar(self, cliente: Cliente) -> Cliente: ...

    def desactivar(self, cliente_id: int) -> None: ...

    def existe_razon_social(self, razon_social_key: str, excluir_id: int | None = None) -> bool: ...


@runtime_checkable
class ConsultaHistorialCliente(Protocol):
    """Verifica si el cliente tiene servicios, cotizaciones o rendiciones asociadas.

    Implementación real: llega con la historia de Servicios. Ver FR-015.
    """

    def tiene_historial(self, cliente_id: int) -> bool: ...
