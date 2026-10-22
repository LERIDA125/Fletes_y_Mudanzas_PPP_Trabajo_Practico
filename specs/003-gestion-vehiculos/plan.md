# Implementation Plan: H4 — Gestión de Vehículos y Tipos de Vehículo

**Spec**: `specs/003-gestion-vehiculos/spec.md`

**Branch**: `feature/H4-gestion-vehiculos`

**Estado**: plan de implementación **retrospectivo**. Documentado el 2026-10-21 por ingeniería
inversa sobre el código ya mergeado (commit `5e1a62f`, merge `f050ee5`). No describe trabajo
pendiente: describe lo que la historia decidió hacer, cómo quedó implementado, y qué desviaciones
del plan original quedaron registradas en el código.

## 1. Qué construye esta historia

Dos entidades encadenadas por dependencia estricta:

```
TipoVehiculo  (catálogo: descripción + capacidad + tarifas)
      │  1
      │
      │  N
   Vehiculo  (patente + tipo + chofer habitual)
```

`TipoVehiculo` es el **catálogo de tarifas**: descripción, capacidad de carga en kg, tarifa hora
base y tarifa de km excedente. `Vehiculo` es la unidad concreta: patente, a qué tipo pertenece y,
opcionalmente, su chofer habitual.

Esta historia es la primera que introduce **dos agregados en una sola**, con dependencias entre
ellos, y la primera que usa **`Decimal` para dinero**.

## 2. Punto de partida: qué ya existe

H4 se brancheó sobre un backend que ya tenía:

- **H1 (Clientes)** mergeada: el patrón de 4 capas, puertos, `Pagina[T]`, la jerarquía de errores y
  la lección de `actualizado_en`.
- **La jerarquía de errores polimórfica** (commit `7d5f8bf`): `ConflictoOperacion` y `DatoInvalido`
  como clases base reales, para que los errores de H4 puedan colgar de ellas y no del `catch-all`.
- **H3 (Choferes)**: la entidad `Chofer` con `ChoferRepo.existe_activo`. Eso permitió que el puerto
  `ConsultaChofer` tuviera **implementación real** desde el primer día, sin stub.
- **H13 (Migración)**: ya había **catalogos provisionales** de tipos de vehículo en
  `scripts/migracion/catalogos.py` (`TIPOS_VEHICULO_CANONICOS`, 8 valores, + 9 alias). H4 crea la
  tabla que finalmente los hospeda.

## 3. Capas y archivos que toca

### 3.1 Dominio — `app/domain/vehiculo.py` (87 líneas)

**Constante y funciones de módulo:**

```python
PATENTE_REGEX = re.compile(r"^[A-Z]{3}\s?\d{3}$|^[A-Z]{2}\s?\d{3}\s?[A-Z]{3}$")
```

- `normalizar_patente(texto)` → `" ".join(texto.split()).upper()` — colapsa espacios, quita
  extremos, pasa a mayúsculas.
- `es_patente_valida(texto)` → `bool(PATENTE_REGEX.match(normalizar_patente(texto)))`.

El regex acepta los dos formatos de patente argentina vigentes: `AAA 123` (viejo) y `AA 123 ABC`
(nuevo).

**Dataclass `Vehiculo`**:

| Campo | Tipo | Default |
|---|---|---|
| `id` | `int \| None` | obligatorio |
| `patente` | `str` | obligatorio |
| `id_tipo_vehiculo` | `int` | obligatorio |
| `id_chofer_habitual` | `int \| None` | obligatorio (hay que pasarlo explícitamente, aunque pueda ser `None`) |
| `activo` | `bool` | `True` |
| `creado_en` / `actualizado_en` | `datetime \| None` | `None` |

**`_validar()`** — 2 reglas: formato de patente argentina y `id_tipo_vehiculo > 0`.
**No valida `id_chofer_habitual`**: esa es una regla de existencia de otra entidad, y por lo tanto
pertenece a la capa de Aplicación (que tiene los puertos para consultarla).

### 3.2 Dominio — `app/domain/tipo_vehiculo.py` (105 líneas)

**Constantes**: `DESCRIPCION_MIN = 3`, `DESCRIPCION_MAX = 80`.

