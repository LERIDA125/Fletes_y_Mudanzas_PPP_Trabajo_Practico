"""Cola de revisión humana.

Todo lo que la migración no puede decidir con confianza se acumula acá en vez de forzar una
categoría (AGENTS.md §6). El reporte final la vuelca en una sección aparte para que alguien la
resuelva antes de que los datos pasen a ser la fuente de verdad.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Motivo(StrEnum):
    """Por qué un caso necesita que lo mire una persona."""

    DUPLICADO = "duplicado"
    MONEDA_EXTRANJERA = "moneda_extranjera"
    DIRECCION_NO_ESTRUCTURADA = "direccion_no_estructurada"
    SIN_MAPEO_EN_MODELO = "sin_mapeo_en_modelo"
    TEXTO_AMBIGUO = "texto_ambiguo"
    DATO_INCOMPLETO = "dato_incompleto"
    SUPUESTO_DE_ANIO = "supuesto_de_anio"
    UNIDAD_IMPLICITA = "unidad_implicita"
    DUPLICADO_EN_ARCHIVO = "duplicado_en_archivo"


class Gravedad(StrEnum):
    """Qué tan bloqueante es el caso."""

    BLOQUEANTE = "bloqueante"
    A_CONFIRMAR = "a_confirmar"


@dataclass(frozen=True)
class RevisionHumana:
    """Un caso que la migración no resolvió sola.

    `hoja` y `fila` apuntan a la celda de la planilla para que se pueda buscar el dato original.
    `detalle` dice qué se hizo y por qué hace falta una decisión humana.
    """

    hoja: str
    fila: int
    clave: str
    motivo: Motivo
    gravedad: Gravedad
    valor_original: str
    detalle: str

    def como_fila_markdown(self) -> str:
        return (
            f"| {self.hoja} | {self.fila} | `{self.clave}` | {self.motivo.value} | "
            f"`{self.valor_original}` | {self.detalle} |"
        )


@dataclass
class ColaDeRevision:
    """Acumula los casos a revisar y lleva la cuenta para el resumen del reporte."""

    casos: list[RevisionHumana] = field(default_factory=list)

    def agregar(self, caso: RevisionHumana) -> None:
        self.casos.append(caso)

    def agregar_varios(self, casos: list[RevisionHumana]) -> None:
        self.casos.extend(casos)

    @property
    def hay_bloqueantes(self) -> bool:
        return any(caso.gravedad is Gravedad.BLOQUEANTE for caso in self.casos)

    def por_hoja(self) -> dict[str, list[RevisionHumana]]:
        agrupado: dict[str, list[RevisionHumana]] = {}
        for caso in self.casos:
            agrupado.setdefault(caso.hoja, []).append(caso)
        return agrupado

    def por_motivo(self) -> dict[Motivo, list[RevisionHumana]]:
        agrupado: dict[Motivo, list[RevisionHumana]] = {}
        for caso in self.casos:
            agrupado.setdefault(caso.motivo, []).append(caso)
        return agrupado

    def extender(self, otra: ColaDeRevision) -> None:
        self.agregar_varios(otra.casos)

    def __len__(self) -> int:
        return len(self.casos)
