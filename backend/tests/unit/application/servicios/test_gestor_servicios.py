from datetime import UTC, date, datetime, time
from decimal import Decimal

import pytest

from app.application.cotizacion.calculadora import CalculadoraCotizacion
from app.application.servicios.gestor_servicios import GestorServicios
from app.application.servicios.puertos import ServicioListadoItem
from app.domain.chofer import Chofer
from app.domain.cliente import Cliente
from app.domain.errores import (
    ClienteInvalido,
    MotivoCancelacionObligatorio,
    ServicioNoCancelable,
    ServicioNoEncontrado,
    TransicionEstadoServicioInvalida,
    VehiculoTipoIncompatible,
)
from app.domain.servicio import Servicio
from app.domain.tipo_vehiculo import TipoVehiculo
from app.domain.vehiculo import Vehiculo


class FakeTipoRepository:
    def __init__(self) -> None:
        self.tipo = TipoVehiculo(
            id=3,
            descripcion="Camioneta",
            capacidad_carga_kg=Decimal("1500"),
            tarifa_hora_base=Decimal("3000"),
            tarifa_km_excedente=Decimal("150"),
        )

    def obtener_por_id(self, tipo_id: int) -> TipoVehiculo | None:
        return self.tipo if self.tipo.id == tipo_id else None


class FakeClienteRepository:
    def __init__(self) -> None:
        self.cliente = Cliente(
            id=8,
            razon_social="Cliente de Prueba",
            telefono="3515550100",
            direccion_habitual="Av. Siempre Viva 123",
            tiene_cuenta_corriente=False,
        )

    def obtener_por_id(self, cliente_id: int) -> Cliente | None:
        return self.cliente if self.cliente.id == cliente_id else None


class FakeChoferRepository:
    def obtener_por_id(self, chofer_id: int) -> Chofer | None:
        return Chofer(id=chofer_id, nombre_completo="Chofer de Prueba", telefono="3515550101")


class FakeVehiculoRepository:
    def __init__(self, tipo_id: int = 3) -> None:
        self.tipo_id = tipo_id

    def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None:
        return Vehiculo(
            id=vehiculo_id,
            patente="AA 123 ABC",
            id_tipo_vehiculo=self.tipo_id,
            id_chofer_habitual=None,
        )


class FakeServicioRepository:
    def __init__(self) -> None:
        self.guardado: Servicio | None = None
        self.items: dict[int, Servicio] = {}

    @staticmethod
    def _item(servicio: Servicio) -> ServicioListadoItem:
        return ServicioListadoItem(
            servicio=servicio,
            razon_social_cliente="Cliente de Prueba",
            descripcion_tipo_vehiculo="Camioneta",
            nombre_chofer=None,
            patente_vehiculo=None,
        )

    def crear(self, servicio: Servicio) -> ServicioListadoItem:
        servicio.id = 1
        servicio.creado_en = datetime.now(UTC)
        servicio.actualizado_en = servicio.creado_en
        self.guardado = servicio
        self.items[servicio.id] = servicio
        return self._item(servicio)

    def obtener_por_id(self, servicio_id: int) -> ServicioListadoItem | None:
        servicio = self.items.get(servicio_id)
        return self._item(servicio) if servicio is not None else None

    def actualizar(self, servicio: Servicio) -> ServicioListadoItem:
        self.guardado = servicio
        if servicio.id is not None:
            self.items[servicio.id] = servicio
        return self._item(servicio)

    def listar(self, offset: int, limit: int) -> list[ServicioListadoItem]:
        return []

    def contar(self) -> int:
        return 0

    def tiene_historial(self, cliente_id: int) -> bool:
        return False

    def tiene_servicios(self, vehiculo_id: int) -> bool:
        return False


def _crear_gestor(
    *,
    vehiculo_tipo_id: int = 3,
) -> tuple[GestorServicios, FakeServicioRepository, FakeClienteRepository]:
    repo = FakeServicioRepository()
    clientes = FakeClienteRepository()
    tipos = FakeTipoRepository()
    gestor = GestorServicios(
        repositorio=repo,
        calculadora=CalculadoraCotizacion(tipos),
        consulta_clientes=clientes,
        consulta_choferes=FakeChoferRepository(),
        consulta_vehiculos=FakeVehiculoRepository(vehiculo_tipo_id),
    )
    return gestor, repo, clientes


