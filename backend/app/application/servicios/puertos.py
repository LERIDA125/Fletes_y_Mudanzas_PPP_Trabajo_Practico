"""Puertos de aplicación para Servicios."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.domain.chofer import Chofer
from app.domain.cliente import Cliente
from app.domain.servicio import Servicio
from app.domain.vehiculo import Vehiculo


@dataclass(frozen=True)
class ServicioListadoItem:
    servicio: Servicio
    razon_social_cliente: str
    descripcion_tipo_vehiculo: str
    nombre_chofer: str | None
    patente_vehiculo: str | None


@runtime_checkable
class ServicioRepository(Protocol):
    def crear(self, servicio: Servicio) -> ServicioListadoItem: ...

    def listar(self, offset: int, limit: int) -> list[ServicioListadoItem]: ...

    def contar(self) -> int: ...

    def tiene_historial(self, cliente_id: int) -> bool: ...

    def tiene_servicios(self, vehiculo_id: int) -> bool: ...


@runtime_checkable
class ConsultaClienteServicio(Protocol):
    def obtener_por_id(self, cliente_id: int) -> Cliente | None: ...


@runtime_checkable
class ConsultaChoferServicio(Protocol):
    def obtener_por_id(self, chofer_id: int) -> Chofer | None: ...


@runtime_checkable
class ConsultaVehiculoServicio(Protocol):
    def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None: ...
