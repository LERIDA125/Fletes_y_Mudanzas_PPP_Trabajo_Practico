# Tasks: H1 — Gestión de Clientes

**Input**: `specs/H1-gestion-clientes.md` (spec) + `specs/H1-gestion-clientes-plan.md` (plan)

**Prerequisites**: plan, spec (para las historias de usuario)

**Branch**: `feature/H1-gestion-clientes`

**Tests**: incluidos y **obligatorios** — AGENTS.md §8 los exige como prioridad #1 para
`app/application/`. Se escriben antes de la implementación y deben fallar primero.

**Organización**: agrupadas por historia de usuario para que cada una se pueda implementar,
testear y entregar de forma independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: historia de usuario a la que pertenece la tarea
- Las rutas son exactas y relativas a la raíz del repo

**Total**: 62 tareas · 7 fases

---

## Phase 1: Setup (scaffolding)

**Purpose**: crear el proyecto, porque el repo está vacío (no hay `backend/`, `frontend/` ni
`docker-compose.yml`).

- [x] **T001** Crear el árbol de carpetas de `backend/` (`app/{core,api/schemas,application/clientes,domain,infrastructure/{db,models,repositories}}`, `tests/{unit/{domain,application/clientes},integration}`, `alembic/versions`) con sus `__init__.py` vacíos
- [x] **T002** Crear `backend/pyproject.toml`: dependencias (fastapi, uvicorn[standard], sqlalchemy>=2.0, alembic, psycopg[binary], pydantic>=2, pydantic-settings) + dev (pytest, httpx, ruff) + `[tool.pytest.ini_options]` con `testpaths` y `[tool.ruff]` con `line-length = 100`
- [x] **T003** [P] Crear `backend/.env.example` (`DATABASE_URL=postgresql+psycopg://fletes:fletes@localhost:5432/fletes`, `ENVIRONMENT=dev`) y `backend/.gitignore` (`.env`, `__pycache__`, `.pytest_cache`)
- [x] **T004** [P] Crear `app/core/config.py` con `Settings` (pydantic-settings, `DATABASE_URL`, `ENVIRONMENT`) y `get_settings()` cacheado con `@lru_cache`
- [x] **T005** Crear `app/infrastructure/db/base.py` con `Base(DeclarativeBase)`
- [x] **T006** Crear `app/infrastructure/db/session.py`: `engine` con `pool_pre_ping=True`, `SessionLocal`, generador `get_db()` con `close()` garantizado
- [x] **T007** Crear `app/main.py`: instancia FastAPI, CORS, ruta `GET /health`, `include_router` vacío por ahora, sin reglas de negocio
- [x] **T008** [P] Crear `docker-compose.yml` con servicios `postgres:16` (volumen nombrado, healthcheck) y `backend` (build del `Dockerfile`, depende de `condition: service_healthy`)
- [x] **T009** [P] Crear `backend/Dockerfile` (python:3.12-slim, `pip install -e .`)
- [x] **T010** [P] Crear `.github/workflows/ci.yml`: job con Python 3.12 → `ruff check` + `pytest tests/unit`; el job de integration se agrega en T056 con servicio PostgreSQL
- [x] **T011** Crear `tests/conftest.py` con fixtures base compartidas
- [x] **T012** Verificar que `pytest tests/unit` corre sin fallos

**Checkpoint**: proyecto importable, `/health` responde, CI arranca en verde

---

## Phase 2: Foundational (núcleo de dominio, aplicación e infraestructura)

**Purpose**: todo el núcleo de negocio, que es donde AGENTS.md §2 exige que vivan las reglas.

**⚠️ CRITICAL**: ninguna historia de usuario puede empezar hasta cerrar esta fase.

