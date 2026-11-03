"""Entidad de Rendición y cálculo del saldo a liquidar."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from app.domain.errores import DatoInvalido, EstadoRendicionInvalido

ESTADOS_RENDICION = ("pendiente", "en revision", "aprobada")
ESTADOS_SERVICIO_RENDIBLES = ("finalizado", "cobrado")
OBSERVACIONES_MAX = 500
CENTAVO = Decimal("0.01")


@dataclass
class Rendicion:
    id: int | None
    id_servicio: int
    id_chofer: int
    fecha: date
    tarifa: Decimal
    adelanto: Decimal
    gasto_combustible: Decimal
    gasto_peajes: Decimal
    gasto_otros: Decimal
    codigo: str | None = None
    estado: str = "pendiente"
    observaciones: str | None = None
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None
    creado_por_id: int | None = None
    modificado_por_id: int | None = None

    def __post_init__(self) -> None:
        self._validar()

    @classmethod
    def crear(
        cls,
        *,
        id_servicio: int,
        id_chofer: int,
        fecha: date,
        tarifa: Decimal,
        adelanto: Decimal,
        gasto_combustible: Decimal,
        gasto_peajes: Decimal,
        gasto_otros: Decimal,
        observaciones: str | None = None,
        creado_por_id: int | None = None,
    ) -> Rendicion:
        return cls(
            id=None,
            id_servicio=id_servicio,
            id_chofer=id_chofer,
            fecha=fecha,
            tarifa=tarifa,
            adelanto=adelanto,
            gasto_combustible=gasto_combustible,
            gasto_peajes=gasto_peajes,
            gasto_otros=gasto_otros,
            observaciones=observaciones,
            creado_por_id=creado_por_id,
            modificado_por_id=creado_por_id,
        )

    @property
    def gastos_total(self) -> Decimal:
        return (self.gasto_combustible + self.gasto_peajes + self.gasto_otros).quantize(
            CENTAVO, rounding=ROUND_HALF_UP
        )

    @property
    def saldo(self) -> Decimal:
        return (self.tarifa - self.adelanto - self.gastos_total).quantize(
            CENTAVO, rounding=ROUND_HALF_UP
        )

    def asignar_codigo(self, codigo: str) -> Rendicion:
        limpio = (codigo or "").strip()
        if not limpio:
            raise DatoInvalido("El código de rendición es obligatorio")
        self.codigo = limpio
        return self

    def cambiar_estado(
        self,
        estado: str,
        *,
        modificado_por_id: int | None = None,
    ) -> Rendicion:
        if estado not in ESTADOS_RENDICION:
            raise EstadoRendicionInvalido(estado)
        self.estado = estado
        if modificado_por_id is not None:
            self.modificado_por_id = modificado_por_id
        return self

    def _validar(self) -> None:
        if self.id_servicio < 1:
            raise DatoInvalido("El servicio de la rendición es obligatorio")
        if self.id_chofer < 1:
            raise DatoInvalido("El chofer de la rendición es obligatorio")

        for nombre, valor in (
            ("tarifa", self.tarifa),
            ("adelanto", self.adelanto),
            ("gasto_combustible", self.gasto_combustible),
            ("gasto_peajes", self.gasto_peajes),
            ("gasto_otros", self.gasto_otros),
        ):
            if not isinstance(valor, Decimal) or not valor.is_finite():
                raise DatoInvalido(f"{nombre} debe ser un valor numérico finito")
            if valor < 0:
                raise DatoInvalido(f"{nombre} no puede ser negativo")

        if self.estado not in ESTADOS_RENDICION:
            raise EstadoRendicionInvalido(self.estado)

        if self.observaciones is not None:
            limpio = self.observaciones.strip()
            if not limpio:
                self.observaciones = None
            elif len(limpio) > OBSERVACIONES_MAX:
                raise DatoInvalido(
                    f"Las observaciones no pueden superar los {OBSERVACIONES_MAX} caracteres"
                )
            else:
                self.observaciones = limpio
