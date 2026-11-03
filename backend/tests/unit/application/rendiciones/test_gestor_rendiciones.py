"""Pruebas de reglas de negocio de Rendiciones."""

from datetime import date, time
from decimal import Decimal

import pytest

from app.application.rendiciones.gestor_rendiciones import GestorRendiciones
from app.application.rendiciones.puertos import (
    ServicioElegible,
    ServicioParaRendir,
)
from app.domain.errores import (
    EstadoRendicionInvalido,
    RendicionNoEncontrada,
    ServicioNoEncontrado,
    ServicioNoRendible,
    ServicioSinChoferParaRendir,
    ServicioYaRendido,
)
from tests.unit.application.rendiciones.fakes import (
    FakeConsultaServicios,
    FakeRendicionRepo,
)

FECHA = date(2026, 11, 3)


def _gestor() -> tuple[GestorRendiciones, FakeRendicionRepo, FakeConsultaServicios]:
    repo = FakeRendicionRepo()
    consulta = FakeConsultaServicios()
    return GestorRendiciones(repo, consulta), repo, consulta


def _registrar(gestor: GestorRendiciones, **overrides):
    datos = {
        "id_servicio": 10,
        "tarifa": Decimal("18500.00"),
        "adelanto": Decimal("12000.00"),
        "gasto_combustible": Decimal("2000.00"),
        "gasto_peajes": Decimal("300.00"),
        "gasto_otros": Decimal("200.00"),
        "usuario_id": 1,
    }
    datos.update(overrides)
    return gestor.registrar(**datos)


def _servicio(estado: str = "finalizado", id_chofer: int | None = 3) -> ServicioParaRendir:
    return ServicioParaRendir(
        id_servicio=10,
        id_chofer=id_chofer,
        fecha=FECHA,
        estado=estado,
    )


def test_registra_rendicion_derivando_datos_del_servicio() -> None:
    gestor, repo, consulta = _gestor()
    consulta.servicios[10] = _servicio()

    item = _registrar(gestor)

    assert item.rendicion.codigo == "REN-001"
    assert item.rendicion.id_chofer == 3
    assert item.rendicion.fecha == FECHA
    assert item.rendicion.saldo == Decimal("4000.00")
    assert item.rendicion.creado_por_id == 1
    assert item.nombre_chofer == "Chofer Demo"
    assert repo.existe_para_servicio(10)


def test_rechaza_servicio_inexistente() -> None:
    gestor, _, _ = _gestor()

    with pytest.raises(ServicioNoEncontrado):
        _registrar(gestor)


@pytest.mark.parametrize("estado", ["pendiente", "confirmado", "en curso", "cancelado"])
def test_rechaza_servicio_no_rendible(estado: str) -> None:
    gestor, _, consulta = _gestor()
    consulta.servicios[10] = _servicio(estado=estado)

    with pytest.raises(ServicioNoRendible):
        _registrar(gestor)


def test_rechaza_servicio_sin_chofer() -> None:
    gestor, _, consulta = _gestor()
    consulta.servicios[10] = _servicio(id_chofer=None)

    with pytest.raises(ServicioSinChoferParaRendir):
        _registrar(gestor)


def test_rechaza_servicio_ya_rendido() -> None:
    gestor, repo, consulta = _gestor()
    consulta.servicios[10] = _servicio()
    _registrar(gestor)
    repo.servicios_rendidos.add(10)

    with pytest.raises(ServicioYaRendido):
        _registrar(gestor)


def test_cambia_estado_y_rechaza_estado_invalido() -> None:
    gestor, _, consulta = _gestor()
    consulta.servicios[10] = _servicio()
    creada = _registrar(gestor)

    actualizada = gestor.cambiar_estado(
        creada.rendicion.id or 0, estado="aprobada", usuario_id=9
    )
    assert actualizada.rendicion.estado == "aprobada"
    assert actualizada.rendicion.modificado_por_id == 9

    with pytest.raises(EstadoRendicionInvalido):
        gestor.cambiar_estado(creada.rendicion.id or 0, estado="cerrada")


def test_cambiar_estado_de_rendicion_inexistente() -> None:
    gestor, _, _ = _gestor()

    with pytest.raises(RendicionNoEncontrada):
        gestor.cambiar_estado(999, estado="aprobada")


def test_lista_con_resumen_y_servicios_elegibles() -> None:
    gestor, _, consulta = _gestor()
    consulta.servicios[10] = _servicio()
    _registrar(gestor)
    consulta.elegibles = [
        ServicioElegible(
            id_servicio=11,
            razon_social_cliente="Acme",
            nombre_chofer="Chofer Demo",
            fecha=FECHA,
            hora_inicio=time(9, 0),
            precio_total=Decimal("12000.00"),
        )
    ]

    items, total, resumen = gestor.listar(busqueda=None, offset=0, limit=10)

    assert total == 1
    assert len(items) == 1
    assert resumen.pendiente_cantidad == 2
    assert resumen.pendiente_total == Decimal("1000.00")
    assert gestor.listar_servicios_elegibles()[0].id_servicio == 11
