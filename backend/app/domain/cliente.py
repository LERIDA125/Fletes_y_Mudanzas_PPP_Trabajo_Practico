from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from datetime import datetime

from app.domain.errores import ReglaNegocioError

RAZON_SOCIAL_MIN = 3
RAZON_SOCIAL_MAX = 120
DIRECCION_MIN = 5
DIRECCION_MAX = 250
TELEFONO_DIGITOS_MIN = 7
TELEFONO_DIGITOS_MAX = 20


def normalizar_razon_visual(texto: str) -> str:
    """Colapsa espacios sobrantes y quita los de los extremos. Para mostrar y guardar."""
    return " ".join(texto.split())


def normalizar_razon_social(texto: str) -> str:
    """Clave de comparación: sin acentos, en minúsculas y sin espacios sobrantes.

    Es la base de la búsqueda (FR-008) y de la unicidad de la razón social (FR-004).
    """
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if not unicodedata.combining(caracter)
    )
    return normalizar_razon_visual(sin_acentos).lower()


def contar_digitos(texto: str) -> int:
    return sum(caracter.isdigit() for caracter in texto)


@dataclass
class Cliente:
    id: int | None
    razon_social: str
    telefono: str
    direccion_habitual: str
    tiene_cuenta_corriente: bool
    activo: bool = True
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None

    def __post_init__(self) -> None:
        self.razon_social = normalizar_razon_visual(self.razon_social)
        self.telefono = normalizar_razon_visual(self.telefono)
        self.direccion_habitual = normalizar_razon_visual(self.direccion_habitual)
        self._validar()

    @classmethod
    def crear(
        cls,
        razon_social: str,
        telefono: str,
        direccion_habitual: str,
        tiene_cuenta_corriente: bool = False,
    ) -> Cliente:
        return cls(
            id=None,
            razon_social=razon_social,
            telefono=telefono,
            direccion_habitual=direccion_habitual,
            tiene_cuenta_corriente=tiene_cuenta_corriente,
        )

    @property
    def razon_social_key(self) -> str:
        return normalizar_razon_social(self.razon_social)

    def actualizar(
        self,
        *,
        razon_social: str,
        telefono: str,
        direccion_habitual: str,
        tiene_cuenta_corriente: bool,
    ) -> Cliente:
        """Valida primero y recién después modifica, para no dejar el cliente a medias."""
        candidatos = {
            "razon_social": normalizar_razon_visual(razon_social),
            "telefono": normalizar_razon_visual(telefono),
            "direccion_habitual": normalizar_razon_visual(direccion_habitual),
            "tiene_cuenta_corriente": tiene_cuenta_corriente,
        }
        Cliente(
            id=self.id,
            activo=self.activo,
            creado_en=self.creado_en,
            actualizado_en=self.actualizado_en,
            **candidatos,
        )

        self.razon_social = candidatos["razon_social"]
        self.telefono = candidatos["telefono"]
        self.direccion_habitual = candidatos["direccion_habitual"]
        self.tiene_cuenta_corriente = candidatos["tiene_cuenta_corriente"]
        return self

    def desactivar(self) -> Cliente:
        self.activo = False
        return self

    def _validar(self) -> None:
        largo_razon_social = len(self.razon_social)
        if not RAZON_SOCIAL_MIN <= largo_razon_social <= RAZON_SOCIAL_MAX:
            raise ReglaNegocioError(
                f"La razón social debe tener entre {RAZON_SOCIAL_MIN} "
                f"y {RAZON_SOCIAL_MAX} caracteres"
            )

        largo_direccion = len(self.direccion_habitual)
        if not DIRECCION_MIN <= largo_direccion <= DIRECCION_MAX:
            raise ReglaNegocioError(
                f"La dirección habitual debe tener entre {DIRECCION_MIN} "
                f"y {DIRECCION_MAX} caracteres"
            )

        digitos = contar_digitos(self.telefono)
        if not TELEFONO_DIGITOS_MIN <= digitos <= TELEFONO_DIGITOS_MAX:
            raise ReglaNegocioError(
                f"El teléfono debe tener entre {TELEFONO_DIGITOS_MIN} y "
                f"{TELEFONO_DIGITOS_MAX} dígitos"
            )

        if not isinstance(self.tiene_cuenta_corriente, bool):
            raise ReglaNegocioError("El indicador de cuenta corriente debe ser booleano")
