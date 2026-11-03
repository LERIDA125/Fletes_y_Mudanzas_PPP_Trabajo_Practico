"""Schemas de búsqueda de direcciones y cálculo de rutas."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MapaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DireccionBuscarRequest(MapaRequest):
    consulta: str = Field(min_length=3, max_length=200)

    @field_validator("consulta")
    @classmethod
    def _consulta_recortada(cls, valor: str) -> str:
        limpio = valor.strip()
        if len(limpio) < 3:
            raise ValueError("Ingresá al menos 3 caracteres para buscar una dirección")
        return limpio


class CoordenadaMapa(MapaRequest):
    longitud: Decimal = Field(
        ge=-180,
        le=180,
        allow_inf_nan=False,
        description="Longitud geográfica en grados decimales.",
    )
    latitud: Decimal = Field(
        ge=-90,
        le=90,
        allow_inf_nan=False,
        description="Latitud geográfica en grados decimales.",
    )


class RutaRequest(MapaRequest):
    origen: CoordenadaMapa
    destino: CoordenadaMapa


class DireccionOpcionRead(CoordenadaMapa):
    etiqueta: str


class DireccionesRead(BaseModel):
    opciones: list[DireccionOpcionRead]


class RutaRead(BaseModel):
    distancia_ida_km: Decimal = Field(
        ge=0,
        description="Distancia de ida en kilómetros, redondeada a dos decimales.",
    )
    duracion_segundos: Decimal = Field(
        ge=0,
        description="Duración estimada de ida en segundos.",
    )
