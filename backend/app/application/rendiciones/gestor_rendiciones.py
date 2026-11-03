"""Reglas de negocio de Rendiciones (capa de Aplicación)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.application.rendiciones.puertos import (
    ConsultaServiciosRendibles,
    RendicionListadoItem,
    RendicionRepository,
    ResumenRendiciones,
    ServicioElegible,
)
from app.domain.errores import (
    RendicionNoEncontrada,
    ServicioNoEncontrado,
    ServicioNoRendible,
    ServicioSinChoferParaRendir,
    ServicioYaRendido,
)
from app.domain.rendicion import ESTADOS_SERVICIO_RENDIBLES, Rendicion


class GestorRendiciones:
    def __init__(
        self,
        repositorio: RendicionRepository,
        consulta_servicios: ConsultaServiciosRendibles,
    ) -> None:
        self._repo = repositorio
        self._servicios = consulta_servicios

    def registrar(
        self,
        *,
        id_servicio: int,
        tarifa: Decimal,
        adelanto: Decimal,
        gasto_combustible: Decimal,
        gasto_peajes: Decimal,
        gasto_otros: Decimal,
        observaciones: str | None = None,
        usuario_id: int | None = None,
    ) -> RendicionListadoItem:
        servicio = self._servicios.obtener_para_rendir(id_servicio)
        if servicio is None:
            raise ServicioNoEncontrado(id_servicio)
        if servicio.estado not in ESTADOS_SERVICIO_RENDIBLES:
            raise ServicioNoRendible(servicio.estado)
        if servicio.id_chofer is None:
            raise ServicioSinChoferParaRendir(id_servicio)
        if self._repo.existe_para_servicio(id_servicio):
            raise ServicioYaRendido(id_servicio)

        rendicion = Rendicion.crear(
            id_servicio=id_servicio,
            id_chofer=servicio.id_chofer,
            fecha=servicio.fecha,
            tarifa=tarifa,
            adelanto=adelanto,
            gasto_combustible=gasto_combustible,
            gasto_peajes=gasto_peajes,
            gasto_otros=gasto_otros,
            observaciones=observaciones,
            creado_por_id=usuario_id,
        )
        return self._repo.crear(rendicion)

    def obtener(self, rendicion_id: int) -> RendicionListadoItem:
        rendicion = self._repo.obtener_por_id(rendicion_id)
        if rendicion is None:
            raise RendicionNoEncontrada(rendicion_id)
        return rendicion

    def listar(
        self,
        *,
        busqueda: str | None,
        offset: int,
        limit: int,
        hoy: date | None = None,
    ) -> tuple[list[RendicionListadoItem], int, ResumenRendiciones]:
        fecha = hoy or date.today()
        return (
            self._repo.listar(busqueda, offset, limit),
            self._repo.contar(busqueda),
            self._repo.resumen(anio=fecha.year, mes=fecha.month),
        )

    def cambiar_estado(
        self,
        rendicion_id: int,
        *,
        estado: str,
        usuario_id: int | None = None,
    ) -> RendicionListadoItem:
        item = self._repo.obtener_por_id(rendicion_id)
        if item is None:
            raise RendicionNoEncontrada(rendicion_id)
        item.rendicion.cambiar_estado(estado, modificado_por_id=usuario_id)
        return self._repo.actualizar(item.rendicion)

    def listar_servicios_elegibles(self) -> list[ServicioElegible]:
        return self._servicios.listar_elegibles()
