"""Puertos de aplicación para Rendiciones."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Protocol, runtime_checkable

from app.domain.rendicion import Rendicion


@dataclass(frozen=True)
class RendicionListadoItem:
    rendicion: Rendicion
    nombre_chofer: str
    razon_social_cliente: str


@dataclass(frozen=True)
class ResumenRendiciones:
    pendiente_total: Decimal
    pendiente_cantidad: int
    aprobado_mes_total: Decimal
    gastos_total: Decimal


@dataclass(frozen=True)
class ServicioParaRendir:
    """Datos mínimos del servicio para validar elegibilidad en Aplicación."""

    id_servicio: int
    id_chofer: int | None
    fecha: date
    estado: str


@dataclass(frozen=True)
class ServicioElegible:
    """Servicio finalizado con chofer que todavía no tiene rendición."""

    id_servicio: int
    razon_social_cliente: str
    nombre_chofer: str
    fecha: date
    hora_inicio: time | None
    precio_total: Decimal


@runtime_checkable
class RendicionRepository(Protocol):
    def crear(self, rendicion: Rendicion) -> RendicionListadoItem: ...

    def obtener_por_id(self, rendicion_id: int) -> RendicionListadoItem | None: ...

    def listar(
        self, busqueda: str | None, offset: int, limit: int
    ) -> list[RendicionListadoItem]: ...

    def contar(self, busqueda: str | None) -> int: ...

    def resumen(self, *, anio: int, mes: int) -> ResumenRendiciones: ...

    def actualizar(self, rendicion: Rendicion) -> RendicionListadoItem: ...

    def existe_para_servicio(self, servicio_id: int) -> bool: ...


@runtime_checkable
class ConsultaServiciosRendibles(Protocol):
    def listar_elegibles(self) -> list[ServicioElegible]: ...

    def obtener_para_rendir(self, servicio_id: int) -> ServicioParaRendir | None: ...
