from datetime import UTC, date, datetime, time
from decimal import Decimal

import pytest

from app.application.cotizacion.calculadora import CalculadoraCotizacion
from app.application.servicios.gestor_servicios import GestorServicios
from app.application.servicios.puertos import AsignacionDia, ServicioListadoItem
from app.application.vehiculos.puertos import VehiculoListadoItem
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
        self.creados: list[Cliente] = []
        self._siguiente_id = 20

    def obtener_por_id(self, cliente_id: int) -> Cliente | None:
        if self.cliente.id == cliente_id:
            return self.cliente
        return next((cliente for cliente in self.creados if cliente.id == cliente_id), None)

    def obtener_por_razon_social(self, razon_social_key: str) -> Cliente | None:
        candidatos = [self.cliente, *self.creados]
        return next(
            (cliente for cliente in candidatos if cliente.razon_social_key == razon_social_key),
            None,
        )

    def crear(self, cliente: Cliente) -> Cliente:
        cliente.id = self._siguiente_id
        self._siguiente_id += 1
        self.creados.append(cliente)
        return cliente


class FakeChoferRepository:
    def __init__(self) -> None:
        self.choferes = [
            Chofer(id=1, nombre_completo="Chofer Uno", telefono="3515550101"),
            Chofer(id=2, nombre_completo="Chofer Dos", telefono="3515550102"),
        ]

    def obtener_por_id(self, chofer_id: int) -> Chofer | None:
        return next((chofer for chofer in self.choferes if chofer.id == chofer_id), None)

    def listar_activos(self) -> list[Chofer]:
        return list(self.choferes)


class FakeVehiculoRepository:
    def __init__(self, tipo_id: int = 3) -> None:
        self.tipo_id = tipo_id
        self.vehiculos = [
            Vehiculo(
                id=21,
                patente="AA 123 ABC",
                id_tipo_vehiculo=tipo_id,
                id_chofer_habitual=None,
            ),
            Vehiculo(
                id=22,
                patente="BB 456 DEF",
                id_tipo_vehiculo=tipo_id,
                id_chofer_habitual=None,
            ),
        ]

    def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None:
        return next(
            (vehiculo for vehiculo in self.vehiculos if vehiculo.id == vehiculo_id),
            Vehiculo(
                id=vehiculo_id,
                patente="AA 123 ABC",
                id_tipo_vehiculo=self.tipo_id,
                id_chofer_habitual=None,
            ),
        )

    def listar_activos_por_tipo(self, tipo_vehiculo_id: int) -> list[VehiculoListadoItem]:
        return [
            VehiculoListadoItem(
                vehiculo=vehiculo,
                descripcion_tipo_vehiculo="Camioneta",
                capacidad_carga_kg=Decimal("1500"),
                nombre_chofer_habitual=None,
            )
            for vehiculo in self.vehiculos
            if vehiculo.id_tipo_vehiculo == tipo_vehiculo_id
        ]


class FakeServicioRepository:
    def __init__(self) -> None:
        self.guardado: Servicio | None = None
        self.items: dict[int, Servicio] = {}
        self.asignaciones: list[AsignacionDia] = []

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

    def eliminar(self, servicio_id: int) -> None:
        if servicio_id not in self.items:
            raise ServicioNoEncontrado(servicio_id)
        del self.items[servicio_id]
        if self.guardado is not None and self.guardado.id == servicio_id:
            self.guardado = None

    def listar(self, offset: int, limit: int) -> list[ServicioListadoItem]:
        return []

    def contar(self) -> int:
        return 0

    def tiene_historial(self, cliente_id: int) -> bool:
        return False

    def tiene_servicios(self, vehiculo_id: int) -> bool:
        return False

    def listar_asignaciones_del_dia(self, fecha: date) -> list[AsignacionDia]:
        return list(self.asignaciones)


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
        consulta_tipos=tipos,
        registro_clientes=clientes,
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


