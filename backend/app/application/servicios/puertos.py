"""Puertos de aplicación para Servicios y Rendiciones."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Protocol, runtime_checkable

from app.application.vehiculos.puertos import VehiculoListadoItem
from app.domain.chofer import Chofer
from app.domain.cliente import Cliente
from app.domain.servicio import Servicio
from app.domain.tipo_vehiculo import TipoVehiculo
from app.domain.vehiculo import Vehiculo


@dataclass(frozen=True)
class ServicioListadoItem:
    servicio: Servicio
    razon_social_cliente: str
    descripcion_tipo_vehiculo: str
    nombre_chofer: str | None
    patente_vehiculo: str | None


@dataclass(frozen=True)
class AsignacionDia:
    """Servicio ya agendado para una fecha, usado para detectar solapamientos."""

    id_chofer: int | None
    id_vehiculo: int | None
    hora_inicio: time | None
    horas_estimadas: Decimal


@dataclass(frozen=True)
class Disponibilidad:
    """Recursos activos que quedan libres para la ventana consultada."""

    hora_fin: time | None
    choferes: list[Chofer]
    vehiculos: list[VehiculoListadoItem]


@runtime_checkable
class AlmacenamientoRemitosPort(Protocol):
    """Puerto para almacenar la foto del remito firmado (Base64 en BD o Vercel Blob en la nube)."""

    def guardar(
        self,
        *,
        id_servicio: int,
        contenido: bytes,
        content_type: str,
        nombre_archivo: str | None = None,
    ) -> str: ...


@runtime_checkable
class ServicioRepository(Protocol):
    def crear(self, servicio: Servicio) -> ServicioListadoItem: ...

    def obtener_por_id(self, servicio_id: int) -> ServicioListadoItem | None: ...

    def actualizar(self, servicio: Servicio) -> ServicioListadoItem: ...

    def eliminar(self, servicio_id: int) -> None: ...

    def listar(
        self, offset: int, limit: int, id_chofer: int | None = None
    ) -> list[ServicioListadoItem]: ...

    def contar(self, id_chofer: int | None = None) -> int: ...

    def tiene_historial(self, cliente_id: int) -> bool: ...

    def tiene_servicios(self, vehiculo_id: int) -> bool: ...

    def listar_asignaciones_del_dia(self, fecha: date) -> list[AsignacionDia]: ...


@runtime_checkable
class ConsultaClienteServicio(Protocol):
    def obtener_por_id(self, cliente_id: int) -> Cliente | None: ...


@runtime_checkable
class RegistroClienteServicio(Protocol):
    """Alta implícita de un cliente desde el formulario de Servicios."""

    def obtener_por_razon_social(self, razon_social_key: str) -> Cliente | None: ...

    def crear(self, cliente: Cliente) -> Cliente: ...


@runtime_checkable
class ConsultaChoferServicio(Protocol):
    def obtener_por_id(self, chofer_id: int) -> Chofer | None: ...

    def listar_activos(self) -> list[Chofer]: ...


@runtime_checkable
class ConsultaVehiculoServicio(Protocol):
    def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None: ...

    def listar_activos_por_tipo(self, tipo_vehiculo_id: int) -> list[VehiculoListadoItem]: ...


@runtime_checkable
class ConsultaTipoServicio(Protocol):
    def obtener_por_id(self, tipo_vehiculo_id: int) -> TipoVehiculo | None: ...
