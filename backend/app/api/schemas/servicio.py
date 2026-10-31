"""Contratos Pydantic para cotizar, crear y listar servicios."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.api.schemas.chofer import ChoferRead
from app.api.schemas.cliente import ClienteCreate
from app.api.schemas.comun import Pagina
from app.api.schemas.vehiculo import VehiculoListadoRead
from app.application.cotizacion.calculadora import Cotizacion
from app.application.servicios.puertos import ServicioListadoItem
from app.domain.servicio import (
    MOTIVO_CANCELACION_MAX,
    OBSERVACION_RENDICION_MAX,
    transiciones_validas_desde,
)


class CotizacionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_tipo_vehiculo: int = Field(gt=0, description="Tipo de vehículo cuya tarifa se utilizará.")
    horas_estimadas: Decimal = Field(
        ge=1,
        max_digits=10,
        decimal_places=2,
        allow_inf_nan=False,
        description="Duración estimada ingresada por el operador; mínimo 1 hora.",
    )
    distancia_ida_km: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
        allow_inf_nan=False,
        description="Kilómetros de ida. El backend los duplica para obtener el recorrido total.",
    )


class CotizacionRead(BaseModel):
    id_tipo_vehiculo: int
    descripcion_tipo_vehiculo: str
    horas_estimadas: Decimal
    distancia_ida_km: Decimal
    distancia_total_km: Decimal
    km_franquicia: Decimal
    km_excedente: Decimal
    tarifa_hora_base: Decimal
    tarifa_km_excedente: Decimal
    precio_final: Decimal
    moneda: Literal["ARS"] = "ARS"

    @classmethod
    def de_cotizacion(cls, cotizacion: Cotizacion) -> CotizacionRead:
        resultado = cotizacion.resultado
        return cls(
            id_tipo_vehiculo=cotizacion.id_tipo_vehiculo,
            descripcion_tipo_vehiculo=cotizacion.descripcion_tipo_vehiculo,
            horas_estimadas=resultado.horas_estimadas,
            distancia_ida_km=resultado.distancia_ida_km,
            distancia_total_km=resultado.distancia_total_km,
            km_franquicia=resultado.km_franquicia,
            km_excedente=resultado.km_excedente,
            tarifa_hora_base=resultado.tarifa_hora_base,
            tarifa_km_excedente=resultado.tarifa_km_excedente,
            precio_final=resultado.precio_final,
        )


class ServicioCreate(CotizacionRequest):
    model_config = ConfigDict(extra="forbid")

    id_cliente: int | None = Field(
        default=None,
        gt=0,
        description="Cliente existente que solicita el servicio. Excluyente con `nuevo_cliente`.",
    )
    nuevo_cliente: ClienteCreate | None = Field(
        default=None,
        description=(
            "Datos de un cliente nuevo. El backend lo crea y lo vincula al servicio; si ya "
            "existe uno activo con la misma razón social, reutiliza ese registro."
        ),
    )
    id_chofer: int | None = Field(default=None, gt=0, description="Chofer asignado, si se conoce.")
    id_vehiculo: int | None = Field(
        default=None, gt=0, description="Vehículo asignado; debe pertenecer al tipo seleccionado."
    )
    fecha: date
    hora_inicio: time | None = None

    @model_validator(mode="after")
    def _cliente_excluyente(self) -> ServicioCreate:
        if (self.id_cliente is None) == (self.nuevo_cliente is None):
            raise ValueError("Indicá `id_cliente` o `nuevo_cliente`, pero no ambos")
        return self


class DisponibilidadRead(BaseModel):
    """Disponibilidad calculada para una ventana de servicio."""

    id_tipo_vehiculo: int
    fecha: date
    hora_inicio: time | None
    hora_fin: time | None
    choferes: list[ChoferRead]
    vehiculos: list[VehiculoListadoRead]


class ServicioCancelar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    motivo: str = Field(
        min_length=1,
        max_length=MOTIVO_CANCELACION_MAX,
        description="Motivo de la cancelación; se recortan los espacios de los extremos.",
        examples=["El cliente reprogramó el viaje"],
    )

    @field_validator("motivo")
    @classmethod
    def _motivo_no_vacio(cls, valor: str) -> str:
        limpio = valor.strip()
        if not limpio:
            raise ValueError("El motivo de cancelación es obligatorio")
        return limpio


class ServicioRead(BaseModel):
    id_servicio: int
    id_cliente: int
    razon_social_cliente: str
    id_tipo_vehiculo: int
    descripcion_tipo_vehiculo: str
    id_chofer: int | None
    nombre_chofer: str | None
    id_vehiculo: int | None
    patente_vehiculo: str | None
    fecha: date
    hora_inicio: time | None
    hora_fin: time | None
    horas_estimadas: Decimal
    distancia_ida_km: Decimal
    distancia_total_km: Decimal
    km_franquicia: Decimal
    km_excedente: Decimal
    tarifa_hora_aplicada: Decimal
    tarifa_km_aplicada: Decimal
    precio_total: Decimal
    moneda: Literal["ARS"] = "ARS"
    estado: str
    transiciones_validas: list[str]
    motivo_cancelacion: str | None
    foto_remito_url: str | None = None
    monto_cobrado_real: Decimal | None = None
    estado_rendicion: str | None = None
    observacion_rendicion: str | None = None
    rendido_en: datetime | None = None
    rendido_por_id: int | None = None
    creado_por_id: int | None = None
    modificado_por_id: int | None = None
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def de_item(cls, item: ServicioListadoItem) -> ServicioRead:
        servicio = item.servicio
        if servicio.id is None or servicio.creado_en is None or servicio.actualizado_en is None:
            raise RuntimeError("El repositorio devolvió un servicio sin identidad o auditoría")

        return cls(
            id_servicio=servicio.id,
            id_cliente=servicio.id_cliente,
            razon_social_cliente=item.razon_social_cliente,
            id_tipo_vehiculo=servicio.id_tipo_vehiculo,
            descripcion_tipo_vehiculo=item.descripcion_tipo_vehiculo,
            id_chofer=servicio.id_chofer,
            nombre_chofer=item.nombre_chofer,
            id_vehiculo=servicio.id_vehiculo,
            patente_vehiculo=item.patente_vehiculo,
            fecha=servicio.fecha,
            hora_inicio=servicio.hora_inicio,
            hora_fin=servicio.hora_fin,
            horas_estimadas=servicio.horas_estimadas,
            distancia_ida_km=servicio.distancia_ida_km,
            distancia_total_km=servicio.distancia_total_km,
            km_franquicia=servicio.km_franquicia,
            km_excedente=servicio.km_excedente,
            tarifa_hora_aplicada=servicio.tarifa_hora_aplicada,
            tarifa_km_aplicada=servicio.tarifa_km_aplicada,
            precio_total=servicio.precio_total,
            estado=servicio.estado,
            transiciones_validas=transiciones_validas_desde(servicio.estado),
            motivo_cancelacion=servicio.motivo_cancelacion,
            foto_remito_url=servicio.foto_remito_url,
            monto_cobrado_real=servicio.monto_cobrado_real,
            estado_rendicion=servicio.estado_rendicion,
            observacion_rendicion=servicio.observacion_rendicion,
            rendido_en=servicio.rendido_en,
            rendido_por_id=servicio.rendido_por_id,
            creado_por_id=servicio.creado_por_id,
            modificado_por_id=servicio.modificado_por_id,
            creado_en=servicio.creado_en,
            actualizado_en=servicio.actualizado_en,
        )


class ServicioListado(Pagina[ServicioRead]):
    """Página de Servicios con relaciones legibles."""


class ServicioEstadoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: Literal[
        "pendiente",
        "confirmado",
        "en curso",
        "finalizado",
        "cobrado",
        "cancelado",
    ] = Field(description="Nuevo estado solicitado para el servicio.")


class ServicioFinalizarRequest(BaseModel):
    """Datos requeridos para el cierre operativo con Prueba de Entrega (POD) (H10)."""

    model_config = ConfigDict(extra="forbid")

    monto_cobrado_real: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
        allow_inf_nan=False,
        description="Monto real cobrado al finalizar el viaje.",
    )
    foto_remito_url: str | None = Field(
        default=None,
        description="Data URL Base64 o URL pública de la foto del remito firmado.",
    )


class RendicionObservarRequest(BaseModel):
    """Observación administrativa sobre la rendición de un viaje (H10)."""

    model_config = ConfigDict(extra="forbid")

    observacion: str = Field(
        min_length=1,
        max_length=OBSERVACION_RENDICION_MAX,
        description="Motivo o nota de observación sobre la diferencia o el comprobante.",
    )

    @field_validator("observacion")
    @classmethod
    def _observacion_no_vacia(cls, valor: str) -> str:
        limpio = valor.strip()
        if not limpio:
            raise ValueError("La observación de rendición es obligatoria")
        return limpio
