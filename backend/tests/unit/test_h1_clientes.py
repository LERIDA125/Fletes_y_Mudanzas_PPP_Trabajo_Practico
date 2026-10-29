"""Suite unificada de Gestión de Clientes (H1).

Comprimido exactamente en 2 tests de alto nivel:
1. `test_h1_dominio`: validaciones de razón social, teléfonos, domicilios e invariantes.
2. `test_h1_gestor_clientes`: ciclo completo (alta, unicidad, listar, editar, baja).
"""

import pytest

from app.application.clientes.gestor_clientes import GestorClientes
from app.domain.cliente import (
    Cliente,
    contar_digitos,
    normalizar_razon_social,
    normalizar_razon_visual,
)
from app.domain.errores import (
    ClienteConHistorial,
    ClienteNoEncontrado,
    RazonSocialDuplicada,
    ReglaNegocioError,
)
from tests.unit.application.clientes.fakes import FakeClienteRepo, FakeHistorial


def test_h1_dominio() -> None:
    # 1. Normalización y claves
    assert (
        normalizar_razon_visual("  Distribuidora   del  Sur S.A. ") == "Distribuidora del Sur S.A."
    )
    assert normalizar_razon_social("Almacén Central S.A.") == "almacen central s.a."
    assert normalizar_razon_social("Mañana S.R.L.") == "manana s.r.l."
    assert normalizar_razon_social("Distribuidora") == normalizar_razon_social("DISTRIBUIDORA")
    assert contar_digitos("+54 9 351 555-0100") == 13

    # 2. Creación válida y valores por defecto
    c = Cliente.crear("  Distribuidora del Sur  ", " 351 555 0100 ", " Av. Colón 1250 ")
    assert c.razon_social == "Distribuidora del Sur"
    assert c.telefono == "351 555 0100"
    assert c.direccion_habitual == "Av. Colón 1250"
    assert c.activo is True
    assert c.tiene_cuenta_corriente is False
    assert c.id is None and c.creado_en is None and c.actualizado_en is None

    c_cc = Cliente.crear("Mudanzas Express 🚚", "+54 9 11 1234-5678", "Calle 123", True)
    assert c_cc.tiene_cuenta_corriente is True
    assert c_cc.razon_social == "Mudanzas Express 🚚"

    # Formatos de teléfono válidos
    for tel in ["0351-555-0100", "(351) 555 0100", "1234567"]:
        assert Cliente.crear("Cliente Valido", tel, "Calle 123").telefono == tel

    # 3. Invariantes y rechazos
    for rs_inv in ["", "   ", "Ab", "A" * 121]:
        with pytest.raises(ReglaNegocioError):
            Cliente.crear(rs_inv, "351 555 0100", "Av. Colón 1250")

    for dir_inv in ["", "   ", "Av 1", "C" * 251]:
        with pytest.raises(ReglaNegocioError):
            Cliente.crear("Cliente Valido", "351 555 0100", dir_inv)

    for tel_inv in [
        "",
        "123456",
        "1" * 21,
        "1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0",
    ]:
        with pytest.raises(ReglaNegocioError):
            Cliente.crear("Cliente Valido", tel_inv, "Av. Colón 1250")

    # 4. Modificación y baja lógica
    c.actualizar(
        razon_social="Distribuidora del Norte",
        telefono="351 999 8888",
        direccion_habitual="Ruta 9 Km 10",
        tiene_cuenta_corriente=True,
    )
    assert c.razon_social == "Distribuidora del Norte"
    assert c.tiene_cuenta_corriente is True

    # Modificación inválida no deja el cliente a medias
    with pytest.raises(ReglaNegocioError):
        c.actualizar(
            razon_social="Ab",
            telefono="351 999 8888",
            direccion_habitual="Ruta 9 Km 10",
            tiene_cuenta_corriente=True,
        )
    assert c.razon_social == "Distribuidora del Norte"

    c.desactivar()
    assert c.activo is False
    c.desactivar()  # Idempotente
    assert c.activo is False


def test_h1_gestor_clientes() -> None:
    repo = FakeClienteRepo()
    historial = FakeHistorial()
    gestor = GestorClientes(repositorio_clientes=repo, consulta_historial=historial)

    # 1. Registrar
    c1 = gestor.registrar(
        razon_social="Distribuidora del Sur S.A.",
        telefono="351 555 0100",
        direccion_habitual="Av. Colón 1250",
        tiene_cuenta_corriente=False,
    )
    assert c1.id == 1 and c1.activo is True

    # Rechazo de duplicados (exacto, con espacios y acentos)
    with pytest.raises(RazonSocialDuplicada):
        gestor.registrar(
            razon_social="  DISTRIBUIDORA DEL SUR S.A.  ",
            telefono="351 555 0100",
            direccion_habitual="Av. Colón 1250",
            tiene_cuenta_corriente=False,
        )

    gestor.registrar(
        razon_social="Almacén Central",
        telefono="351 111 2222",
        direccion_habitual="Calle 10",
        tiene_cuenta_corriente=True,
    )
    with pytest.raises(RazonSocialDuplicada):
        gestor.registrar(
            razon_social="Almacen Central",
            telefono="351 111 2222",
            direccion_habitual="Calle 10",
            tiene_cuenta_corriente=False,
        )

    # Rechazo de datos inválidos en registrar
    with pytest.raises(ReglaNegocioError):
        gestor.registrar(
            razon_social="Ab",
            telefono="351 555 0100",
            direccion_habitual="Av. Colón 1250",
            tiene_cuenta_corriente=False,
        )

    # 2. Listar y buscar
    lista, total = gestor.listar(busqueda="almacen", offset=0, limit=10)
    assert total == 1 and lista[0].razon_social == "Almacén Central"

    assert gestor.obtener(1).razon_social == "Distribuidora del Sur S.A."
    with pytest.raises(ClienteNoEncontrado):
        gestor.obtener(999)

    # 3. Modificación
    c_mod = gestor.actualizar(
        1,
        razon_social="Distribuidora del Sur SRL",
        telefono="351 444 3333",
        direccion_habitual="Av. Colón 2000",
        tiene_cuenta_corriente=True,
    )
    assert c_mod.razon_social == "Distribuidora del Sur SRL"
    assert c_mod.tiene_cuenta_corriente is True

    # No choca consigo mismo
    gestor.actualizar(
        1,
        razon_social="Distribuidora del Sur SRL",
        telefono="351 444 3333",
        direccion_habitual="Av. Colón 2000",
        tiene_cuenta_corriente=True,
    )

    # Choca con otro cliente
    with pytest.raises(RazonSocialDuplicada):
        gestor.actualizar(
            1,
            razon_social="Almacén Central",
            telefono="351 444 3333",
            direccion_habitual="Av. Colón 2000",
            tiene_cuenta_corriente=True,
        )

    # 4. Baja lógica
    historial.marcar_con_historial(1)
    with pytest.raises(ClienteConHistorial):
        gestor.eliminar(1)

    historial.clientes_con_historial.clear()
    gestor.eliminar(1)
    assert repo.obtener_por_id(1).activo is False

    # Idempotencia al eliminar y no encontrado
    gestor.eliminar(1)
    with pytest.raises(ClienteNoEncontrado):
        gestor.eliminar(999)
