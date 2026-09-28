from datetime import UTC, datetime

import pytest

from app.domain.cliente import (
    Cliente,
    contar_digitos,
    normalizar_razon_social,
    normalizar_razon_visual,
)
from app.domain.errores import ReglaNegocioError


class TestNormalizacion:
    def test_normalizar_razon_visual_colapsa_espacios_sobrantes(self) -> None:
        assert normalizar_razon_visual("  Distribuidora   del  Sur S.A. ") == (
            "Distribuidora del Sur S.A."
        )

    def test_normalizar_razon_social_ignora_mayusculas(self) -> None:
        assert normalizar_razon_social("Distribuidora del Sur S.A.") == normalizar_razon_social(
            "DISTRIBUIDORA DEL SUR S.A."
        )

    def test_normalizar_razon_social_ignora_acentos(self) -> None:
        assert normalizar_razon_social("Almacén Central S.A.") == "almacen central s.a."

    def test_normalizar_razon_social_ignora_tildes_de_enie(self) -> None:
        assert normalizar_razon_social("Mañana S.R.L.") == "manana s.r.l."

    def test_contar_digitos_solo_cuenta_numeros(self) -> None:
        assert contar_digitos("+54 9 351 555-0100") == 13


class TestCrearCliente:
    def test_crear_deja_el_id_y_las_fechas_a_cargo_del_sistema(self) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250")

        assert cliente.id is None
        assert cliente.creado_en is None
        assert cliente.actualizado_en is None

    def test_crear_activo_y_sin_cuenta_corriente_por_defecto(self) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250")

        assert cliente.activo is True
        assert cliente.tiene_cuenta_corriente is False

    def test_crear_acepta_cuenta_corriente_true(self) -> None:
        cliente = Cliente.crear(
            "Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250", True
        )

        assert cliente.tiene_cuenta_corriente is True

    def test_crear_normaliza_los_espacios_al_guardar(self) -> None:
        cliente = Cliente.crear(
            "  Distribuidora  del Sur S.A. ", " 351 555 0100 ", " Av. Colón  1250 "
        )

        assert cliente.razon_social == "Distribuidora del Sur S.A."
        assert cliente.telefono == "351 555 0100"
        assert cliente.direccion_habitual == "Av. Colón 1250"

    def test_razon_social_key_esta_en_minusculas_y_sin_acentos(self) -> None:
        cliente = Cliente.crear("Almacén Central S.A.", "351 555 0100", "Av. Colón 1250")

        assert cliente.razon_social_key == "almacen central s.a."

    def test_razon_social_key_es_estable_entre_variantes_de_texto(self) -> None:
        uno = Cliente.crear("Almacén Central S.A.", "351 555 0100", "Av. Colón 1250")
        otro = Cliente.crear("  ALMACEN   central s.a. ", "351 555 0100", "Av. Colón 1250")

        assert uno.razon_social_key == otro.razon_social_key

    def test_crear_acepta_razon_social_con_emoji(self) -> None:
        cliente = Cliente.crear("Mudanzas Express 🚚", "351 555 0100", "Av. Colón 1250")

        assert cliente.razon_social == "Mudanzas Express 🚚"

    @pytest.mark.parametrize(
        "telefono",
        ["351 555 0100", "+54 9 351 555 0100", "0351-555-0100", "(351) 555 0100"],
    )
    def test_crear_acepta_telefonos_en_formatos_variantes(self, telefono: str) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", telefono, "Av. Colón 1250")

        assert cliente.telefono == telefono


class TestInvariantesDeCrear:
    @pytest.mark.parametrize("razon_social", ["", "   ", "Ab", "A" * 121])
    def test_crear_rechaza_razon_social_invalida(self, razon_social: str) -> None:
        with pytest.raises(ReglaNegocioError):
            Cliente.crear(razon_social, "351 555 0100", "Av. Colón 1250")

    @pytest.mark.parametrize("direccion", ["", "    ", "Av 1", "C" * 251])
    def test_crear_rechaza_direccion_invalida(self, direccion: str) -> None:
        with pytest.raises(ReglaNegocioError):
            Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", direccion)

    def test_crear_acepta_los_extremos_de_largo_validos(self) -> None:
        cliente = Cliente.crear("Abc", "351 555 0100", "Av. Colón 1250")
        cliente = Cliente.crear("A" * 120, "351 555 0100", "C" * 250)

        assert cliente.razon_social == "A" * 120
        assert cliente.direccion_habitual == "C" * 250

    @pytest.mark.parametrize("telefono", ["", "123456", "1" * 21])
    def test_crear_rechaza_telefono_invalido(self, telefono: str) -> None:
        with pytest.raises(ReglaNegocioError):
            Cliente.crear("Distribuidora del Sur S.A.", telefono, "Av. Colón 1250")

    def test_crear_acepta_telefono_de_7_digitos(self) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "5550100", "Av. Colón 1250")

        assert cliente.telefono == "5550100"

    def test_crear_rechaza_bandera_que_no_es_booleana(self) -> None:
        with pytest.raises(ReglaNegocioError):
            Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250", "sí")


class TestActualizar:
    def test_actualizar_cambia_los_datos_editables(self) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250")

        cliente.actualizar(
            razon_social="Distribuidora del Norte S.A.",
            telefono="351 555 0199",
            direccion_habitual="Bv. San Juan 450",
            tiene_cuenta_corriente=True,
        )

        assert cliente.razon_social == "Distribuidora del Norte S.A."
        assert cliente.telefono == "351 555 0199"
        assert cliente.direccion_habitual == "Bv. San Juan 450"
        assert cliente.tiene_cuenta_corriente is True

    def test_actualizar_conserva_el_id_y_la_fecha_de_creacion(self) -> None:
        creado_en = datetime(2026, 3, 1, 10, 0, tzinfo=UTC)
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250")
        cliente.id = 7
        cliente.creado_en = creado_en

        cliente.actualizar(
            razon_social="Distribuidora del Sur S.A.",
            telefono="351 555 0199",
            direccion_habitual="Av. Colón 1250",
            tiene_cuenta_corriente=False,
        )

        assert cliente.id == 7
        assert cliente.creado_en == creado_en

    def test_actualizar_invalido_no_deja_el_cliente_a_medias(self) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250")

        with pytest.raises(ReglaNegocioError):
            cliente.actualizar(
                razon_social="Distribuidora del Norte S.A.",
                telefono="1",
                direccion_habitual="Av. Colón 1250",
                tiene_cuenta_corriente=False,
            )

        assert cliente.razon_social == "Distribuidora del Sur S.A."
        assert cliente.telefono == "351 555 0100"

    def test_actualizar_normaliza_lo_que_se_guarda(self) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250")

        cliente.actualizar(
            razon_social="  Distribuidora   del Sur S.A.  ",
            telefono="351 555 0100",
            direccion_habitual="Av. Colón 1250",
            tiene_cuenta_corriente=False,
        )

        assert cliente.razon_social == "Distribuidora del Sur S.A."


class TestDesactivar:
    def test_desactivar_pone_activo_en_false(self) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250")

        cliente.desactivar()

        assert cliente.activo is False

    def test_desactivar_es_idempotente(self) -> None:
        cliente = Cliente.crear("Distribuidora del Sur S.A.", "351 555 0100", "Av. Colón 1250")

        cliente.desactivar()
        cliente.desactivar()

        assert cliente.activo is False
