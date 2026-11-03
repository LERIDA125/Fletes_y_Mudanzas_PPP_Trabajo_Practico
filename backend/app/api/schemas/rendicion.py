"""Schemas de entrada y salida de rendiciones."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.schemas.comun import Pagina
from app.application.rendiciones.puertos import (
    RendicionListadoItem,
    ResumenRendiciones,
    ServicioElegible,
)
from app.domain.rendicion import OBSERVACIONES_MAX


class GastosInformados(BaseModel):
    model_config = ConfigDict(extra="forbid")

    combustible: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
        allow_inf_nan=False,
    )
    peajes: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
        allow_inf_nan=False,
    )
    otros: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
        allow_inf_nan=False,
    )


class RendicionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_servicio: int = Field(gt=0, description="Servicio finalizado o cobrado sin rendición.")
    tarifa: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
        allow_inf_nan=False,
        description="Importe acordado con el chofer.",
    )
    adelanto: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
        allow_inf_nan=False,
        description="Adelanto ya entregado.",
    )
    gastos_informados: GastosInformados = Field(default_factory=GastosInformados)
    observaciones: str | None = Field(default=None, max_length=OBSERVACIONES_MAX)

    @field_validator("tarifa", "adelanto")
    @classmethod
    def _importe_no_negativo(cls, valor: Decimal) -> Decimal:
        if valor < 0:
            raise ValueError("El importe no puede ser negativo")
        return valor

    @field_validator("observaciones")
    @classmethod
    def _observaciones_limpias(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        limpio = valor.strip()
        return limpio or None


class RendicionEstadoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: Literal["pendiente", "en revision", "aprobada"] = Field(
        description="Nuevo estado de la rendición."
    )


class RendicionRead(BaseModel):
    id: int
    codigo: str
    id_servicio: int
    id_chofer: int
    nombre_chofer: str
    razon_social_cliente: str
    fecha: date
    tarifa: Decimal
    adelanto: Decimal
    gastos_informados: GastosInformados
    gastos_total: Decimal
    saldo: Decimal
    moneda: Literal["ARS"] = "ARS"
    estado: str
    observaciones: str | None
    creado_por_id: int | None = None
    modificado_por_id: int | None = None
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def de_item(cls, item: RendicionListadoItem) -> RendicionRead:
        rendicion = item.rendicion
        if rendicion.id is None or rendicion.codigo is None:
            raise RuntimeError("El repositorio devolvió una rendición sin identidad o código")
        if rendicion.creado_en is None or rendicion.actualizado_en is None:
            raise RuntimeError("El repositorio devolvió una rendición sin auditoría")

        return cls(
            id=rendicion.id,
            codigo=rendicion.codigo,
            id_servicio=rendicion.id_servicio,
            id_chofer=rendicion.id_chofer,
            nombre_chofer=item.nombre_chofer,
            razon_social_cliente=item.razon_social_cliente,
            fecha=rendicion.fecha,
            tarifa=rendicion.tarifa,
            adelanto=rendicion.adelanto,
            gastos_informados=GastosInformados(
                combustible=rendicion.gasto_combustible,
                peajes=rendicion.gasto_peajes,
                otros=rendicion.gasto_otros,
            ),
            gastos_total=rendicion.gastos_total,
            saldo=rendicion.saldo,
            estado=rendicion.estado,
            observaciones=rendicion.observaciones,
            creado_por_id=rendicion.creado_por_id,
            modificado_por_id=rendicion.modificado_por_id,
            creado_en=rendicion.creado_en,
            actualizado_en=rendicion.actualizado_en,
        )


class ResumenRendicionesRead(BaseModel):
    pendiente_total: Decimal
    pendiente_cantidad: int
    aprobado_mes_total: Decimal
    gastos_total: Decimal

    @classmethod
    def de_resumen(cls, resumen: ResumenRendiciones) -> ResumenRendicionesRead:
        return cls(
            pendiente_total=resumen.pendiente_total,
            pendiente_cantidad=resumen.pendiente_cantidad,
            aprobado_mes_total=resumen.aprobado_mes_total,
            gastos_total=resumen.gastos_total,
        )


class RendicionListado(Pagina[RendicionRead]):
    resumen: ResumenRendicionesRead


class ServicioElegibleRead(BaseModel):
    id_servicio: int
    razon_social_cliente: str
    nombre_chofer: str
    fecha: date
    hora_inicio: time | None
    precio_total: Decimal

    @classmethod
    def de_item(cls, item: ServicioElegible) -> ServicioElegibleRead:
        return cls(
            id_servicio=item.id_servicio,
            razon_social_cliente=item.razon_social_cliente,
            nombre_chofer=item.nombre_chofer,
            fecha=item.fecha,
            hora_inicio=item.hora_inicio,
            precio_total=item.precio_total,
        )
