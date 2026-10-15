from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.errores import ReglaNegocioError

DESCRIPCION_MIN = 3
DESCRIPCION_MAX = 80


def normalizar_descripcion(texto: str) -> str:
    """Colapsa espacios sobrantes y quita los de los extremos. Para mostrar y guardar."""
    return " ".join(texto.split())


def normalizar_descripcion_key(texto: str) -> str:
    """Clave de comparación: en minúsculas y sin espacios sobrantes."""
    return normalizar_descripcion(texto).lower()


@dataclass
class TipoVehiculo:
    id: int | None
    descripcion: str
    capacidad_carga_kg: Decimal
    tarifa_hora_base: Decimal
    tarifa_km_excedente: Decimal
    activo: bool = True
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None

    def __post_init__(self) -> None:
        self.descripcion = normalizar_descripcion(self.descripcion)
        self._validar()

    @classmethod
    def crear(
        cls,
        descripcion: str,
        capacidad_carga_kg: Decimal,
        tarifa_hora_base: Decimal,
        tarifa_km_excedente: Decimal,
    ) -> TipoVehiculo:
        return cls(
            id=None,
            descripcion=descripcion,
            capacidad_carga_kg=capacidad_carga_kg,
            tarifa_hora_base=tarifa_hora_base,
            tarifa_km_excedente=tarifa_km_excedente,
        )

    @property
    def descripcion_key(self) -> str:
        return normalizar_descripcion_key(self.descripcion)

    def actualizar(
        self,
        *,
        descripcion: str,
        capacidad_carga_kg: Decimal,
        tarifa_hora_base: Decimal,
        tarifa_km_excedente: Decimal,
    ) -> TipoVehiculo:
        """Valida primero y recién después modifica, para no dejar el tipo a medias."""
        candidatos = {
            "descripcion": normalizar_descripcion(descripcion),
            "capacidad_carga_kg": capacidad_carga_kg,
            "tarifa_hora_base": tarifa_hora_base,
            "tarifa_km_excedente": tarifa_km_excedente,
        }
        TipoVehiculo(
            id=self.id,
            activo=self.activo,
            creado_en=self.creado_en,
            actualizado_en=self.actualizado_en,
            **candidatos,
        )

        self.descripcion = candidatos["descripcion"]
        self.capacidad_carga_kg = candidatos["capacidad_carga_kg"]
        self.tarifa_hora_base = candidatos["tarifa_hora_base"]
        self.tarifa_km_excedente = candidatos["tarifa_km_excedente"]
        return self

    def desactivar(self) -> TipoVehiculo:
        self.activo = False
        return self

    def _validar(self) -> None:
        largo_descripcion = len(self.descripcion)
        if not DESCRIPCION_MIN <= largo_descripcion <= DESCRIPCION_MAX:
            raise ReglaNegocioError(
                f"La descripción debe tener entre {DESCRIPCION_MIN} "
                f"y {DESCRIPCION_MAX} caracteres"
            )

        if self.capacidad_carga_kg <= 0:
            raise ReglaNegocioError("La capacidad de carga debe ser positiva")

        if self.tarifa_hora_base < 0:
            raise ReglaNegocioError("La tarifa hora base no puede ser negativa")

        if self.tarifa_km_excedente < 0:
            raise ReglaNegocioError("La tarifa km excedente no puede ser negativa")
