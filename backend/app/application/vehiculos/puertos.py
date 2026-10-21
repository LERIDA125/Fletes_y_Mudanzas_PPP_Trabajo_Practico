from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, runtime_checkable

from app.domain.vehiculo import Vehiculo


@dataclass(frozen=True)
class VehiculoListadoItem:
    vehiculo: Vehiculo
    descripcion_tipo_vehiculo: str
    capacidad_carga_kg: Decimal
    nombre_chofer_habitual: str | None


@runtime_checkable
class VehiculoRepository(Protocol):
    """Puerto de persistencia de vehículos. Lo implementa app/infrastructure/."""

    def crear(self, vehiculo: Vehiculo) -> Vehiculo: ...

    def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None: ...

    def listar(
        self, busqueda: str | None, offset: int, limit: int
    ) -> list[VehiculoListadoItem]: ...

    def contar(self, busqueda: str | None) -> int: ...

    def actualizar(self, vehiculo: Vehiculo) -> Vehiculo: ...

    def desactivar(self, vehiculo_id: int) -> None: ...

    def existe_patente(self, patente: str, excluir_id: int | None = None) -> bool: ...


@runtime_checkable
class ConsultaTipoVehiculo(Protocol):
    """Verifica si un tipo de vehículo existe y está activo.

    Implementación real: llega con la historia de Vehículos. Ver spec H4.
    """

    def existe_activo(self, tipo_id: int) -> bool: ...


@runtime_checkable
class ConsultaChofer(Protocol):
    """Verifica si un chofer existe y está activo.

    Implementación real: llega con la historia de Choferes (H2). Ver spec H4.
    """

    def existe_activo(self, chofer_id: int) -> bool: ...


@runtime_checkable
class ConsultaServiciosVehiculo(Protocol):
    """Verifica si un vehículo tiene servicios asociados.

    Implementación real: llega con la historia de Servicios (H6). Ver spec H4.
    """

    def tiene_servicios(self, vehiculo_id: int) -> bool: ...
