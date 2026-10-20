"""Suite unificada de Gestión de Choferes (H3).

Comprimido exactamente en 2 tests de alto nivel:
1. `test_h3_dominio`: validaciones de nombre, teléfono, valores por defecto e invariantes.
2. `test_h3_gestor_choferes`: ciclo completo (alta, listar activos, editar, baja lógica).
"""

import pytest

from app.application.choferes.gestor_choferes import GestorChoferes
from app.domain.chofer import Chofer, normalizar_nombre
from app.domain.errores import ChoferNoEncontrado, ReglaNegocioError
from tests.unit.application.choferes.fakes import FakeChoferRepo


def test_h3_dominio() -> None:
    # 1. Normalización del nombre
    assert normalizar_nombre("  Juan   Pérez  ") == "Juan Pérez"

    # 2. Creación válida y valores por defecto
    c = Chofer.crear("  Juan Pérez ", " 351 555 0100 ")
    assert c.nombre_completo == "Juan Pérez"
    assert c.telefono == "351 555 0100"
    assert c.activo is True
    assert c.saldo_a_favor == 0.0
    assert c.id is None and c.creado_en is None and c.actualizado_en is None

    # Formatos de teléfono válidos
    for tel in ["0351-555-0100", "(351) 555 0100", "1234567", "+54 9 351 555-0100"]:
        assert Chofer.crear("Chofer Valido", tel).telefono == tel

    # 3. Invariantes y rechazos
    for nombre_inv in ["", "   ", "Ab", "A" * 121]:
        with pytest.raises(ReglaNegocioError):
            Chofer.crear(nombre_inv, "351 555 0100")

    for tel_inv in ["", "123456", "1" * 21]:
        with pytest.raises(ReglaNegocioError):
            Chofer.crear("Chofer Valido", tel_inv)

    # 4. Modificación conserva id, fecha de creación y saldo; y no deja el chofer a medias
    c.id = 1
    c.saldo_a_favor = 1500.0
    c.actualizar(nombre_completo="Juan Carlos Pérez", telefono="351 999 8888")
    assert c.nombre_completo == "Juan Carlos Pérez"
    assert c.telefono == "351 999 8888"
    assert c.id == 1
    assert c.saldo_a_favor == 1500.0

    with pytest.raises(ReglaNegocioError):
        c.actualizar(nombre_completo="Ab", telefono="351 999 8888")
    assert c.nombre_completo == "Juan Carlos Pérez"

    # 5. Baja lógica
    c.desactivar()
    assert c.activo is False
    assert c.saldo_a_favor == 1500.0


def test_h3_gestor_choferes() -> None:
    repo = FakeChoferRepo()
    gestor = GestorChoferes(repositorio_choferes=repo)

    # Alta: valores por defecto
    chofer = gestor.registrar(nombre_completo="Juan Pérez", telefono="351 555 0100")
    assert chofer.id is not None
    assert chofer.activo is True
    assert chofer.saldo_a_favor == 0.0

    otro = gestor.registrar(nombre_completo="María Gómez", telefono="351 555 0200")

    # Listado: filtra por texto insensible a mayúsculas
    items, total = gestor.listar(busqueda="juan", offset=0, limit=20)
    assert total == 1
    assert [i.id for i in items] == [chofer.id]

    # Obtener inexistente → ChoferNoEncontrado
    with pytest.raises(ChoferNoEncontrado):
        gestor.obtener(999)

    # Actualizar conserva id y saldo
    chofer.saldo_a_favor = 500.0
    repo.actualizar(chofer)
    actualizado = gestor.actualizar(
        chofer.id, nombre_completo="Juan C. Pérez", telefono="351 999 8888"
    )
    assert actualizado.id == chofer.id
    assert actualizado.saldo_a_favor == 500.0

    # Actualización inválida no muta al chofer guardado
    with pytest.raises(ReglaNegocioError):
        gestor.actualizar(chofer.id, nombre_completo="Ab", telefono="351 999 8888")
    assert gestor.obtener(chofer.id).nombre_completo == "Juan C. Pérez"

    # Baja lógica: desaparece del listado y del detalle, pero el registro persiste
    gestor.eliminar(otro.id)
    _, total_activos = gestor.listar(busqueda=None, offset=0, limit=20)
    assert total_activos == 1
    with pytest.raises(ChoferNoEncontrado):
        gestor.obtener(otro.id)

    # Baja de un chofer inexistente → ChoferNoEncontrado
    with pytest.raises(ChoferNoEncontrado):
        gestor.eliminar(999)