def test_gestor_transiciona_solo_al_siguiente_estado() -> None:
    gestor, repo, _ = _crear_gestor()
    item = _crear_servicio(gestor)

    actualizado = gestor.cambiar_estado(item.servicio.id, "confirmado")

    assert actualizado.servicio.estado == "confirmado"
    assert repo.guardado is actualizado.servicio
    with pytest.raises(TransicionEstadoServicioInvalida):
        gestor.cambiar_estado(item.servicio.id, "finalizado")
    assert repo.items[item.servicio.id].estado == "confirmado"


def test_gestor_rechaza_cambio_de_estado_de_servicio_inexistente() -> None:
    gestor, _, _ = _crear_gestor()

    with pytest.raises(ServicioNoEncontrado):
        gestor.cambiar_estado(999, "confirmado")


def test_gestor_elimina_servicio_y_rechaza_id_inexistente() -> None:
    gestor, repo, _ = _crear_gestor()
    item = _crear_servicio(gestor)

    gestor.eliminar(item.servicio.id)

    assert item.servicio.id not in repo.items
    with pytest.raises(ServicioNoEncontrado):
        gestor.eliminar(item.servicio.id)


def test_gestor_crea_y_vincula_cliente_nuevo_sin_duplicarlo() -> None:
    gestor, repo, clientes = _crear_gestor()
    nuevo = Cliente.crear(
        razon_social="Mudanzas Nueva",
        telefono="3515559999",
        direccion_habitual="Av. Nueva 456",
    )

    item = gestor.crear(
        id_cliente=None,
        nuevo_cliente=nuevo,
        id_tipo_vehiculo=3,
        id_chofer=None,
        id_vehiculo=None,
        fecha=date(2026, 10, 25),
        hora_inicio=time(9, 30),
        horas_estimadas=Decimal("2"),
        distancia_ida_km=Decimal("15"),
    )

    assert item.servicio.id_cliente == 20
    assert repo.guardado is not None
    assert len(clientes.creados) == 1

    gestor.crear(
        id_cliente=None,
        nuevo_cliente=Cliente.crear(
            razon_social="  mudanzas   NUEVA ",
            telefono="3515559999",
            direccion_habitual="Av. Nueva 456",
        ),
        id_tipo_vehiculo=3,
        id_chofer=None,
        id_vehiculo=None,
        fecha=date(2026, 10, 26),
        hora_inicio=time(10, 0),
        horas_estimadas=Decimal("1"),
        distancia_ida_km=Decimal("0"),
    )

    assert len(clientes.creados) == 1, "La segunda alta debe reutilizar el cliente existente"


def test_disponibilidad_excluye_recursos_solapados_y_conserva_libres() -> None:
    gestor, repo, _ = _crear_gestor()
    repo.asignaciones = [
        AsignacionDia(
            id_chofer=1,
            id_vehiculo=21,
            hora_inicio=time(9, 0),
            horas_estimadas=Decimal("2"),
        ),
        AsignacionDia(
            id_chofer=None,
            id_vehiculo=22,
            hora_inicio=time(15, 0),
            horas_estimadas=Decimal("1"),
        ),
    ]

    disponibilidad = gestor.disponibilidad(
        fecha=date(2026, 10, 25),
        id_tipo_vehiculo=3,
        hora_inicio=time(10, 0),
        horas_estimadas=Decimal("1"),
    )

    assert [chofer.id for chofer in disponibilidad.choferes] == [2]
    assert [vehiculo.vehiculo.id for vehiculo in disponibilidad.vehiculos] == [22]
    assert disponibilidad.hora_fin == time(11, 0)


def test_disponibilidad_bloquea_el_dia_si_falta_la_hora_de_inicio() -> None:
    gestor, repo, _ = _crear_gestor()
    repo.asignaciones = [
        AsignacionDia(
            id_chofer=2,
            id_vehiculo=22,
            hora_inicio=None,
            horas_estimadas=Decimal("1"),
        )
    ]

    disponibilidad = gestor.disponibilidad(
        fecha=date(2026, 10, 25),
        id_tipo_vehiculo=3,
        hora_inicio=time(10, 0),
        horas_estimadas=Decimal("1"),
    )

    assert [chofer.id for chofer in disponibilidad.choferes] == [1]
    assert [vehiculo.vehiculo.id for vehiculo in disponibilidad.vehiculos] == [21]
