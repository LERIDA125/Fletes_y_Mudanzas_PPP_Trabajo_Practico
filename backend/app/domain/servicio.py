"""Entidad de Servicio y máquina explícita de estados."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal

from app.domain.cotizacion import CERO, CotizacionCalculada
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


def transiciones_validas_desde(estado: str) -> list[str]:
    """Acciones de estado disponibles desde `estado` para el panel de administración.

    La cancelación no es una transición más: se ejecuta por su propio endpoint porque
    exige motivo. Se incluye en la lista para que la UI no tenga que duplicar la regla.
    """
    if estado not in ESTADOS_SERVICIO:
        return []

    disponibles: list[str] = []
    siguiente = TRANSICIONES_ESTADO_SERVICIO[estado]
    if siguiente is not None:
        disponibles.append(siguiente)
    if estado not in ESTADOS_NO_CANCELABLES:
        disponibles.append("cancelado")
    return disponibles


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
    km_estimados: Decimal
    distancia_total_km: Decimal
    km_franquicia: Decimal
    km_excedente: Decimal
    tarifa_hora_aplicada: Decimal
    tarifa_km_aplicada: Decimal
    requiere_ayudante: bool
    acceso_escalera: bool
    zona_concurrida: bool
    urgencia_mismo_dia: bool
    recargo_ayudante_aplicado: Decimal
    recargo_escalera_aplicado: Decimal
    importe_recargo_zona_aplicado: Decimal
    importe_recargo_urgencia_aplicado: Decimal
    porcentaje_zona_aplicado: Decimal
    porcentaje_urgencia_aplicado: Decimal
    precio_sugerido: Decimal
    precio_acordado: Decimal
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
        cotizacion: CotizacionCalculada,
        precio_acordado: Decimal,
    ) -> Servicio:
        return cls(
            id=None,
            id_cliente=id_cliente,
            id_tipo_vehiculo=id_tipo_vehiculo,
            id_chofer=id_chofer,
            id_vehiculo=id_vehiculo,
            fecha=fecha,
            hora_inicio=hora_inicio,
            horas_estimadas=cotizacion.horas_estimadas,
            km_estimados=cotizacion.km_estimados,
            distancia_total_km=cotizacion.km_estimados,
            km_franquicia=CERO,
            km_excedente=CERO,
            tarifa_hora_aplicada=cotizacion.tarifa_hora_base,
            tarifa_km_aplicada=cotizacion.tarifa_km_excedente,
            requiere_ayudante=cotizacion.requiere_ayudante,
            acceso_escalera=cotizacion.acceso_escalera,
            zona_concurrida=cotizacion.zona_concurrida,
            urgencia_mismo_dia=cotizacion.urgencia_mismo_dia,
            recargo_ayudante_aplicado=cotizacion.recargo_ayudante,
            recargo_escalera_aplicado=cotizacion.recargo_escalera,
            importe_recargo_zona_aplicado=cotizacion.importe_recargo_zona_concurrida,
            importe_recargo_urgencia_aplicado=(
                cotizacion.importe_recargo_urgencia_mismo_dia
            ),
            porcentaje_zona_aplicado=cotizacion.porcentaje_zona_concurrida,
            porcentaje_urgencia_aplicado=cotizacion.porcentaje_urgencia_mismo_dia,
            precio_sugerido=cotizacion.precio_sugerido,
            precio_acordado=precio_acordado,
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
            ("km_estimados", self.km_estimados),
            ("distancia_total_km", self.distancia_total_km),
            ("km_franquicia", self.km_franquicia),
            ("km_excedente", self.km_excedente),
            ("tarifa_hora_aplicada", self.tarifa_hora_aplicada),
            ("tarifa_km_aplicada", self.tarifa_km_aplicada),
            ("recargo_ayudante_aplicado", self.recargo_ayudante_aplicado),
            ("recargo_escalera_aplicado", self.recargo_escalera_aplicado),
            ("importe_recargo_zona_aplicado", self.importe_recargo_zona_aplicado),
            ("importe_recargo_urgencia_aplicado", self.importe_recargo_urgencia_aplicado),
            ("porcentaje_zona_aplicado", self.porcentaje_zona_aplicado),
            ("porcentaje_urgencia_aplicado", self.porcentaje_urgencia_aplicado),
            ("precio_sugerido", self.precio_sugerido),
            ("precio_acordado", self.precio_acordado),
        ):
            if not isinstance(valor, Decimal) or not valor.is_finite():
                raise DatoInvalido(f"{nombre} debe ser un valor numérico finito")
            if valor < 0:
                raise DatoInvalido(f"{nombre} no puede ser negativo")

        for nombre in (
            "requiere_ayudante",
            "acceso_escalera",
            "zona_concurrida",
            "urgencia_mismo_dia",
        ):
            if not isinstance(getattr(self, nombre), bool):
                raise DatoInvalido(f"{nombre} debe ser un valor booleano")

        if self.horas_estimadas < Decimal("1"):
            raise DatoInvalido("Las horas estimadas deben ser como mínimo 1")
        if not self.requiere_ayudante and self.recargo_ayudante_aplicado != CERO:
            raise DatoInvalido("El recargo por ayudante requiere el modificador activo")
        if not self.acceso_escalera and self.recargo_escalera_aplicado != CERO:
            raise DatoInvalido("El recargo por escalera requiere el modificador activo")
        if not self.zona_concurrida:
            if (
                self.porcentaje_zona_aplicado != CERO
                or self.importe_recargo_zona_aplicado != CERO
            ):
                raise DatoInvalido("El recargo por zona requiere el modificador activo")
        if not self.urgencia_mismo_dia:
            if (
                self.porcentaje_urgencia_aplicado != CERO
                or self.importe_recargo_urgencia_aplicado != CERO
            ):
                raise DatoInvalido("El recargo por urgencia requiere el modificador activo")
        if self.porcentaje_zona_aplicado > Decimal("100"):
            raise DatoInvalido("El porcentaje de zona no puede superar 100")
        if self.porcentaje_urgencia_aplicado > Decimal("100"):
            raise DatoInvalido("El porcentaje de urgencia no puede superar 100")

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