- `normalizar_descripcion(texto)` → `" ".join(texto.split())` (no pasa a mayúsculas).
- `normalizar_descripcion_key(texto)` → `normalizar_descripcion(texto).lower()`.

**Dataclass `TipoVehiculo`** — `capacidad_carga_kg`, `tarifa_hora_base` y `tarifa_km_excedente` son
**`Decimal`**, no `float`. Es la primera entidad con dinero.

**`descripcion_key` es una `@property`**, no un campo: la clave normalizada nunca se desincroniza
de `descripcion`.

**`_validar()`** — 4 reglas: largo de descripción (3–80), `capacidad_carga_kg > 0`,
`tarifa_hora_base >= 0`, `tarifa_km_excedente >= 0`.

### 3.3 Dominio — `app/domain/errores.py`: los 8 errores de H4

| Clase | Base | HTTP | Mensaje |
|---|---|---|---|
| `TipoVehiculoNoEncontrado` | `RecursoNoEncontrado` | 404 | `"No existe un tipo de vehículo con id {id}"` |
| `VehiculoNoEncontrado` | `RecursoNoEncontrado` | 404 | `"No existe un vehículo con id {id}"` |
| `DescripcionDuplicada` | `ConflictoOperacion` | 409 | `"Ya existe un tipo de vehículo con la descripción {descripcion!r}"` |
| `PatenteDuplicada` | `ConflictoOperacion` | 409 | `"Ya existe un vehículo con la patente {patente!r}"` |
| `TipoVehiculoConVehiculos` | `ConflictoOperacion` | 409 | `"El tipo de vehículo {id} tiene vehículos asociados y no se puede dar de baja"` |
| `VehiculoConServicios` | `ConflictoOperacion` | 409 | `"El vehículo {id} tiene servicios asociados y no se puede dar de baja"` |
| `TipoVehiculoInvalido` | `DatoInvalido` | 422 | `"No existe un tipo de vehículo activo con id {id}"` |
| `ChoferInvalido` | `DatoInvalido` | 422 | `"No existe un chofer activo con id {id}"` |

**`ChoferInvalido` es el error de H4 que cuelga de `DatoInvalido` y no de `ReglaNegocioError` pelado**:
es el patrón correcto (referencia a una entidad que no existe o está inactiva → 422), pero es la
**excepción** dentro de H4: los `_validar()` de ambos dominios lanzan la clase base.

### 3.4 Aplicación — `app/application/vehiculos/gestor_vehiculos.py`

`GestorVehiculos(repositorio_vehiculos, consulta_tipos, consulta_choferes, consulta_servicios)` —
**4 puertos inyectados**, uno por cada regla que necesita consultar otra entidad.

| Método | Secuencia de reglas |
|---|---|
| `registrar(*, patente, id_tipo_vehiculo, id_chofer_habitual=None)` | (1) `_verificar_tipo_vehiculo` → (2) `_verificar_chofer_habitual` → (3) `Vehiculo.crear(...)` valida el formato → (4) `_verificar_patente_disponible` → (5) `repo.crear` |
| `obtener(vehiculo_id)` | Repo; `None` **o** inactivo → `VehiculoNoEncontrado` |
| `listar(*, busqueda, offset, limit)` | `(items, total)` |
| `actualizar(vehiculo_id, *, ...)` | `obtener()` → verificar tipo → verificar chofer → verificar patente (**sobre un `Vehiculo` temporal**, para normalizar antes de comparar, con `excluir_id`) → `vehiculo.actualizar(...)` → `repo.actualizar` |
| `eliminar(vehiculo_id)` | Repo → `None` → 404; inactivo → `return` (idempotencia); `tiene_servicios` → `VehiculoConServicios`; si no → baja lógica |

### 3.5 Aplicación — `app/application/tipos_vehiculo/gestor_tipos_vehiculo.py`

`GestorTiposVehiculo(repositorio_tipos, consulta_vehiculos)` — 2 puertos.

`registrar` y `actualizar` reciben **`float`** en la frontera y convierten con
`Decimal(str(x))` — `str()` primero para que `0.1` no-arrastre el error binario de `float`.

`_verificar_descripcion_disponible(descripcion_key, excluir_id=None)` → `DescripcionDuplicada`.
La comparación es **case-insensitive** porque usa la key.