- [x] **T013** Crear `app/domain/errores.py`: `ReglaNegocioError` (base), `ClienteNoEncontrado`, `RazonSocialDuplicada`, `ClienteConHistorial` — sin imports de infra ni de frameworks web
- [x] **T014** [P] Crear `app/application/clientes/puertos.py`: `Protocol`s `ClienteRepository` (`crear`, `obtener_por_id`, `listar`, `actualizar`, `desactivar`, `existe_razon_social`, `contar`) y `ConsultaHistorialCliente.tiene_historial(cliente_id) -> bool`
- [x] **T015** Crear `tests/unit/domain/test_cliente.py` **primero** (debe fallar): normalización de razón social (mayúsculas, acentos, espacios), longitudes 3–120 y 5–250, teléfono de 7–20 dígitos, `tiene_cuenta_corriente` por defecto `false`, `crear()` calcula `razon_social_key`, `actualizar()` conserva `id` y `creado_en`, `desactivar()` setea `activo=False`
- [x] **T016** Crear `app/domain/cliente.py`: dataclass `Cliente` con `__post_init__` validando (levantando `ReglaNegocioError`), funciones puras `normalizar_razon_visual()` y `normalizar_razon_social()`, y métodos `crear()`, `actualizar()`, `desactivar()`
- [x] **T017** Correr `pytest tests/unit/domain` y dejarlo en verde
- [x] **T018** [P] Crear `tests/unit/application/clientes/fakes.py`: `FakeClienteRepo` (en memoria, con unicidad simulada) y `FakeHistorial` (configurable) — sin PostgreSQL
- [x] **T019** Crear `tests/unit/application/clientes/test_gestor_clientes.py` **primero** (debe fallar), cubriendo: registro con cuenta corriente `true`/`false`; razón social duplicada idéntica y con distinta capitalización (FR-004); listado filtra por texto insensible a mayúsculas y excluye inactivos; obtener inexistente → `ClienteNoEncontrado`; actualizar preserva `id`/`creado_en`; actualizar a razón social de otro → `RazonSocialDuplicada` y el original queda intacto; actualizar con campos vacíos → `ReglaNegocioError`; eliminar sin historial desactiva; eliminar con historial → `ClienteConHistorial` **y sin llamar a `desactivar`**; eliminar repetido es idempotente
- [x] **T020** Crear `app/application/clientes/gestor_clientes.py`: clase `GestorClientes` que recibe los puertos por constructor, con `registrar`, `obtener`, `listar`, `actualizar`, `eliminar` — toda la lógica de negocio de FR-004, FR-007, FR-008, FR-010, FR-011, FR-012, FR-014, FR-015
- [x] **T021** Correr `pytest tests/unit` y dejarlo en verde (sin levantar PostgreSQL)
- [x] **T022** Crear `app/infrastructure/models/cliente.py`: `ClienteORM` con `id` identity PK, `razon_social` VARCHAR(120), `razon_social_key` VARCHAR(120) UNIQUE NOT NULL, `telefono` VARCHAR(20), `direccion_habitual` VARCHAR(250), `tiene_cuenta_corriente` BOOLEAN NOT NULL server_default false, `activo` BOOLEAN NOT NULL server_default true, `creado_en`/`actualizado_en` TIMESTAMPTZ con `server_default now()` y `onupdate`
- [x] **T023** [P] Crear `app/infrastructure/models/__init__.py` registrando `ClienteORM` en `Base.metadata` + índice compuesto `(activo, razon_social_key)`
- [x] **T024** Crear `app/infrastructure/repositories/cliente_repo.py`: `ClienteRepo(ClienteRepository)` con `crear`, `obtener_por_id`, `listar` (filtra `activo=True`, busca sobre `razon_social_key`, `order_by` estable por `id`), `actualizar`, `desactivar`, `existe_razon_social`, `contar`; mapper `a_dominio()` / `a_orm()`; y traducción de `IntegrityError` de la restricción UNIQUE a `RazonSocialDuplicada`
- [x] **T025** Crear `app/infrastructure/repositories/historial_cliente_repo.py`: `HistorialClienteRepoVacio` que devuelve `False`, con `TODO(AGENTS)` que apunte a la historia de Servicios (H4) — es lo que hace testeable FR-015 hoy
- [x] **T026** Crear `alembic.ini` y `alembic/env.py` leyendo `Settings`, usando `Base.metadata` y `DATABASE_URL`
- [x] **T027** Generar la migración inicial y **revisarla a mano**: renombrar a `0001_crear_clientes.py`, verificar el `UNIQUE` de `razon_social_key`, los `server_default` y agregar el `downgrade()` con `drop_table("clientes")`
- [x] **T028** Correr `alembic upgrade head`, comprobar la tabla y luego `alembic downgrade -1` + `upgrade head` de nuevo
- [x] **T029** Correr `pytest tests/unit` otra vez para confirmar que la capa de aplicación no se rompió con la infraestructura

