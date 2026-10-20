# Tasks: H3 — Gestión de Choferes

**Input**: `specs/H3-gestion-choferes.md` (spec) + `specs/H3-gestion-choferes-plan.md` (plan)

**Prerequisites**: plan, spec (para las historias de usuario)

**Branch**: `feature/CRUD_choferes`

**Tests**: incluidos y **obligatorios** — AGENTS.md §8 los exige como prioridad #1 para
`app/application/`. Se escriben antes de la implementación y deben fallar primero.

**Organización**: las tareas están desglosadas en orden de dependencia técnica, agrupadas por eje
(dominio → infraestructura → aplicación → presentación → tests → cierre). Cada tarea es atómica y
apunta a un archivo concreto.

## Format: `[ID] [Eje] [P?] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Eje]**: Dominio · Infraestructura · Aplicación · Presentación · Tests · Cierre
- Las rutas son exactas y relativas a la raíz del repo

**Total**: 20 tareas (T01–T20)

---

## Eje 1 — Dominio

- [x] **T01** [Dominio] Agregar en `app/domain/errores.py` la excepción `ChoferNoEncontrado(RecursoNoEncontrado)` — único error nuevo de la historia (el nombre y el teléfono no son únicos, y la baja no tiene dependencias bloqueantes). Cubre FR-015
- [x] **T02** [Dominio] Crear `app/domain/chofer.py`: dataclass `Chofer` con `nombre_completo`, `telefono`, `activo=True`, `saldo_a_favor=0.0`, `id`/`creado_en`/`actualizado_en`; `__post_init__` que normaliza (colapsa espacios) y valida levantando `ReglaNegocioError`; funciones puras `normalizar_nombre()` y `contar_digitos()`; métodos `crear()`, `actualizar()` (valida primero, muta después, sin tocar `activo`/`saldo_a_favor`) y `desactivar()`. Cubre FR-002, FR-003, FR-004, FR-005, FR-006, FR-010, FR-012, FR-013

## Eje 2 — Infraestructura

- [x] **T03** [Infraestructura] Completar `app/infrastructure/models/chofer.py`: `nombre_completo VARCHAR(120) NOT NULL`, `telefono VARCHAR(20) NOT NULL`, `saldo_a_favor NUMERIC(12,2) NOT NULL server_default 0` (que para el dominio es `float`), y el índice `ix_choferes_activo_nombre (activo, nombre_completo)`. Cubre FR-001, FR-013
- [x] **T04** [Infraestructura] Generar y **revisar a mano** la migración Alembic `alembic/versions/0003_completar_choferes.py`: agregar las tres columnas **nullable → backfill → `NOT NULL`** (por las filas de H4), crear el índice y el `downgrade()` que las quita. Cubre FR-016
- [x] **T05** [Infraestructura] Crear `app/infrastructure/repositories/chofer_repo.py`: `ChoferRepo(ChoferRepository)` con mappers `a_dominio()`/`a_orm()`, `crear`, `obtener_por_id`, `listar` (filtra `activo=True`, busca por nombre con `ILIKE`, orden estable por `id`), `contar`, `actualizar` (fuerza `actualizado_en = func.now()`, lección H1/T047) y `desactivar` con `UPDATE activo=false` (baja lógica, sin `DELETE` físico). Implementa también `existe_activo(id)`, que es el puerto `ConsultaChofer` de H4. Cubre FR-007, FR-013, FR-014
- [x] **T06** [Infraestructura] Reemplazar el stub `ConsultaChoferVacio` por `ChoferRepo` en `get_consulta_chofer` de `app/core/dependencias.py`, y eliminar la clase `ConsultaChoferVacio` de `app/infrastructure/repositories/consulta_stub.py`. Así H4 valida de verdad el chofer habitual activo
- [x] **T07** [Infraestructura] Correr `alembic upgrade head` (y probar `downgrade -1` + `upgrade head`) y verificar que el SQL generado agrega las columnas, el backfill, el `NOT NULL` y el índice