### 3.6 Puertos — 6 `Protocol` en total

**`app/application/vehiculos/puertos.py`** — 4:

| Protocol | Método | Lo implementa |
|---|---|---|
| `VehiculoRepository` | `crear`, `obtener_por_id`, `listar`, `contar`, `actualizar`, `desactivar`, `existe_patente(key, excluir_id=None)` | `VehiculoRepo` |
| `ConsultaTipoVehiculo` | `existe_activo(tipo_id)` | `TipoVehiculoRepo.existe_activo` |
| `ConsultaChofer` | `existe_activo(chofer_id)` | `ChoferRepo.existe_activo` (H3) |
| `ConsultaServiciosVehiculo` | `tiene_servicios(vehiculo_id)` | `ConsultaServiciosVehiculoVacio` (**stub**) |

**`app/application/tipos_vehiculo/puertos.py`** — 2:

| Protocol | Método | Lo implementa |
|---|---|---|
| `TipoVehiculoRepository` | `crear`, `obtener_por_id`, `listar`, `contar`, `actualizar`, `desactivar`, `existe_descripcion(key, excluir_id=None)` | `TipoVehiculoRepo` |
| `ConsultaVehiculosPorTipo` | `tiene_vehiculos(tipo_id)` | `VehiculoRepo.tiene_vehiculos` |

**Dato estructural: el mismo repositorio implementa dos puertos.** `VehiculoRepo` es a la vez
`VehiculoRepository` (persistencia) y `ConsultaVehiculosPorTipo` (consulta para H4-2). Y
`TipoVehiculoRepo` es a la vez `TipoVehiculoRepository` y `ConsultaTipoVehiculo`. Eso evita ports
artificiales, pero significa que el repositorio tiene **métodos que no están en su Protocol de
persistencia** (`tiene_vehiculos`, `existe_activo`).

### 3.7 Infraestructura — modelos ORM

**`vehiculos`**: `id` INTEGER identity PK · `patente` **VARCHAR(10) NOT NULL UNIQUE** ·
`id_tipo_vehiculo` INTEGER NOT NULL FK `tipos_vehiculo.id` `ondelete=RESTRICT` ·
`id_chofer_habitual` INTEGER NULL FK `choferes.id` `ondelete=RESTRICT` · `activo` BOOL default true ·
`creado_en`/`actualizado_en` TIMESTAMPTZ default `now()` (+`onupdate`).
Índice `ix_vehiculos_activo_patente` sobre `(activo, patente)`.

**`tipos_vehiculo`**: `id` INTEGER identity PK · `descripcion` VARCHAR(80) NOT NULL ·
`descripcion_key` VARCHAR(80) NOT NULL **UNIQUE** · `capacidad_carga_kg` **NUMERIC(10,2)** default 0 ·
`tarifa_hora_base` **NUMERIC(12,2)** default 0 · `tarifa_km_excedente` **NUMERIC(12,2)** default 0 ·
`activo` BOOL default true · fechas.
Índice `ix_tipos_vehiculo_activo_descripcion_key` sobre `(activo, descripcion_key)`.

**`descripcion_key` se recalcula en el repositorio** (`a_orm` usa `tipo.descripcion_key`; `a_dominio`
no la lee del ORM, la recomputa). Consecuencia: si alguien escribiera directo en la tabla, la key
puede desincronizarse de `descripcion`.

### 3.8 Infraestructura — repositorios

`VehiculoRepo` y `TipoVehiculoRepo`, con la misma estructura que `ClienteRepo` (mappers `a_dominio`/
`a_orm`, `crear` con `commit` en `try` y `IntegrityError` → `PatenteDuplicada` / `DescripcionDuplicada`,
`actualizar` con `actualizado_en` forzado a mano, `desactivar` con UPDATE Core).

**Filtro de búsqueda**:

| Repositorio | Filtro | ¿Case-insensitive? |
|---|---|---|
| `VehiculoRepo._consulta_filtrada` | `patente.contains(busqueda.upper())` | Sí, por `upper()` del input — la columna tiene el `UNIQUE` y se guarda normalizada en mayúsculas |
| `TipoVehiculoRepo._consulta_filtrada` | `descripcion_key.contains(normalizar_descripcion_key(busqueda))` | Sí, por la key en minúsculas |

