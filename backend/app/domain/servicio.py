"""Entidad de Servicio, máquina explícita de estados y cierre con remito / rendición (H10)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import ROUND_HALF_UP, Decimal

from app.domain.errores import (
    DatoInvalido,
    MontoCobradoInvalido,
    MotivoCancelacionObligatorio,
    RemitoObligatorio,
    RendicionNoDisponible,
    ServicioNoCancelable,
    ServicioNoFinalizable,
    TransicionEstadoServicioInvalida,
)

ESTADOS_SERVICIO = ("pendiente", "confirmado", "en curso", "finalizado", "cobrado", "cancelado")
ESTADOS_NO_CANCELABLES = ("finalizado", "cobrado", "cancelado")
ESTADOS_RENDICION = ("PENDIENTE", "RENDIDO", "OBSERVADO")
MOTIVO_CANCELACION_MAX = 255
OBSERVACION_RENDICION_MAX = 255
CENTAVO = Decimal("0.01")

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
    foto_remito_url: str | None = None
    monto_cobrado_real: Decimal | None = None
    estado_rendicion: str | None = None
    observacion_rendicion: str | None = None
    rendido_en: datetime | None = None
    rendido_por_id: int | None = None
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
        creado_por_id: int | None = None,
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
            creado_por_id=creado_por_id,
            modificado_por_id=creado_por_id,
        )

    def transicionar_a(
        self,
        estado_nuevo: str,
        *,
        modificado_por_id: int | None = None,
    ) -> Servicio:
        if TRANSICIONES_ESTADO_SERVICIO.get(self.estado) != estado_nuevo:
            raise TransicionEstadoServicioInvalida(self.estado, estado_nuevo)
        self.estado = estado_nuevo
        if modificado_por_id is not None:
            self.modificado_por_id = modificado_por_id
        return self

    def finalizar_con_remito(
        self,
        *,
        foto_remito_url: str | None,
        monto_cobrado_real: Decimal,
        hora_fin: time,
        modificado_por_id: int | None = None,
        exigir_foto: bool = True,
    ) -> Servicio:
        if self.estado not in ("confirmado", "en curso"):
            raise ServicioNoFinalizable(self.estado)

        url_limpia = (foto_remito_url or "").strip()
        if exigir_foto and not url_limpia:
            raise RemitoObligatorio()

        if not isinstance(monto_cobrado_real, Decimal) or not monto_cobrado_real.is_finite():
            raise MontoCobradoInvalido()
        if monto_cobrado_real < Decimal("0"):
            raise MontoCobradoInvalido("El monto real cobrado no puede ser negativo")

        if not isinstance(hora_fin, time):
            raise DatoInvalido("La hora de finalización debe ser una hora válida")

        self.foto_remito_url = url_limpia or None
        self.monto_cobrado_real = monto_cobrado_real.quantize(CENTAVO, rounding=ROUND_HALF_UP)
        self.estado = "finalizado"
        self.estado_rendicion = "PENDIENTE"
        self.hora_fin = hora_fin
        if modificado_por_id is not None:
            self.modificado_por_id = modificado_por_id
        self._validar()
        return self

    def aprobar_rendicion(
        self,
        *,
        usuario_id: int | None = None,
        ahora: datetime | None = None,
    ) -> Servicio:
        if self.estado not in ("finalizado", "cobrado") or self.estado_rendicion not in (
            "PENDIENTE",
            "OBSERVADO",
        ):
            raise RendicionNoDisponible(
                "Solo se puede aprobar la rendición de un viaje finalizado con rendición "
                "PENDIENTE u OBSERVADA"
            )
        self.estado_rendicion = "RENDIDO"
        if self.estado == "finalizado":
            self.estado = "cobrado"
        self.rendido_en = ahora or datetime.now()
        self.rendido_por_id = usuario_id
        if usuario_id is not None:
            self.modificado_por_id = usuario_id
        self._validar()
        return self

    def observar_rendicion(
        self,
        *,
        observacion: str,
        usuario_id: int | None = None,
    ) -> Servicio:
        if self.estado not in ("finalizado", "cobrado") or self.estado_rendicion not in (
            "PENDIENTE",
            "OBSERVADO",
        ):
            raise RendicionNoDisponible(
                "Solo se puede observar la rendición de un viaje con rendición PENDIENTE"
            )
        obs_limpia = (observacion or "").strip()
        if not obs_limpia:
            raise DatoInvalido("La observación de la rendición es obligatoria")
        if len(obs_limpia) > OBSERVACION_RENDICION_MAX:
            raise DatoInvalido(
                f"La observación no puede superar los {OBSERVACION_RENDICION_MAX} caracteres"
            )
        self.estado_rendicion = "OBSERVADO"
        self.observacion_rendicion = obs_limpia
        if usuario_id is not None:
            self.modificado_por_id = usuario_id
        self._validar()
        return self

    def cancelar(
        self,
        *,
        motivo: str,
        hora_fin: time,
        modificado_por_id: int | None = None,
    ) -> Servicio:
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
        if modificado_por_id is not None:
            self.modificado_por_id = modificado_por_id
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

        if self.monto_cobrado_real is not None:
            es_decimal_finito = (
                isinstance(self.monto_cobrado_real, Decimal)
                and self.monto_cobrado_real.is_finite()
            )
            if not es_decimal_finito:
                raise MontoCobradoInvalido()
            if self.monto_cobrado_real < 0:
                raise MontoCobradoInvalido("El monto real cobrado no puede ser negativo")

        if self.estado_rendicion is not None and self.estado_rendicion not in ESTADOS_RENDICION:
            raise DatoInvalido(f"Estado de rendición inválido: {self.estado_rendicion}")

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
        elif self.motivo_cancelacion is not None or (
            self.hora_fin is not None and self.estado not in ("finalizado", "cobrado")
        ):
            raise DatoInvalido(
                "Solo un servicio cancelado puede tener motivo y hora de finalización"
            )
