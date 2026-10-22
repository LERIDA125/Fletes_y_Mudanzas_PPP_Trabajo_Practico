# Implementation Plan: H1 — Gestión de Clientes

**Spec**: `specs/001-gestion-clientes/spec.md`

**Branch**: `feature/H1-gestion-clientes`

**Estado**: plan de implementación **retrospectivo**. Documentado el 2026-10-21 por ingeniería
inversa sobre el código ya mergeado (PR #1, merge `764a112`). No describe trabajo pendiente: describe
lo que la historia decidió hacer, cómo quedó implementado, y qué desviaciones del plan original
quedaron registradas en el código.

## 1. Qué construye esta historia

El primer CRUD completo del proyecto y la **historia fundacional** del backend: define la forma en
que se hacen todas las demás historias.

`Cliente` es una entidad con razón social, teléfono, dirección habitual y un indicador de cuenta
corriente. Sobre ella se define:

- **La normalización en dos niveles** (DD-2): el texto que se muestra y el texto con el que se
  compara son dos cosas distintas.
- **La baja lógica** (DD-1): un cliente no se borra, se da de baja.
- **El patrón "validar primero, mutar después"** de la entidad.
- **La estructura de 4 capas + puertos** que el resto de las historias copian.

## 2. Punto de partida: qué ya existe

H1 es la **primera historia del backend**. No había `backend/`, ni `app/`, ni Alembic, ni
dependencias. La tarea T001 ("crear la estructura del proyecto") es parte de esta misma historia.

Lo único preexistente era el `.specify/` de Spec Kit (plantillas) y la documentación del proyecto.
**Todo** el backend nació aquí: `pyproject.toml`, `alembic.ini`, `alembic/`, `app/`, `tests/`.

## 3. Capas y archivos que toca

### 3.1 Dominio — `app/domain/cliente.py` (132 líneas)

**Constantes** (las 6 que se comparten con toda la aplicación):

| Constante | Valor | Regla |
|---|---|---|
| `RAZON_SOCIAL_MIN` / `MAX` | 3 / 120 | FR-006 |
| `DIRECCION_MIN` / `MAX` | 5 / 250 | FR-006 |
| `TELEFONO_DIGITOS_MIN` / `MAX` | 7 / 20 | FR-005 (DD-4) |

**Funciones puras de módulo** (3):

- `normalizar_razon_visual(texto)` → `" ".join(texto.split())`. Colapsa espacios sobrantes y quita
  extremos. **Es lo que se muestra y se guarda.**
- `normalizar_razon_social(texto)` → NFD + filtro de diacríticos + `normalizar_razon_visual` +
  `.lower()`. **Es la clave de comparación.**
- `contar_digitos(texto)` → `sum(c.isdigit() for c in texto)`. Cuenta dígitos Unicode con
  `str.isdigit()`, no con regex `\d`.

**Dataclass `Cliente`** — `@dataclass` **sin** `frozen=True` (la entidad se muta):

| Campo | Tipo | Default |
|---|---|---|
| `id` | `int \| None` | obligatorio (sin default) |
| `razon_social` | `str` | obligatorio |
| `telefono` | `str` | obligatorio |
| `direccion_habitual` | `str` | obligatorio |
| `tiene_cuenta_corriente` | `bool` | obligatorio (sin default) |
| `activo` | `bool` | `True` (DD-1) |
| `creado_en` / `actualizado_en` | `datetime \| None` | `None` (los pone la base) |

**`__post_init__`** normaliza `razon_social`, `telefono` y `direccion_habitual` con
`normalizar_razon_visual` y recién después valida. **Toda instancia de `Cliente` —venga de donde
venga— queda normalizada y validada.** Es la garantía de la que dependen tanto la API como la
migración de H13.

**Métodos**:

- `crear(razon_social, telefono, direccion_habitual, tiene_cuenta_corriente=False)` — fábrica. El
  default `False` de `tiene_cuenta_corriente` es FR-002.
- `razon_social_key` → **property**, calculada en vivo. No es un campo persistido en el dataclass
  (sí lo es en la tabla).
- `actualizar(*, razon_social, telefono, direccion_habitual, tiene_cuenta_corriente)` —
  **keyword-only**. El patrón: construye un `Cliente` **temporal** con los candidatos → ese
  constructor normaliza y valida (lanza `ReglaNegocioError` si algo no da la talla) → recién
  después asigna los 4 atributos a `self`. **El cliente nunca queda a medias.** El `id`, `activo`,
  `creado_en` y `actualizado_en` originales se preservan.
- `desactivar()` → `self.activo = False`. No valida nada: la verificación de historial es de la
  capa de Aplicación. Es idempotente.
- `_validar()` → 4 reglas, todas con `ReglaNegocioError`.

**No existe** en el dominio: `activar()`, `reactivar()`, `es_activo`, `eliminar()`, ni un método de
validación público.

### 3.2 Dominio — `app/domain/errores.py` (106 líneas)

Jerarquía base, que es el contrato de traducción a HTTP de toda la aplicación:

```
Exception
└── ReglaNegocioError              → 422 (catch-all)
    ├── RecursoNoEncontrado        → 404
    │   └── ClienteNoEncontrado    (H1)
    ├── ConflictoOperacion          → 409
    │   ├── RazonSocialDuplicada    (H1)
    │   └── ClienteConHistorial     (H1)
    └── DatoInvalido                → 422
```

| Error | Mensaje | Cuándo |
|---|---|---|
| `ClienteNoEncontrado` | `"No existe un cliente con id {id}"` | id inexistente **o** cliente dado de baja |
| `RazonSocialDuplicada` | `"Ya existe un cliente con la razón social {razon_social!r}"` | violación de unicidad |
| `ClienteConHistorial` | `"El cliente {id} tiene servicios, cotizaciones o rendiciones asociadas y no se puede dar de baja"` | baja con historial |

> Detalle que quedó registrado: `RazonSocialDuplicada` se lanza con la **razón social normalizada**
> desde `GestorClientes._verificar_razon_social_disponible`, pero con la **razón social original**
> desde `ClienteRepo.crear`/`actualizar` (cota del `IntegrityError`). El mensaje al usuario difiere
> según el camino. No es un bug, pero es una inconsistencia de UX que conviene unificar cuando se
> implemente autenticación.

### 3.3 Aplicación — `app/application/clientes/gestor_clientes.py` (91 líneas)

`GestorClientes(repositorio_clientes: ClienteRepository, consulta_historial: ConsultaHistorialCliente)`.

| Método | Qué hace |
|---|---|
| `registrar(*, razon_social, telefono, direccion_habitual, tiene_cuenta_corriente)` | `Cliente.crear(...)` → verifica unicidad → `repo.crear(...)` |
| `obtener(cliente_id)` | Repo; si es `None` **o** `not cliente.activo` → `ClienteNoEncontrado`. **Cliente dado de baja = inexistente** (FR-014/FR-016). |
| `listar(*, busqueda, offset, limit)` | `total = repo.contar(busqueda)`; devuelve `(repo.listar(...), total)` |
| `actualizar(cliente_id, *, ...)` | `obtener()` → verifica unicidad **sobre un `Cliente` temporal** con `excluir_id` (así no choca consigo mismo) → `cliente.actualizar(...)` → `repo.actualizar(...)` |
| `eliminar(cliente_id)` | Repo → si `None` → 404; si ya está inactivo → `return` (idempotencia, sin error); si `tiene_historial` → `ClienteConHistorial`; si no → baja lógica |

El **stub** de historial (`HistorialClienteRepoVacio`, 14 líneas) vive en
`app/infrastructure/repositories/historial_cliente_repo.py` con un `TODO(AGENTS)` explícito: se
reemplaza por la consulta real cuando exista Servicios, cambiando **solo** la inyección en
`app/core/dependencias.py`.

### 3.4 Puertos — `app/application/clientes/puertos.py` (32 líneas)

Dos `Protocol` con `@runtime_checkable`:

- `ClienteRepository` — `crear`, `obtener_por_id`, `listar`, `contar`, `actualizar`, `desactivar`,
  `existe_razon_social(razon_social_key, excluir_id=None)`. Todos devuelven la entidad `Cliente`
  **del dominio**, nunca el ORM.
- `ConsultaHistorialCliente` — `tiene_historial(cliente_id) -> bool`. Docstring: *"Implementación
  real: llega con la historia de Servicios. Ver FR-015."*

### 3.5 Infraestructura — `app/infrastructure/models/cliente.py` (28 líneas)

`ClienteORM(Base)`, `__tablename__ = "clientes"`.

| Columna | Tipo | Nulable | Default | Constraint |
|---|---|---|---|---|
| `id` | `INTEGER` (`Identity()`) | NO | identity | PK |
| `razon_social` | `VARCHAR(120)` | NO | — | — |
| `razon_social_key` | `VARCHAR(120)` | NO | — | **`UNIQUE`** |
| `telefono` | `VARCHAR(20)` | NO | — | — |
| `direccion_habitual` | `VARCHAR(250)` | NO | — | — |
| `tiene_cuenta_corriente` | `BOOLEAN` | NO | `false` | — |
| `activo` | `BOOLEAN` | NO | `true` | — |
| `creado_en` | `TIMESTAMPTZ` | NO | `now()` | — |
| `actualizado_en` | `TIMESTAMPTZ` | NO | `now()` | `onupdate=now()` |

Índice: `ix_clientes_activo_razon_social_key` sobre `(activo, razon_social_key)`.

**El `UNIQUE` de `razon_social_key` es global, no compuesto con `activo`.** Es lo que hace que la
razón social de un cliente dado de baja siga reservada (DD-1 / SC-007).

### 3.6 Infraestructura — `app/infrastructure/repositories/cliente_repo.py` (110 líneas)

`ClienteRepo(db: Session)` — "Único punto de acceso a PostgreSQL para clientes". Mappers de módulo
`a_dominio(orm)` y `a_orm(cliente)`.

| Método | SQL / comportamiento |
|---|---|
| `crear` | `add` → `commit`; en `IntegrityError`: `rollback` + si `"razon_social_key" in str(error.orig)` → `RazonSocialDuplicada(razon_social)`; si no, re-lanza. `refresh` + `a_dominio`. |
| `obtener_por_id` | `db.get(ClienteORM, id)`. **No filtra por `activo`** (el filtro lo hace el gestor). |
| `listar` | `_consulta_filtrada(...).order_by(id).offset(...).limit(...)` |
| `contar` | `with_only_columns(func.count())` → `scalar(...) or 0` |
| `actualizar` | `get` → asigna los 5 campos → **`orm.actualizado_en = func.now()` forzado a mano** → `commit` con el mismo manejo de `IntegrityError` → `refresh` + `a_dominio` |
| `desactivar` | `update(ClienteORM).where(id == ...).values(activo=False)` + `commit` |
| `existe_razon_social(key, excluir_id=None)` | `select(id).where(razon_social_key == key)` [+ `id != excluir_id`] → `scalar(consulta.limit(1)) is not None`. **No filtra por `activo`** → la razón social de un cliente dado de baja sigue ocupada. |
| `_consulta_filtrada(busqueda)` (privado) | `where(activo IS true)` + si hay búsqueda: `where(razon_social_key.contains(normalizar_razon_social(busqueda)))` |

**SQL compilado (dialecto PostgreSQL, verificado):**

```sql
-- listar
SELECT clientes.id, clientes.razon_social, ... FROM clientes
WHERE clientes.activo IS true
  AND (clientes.razon_social_key LIKE '%%' || :razon_social_key_1 || '%%')
ORDER BY clientes.id LIMIT :limit OFFSET :offset

-- desactivar
UPDATE clientes SET activo=:activo, actualizado_en=now() WHERE clientes.id = :id_1
```

**Aclaración importante sobre la búsqueda**: **NO usa `ILIKE`**. Usa `ColumnOperators.contains()`, que
compila a `LIKE '%%' || :param || '%%'`. La insensibilidad a mayúsculas y acentos **no viene del
`LIKE`**: viene de que **ambos lados están normalizados** (la columna está en minúsculas sin acentos
y el término pasa por `normalizar_razon_social`). Efecto secundario: `contains()` **no escapa** `%`
ni `_`, así que un término de búsqueda con esos caracteres actúa como comodín.

**`actualizado_en` — la lección H1/T047.** `cliente_repo.py:79-83`:

```python
# FR-020: guardar tiene que refrescar la fecha de última modificación aunque el cliente se
# guarde idéntico. El `onupdate` de la columna no alcanza para eso, porque si ningún
# atributo cambió SQLAlchemy no emite el UPDATE y el `onupdate` nunca llega a evaluarse;
# marcar la columna como modificada a mano es lo que fuerza la escritura.
orm.actualizado_en = func.now()
```

El `UPDATE` de `desactivar` **sí** dispara el `onupdate` (es un UPDATE Core explícito, no un flush
de ORM) — se ve en el SQL compilado.

### 3.7 Presentación — `app/api/clientes.py` (192 líneas)

`APIRouter(prefix="/api/clientes", tags=["clientes"])`. `TAMANO_DE_PAGINA_POR_DEFECTO = 20`,
`TAMANO_DE_PAGINA_MAXIMO = 100`.

| # | Método + ruta | Rol | Éxito | Errores |
|---|---|---|---|---|
| 1 | `POST /api/clientes` | **admin** | 201 | 403, 409, 422 |
| 2 | `GET /api/clientes` | cualquiera | 200 | 422 |
| 3 | `GET /api/clientes/{id}` | cualquiera | 200 | 404 |
| 4 | `PUT /api/clientes/{id}` | **admin** | 200 | 403, 404, 409, 422 |
| 5 | `DELETE /api/clientes/{id}` | **admin** | 204 (sin body) | 403, 404, 409 |

`listar_clientes` traduce `page`/`size` a `offset=(page-1)*size`, `limit=size` y devuelve
`ClienteListado(items=[...], total=total, page=page, size=size)`. `eliminar_cliente` devuelve
`Response(status_code=204)`.

**Traducción de errores**: vive en `app/main.py` (4 exception handlers), **no** en el router.
`ReglaNegocioError` → 422, `DatoInvalido` → 422, `RecursoNoEncontrado` → 404,
`ConflictoOperacion` → 409. Cuerpo: `{"detail": str(error)}`.

**Permisos (FR-018 / DP-03)**: el rol se lee del header `X-Rol` (stub). **Si no viene header, el rol
por defecto es `chofer`** → sin header, POST/PUT/DELETE devuelven 403.

### 3.8 Presentación — `app/api/schemas/cliente.py` (108 líneas)

| Schema | Base | Notas |
|---|---|---|
| `ClienteCreate` | `BaseModel` | `extra="forbid"`. `razon_social` (3–120), `telefono` (sin min/max: el conteo es de dígitos), `direccion_habitual` (5–250), `tiene_cuenta_corriente` (default `False`). |
| `ClienteUpdate` | `ClienteCreate` | **No redefine nada.** Hereda los 4 campos obligatorios y `extra="forbid"`. Es DD-5: la edición es un `PUT` completo, no un `PATCH`. |
| `ClienteRead` | `BaseModel` | `from_attributes=True`, **sin** `extra="forbid"`. 8 campos + `de_cliente(cliente)`classmethod. |
| `ClienteListado` | `Pagina[ClienteRead]` | Genérica de `app/api/schemas/comun.py`. |

Validador `ClienteCreate._normalizar_espacios` (`mode="before"`) aplica `normalizar_razon_visual` a
los 3 textos: colapsa espacios **antes** de medir, así un texto de solo espacios se rechaza.

Validador `ClienteCreate._validar_digitos_del_telefono` cuenta dígitos y lanza `ValueError` → 422.

### 3.9 Presentación — `app/core/dependencias.py` (184 líneas)

Bloque `# ── Clientes (H1) ──`:

- `get_repo_clientes(db)` → `ClienteRepo(db)`
- `get_historial_clientes()` → `HistorialClienteRepoVacio()` (stub con `TODO(AGENTS)`)
- `get_gestor_clientes(repositorio_clientes, consulta_historial)` → `GestorClientes(...)`

**Único punto donde se arma el gestor.** Los tests de integración la sobreescriben con
`app.dependency_overrides`.

Compartidos: `HEADER_ROL = "X-Rol"`, `ROL_ADMIN = "admin"`, `ROL_CHOFER = "chofer"`,
`get_rol_actual(x_rol)` (stub TODO(AGENTS): no decodifica JWT) y `require_rol(rol_requerido)` →
`HTTPException(403, detail=f"Se requiere el rol {rol_requerido!r} para esta operación")`.

### 3.10 Migración — `alembic/versions/0001_crear_clientes.py` (53 líneas)

`revision = "0001"`, `down_revision = None`. `upgrade()` crea la tabla con las 9 columnas y el índice
`ix_clientes_activo_razon_social_key`; `downgrade()` **sí existe** (borra el índice y la tabla).

**Es una migración manual, no autogenerada**: el estilo con `sa.Column(...)` posicional y
`server_default=sa.text("now()")` está escrito a mano.

`sa.Identity(always=False)` → `GENERATED BY DEFAULT AS IDENTITY` (permite insertar IDs explícitos).

**La migración no replica el `onupdate=func.now()`** del modelo ORM — `onupdate` es comportamiento de
SQLAlchemy, no de la columna. Por eso el repo tiene que forzar `actualizado_en` a mano.

### 3.11 Tests

| Archivo | Contenido |
|---|---|
| `tests/unit/test_h1_clientes.py` | **188 líneas, 2 tests**: `test_h1_dominio`, `test_h1_gestor_clientes` |
| `tests/unit/application/clientes/fakes.py` | **79 líneas**: `ClienteYaExiste`, `FakeClienteRepo`, `FakeHistorial` |
| `tests/integration/api/test_clientes_api.py` | **151 líneas, 2 tests**: `test_clientes_api_ciclo_completo_admin`, `test_clientes_api_seguridad_y_errores` |
| `tests/integration/conftest.py` | **156 líneas**: fixtures + `HistorialSimulado` |

**Total: 4 funciones de test para toda la historia.** El docstring del archivo lo dice explícito:
*"Comprimido exactamente en 2 tests de alto nivel"* / *"Comprimido en exactamente 2 tests
integrales"*.

**El test de integración verifica DD-2 contra PostgreSQL real**:

```python
SELECT activo, razon_social_key FROM clientes WHERE id = :id
# fila["razon_social_key"] == "distribuidora del sur s.a."
```

y que la baja **deja la fila en la base** con `activo = False`.

## 4. Decisiones de diseño aplicadas

| Decisión | Cómo se aplica en H1 |
|---|---|
| **DD-1** (baja lógica) | `activo` + `desactivar()`. El `UNIQUE` de `razon_social_key` es global → la razón social sigue reservada. El gestor filtra por `activo` en listados y trata un cliente inactivo como inexistente en el detalle. |
| **DD-2** (dato visual + clave normalizada) | `razon_social` (lo que se muestra) + `razon_social_key` (columna `UNIQUE` + índice). Dos funciones: `normalizar_razon_visual` y `normalizar_razon_social`. |
| **DD-3** (permisos por puerto) | `require_rol` en `app/core/dependencias.py`, las rutas declaran `dependencies=[...]` y no tocan el rol. |
| **DD-4** (teléfono sin formato único) | Se guarda texto; solo se valida el **conteo de dígitos** (7–20), no el formato. `+`, espacios y guiones son libres. |
| **DD-5** (`PUT` completo) | `ClienteUpdate(ClienteCreate)` no redefine campos: hereda los 4 obligatorios y el `extra="forbid"`. |
| **Principio II** (capas y puertos) | 4 capas + `Protocol` en Aplicación + repositorio como único acceso a PostgreSQL. |
| **Principio III** (contrato de API) | `Pagina[T]` genérica, `ClienteRead` con `from_attributes`, `de_cliente()`classmethod. |

## 5. Puntos que el plan NO resuelve solo

- **FR-015 (baja con historial) nunca bloquea en producción**: `HistorialClienteRepoVacio.tiene_historial`
  devuelve siempre `False`. La regla está implementada y testeada en el gestor; lo que falta es el
  **dato**. Se resuelve cambiando solo la inyección en `dependencias.py` cuando llegue Servicios.
- **La autenticación es un stub**: `X-Rol` en vez de JWT. Sin header, el rol por defecto es `chofer`.
- **`tiene_cuenta_corriente` es un `bool` sin semántica**: no hay tabla de cuenta corriente todavía
  (llega con Pagos/Cuenta Corriente). H13 además fuerza el valor a `False` (DP-06) porque el Excel
  histórico no tiene ese dato estructurado.
- **El teléfono no tiene política de normalización**: se acepta cualquier formato con 7–20 dígitos.
  La detección de prefijo de país de H13 es un supuesto, no una regla.
- **No hay `frontend/`**: H1 es backend puro. El contrato OpenAPI es la primera aproximación al
  contrato de frontend.

## 6. Riesgos y cuidados — y desviaciones registradas

Verificados contra el código en la revisión retrospectiva del 2026-10-21:

1. **FR-020 no tiene test.** Ningún test asserta que `actualizado_en` cambie tras un `PUT`, ni que
   se refresque al guardar datos idénticos. El comentario `# FR-020` en `cliente_repo.py:79` es la
   única huella. Es la regla más sutil de la historia y la única sin cobertura.
2. **La rama de `IntegrityError` del repositorio no tiene cobertura.** `FakeClienteRepo` lanza
   `ClienteYaExiste` (una `Exception` propia), no `RazonSocialDuplicada`. La rama
   `if "razon_social_key" in str(error.orig)` **nunca se ejecuta en los tests**: el fake_prev del
   repositorio real solo se ejercita a través de la API de integración, y ahí la pre-verificación
   del gestor ya cortó antes.
3. **`ClienteRead.activo` no se asserta en ningún test**, pese a ser el campo que implementa DD-1.
4. **`Pagina.pages` no se testea**, y `total == 0` con filtro sin coincidencias tampoco.
5. **No hay test del `POST` sin `tiene_cuenta_corriente`**: el default `False` del schema no está
   cubierto.
6. **`tests/unit/domain/` está vacío** (solo `__init__.py`): los tests de dominio viven dentro de
   `test_h1_clientes.py`. La compresión de suites (commit `602d218`) dejó los directorios de tests
   con la estructura de la arquitectura original pero sin archivos `test_*.py`.
7. **`ENVIRONMENT` no se usa en ningún lado** del código. Es un setting declarado y muerto.
8. **`repo_test` y `datos_cliente`** están definidos en `tests/integration/conftest.py` pero **no los
   usa** ningún test.
9. **El mensaje de `RazonSocialDuplicada` difiere según el camino** (razón social normalizada vs
   original). Inconsistencia de UX documentada en §3.2.
10. **`contains()` no escapa `%` ni `_`**: la búsqueda de clientes interpreta esos caracteres como
    comodines. No es un problema de seguridad (es `LIKE` con parámetro, no concatenación), pero sí
    de exactitud de la búsqueda.
11. **La spec de H1 no tenía `plan.md` ni `tasks.md`**, a diferencia de H3. El plan de esta historia
    es este documento retrospectivo.

## 7. Trazabilidad spec → plan → código

| Capa | Archivos | Responsabilidad | No debe contener |
|---|---|---|---|
| **1. Presentación** | `app/api/clientes.py`, `app/api/schemas/cliente.py`, `app/api/schemas/comun.py` | Routing, validación de forma, traducción de errores a HTTP. | Reglas de negocio |
| **2. Aplicación** | `app/application/clientes/gestor_clientes.py`, `app/application/clientes/puertos.py` | Casos de uso: alta, baja lógica, unicidad, filtro de historial. | SQL, ORM, HTTP |
| **3. Dominio** | `app/domain/cliente.py`, `app/domain/errores.py` | Invariantes de `Cliente`, normalización, jerarquía de errores. | Persistencia, HTTP |
| **4. Infraestructura** | `app/infrastructure/models/cliente.py`, `app/infrastructure/repositories/cliente_repo.py`, `app/infrastructure/repositories/historial_cliente_repo.py`, `app/infrastructure/db/session.py` | Mapeo ORM, SQL, sesiones. | Reglas de negocio |
| **Núcleo** | `app/core/dependencias.py`, `app/core/config.py`, `app/main.py` | DI, settings, CORS, exception handlers, registro de routers. | — |
| **Migración** | `alembic/versions/0001_crear_clientes.py` | Esquema de la tabla `clientes`. | — |

**Cadena de dependencias**:

```
app/api/clientes.py
  └─ ClienteCreate/Update/Read/Listado          (app/api/schemas/cliente.py)
       └─ reusa constantes y helpers             (app/domain/cliente.py)
  └─ get_gestor_clientes                         (app/core/dependencias.py:85)
       ├─ get_repo_clientes   → ClienteRepo(db)  (app/infrastructure/repositories/cliente_repo.py:37)
       │     └─ ClienteORM                        (app/infrastructure/models/cliente.py:9)
       │           └─ tabla "clientes"           (alembic/versions/0001_crear_clientes.py)
       └─ get_historial_clientes → HistorialClienteRepoVacio()   (stub)
  └─ ClienteNoEncontrado/RazonSocialDuplicada/ClienteConHistorial (app/domain/errores.py)
       └─ handlers en app/main.py:38-67          → 404 / 409 / 422
```

## 8. Plan de entrega

- **MVP**: `Cliente` + `ClienteRepo` + `ClienteORM` + migración `0001` + `GestorClientes` + 5
  endpoints + tests. El criterio de éxito es el ciclo completo por HTTP: crear → listar → filtrar →
  ver → modificar → dar de baja → verificar que la fila queda con `activo = False`.
- **Capa de datos**: el `UNIQUE` de `razon_social_key` + el índice `(activo, razon_social_key)` son
  la base de la performance del listado con filtro.
- **Futuro**: `HistorialClienteRepoVacio` → consulta real (Servicios); `X-Rol` → JWT; `frontend/`
  consumiendo el contrato OpenAPI.

## 9. Mapeo a la arquitectura de monolito modular en capas

H1 **es** la historia que define la arquitectura. Todo lo que vino después (H13, H4, H3) copió esta
estructura.

| Capa | Responsabilidad | Señal de que se está respetando |
|---|---|---|
| **1. Presentación** | Traduce HTTP ↔ Aplicación. | Los routers no tienen `if` de negocio; solo delegan en un método del gestor. |
| **2. Aplicación** | Orquesta los casos de uso y coordina entidades y repositorios. | `GestorClientes` no importa SQLAlchemy ni FastAPI. |
| **3. Dominio** | Garantiza las invariantes sin importar nada de la infraestructura. | `app/domain/` no importa `sqlalchemy`. `Cliente` se puede instanciar y testear sin base de datos. |
| **4. Infraestructura** | Única capa que conoce PostgreSQL. | Solo `app/infrastructure/` importa `sqlalchemy`. Los repos devuelven entidades de dominio, nunca ORM. |

**Regla de dependencia**: las flechas van **hacia adentro**. `api → application → domain`, e
`infrastructure → domain`. El Dominio no depende de nadie. Esa es la razón por la que el test
`test_h1_dominio` no necesita ni una fixture de base de datos.
