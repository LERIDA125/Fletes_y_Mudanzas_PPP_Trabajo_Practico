from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.errores import ReglaNegocioError
from app.domain.normalizacion import contar_digitos, normalizar_espacios

NOMBRE_MIN = 3
NOMBRE_MAX = 120
TELEFONO_DIGITOS_MIN = 7
TELEFONO_DIGITOS_MAX = 20
TELEFONO_MAX = 20  # longitud del texto que admite la columna, separadores incluidos


def normalizar_nombre(texto: str) -> str:
    """Colapsa espacios sobrantes y quita los de los extremos. Para mostrar y guardar."""
    return normalizar_espacios(texto)


@dataclass
class Chofer:
    id: int | None
    nombre_completo: str
    telefono: str
    activo: bool = True
    saldo_a_favor: float = 0.0
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None

    def __post_init__(self) -> None:
        self.nombre_completo = normalizar_nombre(self.nombre_completo)
        self.telefono = normalizar_nombre(self.telefono)
        self._validar()

    @classmethod
    def crear(cls, nombre_completo: str, telefono: str) -> Chofer:
        return cls(id=None, nombre_completo=nombre_completo, telefono=telefono)

    def actualizar(self, *, nombre_completo: str, telefono: str) -> Chofer:
        """Valida primero y recién después modifica, para no dejar el chofer a medias.

        No toca `activo` ni `saldo_a_favor`: el estado solo cambia por la baja lógica y el saldo
        se mueve por los flujos económicos (H10/H11), no por esta historia (FR-012).
        """
        candidatos = {
            "nombre_completo": normalizar_nombre(nombre_completo),
            "telefono": normalizar_nombre(telefono),
        }
        Chofer(
            id=self.id,
            activo=self.activo,
            saldo_a_favor=self.saldo_a_favor,
            creado_en=self.creado_en,
            actualizado_en=self.actualizado_en,
            **candidatos,
        )

        self.nombre_completo = candidatos["nombre_completo"]
        self.telefono = candidatos["telefono"]
        return self

    def desactivar(self) -> Chofer:
        self.activo = False
        return self

    def _validar(self) -> None:
        largo_nombre = len(self.nombre_completo)
        if not NOMBRE_MIN <= largo_nombre <= NOMBRE_MAX:
            raise ReglaNegocioError(
                f"El nombre completo debe tener entre {NOMBRE_MIN} y {NOMBRE_MAX} caracteres"
            )

        if len(self.telefono) > TELEFONO_MAX:
            raise ReglaNegocioError(f"El teléfono no puede superar los {TELEFONO_MAX} caracteres")

        digitos = contar_digitos(self.telefono)
        if not TELEFONO_DIGITOS_MIN <= digitos <= TELEFONO_DIGITOS_MAX:
            raise ReglaNegocioError(
                f"El teléfono debe tener entre {TELEFONO_DIGITOS_MIN} y "
                f"{TELEFONO_DIGITOS_MAX} dígitos"
            )