### 3.9 Presentación — `app/api/vehiculos.py` y `app/api/tipos_vehiculo.py`

| Router | Prefijo | Endpoints |
|---|---|---|
| `vehiculos.py` | `/api/vehiculos` | `POST` (admin, 201), `GET` (cualquiera), `GET /{id}` (cualquiera), `PUT` (admin), `DELETE` (admin, 204) |
| `tipos_vehiculo.py` | **`/api/tipos-vehiculo`** | `POST` (admin, 201), `GET` (cualquiera), `GET /{id}` (cualquiera), `PUT` (admin), `DELETE` (admin, 204) |

Paginación idéntica a H1: `page` (ge=1), `size` (ge=1, le=100), default 20.

**Los `GET` de listado y detalle NO declaran `dependencies`**: cualquier rol puede leer. Coincide
con el contrato de la spec ("admin, chofer"), pero no es una whitelist explícita — el rol por
defecto sin header es `chofer`, así que un cliente sin `X-Rol` también lee.

### 3.10 Presentación — schemas

| Schema | Base | Notas |
|---|---|---|
| `VehiculoBase` | `BaseModel` | `patente` (min 6, max **15**), `id_tipo_vehiculo` (`gt=0`), `id_chofer_habitual` (default `None`, **sin `gt=0`**) |
| `VehiculoCreate` | `VehiculoBase` | `extra="forbid"` |
| `VehiculoUpdate` | `VehiculoCreate` | Sin redefinir nada (DD-5) |
| `VehiculoRead` | `VehiculoBase` | `from_attributes=True`, `+id/activo/creado_en/actualizado_en`, `de_vehiculo()` |
| `VehiculoListado` | `Pagina[VehiculoRead]` | |
| `TipoVehiculoBase` | `BaseModel` | `descripcion` (3–80), `capacidad_carga_kg: Decimal` (`gt=0`), `tarifa_hora_base: Decimal` (`ge=0`), `tarifa_km_excedente: Decimal` (`ge=0`) |
| `TipoVehiculoCreate` / `Update` / `Read` / `Listado` | ídem | `extra="forbid"` heredado |

El schema **normaliza la patente** (`_normalizar_patente`, `mode="before"`) y el dominio **también**
(`__post_init__`). Redundante, pero inofensivo.

### 3.11 Migración — `alembic/versions/0002_crear_tipos_vehiculo_y_vehiculos.py` (126 líneas)

`revision = "0002"`, `down_revision = "0001"`. **`upgrade()` crea 3 tablas**, no 2:

| Tabla | Qué aporta |
|---|---|
| `tipos_vehiculo` | La tabla de H4. |
| `vehiculos` | La tabla de H4, con sus 2 FK (`RESTRICT`). |
| **`choferes`** | **Tabla mínima** de H4: solo `id`, `activo`, `creado_en`, `actualizado_en`. |