## Eje 3 — Aplicación

- [x] **T08** [Aplicación] [P] Crear `app/application/choferes/puertos.py`: `Protocol ChoferRepository` con `crear`, `obtener_por_id`, `listar`, `contar`, `actualizar`, `desactivar` — sin `existe_*` (no hay unicidad que validar, DP-02/DP-04)
- [x] **T09** [Aplicación] Crear `app/application/choferes/gestor_choferes.py`: `GestorChoferes` que recibe el puerto por constructor, con `registrar`, `obtener`, `listar`, `actualizar`, `eliminar` — toda la lógica de negocio de la historia. Cubre FR-001…FR-015

## Eje 4 — Presentación

- [x] **T10** [Presentación] [P] Crear `app/api/schemas/chofer.py`: `ChoferCreate` (nombre 3–120, teléfono 7–20 dígitos, `extra="forbid"`), `ChoferUpdate` (mismos campos, DD-5), `ChoferRead` (con `id`, `activo`, `saldo_a_favor`, fechas y `de_chofer()`) y `ChoferListado(Pagina[ChoferRead])`. Cubre FR-002, FR-004, FR-006, FR-011, FR-012
- [x] **T11** [Presentación] Agregar en `app/core/dependencias.py` `get_repo_choferes` y `get_gestor_choferes` (único punto donde se arma el gestor), y registrar `choferes_router` en `app/main.py`
- [x] **T12** [Presentación] Crear `app/api/choferes.py` con las 5 rutas, cada handler delegando en un único método del gestor, con `summary`/`responses` documentados y `dependencies=[Depends(require_rol(ROL_ADMIN))]` en las escrituras (DD-3):
  - `POST /api/choferes` → `201` (admin)
  - `GET /api/choferes` → `200` página de activos (admin, chofer)
  - `GET /api/choferes/{id}` → `200` detalle (admin, chofer)
  - `PUT /api/choferes/{id}` → `200` actualizado (admin)
  - `DELETE /api/choferes/{id}` → `204` baja lógica (admin)
  Cubre FR-018
- [x] **T13** [Presentación] Verificar en `/docs` (OpenAPI) que los 5 endpoints aparecen documentados con sus códigos de éxito y error

## Eje 5 — Tests

- [x] **T14** [Tests] [P] Crear `tests/unit/application/choferes/fakes.py`: `FakeChoferRepo` en memoria (listado filtra inactivos y busca por nombre), sin PostgreSQL
- [x] **T15** [Tests] Crear `tests/unit/test_h3_choferes.py` **primero, debe fallar** — dos tests de alto nivel:
  - `test_h3_dominio`: normalización del nombre, longitudes 3–120, teléfono 7–20 dígitos, `saldo_a_favor=0.0`, `actualizar()` conserva id/creado_en/saldo y no deja el chofer a medias, `desactivar()`
  - `test_h3_gestor_choferes`: alta con valores por defecto, listado excluye inactivos y filtra insensible a mayúsculas, detalle inexistente/inactivo → `ChoferNoEncontrado`, actualizar conserva id y saldo, baja lógica, baja de inexistente
  Cubre FR-002…FR-015 (capa de Aplicación, prioridad AGENTS.md §8)
- [x] **T16** [Tests] Correr `pytest tests/unit` y dejarlo en verde sin levantar PostgreSQL
- [x] **T17** [Tests] Crear `tests/integration/api/test_choferes_api.py` **primero, debe fallar** — contra PostgreSQL real:
  - `test_choferes_api_ciclo_completo_admin`: ciclo CRUD completo, persistencia verificada por SQL directo, y tras la baja la fila sigue con `activo=false` (DD-1)
  - `test_choferes_api_seguridad_y_reglas`: `403` para `chofer` en escrituras, `200` en lecturas, `422` por datos inválidos y por mandar `activo`/`saldo_a_favor`, `404` en inexistentes
  Cubre FR-001, FR-007, FR-009, FR-013, FR-014, FR-016, FR-017, FR-019
