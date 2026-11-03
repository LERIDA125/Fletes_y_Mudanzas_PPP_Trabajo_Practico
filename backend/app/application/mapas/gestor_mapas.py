"""Casos de uso de geocodificación y rutas."""

from app.application.mapas.puertos import (
    Coordenada,
    RutaCalculada,
    ServicioMapas,
    SugerenciaDireccion,
)


class GestorMapas:
    def __init__(self, servicio: ServicioMapas) -> None:
        self._servicio = servicio

    async def buscar_direcciones(self, consulta: str) -> list[SugerenciaDireccion]:
        return await self._servicio.buscar_direcciones(consulta)

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> RutaCalculada:
        return await self._servicio.calcular_ruta(origen, destino)