**Checkpoint**: dominio + aplicación + repositorio funcionando, `tests/unit` en verde sin base de datos

---

## Phase 3: User Story 1 — Registrar cliente (Priority: P1) 🎯 MVP

**Goal**: el administrador crea clientes y los ve en el listado.
**Independent Test**: `POST /api/clientes` con los 4 datos → `201`, y el cliente aparece en
`GET /api/clientes`.

- [x] **T030** [P] Crear `app/api/schemas/cliente.py`: `ClienteCreate` (razón social 3–120, teléfono 7–20 dígitos tras filtrar no-dígitos, dirección 5–250, `tiene_cuenta_corriente` bool default `false`), `ClienteRead`, `ClienteListado` (`items`, `total`, `page`, `size`)
- [x] **T031** [P] Crear `app/core/dependencias.py`: `get_rol_actual()` **stub** leyendo el header `X-Rol` (default `chofer`, `TODO(AGENTS)` a la historia de auth) y `require_rol("admin")` como `Depends`
- [x] **T032** Crear `app/api/clientes.py` con **solo** la ruta `POST /api/clientes` (admin), `response_model=ClienteRead`, `status_code=201`, `summary` y `responses` documentados; cuerpo delegado a `GestorClientes.registrar()`, sin ninguna regla de negocio
- [x] **T033** Registrar el router de clientes y el handler global de excepciones de dominio (`ClienteNoEncontrado`→404, `RazonSocialDuplicada`/`ClienteConHistorial`→409, `ReglaNegocioError`→422) en `app/main.py`, inyectando `GestorClientes` y los repos
- [x] **T034** Crear `tests/integration/conftest.py`: engine de test, creación/limpieza de schema por sesión, `Settings` de test, `cliente` de `TestClient` y factory de `ClienteCreate`
- [x] **T035** [P] Crear `tests/integration/api/test_clientes_api.py` con los tests de US1: `201` y cuerpo con los 4 datos; `tiene_cuenta_corriente=true` y `false`; `id` y fechas generados por el sistema; `409` por razón social duplicada (idéntica y con distinta capitalización); `422` por cada campo requerido vacío; `403` si el rol es `chofer`
- [x] **T036** Correr `alembic upgrade head` + `pytest tests/integration` y dejarlo en verde
- [x] **T037** Verificar en Swagger (`/docs`) que `POST /api/clientes` está documentada con sus respuestas (FR-019)

**Checkpoint**: US1 funcionando de punta a punta

---

## Phase 4: User Story 2 — Consultar clientes (Priority: P1)

**Goal**: listado con filtro y detalle.
**Independent Test**: cargar 3 clientes, filtrar por texto, abrir un detalle.

- [x] **T038** [P] Agregar a `tests/integration/api/test_clientes_api.py` los tests de US2 **primero** (deben fallar): `GET /api/clientes` devuelve items + `total` con orden estable; filtro `q` insensible a mayúsculas; búsqueda sin resultados devuelve lista vacía con `total=0` (no error); `GET /api/clientes/{id}` devuelve los 4 datos + fechas; id inexistente → `404`; `chofer` puede leer (200)
- [x] **T039** [P] Agregar en `app/api/schemas/cliente.py` el schema `ClienteListado` si no quedó en T030
- [x] **T040** Agregar a `app/api/clientes.py` las rutas `GET /api/clientes` (params `q`, `page` default 1, `size` default 20 con `le=100`) y `GET /api/clientes/{id}`, delegando a `GestorClientes.listar/obtener`
- [x] **T041** Correr `pytest tests/unit tests/integration` y dejarlo en verde
- [x] **T042** Confirmar en Swagger que las dos rutas de lectura están documentadas

