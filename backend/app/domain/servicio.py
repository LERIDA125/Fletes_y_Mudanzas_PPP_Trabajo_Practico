"""Entidad de Servicio y máquina explícita de estados."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal

from app.domain.errores import (
    DatoInvalido,
    MotivoCancelacionObligatorio,
    ServicioNoCancelable,
    TransicionEstadoServicioInvalida,
)

ESTADOS_SERVICIO = ("pendiente", "confirmado", "en curso", "finalizado", "cobrado", "cancelado")
ESTADOS_NO_CANCELABLES = ("finalizado", "cobrado", "cancelado")
MOTIVO_CANCELACION_MAX = 255
TRANSICIONES_ESTADO_SERVICIO = {
    "pendiente": "confirmado",
    "confirmado": "en curso",
    "en curso": "finalizado",
    "finalizado": "cobrado",
    "cobrado": None,
    "cancelado": None,
}


@dataclass
class Servicio:
    id: int | None
    id_cliente: int
    id_tipo_vehiculo: int
    id_chofer: int | None
    id_vehiculo: int | None
    fecha: date
    hora_inicio: time | None
    horas_estimadas: Decimal
    distancia_ida_km: Decimal
    distancia_total_km: Decimal
    km_franquicia: Decimal
    km_excedente: Decimal
    tarifa_hora_aplicada: Decimal
    tarifa_km_aplicada: Decimal
    precio_total: Decimal
    estado: str = "pendiente"
    hora_fin: time | None = None
    motivo_cancelacion: str | None = None
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None

    def __post_init__(self) -> None:
        self._validar()

    @classmethod
    def crear(
        cls,
        *,
        id_cliente: int,
        id_tipo_vehiculo: int,
        id_chofer: int | None,
        id_vehiculo: int | None,
        fecha: date,
        hora_inicio: time | None,
        horas_estimadas: Decimal,
        distancia_ida_km: Decimal,
        distancia_total_km: Decimal,
        km_franquicia: Decimal,
        km_excedente: Decimal,
        tarifa_hora_aplicada: Decimal,
        tarifa_km_aplicada: Decimal,
        precio_total: Decimal,
    ) -> Servicio:
        return cls(
            id=None,
            id_cliente=id_cliente,
            id_tipo_vehiculo=id_tipo_vehiculo,
            id_chofer=id_chofer,
            id_vehiculo=id_vehiculo,
            fecha=fecha,
            hora_inicio=hora_inicio,
            horas_estimadas=horas_estimadas,
            distancia_ida_km=distancia_ida_km,
            distancia_total_km=distancia_total_km,
            km_franquicia=km_franquicia,
            km_excedente=km_excedente,
            tarifa_hora_aplicada=tarifa_hora_aplicada,
            tarifa_km_aplicada=tarifa_km_aplicada,
            precio_total=precio_total,
        )

    def transicionar_a(self, estado_nuevo: str) -> Servicio:
        if TRANSICIONES_ESTADO_SERVICIO.get(self.estado) != estado_nuevo:
            raise TransicionEstadoServicioInvalida(self.estado, estado_nuevo)
        self.estado = estado_nuevo
        return self

    def cancelar(self, *, motivo: str, hora_fin: time) -> Servicio:
        if self.estado in ESTADOS_NO_CANCELABLES:
            raise ServicioNoCancelable(self.estado)

        motivo_limpio = (motivo or "").strip()
        if not motivo_limpio:
            raise MotivoCancelacionObligatorio()
        if len(motivo_limpio) > MOTIVO_CANCELACION_MAX:
            raise DatoInvalido(
                f"El motivo de cancelación no puede superar los {MOTIVO_CANCELACION_MAX} caracteres"
            )
        if not isinstance(hora_fin, time):
            raise DatoInvalido("La hora de finalización debe ser una hora válida")

        self.motivo_cancelacion = motivo_limpio
        self.hora_fin = hora_fin
        self.estado = "cancelado"
        self._validar()
        return self

    def _validar(self) -> None:
        for nombre, valor in (
            ("horas_estimadas", self.horas_estimadas),
            ("distancia_ida_km", self.distancia_ida_km),
            ("distancia_total_km", self.distancia_total_km),
            ("km_franquicia", self.km_franquicia),
            ("km_excedente", self.km_excedente),
            ("tarifa_hora_aplicada", self.tarifa_hora_aplicada),
            ("tarifa_km_aplicada", self.tarifa_km_aplicada),
            ("precio_total", self.precio_total),
        ):
            if not isinstance(valor, Decimal) or not valor.is_finite():
                raise DatoInvalido(f"{nombre} debe ser un valor numérico finito")
            if valor < 0:
                raise DatoInvalido(f"{nombre} no puede ser negativo")

        if self.horas_estimadas < Decimal("1"):
            raise DatoInvalido("Las horas estimadas deben ser como mínimo 1")
        if min(self.id_cliente, self.id_tipo_vehiculo) < 1:
            raise DatoInvalido("Cliente y tipo de vehículo son obligatorios")
        if self.id_chofer is not None and self.id_chofer < 1:
            raise DatoInvalido("El identificador del chofer debe ser positivo")
        if self.id_vehiculo is not None and self.id_vehiculo < 1:
            raise DatoInvalido("El identificador del vehículo debe ser positivo")
        if self.estado not in ESTADOS_SERVICIO:
            raise DatoInvalido(f"Estado de servicio inválido: {self.estado}")
        if self.estado != "pendiente" and self.id is None:
            raise DatoInvalido("Un servicio nuevo debe iniciar en estado pendiente")
        if self.hora_fin is not None and not isinstance(self.hora_fin, time):
            raise DatoInvalido("La hora de finalización debe ser una hora válida")
        if (
            self.motivo_cancelacion is not None
            and len(self.motivo_cancelacion) > MOTIVO_CANCELACION_MAX
        ):
            raise DatoInvalido(
                f"El motivo de cancelación no puede superar los {MOTIVO_CANCELACION_MAX} caracteres"
            )
        if self.estado == "cancelado":
            if not (self.motivo_cancelacion or "").strip():
                raise MotivoCancelacionObligatorio()
            if self.hora_fin is None:
                raise DatoInvalido("Un servicio cancelado debe registrar la hora de finalización")
        elif self.motivo_cancelacion is not None or self.hora_fin is not None:
            raise DatoInvalido(
                "Solo un servicio cancelado puede tener motivo y hora de finalización"
            )