- [x] **T18** [Tests] Correr `pytest tests/unit tests/integration` y dejarlo en verde (integración requiere PostgreSQL)

## Eje 6 — Cierre

- [x] **T19** [Cierre] Correr `ruff check` + `ruff format` sobre `backend/` y verificar que H4 sigue verde tras reemplazar el stub (`ConsultaChoferVacio`)
- [ ] **T20** [Cierre] Verificar el DoD (AGENTS.md §9): persistencia real con `docker compose up`, actualizar la spec/AGENTS.md si cambió algo, y abrir el PR a `main` — *pendiente: el entorno no tiene Docker ni PostgreSQL; el PR lo abre el equipo*

---

## Dependencias entre tareas

```text
T01 ─► T02 ─► T03 ─► T04 ─► T05 ─► T06 ─► T07 ─┐
                                               ├─► T08 ─► T09 ─► T11 ─► T12 ─► T13
T14 ─► T15 ─► T16 ─────────────────────────────┘         (T10 [P] con T15/T17)
T17 ─► T18 ─► T19 ─► T20
```

- **Dominio antes que todo**: `T01→T02` son la base; nada de infraestructura ni aplicación importa
  la entidad si `chofer.py` no existe.
- **Infraestructura (T03–T07) es bloqueante para Aplicación y Presentación**: el repo implementa el
  puerto, así que va antes de cablear el gestor.
- **Presentación (T10–T13) después de Aplicación (T08–T09)**: los handlers solo delegan.
- **Tests primero donde corresponde**: T15 y T17 se escriben antes que el código que prueban
  (TDD), y deben fallar primero.
- **`[P]` real**: T08/T10/T14 (archivos independientes entre sí).

## Trazabilidad tarea → capa → FR

| Tarea | Capa | Archivos | FR |
|---|---|---|---|
| T01–T02 | Dominio | `app/domain/{errores,chofer}.py` | FR-002…FR-006, FR-010, FR-012, FR-013, FR-015 |
| T03–T07 | Infraestructura | `models/chofer.py`, `repositories/chofer_repo.py`, `consulta_stub.py`, `alembic/versions/0003_*` | FR-001, FR-007, FR-013, FR-014, FR-016 |
| T08–T09 | Aplicación | `app/application/choferes/{puertos,gestor_choferes}.py` | FR-001…FR-015 |
| T10–T13 | Presentación | `app/api/choferes.py`, `app/api/schemas/chofer.py`, `core/dependencias.py`, `main.py` | FR-011, FR-012, FR-018 |
| T14–T18 | Tests | `tests/unit/…`, `tests/integration/api/…` | todos (SC-001) |
| T19–T20 | Cierre | — | DoD §9 |

---

## Estrategia de entrega

1. **MVP real = Dominio + Infraestructura + Aplicación + Presentación de alta y consulta
   (T01–T13)**: el administrador ya puede cargar choferes y buscarlos entre los activos.
2. Modificación (PUT) y baja lógica (DELETE) quedan incluidas en T12.
3. Reemplazar el stub de `ConsultaChofer` (T06) deja el MVP de H4 funcionando de verdad al cerrar H3.

## Notas

- Los tests son obligatorios por AGENTS.md §8, no opcionales.
- Revisar la lección de H1/T047: `onupdate` no refresca `actualizado_en` si el UPDATE no cambia
  nada; forzarlo a mano en `ChoferRepo.actualizar` (T05).
- La migración (T04) toca una tabla con filas de H4: revisarla a mano (plan §6).
- **DP-05 (origen y signo de `saldo_a_favor`) sigue sin confirmar con el cliente.** No bloquea H3,
  pero hay que cerrarlo antes de H10/H11, porque define la operatoria económica del saldo.