**Checkpoint**: US1 + US2 funcionando de forma independiente

---

## Phase 5: User Story 3 — Modificar cliente (Priority: P2)

**Goal**: corregir datos de un cliente existente.
**Independent Test**: cambiar un teléfono y verificar detalle + fecha de modificación.

- [x] **T043** [P] Agregar a `tests/integration/api/test_clientes_api.py` los tests de US3 **primero** (deben fallar): `200` al cambiar teléfono; cambiar `tiene_cuenta_corriente` a `true`; guardar sin cambios conserva `id` y `creado_en` y refresca `actualizado_en`; `409` al poner la razón social de otro cliente y verificar que el original queda intacto (re-consultar); `422` con campos vacíos; `404` con id inexistente y **verificar que no se creó ningún registro**; `403` con rol `chofer`
- [x] **T044** [P] Agregar a `tests/unit/application/clientes/test_gestor_clientes.py` el caso de borde que solo se ve con fake: razón social que al normalizar colisiona consigo misma (no debe rechazarse)
- [x] **T045** Crear `ClienteUpdate` en `app/api/schemas/cliente.py` (mismos 4 campos obligatorios que `ClienteCreate`, DD-5)
- [x] **T046** Agregar a `app/api/clientes.py` la ruta `PUT /api/clientes/{id}` (admin), delegando a `GestorClientes.actualizar`
- [x] **T047** Correr `pytest tests/unit tests/integration` y dejarlo en verde
- [x] **T048** Confirmar en Swagger que `PUT` está documentada con `404` y `409`

**Checkpoint**: US1–US3 funcionales

---

## Phase 6: User Story 4 — Eliminar cliente (Priority: P3)

**Goal**: dar de baja un cliente.
**Independent Test**: dar de baja un cliente sin historial y verificar que desaparece del listado.

- [ ] **T049** [P] Agregar a `tests/unit/application/clientes/test_gestor_clientes.py` el test de FR-015 con `FakeHistorial(tiene=True)`: assert `ClienteConHistorial` y que `FakeClienteRepo.desactivar` **nunca fue llamado**
- [ ] **T050** [P] Agregar a `tests/integration/api/test_clientes_api.py` los tests de US4 **primero** (deben fallar): `204` al dar de baja un cliente sin historial; deja de aparecer en el listado y su detalle da `404`; baja repetida responde `204` sin error; `404` con id inexistente; `403` con rol `chofer`; **test de regresión que sobrescribe la dependencia** con un historial fake para verificar el `409` de FR-015 a nivel HTTP
- [ ] **T051** Agregar a `app/api/clientes.py` la ruta `DELETE /api/clientes/{id}` (admin, `status_code=204`, `response_class=Response`) delegando a `GestorClientes.eliminar`
- [ ] **T052** Correr `pytest tests/unit tests/integration` y dejarlo en verde
- [ ] **T053** Confirmar en Swagger que `DELETE` está documentada

**Checkpoint**: CRUD completo

---

## Phase 7: Polish y Definition of Done

- [ ] **T054** [P] Correr `ruff check` y `ruff format` sobre todo `backend/` y dejar el linter en verde
- [ ] **T055** [P] Levantar `docker compose up` y verificar los 5 endpoints a mano (persistencia real tras reiniciar el servidor, SC-005)
- [ ] **T056** [P] Agregar el job de `pytest tests/integration` con servicio PostgreSQL al CI
- [ ] **T057** Verificar cobertura de los escenarios de aceptación: cada FR-001…FR-020 mapeado a al menos un test (SC-001)
- [ ] **T058** Revisar que ninguna regla de negocio quedó en `app/api/` ni en `app/infrastructure/` (gate de AGENTS.md §2)
- [ ] **T059** [P] Actualizar `AGENTS.md`: DD-1 a DD-4, convención de PK `integer` identity, y nota de que el chequeo de roles es un stub hasta la historia de autenticación
- [ ] **T060** [P] Escribir `specs/H1-gestion-clientes-quickstart.md` con los comandos para levantar el entorno y probar los endpoints
- [ ] **T061** Correr la checklist completa del DoD de AGENTS.md §9
- [ ] **T062** Abrir el PR a `main` con Conventional Commits y pedir revisión cruzada (no autoaprobarse)

