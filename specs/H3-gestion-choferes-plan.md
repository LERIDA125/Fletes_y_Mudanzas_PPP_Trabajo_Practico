# Implementation Plan: H3 — Gestión de Choferes

**Spec**: `specs/H3-gestion-choferes.md`

**Branch**: `feature/CRUD_choferes`

**Estado**: plan de implementación (previo a `/tasks`).

## 1. Qué construye esta historia

El CRUD de choferes dentro del monolito modular en capas (AGENTS.md §2). No se agrega ninguna
capa nueva: se sigue el mismo camino que H1 (clientes) y H4 (vehículos/tipos de vehículo):

```
Presentación (app/api/choferes.py + schemas/chofer.py)
        │  valida rol, arma el request
        ▼
Aplicación (app/application/choferes/gestor_choferes.py)
        │  toda la regla de negocio
        ▼
Dominio (app/domain/chofer.py)
        │  invariantes del chofer (dataclass puro)
        ▼
Infraestructura (models/chofer.py + repositories/chofer_repo.py)
           único punto de acceso a PostgreSQL
```

## 2. Punto de partida: qué ya existe

H4 creó la tabla mínima `choferes` (`ChoferORM` con `id`, `activo`, `creado_en`, `actualizado_en`)
solo para sostener el FK `id_chofer_habitual` de vehículos, y un **stub** `ConsultaChoferVacio`
que siempre responde "no existe". Esta historia:

- **Completa la tabla** con `nombre_completo`, `telefono` y `saldo_a_favor` vía migración Alembic
  (`0003_completar_choferes.py`).
- **Reemplaza el stub** `ConsultaChoferVacio` por una implementación real contra `choferes`, para
  que H4 (validar chofer habitual activo) empiece a funcionar de verdad. Es el único cambio que
  toca código de H4 y se hace **solo en la inyección** (`app/core/dependencias.py`, `get_consulta_chofer`),
  sin tocar `app/application/vehiculos/` ni `app/api/vehiculos.py`. La clase `ConsultaChoferVacio`
  se elimina.

## 3. Capas y archivos que toca

### 3.1 Dominio — `app/domain/`

- **`chofer.py` (nuevo)**: dataclass `Chofer` (Python puro, sin SQLAlchemy ni FastAPI) con los
  campos y valores por defecto:

  | Campo | Tipo | Defecto | Origen | Regla |
  |---|---|---|---|---|
  | `id` | `int \| None` | `None` | sistema | PK, asignada al persistir |
  | `nombre_completo` | `str` | — | usuario | 3–120 chars, espacios colapsados |
  | `telefono` | `str` | — | usuario | 7–20 dígitos (DD-4) |
  | `activo` | `bool` | `True` | sistema | baja lógica (DD-1) |
  | `saldo_a_favor` | `float` | `0.0` | sistema | saldo a favor del chofer (DP-05) |
  | `creado_en` | `datetime \| None` | `None` | sistema | auditoría |
  | `actualizado_en` | `datetime \| None` | `None` | sistema | auditoría |

  - `__post_init__` normaliza (colapsa espacios) y valida, levantando `ReglaNegocioError`.
  - Función pura `normalizar_nombre(texto)` (colapsa espacios) para el texto de búsqueda/guardado.
  - `contar_digitos(texto)` para la validación del teléfono (mismo criterio que clientes, DD-4).
  - Métodos `crear(nombre_completo, telefono)`, `actualizar(*, nombre_completo, telefono)` y
    `desactivar()`. `actualizar()` sigue el patrón de `vehiculo.py` de “validar primero, mutar
    después”, y **no toca** `activo` ni `saldo_a_favor` (FR-012).
- **`errores.py` (modificado)**: `ChoferNoEncontrado(RecursoNoEncontrado)`. Es el único error
  nuevo: el nombre no es único (DP-02), el teléfono tampoco, y la baja es lógica sin dependencias
  bloqueantes (a diferencia de H1/H4, no hay `ConflictoOperacion` en esta historia).

### 3.2 Aplicación — `app/application/choferes/`

- **`puertos.py` (nuevo)**: `Protocol ChoferRepository` con `crear`, `obtener_por_id`, `listar`
  (solo activos, `busqueda` + paginación), `contar`, `actualizar`, `desactivar`. Igual forma que
  `VehiculoRepository` pero sin `existe_*` (no hay unicidad que validar).
