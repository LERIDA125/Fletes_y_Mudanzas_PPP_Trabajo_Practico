from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from app.domain.errores import ReglaNegocioError

PATENTE_REGEX = re.compile(r"^[A-Z]{3}\s?\d{3}$|^[A-Z]{2}\s?\d{3}\s?[A-Z]{3}$")


def normalizar_patente(texto: str) -> str:
    """Colapsa espacios sobrantes, quita los de los extremos y pone en mayúsculas."""
    return " ".join(texto.split()).upper()


def es_patente_valida(texto: str) -> bool:
    """Verifica que la patente tenga formato de patente argentina."""
    return bool(PATENTE_REGEX.match(normalizar_patente(texto)))


@dataclass
class Vehiculo:
    id: int | None
    patente: str
    id_tipo_vehiculo: int
    id_chofer_habitual: int | None
    activo: bool = True
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None

    def __post_init__(self) -> None:
        self.patente = normalizar_patente(self.patente)
        self._validar()

    @classmethod
    def crear(
        cls,
        patente: str,
        id_tipo_vehiculo: int,
        id_chofer_habitual: int | None = None,
    ) -> Vehiculo:
        return cls(
            id=None,
            patente=patente,
            id_tipo_vehiculo=id_tipo_vehiculo,
            id_chofer_habitual=id_chofer_habitual,
        )

    def actualizar(
        self,
        *,
        patente: str,
        id_tipo_vehiculo: int,
        id_chofer_habitual: int | None,
    ) -> Vehiculo:
        """Valida primero y recién después modifica, para no dejar el vehículo a medias."""
        candidatos = {
            "patente": normalizar_patente(patente),
            "id_tipo_vehiculo": id_tipo_vehiculo,
            "id_chofer_habitual": id_chofer_habitual,
        }
        Vehiculo(
            id=self.id,
            activo=self.activo,
            creado_en=self.creado_en,
            actualizado_en=self.actualizado_en,
            **candidatos,
        )

        self.patente = candidatos["patente"]
        self.id_tipo_vehiculo = candidatos["id_tipo_vehiculo"]
        self.id_chofer_habitual = candidatos["id_chofer_habitual"]
        return self

    def desactivar(self) -> Vehiculo:
        self.activo = False
        return self

    def _validar(self) -> None:
        if not es_patente_valida(self.patente):
            raise ReglaNegocioError(
                "La patente debe tener formato de patente argentina (AAA 123 o AA 123 ABC)"
            )

        if self.id_tipo_vehiculo is None or self.id_tipo_vehiculo <= 0:
            raise ReglaNegocioError("El tipo de vehículo es obligatorio")
