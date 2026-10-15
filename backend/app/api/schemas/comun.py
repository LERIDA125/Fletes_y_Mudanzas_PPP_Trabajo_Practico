"""Esquemas comunes y genéricos para la API."""

import math

from pydantic import BaseModel, Field


class Pagina[T](BaseModel):
    """Página de resultados con paginación genérica."""

    items: list[T]
    total: int = Field(description="Cantidad total de registros que cumplen el filtro.")
    page: int = Field(description="Número de página actual (base 1).")
    size: int = Field(description="Cantidad de elementos por página.")

    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.size) if self.size > 0 else 0
