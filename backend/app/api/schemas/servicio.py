"""Contratos Pydantic para cotizar, crear y listar servicios."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.comun import Pagina
from app.application.cotizacion.calculadora import Cotizacion
from app.application.servicios.puertos import ServicioListadoItem


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

    id_cliente: int = Field(gt=0, description="Cliente que solicita el servicio.")
    id_chofer: int | None = Field(default=None, gt=0, description="Chofer asignado, si se conoce.")
    id_vehiculo: int | None = Field(
        default=None, gt=0, description="Vehículo asignado; debe pertenecer al tipo seleccionado."
    )
    fecha: date
    hora_inicio: time | None = None


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
            horas_estimadas=servicio.horas_estimadas,
            distancia_ida_km=servicio.distancia_ida_km,
            distancia_total_km=servicio.distancia_total_km,
            km_franquicia=servicio.km_franquicia,
            km_excedente=servicio.km_excedente,
            tarifa_hora_aplicada=servicio.tarifa_hora_aplicada,
            tarifa_km_aplicada=servicio.tarifa_km_aplicada,
            precio_total=servicio.precio_total,
            estado=servicio.estado,
            creado_en=servicio.creado_en,
            actualizado_en=servicio.actualizado_en,
        )


class ServicioListado(Pagina[ServicioRead]):
    """Página de Servicios con relaciones legibles."""