- **`gestor_choferes.py` (nuevo)**: `GestorChoferes` con `registrar`, `obtener`, `listar`,
  `actualizar`, `eliminar`. Toda la lógica de FR-002…FR-015. Nada de SQL ni de HTTP acá.

### 3.3 Infraestructura — `app/infrastructure/`

- **`models/chofer.py` (modificado)**: tabla `choferes` mapeada con SQLAlchemy 2.0 (`Mapped` /
  `mapped_column`), completando la tabla mínima que dejó H4:

  | Columna | Tipo SQL | Nulabilidad | Defecto BD | Notas |
  |---|---|---|---|---|
  | `id` | `INTEGER` identity | PK | autoincremental | `Identity()` |
  | `nombre_completo` | `VARCHAR(120)` | `NOT NULL` | — | agregada por H3 |
  | `telefono` | `VARCHAR(20)` | `NOT NULL` | — | agregada por H3 |
  | `activo` | `BOOLEAN` | `NOT NULL` | `true` | ya existía (H4) |
  | `saldo_a_favor` | `NUMERIC(12,2)` | `NOT NULL` | `0` | agregada por H3 |
  | `creado_en` | `TIMESTAMPTZ` | `NOT NULL` | `now()` | auditoría (H4) |
  | `actualizado_en` | `TIMESTAMPTZ` | `NOT NULL` | `now()` | auditoría, con `onupdate` (H4) |

  Índice compuesto `ix_choferes_activo_nombre (activo, nombre_completo)` para el filtro del listado.
  Se eligió `NUMERIC(12,2)` (decimal exacto) sobre `float` para el saldo, por ser un dato
  económico; el dominio lo expone igual como `float`.
- **`repositories/chofer_repo.py` (nuevo)**: `ChoferRepo` con los mappers `a_dominio`/`a_orm`,
  `crear`, `obtener_por_id`, `listar` (filtrando `activo=True` y buscando por nombre con `ILIKE`),
  `contar`, `actualizar` (fuerza `actualizado_en = func.now()`, lección de H1/T047: `onupdate` no
  dispara si el `UPDATE` no cambia nada) y `desactivar` con `UPDATE ... activo=False` (baja lógica,
  DD-1, sin `DELETE` físico). Además implementa `existe_activo(id)`, que es el puerto
  `ConsultaChofer` de H4.
- **`repositories/consulta_stub.py` (modificado)**: se **elimina** `ConsultaChoferVacio`, porque la
  consulta de choferes ya tiene implementación real (`ChoferRepo.existe_activo`). Queda solo el
  stub de servicios (`ConsultaServiciosVehiculoVacio`, hasta H6).
- **`alembic/versions/0003_completar_choferes.py` (nuevo)**: migración que agrega las tres columnas
  a `choferes`. Como la tabla puede tener filas de H4 (sin nombre ni teléfono), agrega las columnas
  **nullable → backfill → `NOT NULL`**, crea el índice y define el `downgrade()` que las quita.

### 3.4 Presentación — `app/api/`

- **`schemas/chofer.py` (nuevo)**: `ChoferCreate` / `ChoferUpdate` (nombre 3–120, teléfono 7–20
  dígitos; `extra="forbid"` para que el usuario no pueda mandar `saldo_a_favor` ni `activo`,
  FR-006/FR-012), `ChoferRead` (con `id`, `activo`, `saldo_a_favor`, fechas y `de_chofer()`) y
  `ChoferListado(Pagina[ChoferRead])`.
- **`choferes.py` (nuevo)**: router `/api/choferes` con las 5 rutas, `dependencies=[Depends(require_rol(ROL_ADMIN))]`
  en las escrituras y lectura abierta a `chofer` (DD-3). Los handlers solo delegan en un único
  método del gestor; acá no hay reglas de negocio.
- **`app/core/dependencias.py` (modificado)**: `get_repo_choferes`, `get_gestor_choferes`, y el
  reemplazo real de `get_consulta_chofer` (sección 2).
- **`app/main.py` (modificado)**: `include_router(choferes_router)`.

**Endpoints** (roles y códigos):

