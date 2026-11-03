"""Fakes de los puertos de Rendiciones para pruebas de Aplicación."""

from __future__ import annotations

from decimal import Decimal

from app.application.rendiciones.puertos import (
    RendicionListadoItem,
    ResumenRendiciones,
    ServicioElegible,
    ServicioParaRendir,
)
from app.domain.rendicion import Rendicion


class FakeRendicionRepo:
    def __init__(self) -> None:
        self.items: dict[int, RendicionListadoItem] = {}
        self.servicios_rendidos: set[int] = set()
        self._siguiente_id = 1

    def crear(self, rendicion: Rendicion) -> RendicionListadoItem:
        if rendicion.id is None:
            rendicion.id = self._siguiente_id
            self._siguiente_id += 1
        if rendicion.codigo is None:
            rendicion.asignar_codigo(f"REN-{rendicion.id:03d}")
        item = RendicionListadoItem(
            rendicion=rendicion,
            nombre_chofer="Chofer Demo",
            razon_social_cliente="Cliente Demo",
        )
        self.items[rendicion.id] = item
        self.servicios_rendidos.add(rendicion.id_servicio)
        return item

    def obtener_por_id(self, rendicion_id: int) -> RendicionListadoItem | None:
        return self.items.get(rendicion_id)

    def listar(
        self, busqueda: str | None, offset: int, limit: int
    ) -> list[RendicionListadoItem]:
        return list(self.items.values())[offset : offset + limit]

    def contar(self, busqueda: str | None) -> int:
        return len(self.items)

    def resumen(self, *, anio: int, mes: int) -> ResumenRendiciones:
        return ResumenRendiciones(
            pendiente_total=Decimal("1000.00"),
            pendiente_cantidad=2,
            aprobado_mes_total=Decimal("5000.00"),
            gastos_total=Decimal("600.00"),
        )

    def actualizar(self, rendicion: Rendicion) -> RendicionListadoItem:
        item = RendicionListadoItem(
            rendicion=rendicion,
            nombre_chofer="Chofer Demo",
            razon_social_cliente="Cliente Demo",
        )
        self.items[rendicion.id] = item
        return item

    def existe_para_servicio(self, servicio_id: int) -> bool:
        return servicio_id in self.servicios_rendidos


class FakeConsultaServicios:
    def __init__(self) -> None:
        self.servicios: dict[int, ServicioParaRendir] = {}
        self.elegibles: list[ServicioElegible] = []

    def listar_elegibles(self) -> list[ServicioElegible]:
        return self.elegibles

    def obtener_para_rendir(self, servicio_id: int) -> ServicioParaRendir | None:
        return self.servicios.get(servicio_id)
