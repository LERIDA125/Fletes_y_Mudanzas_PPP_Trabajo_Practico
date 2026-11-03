"""Contratos de salida para los servicios externos de mapas."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Coordenada:
    longitud: Decimal
    latitud: Decimal


@dataclass(frozen=True)
class SugerenciaDireccion:
    etiqueta: str
    coordenada: Coordenada


@dataclass(frozen=True)
class RutaCalculada:
    distancia_ida_km: Decimal
    duracion_segundos: Decimal


class ServicioMapas(Protocol):
    async def buscar_direcciones(self, consulta: str) -> list[SugerenciaDireccion]: ...

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> RutaCalculada: ...