---

## Dependencias y orden de ejecución

```text
Phase 1 (Setup) ──► Phase 2 (Foundational) ──► US1 ──► US2 ──► US3 ──► US4 ──► Phase 7
                                        └───────────────────────────┘
                                        (paralelizables con 4 personas, pero
                                         app/api/clientes.py se toca en las 4
                                         fases: no tomar dos US a la vez)
```

- **Fase 2 es bloqueante**: nada de `app/api/` empieza hasta que dominio, aplicación e
  infraestructura están verdes.
- Dentro de cada US: **tests primero (deben fallar) → schema → ruta → correr tests**.
- Dentro de la Fase 2, T015→T016 y T019→T020 son pares de TDD: el test va antes.
- `[P]` real: T003/T004, T008/T009/T010, T014, T018, T023, T030/T031, T038/T039,
  T043/T044/T045, T049/T050, T054–T056, T059/T060.

## Estrategia de entrega

1. **MVP real = Fase 1 + Fase 2 + US1 + US2**: el administrador ya puede cargar clientes y
   buscarlos, que es lo que reemplaza la planilla de Excel. Se puede mergear y hacer tag `v0.1` ahí.
2. US3 y US4 van después como incrementos, sin romper lo anterior.
3. La regla de FR-015 queda implementada y testeada desde la Fase 2 aunque el cableado real
   espere a H4.

## Notas

- Los tests son obligatorios por AGENTS.md §8, no opcionales como en el template genérico.
- El cableado de `historial_cliente_repo.py` no es definitivo: cuando llegue la historia de
  Servicios se cambia **solo la inyección en `app/main.py`**.
- **DP-05 (CUIT/CUIL obligatorio) sigue sin confirmar con el cliente.** No bloquea H1, pero hay
  que cerrarlo antes de arrancar H2, porque define el modelo de datos.
- **`str(URL)` de SQLAlchemy 2.x enmascara la contraseña como `***`.** Por eso `_url_de_test()` en
  `tests/integration/conftest.py` devuelve el objeto `URL` y nunca un `str`: si se convierte a
  texto, `create_engine` recibe `***` como password y todos los tests de integración fallan con
  `password authentication failed`, que es un error muy difícil de ubicar.
- **El fixture `_limpiar_tablas` tiene que commitear.** Sin `commit()`, el `DELETE` queda en la
  transacción que revierte el `close()` de la sesión y los datos de un test se filtran al
  siguiente: los tests que comparten razón social empiezan a fallar con `409` sin motivo aparente.
- **El stub de roles vive en `app/core/dependencias.py`, no en los routers.** `get_gestor_clientes`
  es el único punto donde se arma el gestor de Aplicación, así que los tests la sobreescriben con
  `app.dependency_overrides` (ver T050) sin tocar `app/api/`.
- **`onupdate=func.now()` no refresca `actualizado_en` si el cliente se guarda idéntico.** Cuando
  ningún atributo cambia, SQLAlchemy no emite el `UPDATE` y el `onupdate` de la columna nunca llega
  a evaluarse, así que la fecha de la última modificación se quedaba congelada (rompía FR-020).
  `ClienteRepo.actualizar` marca la columna a mano (`orm.actualizado_en = func.now()`) para forzar
  la escritura. Si se agrega una columna de auditoría con `onupdate`, hay que hacer lo mismo.
- **T044 ya estaba cubierto a medias.** `test_guardar_los_mismos_datos_no_choca_consigo_mismo` cubría
  la autocolisión con un solo cliente cargado; se agregaron los dos casos que faltaban: razón social
  que solo cambia de forma pero no de clave, y autocolisión *con otro cliente cargado* (que es donde
  una comprobación de duplicados sin `excluir_id` se rompería).
