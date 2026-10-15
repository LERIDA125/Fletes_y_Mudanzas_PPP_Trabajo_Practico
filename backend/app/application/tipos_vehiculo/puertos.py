from typing import Protocol, runtime_checkable

from app.domain.tipo_vehiculo import TipoVehiculo


@runtime_checkable
class TipoVehiculoRepository(Protocol):
    """Puerto de persistencia de tipos de vehículo. Lo implementa app/infrastructure/."""

    def crear(self, tipo: TipoVehiculo) -> TipoVehiculo: ...

    def obtener_por_id(self, tipo_id: int) -> TipoVehiculo | None: ...

    def listar(self, busqueda: str | None, offset: int, limit: int) -> list[TipoVehiculo]: ...

    def contar(self, busqueda: str | None) -> int: ...

    def actualizar(self, tipo: TipoVehiculo) -> TipoVehiculo: ...

    def desactivar(self, tipo_id: int) -> None: ...

    def existe_descripcion(self, descripcion_key: str, excluir_id: int | None = None) -> bool: ...


@runtime_checkable
class ConsultaVehiculosPorTipo(Protocol):
    """Verifica si un tipo de vehículo tiene vehículos asociados.

    Implementación real: llega con la historia de Vehículos. Ver spec H4.
    """

    def tiene_vehiculos(self, tipo_id: int) -> bool: ...
