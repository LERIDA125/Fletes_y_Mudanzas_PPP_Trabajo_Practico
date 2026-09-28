"""Tests de integración de H1 contra PostgreSQL real (AGENTS.md §8, prioridad #2).

US1 — Registrar un cliente nuevo (P1).
US2 — Consultar clientes: listado con filtro y detalle (P1).
US3 — Modificar un cliente existente (P2).
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.cliente import Cliente
from app.domain.errores import RazonSocialDuplicada
from app.infrastructure.repositories.cliente_repo import ClienteRepo

REGISTROS = (
    "SELECT razon_social, razon_social_key, telefono, direccion_habitual, "
    "tiene_cuenta_corriente, activo FROM clientes"
)

TELEFONO = "351 555 0100"
DIRECCION = "Av. Colón 1250, Córdoba"


def _total_de_clientes(sesion: Session) -> int:
    return sesion.execute(text("SELECT count(*) FROM clientes")).scalar_one()


def _sembrar(repositorio: ClienteRepo, razones_sociales: list[str]) -> list[Cliente]:
    """Carga clientes por el repositorio, sin pasar por el endpoint de alta.

    Los tests de lectura no necesitan probar el alta —eso es US1—, y sembrar por el repositorio
    los deja independientes de que el endpoint de escritura cambie.
    """
    return [
        repositorio.crear(
            Cliente.crear(
                razon_social=razon_social,
                telefono=TELEFONO,
                direccion_habitual=DIRECCION,
            )
        )
        for razon_social in razones_sociales
    ]


def _razones_generadas(cantidad: int) -> list[str]:
    """Razones sociales distintas y ordenables, para probar el orden estable del listado."""
    return [f"Empresa Numero {indice:02d} S.A." for indice in range(1, cantidad + 1)]


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
        repo_test.crear(Cliente.crear("Almacén Central S.A.", TELEFONO, DIRECCION))
        segundo = Cliente.crear("almacen central s.a.", TELEFONO, "Bv. San Juan 450")

        with pytest.raises(RazonSocialDuplicada):
            repo_test.crear(segundo)

        assert _total_de_clientes(sesion_test) == 1


class TestListarClientes:
    def test_devuelve_los_clientes_cargados_con_el_total(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, _razones_generadas(3))

        respuesta = cliente.get("/api/clientes", headers=admin)

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["total"] == 3
        assert len(cuerpo["items"]) == 3

    def test_el_listado_vacio_no_es_un_error(
        self, cliente: TestClient, admin: dict[str, str]
    ) -> None:
        respuesta = cliente.get("/api/clientes", headers=admin)

        assert respuesta.status_code == 200
        assert respuesta.json() == {"items": [], "total": 0, "page": 1, "size": 20}

    def test_el_orden_es_estable_entre_peticiones(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, _razones_generadas(25))

        primera = cliente.get("/api/clientes?size=100", headers=admin).json()["items"]
        segunda = cliente.get("/api/clientes?size=100", headers=admin).json()["items"]

        assert [item["razon_social"] for item in primera] == _razones_generadas(25)
        assert [item["id"] for item in segunda] == [item["id"] for item in primera]

    def test_pagina_por_defecto_en_veinte_y_conserva_el_total_real(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, _razones_generadas(25))

        cuerpo = cliente.get("/api/clientes", headers=admin).json()

        assert len(cuerpo["items"]) == 20
        assert cuerpo["total"] == 25
        assert cuerpo["page"] == 1
        assert cuerpo["size"] == 20

    def test_la_segunda_pagina_sigue_a_la_primera_sin_repetir_ni_saltar(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, _razones_generadas(25))

        primera = cliente.get("/api/clientes", headers=admin).json()
        segunda = cliente.get("/api/clientes?page=2", headers=admin).json()

        assert [item["razon_social"] for item in primera["items"] + segunda["items"]] == (
            _razones_generadas(25)
        )
        assert segunda["page"] == 2
        assert segunda["total"] == 25

    def test_una_pagina_mas_alla_del_total_devuelve_lista_vacia_y_no_un_error(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, _razones_generadas(3))

        respuesta = cliente.get("/api/clientes?page=9", headers=admin)

        assert respuesta.status_code == 200
        assert respuesta.json()["items"] == []
        assert respuesta.json()["total"] == 3

    @pytest.mark.parametrize("consulta", ["size=101", "size=0", "page=0", "page=-1"])
    def test_rechaza_una_paginacion_invalida(
        self, cliente: TestClient, admin: dict[str, str], consulta: str
    ) -> None:
        respuesta = cliente.get(f"/api/clientes?{consulta}", headers=admin)

        assert respuesta.status_code == 422


class TestFiltrarClientes:
    RAZONES = [
        "Distribuidora del Sur S.A.",
        "Distribuidora del Norte S.A.",
        "Transportes del Sur S.A.",
        "Muebles del Litoral S.A.",
    ]

    @pytest.mark.parametrize(
        "texto",
        ["Distribuidora", "distribuidora", "DISTRIBUIDORA", "distri", "ibuidora"],
    )
    def test_el_filtro_ignora_las_mayusculas(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo, texto: str
    ) -> None:
        _sembrar(repo_test, self.RAZONES)

        cuerpo = cliente.get(f"/api/clientes?q={texto}", headers=admin).json()

        assert cuerpo["total"] == 2
        assert [item["razon_social"] for item in cuerpo["items"]] == self.RAZONES[:2]

    def test_el_filtro_coincide_con_parte_de_la_razon_social(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, self.RAZONES)

        cuerpo = cliente.get("/api/clientes?q=sur", headers=admin).json()

        assert [item["razon_social"] for item in cuerpo["items"]] == [
            "Distribuidora del Sur S.A.",
            "Transportes del Sur S.A.",
        ]
        assert cuerpo["total"] == 2

    def test_una_busqueda_sin_coincidencias_devuelve_lista_vacia_y_no_un_error(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, self.RAZONES)

        respuesta = cliente.get("/api/clientes?q=zincorp", headers=admin)

        assert respuesta.status_code == 200
        assert respuesta.json()["items"] == []
        assert respuesta.json()["total"] == 0

    def test_el_total_del_filtro_cuenta_solo_a_los_que_coinciden(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, _razones_generadas(25))

        cuerpo = cliente.get("/api/clientes?q=empresa%20numero%201", headers=admin).json()

        # Solo entran "numero 10" a "numero 19": el "01" no matchea porque el 0 separa al 1.
        assert cuerpo["total"] == 10
        assert len(cuerpo["items"]) == 10

    def test_el_filtro_se_combina_con_la_paginacion(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, _razones_generadas(25))

        cuerpo = cliente.get("/api/clientes?q=empresa&size=5&page=2", headers=admin).json()

        assert len(cuerpo["items"]) == 5
        assert cuerpo["total"] == 25
        assert cuerpo["page"] == 2
        assert cuerpo["size"] == 5


class TestDetalleDeCliente:
    def test_devuelve_los_cuatro_datos_y_las_fechas(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = repo_test.crear(
            Cliente.crear(
                razon_social="Distribuidora del Sur S.A.",
                telefono=TELEFONO,
                direccion_habitual=DIRECCION,
                tiene_cuenta_corriente=True,
            )
        )

        respuesta = cliente.get(f"/api/clientes/{creado.id}", headers=admin)

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["id"] == creado.id
        assert cuerpo["razon_social"] == "Distribuidora del Sur S.A."
        assert cuerpo["telefono"] == TELEFONO
        assert cuerpo["direccion_habitual"] == DIRECCION
        assert cuerpo["tiene_cuenta_corriente"] is True
        assert cuerpo["activo"] is True
        assert cuerpo["creado_en"] is not None
        assert cuerpo["actualizado_en"] is not None

    def test_consultar_el_detalle_no_modifica_la_fecha_de_ultima_modificacion(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = repo_test.crear(Cliente.crear("Distribuidora del Sur S.A.", TELEFONO, DIRECCION))

        antes = cliente.get(f"/api/clientes/{creado.id}", headers=admin).json()
        despues = cliente.get(f"/api/clientes/{creado.id}", headers=admin).json()

        assert despues["actualizado_en"] == antes["actualizado_en"]  # FR-020

    def test_un_identificador_inexistente_responde_404(
        self, cliente: TestClient, admin: dict[str, str]
    ) -> None:
        respuesta = cliente.get("/api/clientes/999999", headers=admin)

        assert respuesta.status_code == 404
        assert "999999" in respuesta.json()["detail"]

    def test_un_identificador_inexistente_no_crea_ningun_registro(
        self, cliente: TestClient, admin: dict[str, str], sesion_test: Session
    ) -> None:
        cliente.get("/api/clientes/999999", headers=admin)

        assert _total_de_clientes(sesion_test) == 0

    def test_un_cliente_dado_de_baja_deja_de_poder_consultarse(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = repo_test.crear(Cliente.crear("Distribuidora del Sur S.A.", TELEFONO, DIRECCION))
        repo_test.desactivar(creado.id)

        respuesta = cliente.get(f"/api/clientes/{creado.id}", headers=admin)

        assert respuesta.status_code == 404  # FR-014


class TestConsultarComoChofer:
    def test_el_chofer_puede_listar(
        self, cliente: TestClient, chofer: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, ["Distribuidora del Sur S.A."])

        respuesta = cliente.get("/api/clientes", headers=chofer)

        assert respuesta.status_code == 200
        assert respuesta.json()["total"] == 1

    def test_el_chofer_puede_ver_el_detalle(
        self, cliente: TestClient, chofer: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = repo_test.crear(Cliente.crear("Distribuidora del Sur S.A.", TELEFONO, DIRECCION))

        respuesta = cliente.get(f"/api/clientes/{creado.id}", headers=chofer)

        assert respuesta.status_code == 200
        assert respuesta.json()["razon_social"] == "Distribuidora del Sur S.A."

    def test_el_chofer_tambien_puede_filtrar(
        self, cliente: TestClient, chofer: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _sembrar(repo_test, ["Distribuidora del Sur S.A.", "Transportes del Norte S.A."])

        cuerpo = cliente.get("/api/clientes?q=distribuidora", headers=chofer).json()

        assert cuerpo["total"] == 1


def _cuerpo_de_edicion(razon_social: str = "Distribuidora del Sur S.A.", **cambios) -> dict:
    """Cuerpo del PUT. DD-5: los mismos cuatro datos requeridos que en el alta."""
    cuerpo = {
        "razon_social": razon_social,
        "telefono": TELEFONO,
        "direccion_habitual": DIRECCION,
        "tiene_cuenta_corriente": False,
    }
    cuerpo.update(cambios)
    return cuerpo


def _crear_para_editar(repo_test: ClienteRepo, **cambios) -> Cliente:
    return repo_test.crear(
        Cliente.crear(
            razon_social="Distribuidora del Sur S.A.",
            telefono=TELEFONO,
            direccion_habitual=DIRECCION,
            **cambios,
        )
    )


class TestModificarCliente:
    def test_devuelve_200_con_el_telefono_nuevo(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        respuesta = cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(telefono="351 555 0199"),
            headers=admin,
        )

        assert respuesta.status_code == 200
        assert respuesta.json()["telefono"] == "351 555 0199"

    def test_el_detalle_refleja_el_telefono_nuevo(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(telefono="351 555 0199"),
            headers=admin,
        )

        detalle = cliente.get(f"/api/clientes/{creado.id}", headers=admin).json()
        assert detalle["telefono"] == "351 555 0199"

    def test_la_fecha_de_modificacion_queda_despues_de_la_de_creacion(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        cuerpo = cliente.put(
            f"/api/clientes/{creado.id}", json=_cuerpo_de_edicion(), headers=admin
        ).json()

        creado_en = datetime.fromisoformat(cuerpo["creado_en"])
        actualizado_en = datetime.fromisoformat(cuerpo["actualizado_en"])
        assert actualizado_en > creado_en

    def test_habilita_la_cuenta_corriente(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        respuesta = cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(tiene_cuenta_corriente=True),
            headers=admin,
        )

        assert respuesta.status_code == 200
        assert respuesta.json()["tiene_cuenta_corriente"] is True

    def test_cambia_tambien_la_razon_social_y_el_domicilio(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        respuesta = cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(
                "Distribuidora Del Sur S.A.", direccion_habitual="Bv. San Juan 450"
            ),
            headers=admin,
        )

        cuerpo = respuesta.json()
        assert respuesta.status_code == 200
        assert cuerpo["razon_social"] == "Distribuidora Del Sur S.A."
        assert cuerpo["direccion_habitual"] == "Bv. San Juan 450"

    def test_guardar_sin_cambios_conserva_el_id_y_la_fecha_de_creacion(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test, tiene_cuenta_corriente=True)
        antes = cliente.get(f"/api/clientes/{creado.id}", headers=admin).json()

        cuerpo = cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(tiene_cuenta_corriente=True),
            headers=admin,
        ).json()

        assert cuerpo["id"] == creado.id
        assert cuerpo["creado_en"] == antes["creado_en"]
        assert cuerpo["razon_social"] == antes["razon_social"]
        assert cuerpo["telefono"] == antes["telefono"]
        assert cuerpo["direccion_habitual"] == antes["direccion_habitual"]
        assert cuerpo["tiene_cuenta_corriente"] is True

    def test_guardar_sin_cambios_refresca_la_fecha_de_modificacion(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)
        antes = cliente.get(f"/api/clientes/{creado.id}", headers=admin).json()

        cuerpo = cliente.put(
            f"/api/clientes/{creado.id}", json=_cuerpo_de_edicion(), headers=admin
        ).json()

        # FR-020: toda actualización refresca la fecha, aunque no cambie ningún dato.
        assert cuerpo["actualizado_en"] > antes["actualizado_en"]

    def test_no_se_crea_un_cliente_nuevo_al_modificar(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        repo_test: ClienteRepo,
        sesion_test: Session,
    ) -> None:
        creado = _crear_para_editar(repo_test)

        cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(telefono="351 555 0199"),
            headers=admin,
        )

        assert _total_de_clientes(sesion_test) == 1

    def test_rechaza_tomar_la_razon_social_de_otro_cliente(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        _crear_para_editar(repo_test)
        segundo = repo_test.crear(
            Cliente.crear("Distribuidora del Norte S.A.", TELEFONO, DIRECCION)
        )

        respuesta = cliente.put(
            f"/api/clientes/{segundo.id}",
            json=_cuerpo_de_edicion("Distribuidora del Sur S.A."),
            headers=admin,
        )

        assert respuesta.status_code == 409

    def test_rechazar_un_duplicado_deja_intacto_al_cliente_original(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        primero = _crear_para_editar(repo_test)
        segundo = repo_test.crear(
            Cliente.crear("Distribuidora del Norte S.A.", TELEFONO, DIRECCION)
        )

        cliente.put(
            f"/api/clientes/{segundo.id}",
            json=_cuerpo_de_edicion("DISTRIBUIDORA DEL SUR S.A."),
            headers=admin,
        )

        intacto = cliente.get(f"/api/clientes/{primero.id}", headers=admin).json()
        sin_tocar = cliente.get(f"/api/clientes/{segundo.id}", headers=admin).json()
        assert intacto["razon_social"] == "Distribuidora del Sur S.A."
        assert sin_tocar["razon_social"] == "Distribuidora del Norte S.A."

    def test_rechaza_razon_social_duplicada_variando_acentos(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        primero = repo_test.crear(Cliente.crear("Almacén Central S.A.", TELEFONO, DIRECCION))
        segundo = repo_test.crear(Cliente.crear("Transportes del Sur S.A.", TELEFONO, DIRECCION))

        respuesta = cliente.put(
            f"/api/clientes/{segundo.id}",
            json=_cuerpo_de_edicion("Almacen Central S.A."),
            headers=admin,
        )

        assert respuesta.status_code == 409
        assert (
            cliente.get(f"/api/clientes/{primero.id}", headers=admin).json()["razon_social"]
            == "Almacén Central S.A."
        )

    def test_guardar_la_misma_razon_social_no_se_rechaza_a_si_mismo(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = repo_test.crear(Cliente.crear("Almacén Central S.A.", TELEFONO, DIRECCION))

        respuesta = cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion("  ALMACEN   central S.A.  "),
            headers=admin,
        )

        assert respuesta.status_code == 200
        assert respuesta.json()["razon_social"] == "ALMACEN central S.A."

    @pytest.mark.parametrize("campo", ["razon_social", "telefono", "direccion_habitual"])
    def test_rechaza_datos_requeridos_ausentes(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo, campo: str
    ) -> None:
        creado = _crear_para_editar(repo_test)
        cuerpo = {clave: valor for clave, valor in _cuerpo_de_edicion().items() if clave != campo}

        respuesta = cliente.put(f"/api/clientes/{creado.id}", json=cuerpo, headers=admin)

        assert respuesta.status_code == 422

    @pytest.mark.parametrize(
        ("campo", "valor"),
        [
            ("razon_social", "Ab"),
            ("razon_social", "   "),
            ("razon_social", "A" * 121),
            ("telefono", "123"),
            ("telefono", ""),
            ("direccion_habitual", "Av 1"),
            ("direccion_habitual", "C" * 251),
        ],
    )
    def test_rechaza_datos_invalidos(
        self,
        cliente: TestClient,
        admin: dict[str, str],
        repo_test: ClienteRepo,
        campo: str,
        valor: str,
    ) -> None:
        creado = _crear_para_editar(repo_test)

        respuesta = cliente.put(
            f"/api/clientes/{creado.id}", json=_cuerpo_de_edicion(**{campo: valor}), headers=admin
        )

        assert respuesta.status_code == 422

    def test_un_dato_invalido_no_altera_el_cliente_guadado(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(telefono="351 555 0199", direccion_habitual="Av 1"),
            headers=admin,
        )

        # FR-011: no hay cambios parciales, ni el teléfono válido ni el domicilio inválido.
        detalle = cliente.get(f"/api/clientes/{creado.id}", headers=admin).json()
        assert detalle["telefono"] == TELEFONO
        assert detalle["direccion_habitual"] == DIRECCION

    def test_un_identificador_inexistente_responde_404(
        self, cliente: TestClient, admin: dict[str, str]
    ) -> None:
        respuesta = cliente.put("/api/clientes/999999", json=_cuerpo_de_edicion(), headers=admin)

        assert respuesta.status_code == 404

    def test_un_identificador_inexistente_no_crea_ningun_registro(
        self, cliente: TestClient, admin: dict[str, str], sesion_test: Session
    ) -> None:
        cliente.put("/api/clientes/999999", json=_cuerpo_de_edicion(), headers=admin)

        assert _total_de_clientes(sesion_test) == 0  # FR-016

    def test_rechaza_que_el_usuario_informe_el_id_o_las_fechas(
        self, cliente: TestClient, admin: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        respuesta = cliente.put(
            f"/api/clientes/{creado.id}",
            json={**_cuerpo_de_edicion(), "id": 99, "creado_en": "2020-01-01T00:00:00Z"},
            headers=admin,
        )

        assert respuesta.status_code == 422

    def test_el_chofer_no_puede_modificar(
        self, cliente: TestClient, chofer: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        respuesta = cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(telefono="351 555 0199"),
            headers=chofer,
        )

        assert respuesta.status_code == 403

    def test_el_rechazo_por_permiso_no_altera_el_cliente(
        self, cliente: TestClient, chofer: dict[str, str], repo_test: ClienteRepo
    ) -> None:
        creado = _crear_para_editar(repo_test)

        cliente.put(
            f"/api/clientes/{creado.id}",
            json=_cuerpo_de_edicion(telefono="351 555 0199"),
            headers=chofer,
        )

        detalle = cliente.get(f"/api/clientes/{creado.id}", headers=chofer).json()
        assert detalle["telefono"] == TELEFONO