def test_gestor_guarda_snapshot_calculado_por_la_estrategia() -> None:
    gestor, repo, _ = _crear_gestor()

    item = gestor.crear(
        id_cliente=8,
        id_tipo_vehiculo=3,
        id_chofer=None,
        id_vehiculo=None,
        fecha=date(2026, 10, 25),
        hora_inicio=time(9, 30),
        horas_estimadas=Decimal("2"),
        distancia_ida_km=Decimal("15"),
    )

    assert repo.guardado is item.servicio
    assert item.servicio.distancia_total_km == Decimal("30")
    assert item.servicio.km_franquicia == Decimal("10")
    assert item.servicio.km_excedente == Decimal("20")
    assert item.servicio.tarifa_hora_aplicada == Decimal("3000")
    assert item.servicio.tarifa_km_aplicada == Decimal("150")
    assert item.servicio.precio_total == Decimal("9000.00")
    assert item.servicio.estado == "pendiente"
    item.servicio.transicionar_a("confirmado")
    assert item.servicio.estado == "confirmado"
    with pytest.raises(TransicionEstadoServicioInvalida):
        item.servicio.transicionar_a("cobrado")


def test_gestor_rechaza_cliente_inactivo() -> None:
    gestor, repo, clientes = _crear_gestor()
    clientes.cliente.activo = False

    with pytest.raises(ClienteInvalido):
        gestor.crear(
            id_cliente=8,
            id_tipo_vehiculo=3,
            id_chofer=None,
            id_vehiculo=None,
            fecha=date(2026, 10, 25),
            hora_inicio=None,
            horas_estimadas=Decimal("1"),
            distancia_ida_km=Decimal("0"),
        )

    assert repo.guardado is None


def test_gestor_rechaza_vehiculo_de_otro_tipo() -> None:
    gestor, repo, _ = _crear_gestor(vehiculo_tipo_id=4)

    with pytest.raises(VehiculoTipoIncompatible):
        gestor.crear(
            id_cliente=8,
            id_tipo_vehiculo=3,
            id_chofer=None,
            id_vehiculo=22,
            fecha=date(2026, 10, 25),
            hora_inicio=None,
            horas_estimadas=Decimal("1"),
            distancia_ida_km=Decimal("0"),
        )

    assert repo.guardado is None


def _crear_servicio(gestor: GestorServicios) -> ServicioListadoItem:
    return gestor.crear(
        id_cliente=8,
        id_tipo_vehiculo=3,
        id_chofer=None,
        id_vehiculo=None,
        fecha=date(2026, 10, 25),
        hora_inicio=time(9, 30),
        horas_estimadas=Decimal("2"),
        distancia_ida_km=Decimal("15"),
    )


def test_gestor_cancela_con_motivo_recortado_y_hora_inyectada() -> None:
    gestor, repo, _ = _crear_gestor()
    item = _crear_servicio(gestor)

    cancelado = gestor.cancelar(
        id_servicio=item.servicio.id,
        motivo="  El cliente reprogramó el viaje  ",
        ahora=datetime(2026, 10, 22, 16, 45, 30, 123456),
    )

    assert cancelado.servicio.estado == "cancelado"
    assert cancelado.servicio.motivo_cancelacion == "El cliente reprogramó el viaje"
    assert cancelado.servicio.hora_fin == time(16, 45, 30)
    assert repo.guardado is cancelado.servicio
    assert repo.items[item.servicio.id].estado == "cancelado"


def test_gestor_rechaza_cancelacion_sin_motivo() -> None:
    gestor, repo, _ = _crear_gestor()
    item = _crear_servicio(gestor)

    with pytest.raises(MotivoCancelacionObligatorio):
        gestor.cancelar(id_servicio=item.servicio.id, motivo="   ")

    assert repo.guardado is not None
    assert repo.guardado.estado == "pendiente"
    assert repo.guardado.motivo_cancelacion is None
    assert repo.guardado.hora_fin is None


def test_gestor_rechaza_cancelacion_de_servicio_finalizado() -> None:
    gestor, repo, _ = _crear_gestor()
    item = _crear_servicio(gestor)
    item.servicio.estado = "finalizado"

    with pytest.raises(ServicioNoCancelable):
        gestor.cancelar(id_servicio=item.servicio.id, motivo="Cliente desiste")

    assert repo.guardado is not None
    assert repo.guardado.estado == "finalizado"
    assert repo.guardado.motivo_cancelacion is None


def test_gestor_rechaza_cancelacion_de_servicio_inexistente() -> None:
    gestor, _, _ = _crear_gestor()

    with pytest.raises(ServicioNoEncontrado):
        gestor.cancelar(id_servicio=999, motivo="Cliente desiste")
