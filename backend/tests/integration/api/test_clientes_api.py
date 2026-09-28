"""Tests de integración de H1 contra PostgreSQL real (AGENTS.md §8, prioridad #2).

US1 — Registrar un cliente nuevo (P1).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.repositories.cliente_repo import ClienteRepo

REGISTROS = (
    "SELECT razon_social, razon_social_key, telefono, direccion_habitual, "
    "tiene_cuenta_corriente, activo FROM clientes"
)


def _total_de_clientes(sesion: Session) -> int:
    return sesion.execute(text("SELECT count(*) FROM clientes")).scalar_one()


class TestRegistrarCliente:
    def test_devuelve_201_con_los_cuatro_datos_pedidos(
        self, cliente: TestClient, admin: dict[str, str], datos_cliente: dict[str, object]
    ) -> None:
        respuesta = cliente.post("/api/clientes", json=datos_cliente, headers=admin)

        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["razon_social"] == "Distribuidora del Sur S.A."
        assert cuerpo["telefono"] == "351 555 0100"
        assert cuerpo["direccion_habitual"] == "Av. Colón 1250, Córdoba"
        assert cuerpo["tiene_cuenta_corriente"] is True

    def test_asigna_identificador_y_fechas_del_sistema(
        self, cliente: TestClient, admin: dict[str, str], datos_cliente: dict[str, object]
    ) -> None:
        cuerpo = cliente.post("/api/clientes", json=datos_cliente, headers=admin).json()

        assert isinstance(cuerpo["id"], int)
        assert cuerpo["id"] > 0
        assert cuerpo["creado_en"] is not None
        assert cuerpo["actualizado_en"] is not None
        assert cuerpo["activo"] is True

    @pytest.mark.parametrize("tiene_cuenta_corriente", [True, False])
    def test_respeta_el_indicador_de_cuenta_corriente(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        tiene_cuenta_corriente: bool,
    ) -> None:
        respuesta = cliente.post(
            "/api/clientes",
            json={**datos_cliente, "tiene_cuenta_corriente": tiene_cuenta_corriente},
            headers=admin,
        )

        assert respuesta.status_code == 201
        assert respuesta.json()["tiene_cuenta_corriente"] is tiene_cuenta_corriente

    def test_el_indicador_de_cuenta_corriente_por_defecto_es_false(
        self, cliente: TestClient, admin: dict[str, str], datos_cliente: dict[str, object]
    ) -> None:
        cuerpo = {
            clave: valor
            for clave, valor in datos_cliente.items()
            if clave != "tiene_cuenta_corriente"
        }

        respuesta = cliente.post("/api/clientes", json=cuerpo, headers=admin)

        assert respuesta.status_code == 201
        assert respuesta.json()["tiene_cuenta_corriente"] is False

    def test_el_cliente_queda_persistido_en_la_base(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        sesion_test: Session,
    ) -> None:
        id_creado = cliente.post("/api/clientes", json=datos_cliente, headers=admin).json()["id"]

        fila = sesion_test.execute(text(f"{REGISTROS} WHERE id = :id"), {"id": id_creado}).one()

        assert fila.razon_social == "Distribuidora del Sur S.A."
        assert fila.telefono == "351 555 0100"
        assert fila.direccion_habitual == "Av. Colón 1250, Córdoba"
        assert fila.tiene_cuenta_corriente is True
        assert fila.activo is True

    def test_guarda_la_razon_social_normalizada_para_buscar_y_comparar(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        sesion_test: Session,
    ) -> None:
        respuesta = cliente.post(
            "/api/clientes",
            json={**datos_cliente, "razon_social": "  Almacén  Central S.A.  "},
            headers=admin,
        )

        assert respuesta.json()["razon_social"] == "Almacén Central S.A."
        fila = sesion_test.execute(text(REGISTROS)).one()
        assert fila.razon_social_key == "almacen central s.a."

    def test_rechaza_que_el_usuario_informe_el_id_o_las_fechas(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        sesion_test: Session,
    ) -> None:
        respuesta = cliente.post(
            "/api/clientes",
            json={**datos_cliente, "id": 99, "creado_en": "2020-01-01T00:00:00Z"},
            headers=admin,
        )

        assert respuesta.status_code == 422
        assert _total_de_clientes(sesion_test) == 0

    def test_acepta_telefonos_en_formatos_variantes(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        sesion_test: Session,
    ) -> None:
        for telefono in ["+54 9 351 555 0100", "0351-555-0100", "(351) 555 0100"]:
            respuesta = cliente.post(
                "/api/clientes",
                json={
                    **datos_cliente,
                    "telefono": telefono,
                    "razon_social": f"Cliente {telefono}",
                },
                headers=admin,
            )
            assert respuesta.status_code == 201, respuesta.text

        assert _total_de_clientes(sesion_test) == 3

    def test_acepta_razon_social_con_emoji(
        self, cliente: TestClient, admin: dict[str, str], datos_cliente: dict[str, object]
    ) -> None:
        respuesta = cliente.post(
            "/api/clientes",
            json={**datos_cliente, "razon_social": "Mudanzas Express 🚚"},
            headers=admin,
        )

        assert respuesta.status_code == 201


class TestRegistrarDuplicado:
    def test_rechaza_razon_social_ya_registrada(
        self, cliente: TestClient, admin: dict[str, str], datos_cliente: dict[str, object]
    ) -> None:
        cliente.post("/api/clientes", json=datos_cliente, headers=admin)

        respuesta = cliente.post("/api/clientes", json=datos_cliente, headers=admin)

        assert respuesta.status_code == 409

    @pytest.mark.parametrize(
        "variante",
        [
            "DISTRIBUIDORA DEL SUR S.A.",
            "  Distribuidora   del  Sur S.A.  ",
            "Distribuidora Del Sur s.a.",
        ],
    )
    def test_rechaza_razon_social_duplicada_variando_mayusculas_y_espacios(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        variante: str,
    ) -> None:
        cliente.post("/api/clientes", json=datos_cliente, headers=admin)

        respuesta = cliente.post(
            "/api/clientes", json={**datos_cliente, "razon_social": variante}, headers=admin
        )

        assert respuesta.status_code == 409

    def test_no_persiste_un_segundo_cliente_al_rechazar_el_duplicado(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        sesion_test: Session,
    ) -> None:
        cliente.post("/api/clientes", json=datos_cliente, headers=admin)

        cliente.post(
            "/api/clientes",
            json={**datos_cliente, "razon_social": "otra empresa s.a."},
            headers=admin,
        )
        respuesta = cliente.post("/api/clientes", json=datos_cliente, headers=admin)

        assert respuesta.status_code == 409
        assert _total_de_clientes(sesion_test) == 2

    def test_permite_registrar_una_razon_social_distinta(
        self, cliente: TestClient, admin: dict[str, str], datos_cliente: dict[str, object]
    ) -> None:
        cliente.post("/api/clientes", json=datos_cliente, headers=admin)

        respuesta = cliente.post(
            "/api/clientes",
            json={**datos_cliente, "razon_social": "Distribuidora del Norte S.A."},
            headers=admin,
        )

        assert respuesta.status_code == 201


class TestRegistrarDatosInvalidos:
    @pytest.mark.parametrize(
        "campo",
        ["razon_social", "telefono", "direccion_habitual"],
    )
    def test_rechaza_datos_requeridos_ausentes(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        campo: str,
    ) -> None:
        cuerpo = {clave: valor for clave, valor in datos_cliente.items() if clave != campo}

        respuesta = cliente.post("/api/clientes", json=cuerpo, headers=admin)

        assert respuesta.status_code == 422

    @pytest.mark.parametrize(
        ("campo", "valor"),
        [
            ("razon_social", "Ab"),
            ("razon_social", "   "),
            ("razon_social", "A" * 121),
            ("telefono", "123"),
            ("telefono", "1" * 21),
            ("telefono", ""),
            ("direccion_habitual", "Av 1"),
            ("direccion_habitual", "C" * 251),
        ],
    )
    def test_rechaza_datos_invalidos(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        campo: str,
        valor: str,
    ) -> None:
        respuesta = cliente.post(
            "/api/clientes", json={**datos_cliente, campo: valor}, headers=admin
        )

        assert respuesta.status_code == 422

    def test_no_persiste_nada_ante_un_dato_invalido(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        sesion_test: Session,
    ) -> None:
        respuesta = cliente.post(
            "/api/clientes", json={**datos_cliente, "telefono": "1"}, headers=admin
        )

        assert respuesta.status_code == 422
        assert _total_de_clientes(sesion_test) == 0


class TestPermisos:
    def test_el_chofer_no_puede_registrar(
        self, cliente: TestClient, chofer: dict[str, str], datos_cliente: dict[str, object]
    ) -> None:
        respuesta = cliente.post("/api/clientes", json=datos_cliente, headers=chofer)

        assert respuesta.status_code == 403

    def test_sin_rol_indicado_no_puede_registrar(
        self, cliente: TestClient, datos_cliente: dict[str, object]
    ) -> None:
        respuesta = cliente.post("/api/clientes", json=datos_cliente)

        assert respuesta.status_code == 403

    def test_un_rol_desconocido_no_puede_registrar(
        self, cliente: TestClient, datos_cliente: dict[str, object]
    ) -> None:
        respuesta = cliente.post(
            "/api/clientes", json=datos_cliente, headers={"X-Rol": "supervisor"}
        )

        assert respuesta.status_code == 403

    def test_el_rechazo_por_permiso_no_persiste_nada(
        self,
        cliente: TestClient,
        chofer: dict[str, str],
        datos_cliente: dict[str, object],
        sesion_test: Session,
    ) -> None:
        cliente.post("/api/clientes", json=datos_cliente, headers=chofer)

        assert _total_de_clientes(sesion_test) == 0


class TestUnicidadEnLaBase:
    def test_la_base_impide_dos_razones_sociales_iguales_aunque_el_gestor_no_lo_vea(
        self,
        admin: dict[str, str],
        datos_cliente: dict[str, object],
        repo_test: ClienteRepo,
        sesion_test: Session,
    ) -> None:
        """Defensa en profundidad: la restricción UNIQUE de la base es la última línea."""
        from app.domain.cliente import Cliente
        from app.domain.errores import RazonSocialDuplicada

        repo_test.crear(Cliente.crear("Almacén Central S.A.", "351 555 0100", "Av. Colón 1250"))
        segundo = Cliente.crear("almacen central s.a.", "351 555 0100", "Bv. San Juan 450")

        with pytest.raises(RazonSocialDuplicada):
            repo_test.crear(segundo)

        assert _total_de_clientes(sesion_test) == 1