| Método | Ruta | Rol | Éxito | Errores | Caso de uso |
|---|---|---|---|---|---|
| `POST` | `/api/choferes` | admin | `201` con el chofer | `403`, `422` | `GestorChoferes.registrar` |
| `GET` | `/api/choferes` | admin, chofer | `200` página de activos | `403` | `GestorChoferes.listar` |
| `GET` | `/api/choferes/{id}` | admin, chofer | `200` detalle | `404` | `GestorChoferes.obtener` |
| `PUT` | `/api/choferes/{id}` | admin | `200` actualizado | `403`, `404`, `422` | `GestorChoferes.actualizar` |
| `DELETE` | `/api/choferes/{id}` | admin | `204` sin cuerpo (baja lógica) | `403`, `404` | `GestorChoferes.eliminar` |

**¿Por qué `PUT` y no `PATCH`?** El body de edición repite los mismos campos obligatorios que el
alta (DD-5): así el dominio siempre valida un chofer entero y no queda un registro a medio
modificar por un campo que el cliente olvidó mandar. Un `PATCH` parcial obligaría a manejar
“campos ausentes” en la capa de negocio, que es justo lo que DD-5 evita.

### 3.5 Tests

Prioridad según AGENTS.md §8: **primero la capa de Aplicación con el repositorio mockeado**. El
repo comprime los tests de una historia en pocos tests de alto nivel (así están H1 y H4), en vez
de un archivo por capa:

- **Unit (dominio + aplicación)**: `tests/unit/test_h3_choferes.py` con dos tests de alto nivel:
  - `test_h3_dominio` — normalización del nombre, longitudes 3–120, teléfono 7–20 dígitos,
    `saldo_a_favor` por defecto `0.0`, `actualizar()` conserva id/creado_en/saldo y no deja el
    chofer a medias, `desactivar()`.
  - `test_h3_gestor_choferes` — alta con valores por defecto, listado filtra inactivos y búsqueda
    insensible a mayúsculas, detalle inexistente/inactivo → `ChoferNoEncontrado`, actualizar
    conserva id y saldo, baja lógica, baja de inexistente.
  - Doble en memoria: `tests/unit/application/choferes/fakes.py` (`FakeChoferRepo`), sin PostgreSQL.
- **Integración**: `tests/integration/api/test_choferes_api.py` contra PostgreSQL real, comprimido
  en dos tests:
  - `test_choferes_api_ciclo_completo_admin` — ciclo CRUD, persistencia verificada por SQL directo,
    y que tras la baja la fila sigue con `activo=false` (DD-1).
  - `test_choferes_api_seguridad_y_reglas` — `403` para `chofer` en escrituras, `200` en lecturas,
    `422` por datos inválidos y por intentar mandar `activo`/`saldo_a_favor`, `404` en
    inexistentes.

## 4. Decisiones de diseño aplicadas

| Decisión | Cómo se aplica en H3 |
|---|---|
| **DD-1** (baja lógica) | `desactivar()` setea `activo=False`; el listado y el detalle lo esconden; el registro y su saldo quedan intactos (FR-013/FR-014). |
| **DD-3** (rol por puerto) | Las rutas usan `require_rol(ROL_ADMIN)`; no leen el rol directo. Cuando llegue el JWT se cambia solo `get_rol_actual`. |
| **DD-4** (teléfono 7–20 dígitos) | Misma validación que clientes: se cuentan solo los dígitos, se admiten `+`, espacios y guiones. |
| **DD-5** (PUT completo) | `ChoferUpdate` repite los mismos campos obligatorios que `ChoferCreate`. |
| **PK integer identity** | `id` identity, expuesto como `id` en la API (igual que clientes/vehículos). |

## 5. Puntos que el plan NO resuelve solo (van a las DP de la spec)

- **Saldo**: la spec deja `saldo_a_favor` como dato persistido y expuesto; **ninguna** operación de
  esta historia lo mueve (DP-05). El tipo de columna se fijó en `NUMERIC(12,2)` (decimal exacto,
  ver sección 3.3) y el dominio lo expone como `float`; la operación económica que mueve el saldo
  se define en H10/H11, cuando el cliente confirme la regla.
- **Ayudantes/peones**: fuera de alcance (DP-06, AGENTS.md §6).
- **Unicidad del nombre/teléfono**: no se implementa (DP-02/DP-04); los choferes se distinguen por `id`.

## 6. Riesgos y cuidados