**Por qué H4 creó `choferes`**: la FK `vehiculos.id_chofer_habitual` necesita una tabla `choferes`
que existía. Como la entidad Chofer todavía no se había implementado, H4 creó la tabla con los
campos mínimos **solo para sostener el FK**. Está documentado literalmente en tres lugares:
la propia migración `0002`, la docstring de `0003_completar_choferes.py` (*"H4 creó `choferes` con
solo `id`, `activo` y las fechas, para sostener el FK `id_chofer_habitual` de vehículos. H3 agrega
`nombre_completo`, `telefono` y `saldo_a_favor`"*), y la docstring de
`app/infrastructure/models/chofer.py`.

`downgrade()` **sí existe** y borra en el orden correcto: `vehiculos` → `choferes` →
`tipos_vehiculo` (con sus índices).

### 3.12 Tests

| Archivo | Contenido |
|---|---|
| `tests/unit/test_h4_vehiculos.py` | **215 líneas, 3 tests**: `test_h4_dominio`, `test_h4_gestor_tipos_vehiculo`, `test_h4_gestor_vehiculos` |
| `tests/unit/application/vehiculos/fakes.py` | **105 líneas**: `VehiculoYaExiste`, `FakeVehiculoRepo`, `FakeConsultaTipoVehiculo`, `FakeConsultaChofer`, `FakeConsultaServiciosVehiculo` |
| `tests/unit/application/tipos_vehiculo/fakes.py` | **78 líneas**: `TipoVehiculoYaExiste`, `FakeTipoVehiculoRepo`, `FakeConsultaVehiculosPorTipo` |
| `tests/integration/api/test_vehiculos_api.py` | **162 líneas, 2 tests**: `test_vehiculos_api_ciclo_completo_admin`, `test_vehiculos_api_seguridad_y_reglas` |

**Total: 5 funciones de test** (3 unitarias + 2 de integración) para dos entidades.

**Los tipos de vehículo no tienen archivo de test de API propio**: se testean dentro de
`test_vehiculos_api.py`.

El test de integración verifica **contra PostgreSQL real** que el alta persiste (`SELECT activo,
patente FROM vehiculos WHERE id = :id`) y que tras el `DELETE` el `GET` da 404.

## 4. Decisiones de diseño aplicadas

| Decisión | Cómo se aplica en H4 |
|---|---|
| **DD-1** (baja lógica) | `activo` + `desactivar()` en ambas entidades. Listados filtran por `activo IS true`; el detalle trata un inactivo como inexistente. |
| **DD-5** (`PUT` completo) | `VehiculoUpdate(VehiculoCreate)` y `TipoVehiculoUpdate(TipoVehiculoCreate)` no redefinen campos. |
| **DD-2** (clave normalizada) | Aplicado a `TipoVehiculo.descripcion_key` (minúsculas) — pero la normalización **no** quita acentos, a diferencia de `Cliente.razon_social_key`. |
| **Validar primero, mutar después** | `actualizar()` de ambas entidades construye una entidad temporal antes de tocar `self`. |
| **Puertos por regla** | 4 puertos en vehículos, 2 en tipos. Cada regla que necesita consultar otra entidad tiene su puerto. |
| **Errores polimórficos** | `TipoVehiculoInvalido` y `ChoferInvalido` cuelgan de `DatoInvalido` (422); los de conflicto, de `ConflictoOperacion` (409). |
| **`Decimal` para dinero** | En el dominio y en la columna (`NUMERIC`). La conversión a `float` ocurre solo en la frontera de Aplicación. |

## 5. Puntos que el plan NO resuelve solo

- **FR-021 (baja de vehículo con servicios) nunca bloquea en producción**:
  `ConsultaServiciosVehiculoVacio.tiene_servicios` devuelve siempre `False`. La regla está
  implementada y testeada en el gestor; falta el dato. Se resuelve cambiando la inyección en
  `dependencias.py` cuando llegue Servicios (H6).
- **La tabla `choferes` nació en H4** y la completó H3. La numeración de historias no coincide con el
  orden real de los hechos: la spec de H4 habla de "H2" para choferes, pero llegó como H3.
- **Las tarifas viven en la tabla `tipos_vehiculo`**, no en una   tabla de configuración aparte. La
  constitución exige leer de "una tabla de configuración" — `tipos_vehiculo` cumple ese rol, pero
  conviene tenerlo explícito cuando llegue la tabla de configuración definitiva.
- **H13 no carga móviles ni vehículos**: los catálogos provisionales de
  `scripts/migracion/catalogos.py` siguen siendo la fuente de los tipos de vehículo hasta que se
  escriba el cargador.
- **`id_chofer_habitual` no tiene `gt=0` en el schema**: un `0` o `-1` pasa Pydantic y muere en
  `ChoferInvalido` (422). El resultado es correcto; la validación está en el lugar equivocado.

## 6. Riesgos y cuidados — y desviaciones registradas

Verificados contra el código en la revisión retrospectiva del 2026-10-21:

1. **`patente` tiene longitudes inconsistentes: el schema permite 6–15 caracteres pero la columna es
   `VARCHAR(10)`.** Una patente de 11 a 15 caracteres pasa la validación de Pydantic y revienta con
   un `DataError` de PostgreSQL → **HTTP 500 en lugar de 422**. Es el único punto donde un dato
   inválido produce un error de servidor en todo el backend. Las patentes válidas más largas
   (`AA 123 ABC` = 9) entran bien, así que el bug no se manifiesta con datos reales — por eso nadie
   lo notó.
2. **Prefijo de ruta inconsistente**: `/api/tipos-vehiculo` (guion) contra `/api/vehiculos`, y los
   módulos Python usan `tipos_vehiculo` (underscore). Conviene elegir un criterio y aplicarlo a
   todos los routers.
3. **`id_chofer_habitual` sin `gt=0`**, mientras `id_tipo_vehiculo` sí lo tiene. Asimetría
   registrada; el error sale 422 pero por el camino largo.
4. **El dominio lanza la clase base `ReglaNegocioError`**, no `DatoInvalido`. Funciona por el
   catch-all de `main.py`, pero no es polimórfico como el resto de la jerarquía.
5. **`patente` se normaliza dos veces** (schema Pydantic + `__post_init__` del dominio).
6. **`descripcion_key` se recalcula en el repositorio**, no se persiste desde el dominio.
7. **`actualizado_en` se fuerza a mano en `actualizar` pero no en `desactivar`**: verificado que el
   `onupdate` **sí** se aplica en el UPDATE bulk de `desactivar` (SQL compilado:
   `SET activo=..., actualizado_en=now()`). Pero **los repos de H4 no tienen el comentario de la
   lección H1/T047** que sí está en `chofer_repo.py:66` — la decisión quedó implícita, sin el
   porqué documentado.
8. **`Decimal` se pierde en la frontera de Aplicación**: `GestorTiposVehiculo.registrar` recibe
   `float`. La API sí entrega `Decimal` en el schema, pero FastAPI lo serializa a `float` en JSON.
   El `Decimal(str(x))` evita el error binario en la conversión interna, pero el valor que viaja por
   HTTP es float.
9. **Los `GET` no declaran `dependencies`**: leen cualquier rol, incluso sin header `X-Rol`.
10. **No hay tests de dominio en `tests/unit/domain/`** (solo `__init__.py`): los tests de dominio
    de H4 están comprimidos dentro de `test_h4_dominio`.
11. **No hay `plan.md` ni `tasks.md` de H4**: el código llegó por el commit `5e1a62f` **sin commit de
    documentación**, a diferencia de H3 (`7fa319e docs(H3): especificar, planificar y desglosar...`).
    Este documento es la reconstrucción de ese plan perdido.
12. **La spec sigue con `Status: Draft`** aunque la historia está implementada, mergeada y con
    tests en verde.
13. **Los tests acceden a atributos privados de los fakes** (`consulta_vehiculos._tipos_con_vehiculos.clear()`,
    `consulta_servicios._vehiculos_con_servicios.clear()`) para resetear el estado. Acoplamiento de los
    tests a la implementación interna de los dobles.
14. **La rama de `IntegrityError` de los repositorios no tiene cobertura**, igual que en H1: los
    fakes lanzan excepciones propias (`VehiculoYaExiste`, `TipoVehiculoYaExiste`) y nunca
    `PatenteDuplicada` / `DescripcionDuplicada` desde el `IntegrityError` real.

## 7. Trazabilidad spec → plan → código

| Capa | Archivos | Responsabilidad | No debe contener |
|---|---|---|---|
| **1. Presentación** | `app/api/vehiculos.py`, `app/api/tipos_vehiculo.py`, `app/api/schemas/vehiculo.py`, `app/api/schemas/tipo_vehiculo.py`, `app/api/schemas/comun.py` | Routing, validación de forma, serialización. | Reglas de negocio |
| **2. Aplicación** | `app/application/vehiculos/`, `app/application/tipos_vehiculo/` | Casos de uso; verificación de existencia de tipos, choferes y servicios. | SQL, ORM, HTTP |
| **3. Dominio** | `app/domain/vehiculo.py`, `app/domain/tipo_vehiculo.py`, `app/domain/errores.py` | Formato de patente, rangos, `Decimal`. | Persistencia |
| **4. Infraestructura** | `app/infrastructure/models/vehiculo.py`, `app/infrastructure/models/tipo_vehiculo.py`, `app/infrastructure/repositories/vehiculo_repo.py`, `app/infrastructure/repositories/tipo_vehiculo_repo.py`, `app/infrastructure/repositories/chofer_repo.py` (H3), `app/infrastructure/repositories/consulta_stub.py` | Mapeo ORM, SQL, implementación de los puertos de consulta. | Reglas de negocio |
| **Núcleo** | `app/core/dependencias.py` (8 providers de H4), `app/main.py` (2 routers + 4 handlers) | DI, CORS, traducción de errores. | — |
| **Migración** | `alembic/versions/0002_...py` | Esquema de `tipos_vehiculo`, `vehiculos` y `choferes` mínima. | — |

**Cadena de dependencias**:

```
app/api/vehiculos.py
  └─ VehiculoCreate/Update/Read/Listado       (app/api/schemas/vehiculo.py)
       └─ reusa PATENTE_REGEX/normalizar_patente (app/domain/vehiculo.py)
  └─ get_gestor_vehiculos                      (app/core/dependencias.py)
       ├─ get_repo_vehiculos        → VehiculoRepo(db)
       │     ├─ VehiculoORM                        (app/infrastructure/models/vehiculo.py)
       │     └─ tiene_vehiculos() → ConsultaVehiculosPorTipo
       ├─ get_consulta_tipo_vehiculo → TipoVehiculoRepo(db).existe_activo
       ├─ get_consulta_chofer        → ChoferRepo(db).existe_activo        (H3)
       └─ get_consulta_servicios_vehiculo → ConsultaServiciosVehiculoVacio()  (STUB, H6)

app/api/tipos_vehiculo.py
  └─ get_gestor_tipos_vehiculo
       ├─ get_repo_tipos_vehiculo → TipoVehiculoRepo(db)
       │     ├─ TipoVehiculoORM
       │     └─ existe_activo() → ConsultaTipoVehiculo
       └─ get_consulta_vehiculos_por_tipo → VehiculoRepo(db)
```

## 8. Plan de entrega

- **MVP**: `TipoVehiculo` completo (dominio + aplicación + repositorio + router + migración) porque
  `Vehiculo` depende de él. Después `Vehiculo`.
- **Orden de migración**: una sola migración `0002` con las 3 tablas, en el orden
  `tipos_vehiculo` → `choferes` → `vehiculos` (respetando las FK), con `downgrade()` inverso.
- **Criterio de éxito**: ciclo completo por HTTP de ambas entidades + las 5 reglas de integridad
  verificadas con sus códigos: 404 (inexistente), 409 (duplicado), 409 (dependencia con
  vehículos/servicios), 422 (tipo o chofer inválido), 403 (rol insuficiente).
- **Futuro**: `ConsultaServiciosVehiculoVacio` → consulta real (H6); carga de móviles desde el
  Excel (H13); tabla de configuración de tarifas definitiva.

## 9. Mapeo a la arquitectura de monolito modular en capas

H4 es la historia que **estrena la dependencia entre agregados** dentro de la capa de Aplicación.

| Capa | Responsabilidad | Señal de que se está respetando |
|---|---|---|
| **1. Presentación** | HTTP ↔ Aplicación. | Los routers no saben qué es un tipo de vehículo activo; solo traducen `id` y delegan. |
| **2. Aplicación** | Coordina las reglas que cruzan entidades. | `GestorVehiculos` **no** importa los repositorios concretos: recibe 4 puertos y por eso se testea sin base de datos. |
| **3. Dominio** | Invariantes de una sola entidad. | `Vehiculo` no sabe si el chofer existe: solo valida su **formato** y que el tipo sea un id positivo. Las reglas de existencia son de Aplicación. |
| **4. Infraestructura** | Única capa que conoce PostgreSQL. | `TipoVehiculoRepo` implementa dos puertos; `VehiculoRepo` también. Los repos devuelven entidades de dominio. |

**El patrón que H4 consolida y que H3 no tenía**: cada regla que necesita consultar **otra**
entidad tiene su propio puerto (`ConsultaTipoVehiculo`, `ConsultaChofer`,
`ConsultaServiciosVehiculo`, `ConsultaVehiculosPorTipo`). Cada puerto tiene su propio
`Protocol` y su propio provider en `dependencias.py`. Cuando la entidad correspondiente exista
(H6 para Servicios), **solo se cambia el provider** — el gestor, el dominio, el router y los tests
no se tocan. Esa es la prueba de que la arquitectura está cumpliendo su propósito: el cambio de
reglas del cliente impacta lo menos posible, tal como pide AGENTS.md §2.