- **Migración sobre tabla con datos de H4**: las filas creadas para el FK de vehículos no tienen
  nombre ni teléfono. La migración agrega las columnas **nullable**, backfillea (`'Chofer sin
  nombre'` / `'0000000'` / `0`) y recién después aplica `NOT NULL`. Ese backfill es un supuesto:
  si la base real no tiene filas huérfanas de H4, se puede endurecer la migración. Se revisa a mano
  como en H1/T027.
- **`actualizado_en` con `onupdate`**: forzarlo a mano en el repo (lección de H1/T047).
- **No mezclar capas**: el gate de AGENTS.md §2 se repite al cierre (¿quedó alguna regla en `api/`
  o `infrastructure/`?).

## 7. Trazabilidad spec → plan

| US de la spec | Endpoints | Capas |
|---|---|---|
| US1 Alta | `POST /api/choferes` | dominio + aplicación + infra + api |
| US2 Consulta activos | `GET /api/choferes`, `GET /api/choferes/{id}` | aplicación (filtro activo) + repo + api |
| US3 Modificación | `PUT /api/choferes/{id}` | dominio (`actualizar`) + aplicación + api |
| US4 Baja lógica | `DELETE /api/choferes/{id}` | dominio (`desactivar`) + repo + api |

## 8. Plan de entrega

- **MVP**: US1 + US2 (alta y consulta de activos) — es lo que reemplaza el control de choferes de
  la planilla.
- **Incrementos**: US3 (edición) y US4 (baja lógica), sin romper lo anterior.
- Al cerrar: actualizar `AGENTS.md` §11 si aparece una decisión de fondo nueva, dejar la spec
  estable y completar la checklist del DoD (AGENTS.md §9).

## 9. Mapeo a la arquitectura de monolito modular en capas

Resumen de cómo cada capa de AGENTS.md §2 queda cubierta por H3. Las flechas indican quién depende
de quién: las capas externas conocen a las internas, **nunca al revés**.

```
app/api/choferes.py ──────────────┐
  (Presentación: rol + contrato)  │  Depends(get_gestor_choferes)
                                  ▼
app/application/choferes/ ────────┐
  (Aplicación: casos de uso)      │  importa el modelo de dominio y el puerto
                                  ▼
app/domain/chofer.py ─────────────┐
  (Dominio: invariantes puras)    │  NO conoce SQLAlchemy ni FastAPI
                                  ▼
app/infrastructure/ ──────────────┘
  (repositories/chofer_repo.py + models/chofer.py)
  implementa el puerto del dominio
```

| # | Capa (según el pedido) | Archivos | Responsabilidad | No debe contener |
|---|---|---|---|---|
| 1 | **Dominio** | `app/domain/chofer.py`, `errores.py` | Entidad `Chofer` con `saldo_a_favor: float` y `activo: bool`; validaciones e invariantes; `actualizar`/`desactivar` | Dependencias de framework, SQL, HTTP |
| 2 | **Infraestructura** | `app/infrastructure/models/chofer.py`, `repositories/chofer_repo.py`, `alembic/versions/0003_*.py` | Mapeo SQLAlchemy ↔ PostgreSQL; persistencia; **baja lógica** (`UPDATE activo=false`) | Reglas de negocio |
| 3 | **Aplicación** | `app/application/choferes/{puertos,gestor_choferes}.py` | Casos de uso: `registrar`, `obtener`, `listar`, `actualizar`, `eliminar`; reglas de FR-002…FR-015 | SQL, HTTP, objetos de FastAPI |
| 4 | **Presentación** | `app/api/choferes.py`, `app/api/schemas/chofer.py`, `app/core/dependencias.py`, `app/main.py` | Endpoints POST/GET/PUT/DELETE, validación de rol `admin` (DD-3), esquemas Pydantic, inyección de dependencias | Lógica de negocio |
| 5 | **Testing** | `tests/unit/test_h3_choferes.py`, `tests/unit/application/choferes/fakes.py`, `tests/integration/api/test_choferes_api.py` | Unit de la capa de Aplicación con repo mockeado (prioridad §8) + integración HTTP contra PostgreSQL | — |

**Principio de dependencia**: `api` → `application` → `domain`; `infrastructure` implementa los
puertos que declara `application` y devuelve entidades de `domain`. Un cambio en la fórmula del
saldo o en la baja solo debería tocar `app/application/` y `app/domain/`.
