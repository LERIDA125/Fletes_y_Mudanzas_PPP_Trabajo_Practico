# Requirements Quality Checklist: H3 — Gestión de Choferes

**Purpose**: Verificar la calidad de los requisitos de la historia H3 antes y después de su implementación.
**Created**: 2026-10-21
**Feature**: [spec.md](../spec.md) — [plan.md](../plan.md) — [tasks.md](../tasks.md)
**Historia**: H3 · **Rama**: `feature/CRUD_choferes` · **Directorio**: `specs/004-gestion-choferes`

**Note**: Artefacto de revisión de calidad de requisitos, propiedad del revisor. `[x]` significa que el
criterio fue revisado y satisfecho **en calidad de requisito**; no significa que el trabajo de
implementación esté terminado.
**Estado de la revisión retrospectiva**: 2026-10-21 — los ítems marcados se verificaron contra el
código real de `backend/`; los que quedan sin marcar requieren decisión del Tech Lead.

## A. Claridad y completitud de la spec

- [x] CHK001 Cada User Story tiene criterios de aceptación en formato Dado/Cuando/Entonces
- [ ] CHK002 Cada criterio de aceptación es verificable por un test automatizado
- [x] CHK003 La sección *Out of Scope* delimita explícitamente lo que esta historia NO implementa
- [x] CHK004 Las reglas no confirmadas por el cliente están marcadas como decisión pendiente, no resueltas por intuición
- [x] CHK005 La spec deja explícito que el `saldo_a_favor` se persiste y se expone pero que ninguna operación de esta historia lo mueve

## B. Trazabilidad

- [x] CHK006 Cada requisito funcional (FR) tiene al menos un endpoint asociado
- [x] CHK007 El plan.md describe las 4 capas con los archivos concretos que crea o modifica
- [x] CHK008 El tasks.md cubre implementación, tests y documentación
- [x] CHK009 El quickstart.md permite levantar el entorno y ejercitar los endpoints
- [x] CHK010 El `**Feature Branch**` declarado en la spec coincide con la rama real del repositorio

## C. Conformidad con la Constitución

- [x] CHK011 No hay reglas de negocio en `app/api/` (Principio II)
- [x] CHK012 La capa de Aplicación no importa SQLAlchemy ni FastAPI; habla solo por puertos (Principio II)
- [x] CHK013 La baja es lógica con flag `activo` y la fila no se borra físicamente (DD-1)
- [x] CHK014 La autorización se consume por `require_rol` y ningún handler lee el rol directamente (DD-3)
- [ ] CHK015 El teléfono se valida por cantidad de dígitos (7–20), con `+`, espacios y guiones libres (DD-4)
- [x] CHK016 La modificación es `PUT` completo y repite los campos obligatorios del alta (DD-5)
- [x] CHK017 La migración que completa la tabla `choferes` es reversible y declara `downgrade()`

## D. Criterios de aceptación verificables

- [ ] CHK018 Existe test unitario de la capa de Aplicación por cada criterio de aceptación
- [x] CHK019 Existe test de integración del endpoint contra PostgreSQL real
- [x] CHK020 Los listados devuelven el esquema genérico `Pagina[ChoferRead]`
- [x] CHK021 Los errores de dominio heredan de la jerarquía base y se traducen a 404 / 409 / 422
- [x] CHK022 Los schemas de escritura usan `extra="forbid"` y no aceptan `activo` ni `saldo_a_favor`

## E. Cierre

- [ ] CHK023 La spec quedó estable: cualquier cambio posterior a la implementación está documentado en la spec
- [x] CHK024 El `Feature Branch` de la spec coincide con la rama real del repositorio: la spec declara `feature/CRUD_choferes`, que **es** la rama real usada en el PR #4 — la inconsistencia es de convención de nombres (`CRUD_choferes` en vez de `H3-gestion-choferes`), no de spec contra realidad
- [x] CHK025 No quedó en el código ninguna regla de negocio que la spec deje como pendiente

## Evidencia de la verificación retrospectiva (2026-10-21)

Ítems marcados y dónde se verificó:

| Ítem | Evidencia |
|---|---|
| CHK001 | 4 User Stories, 21 criterios de aceptación, todos literalmente en formato Dado/Cuando/Entonces (`spec.md:38-55, 73-91, 107-126, 144-154`) |
| CHK003 | `## Out of Scope` con 7 exclusiones, incluida explícitamente la asignación de choferes a servicios (`spec.md:17`) y los movimientos de saldo (`spec.md:18-19`) |
| CHK004 | DP-01..DP-06, todas con `[Supuesto temporal]` (`spec.md:262-275`), y ninguna se codificó por intuición (ver CHK025) |
| CHK005 | Spec lo dice en 5 lugares (`spec.md:18-19, 250, 254, 271-273`); el código lo cumple: `ChoferRepo.actualizar` sólo escribe `nombre_completo` y `telefono` (`chofer_repo.py:64-65`), así que `saldo_a_favor` no tiene ruta de escritura en H3 |
| CHK006 | Los 19 FR se asocian a los 5 endpoints del router (`app/api/choferes.py:21, 51, 78, 99, 133`) |
| CHK007 | `plan.md` §3 (líneas 42-135) describe las 4 capas con rutas exactas; §9 (líneas 225-231) cierra con la tabla capa→archivos→responsabilidad→prohibiciones |
| CHK008 | `tasks.md`: 20 tareas T01–T20 en 6 ejes; T01–T19 `[x]`, T20 (DoD con `docker compose`) sigue `[ ]` (`tasks.md:74`) |
| CHK009 | `quickstart.md`: opciones Docker y local (11-40), stub de autenticación por `X-Rol` (42-47), los 5 endpoints con `curl` (58-104), tabla de errores esperados (106-112), tests (114-122) |
| CHK010 | La spec declara `feature/CRUD_choferes` (`spec.md:3`), que fue exactamente la rama del PR #4, mergeada en `a3a8389`. La rama ya no está en el repo porque se borró tras el merge; la trazabilidad queda en el merge commit. La convención del nombre difiere de AGENTS.md §5, que es lo que el propio ítem anticipa |
| CHK011 | Los 5 handlers delegan en un único método del gestor (`choferes.py:44, 69, 96, 125, 153`). El único cálculo local es `offset=(page-1)*size` (`choferes.py:69`), que es paginación y no regla de dominio |
| CHK012 | Grep de `sqlalchemy`/`fastapi`/`pydantic`/`app.infrastructure`/`app.api` sobre `backend/app/application/` → 0 resultados. `application/choferes/gestor_choferes.py:1-3` y `puertos.py:1-3` importan sólo `app.domain`; la persistencia va por el `Protocol ChoferRepository` (`puertos.py:7-24`) |
| CHK013 | La baja es `UPDATE ... SET activo=False` (`chofer_repo.py:72-74`); no hay ningún `DELETE`. El test lo verifica con `SELECT` directo y comprueba que la fila persiste con `activo is False` (`test_choferes_api.py:78-86`) |
| CHK014 | `require_rol(ROL_ADMIN)` en `dependencies=[...]` de las 3 rutas de escritura (`choferes.py:38, 118, 147`); ninguna firma de handler recibe el rol y ningún handler lee `X-Rol`. Salvedad: los 2 `GET` no declaran dependencia de rol (ver fila siguiente y CHK002) |
| CHK016 | El router expone `PUT` y no `PATCH` (`choferes.py:99`); `ChoferUpdate(ChoferCreate)` repite los campos obligatorios con el docstring de DD-5 (`schemas/chofer.py:67-68`); el gestor los recibe keyword-only requeridos (`gestor_choferes.py:30`) |
| CHK017 | `0003_completar_choferes.py:51-55` declara `downgrade()` (elimina el índice y las 3 columnas); el `upgrade` sigue la secuencia nullable → backfill → `NOT NULL` → índice (`0003:27-48`), necesaria porque la tabla ya podía tener filas de H4. Salvedad: no se ejercita en CI (ver CHK018) |
| CHK019 | `test_choferes_api.py` (175 líneas, 2 tests) corre contra PostgreSQL real en la base propia `fletes_test` (`conftest.py:23, 46-58`) y verifica la persistencia con `SELECT` directo a `choferes` (`test_choferes_api.py:34, 80`) |
| CHK020 | `class ChoferListado(Pagina[ChoferRead])` (`schemas/chofer.py:89-90`); `Pagina[T]` con `items/total/page/size` en `schemas/comun.py:8-15`; `response_model=ChoferListado` (`choferes.py:53`) |
| CHK021 | Jerarquía `ReglaNegocioError` (`errores.py:1`) → `RecursoNoEncontrado` (`:8`) / `ConflictoOperacion` (`:12`) / `DatoInvalido` (`:16`). H3 sólo agrega `ChoferNoEncontrado(RecursoNoEncontrado)` (`errores.py:103-106`). Los 4 handlers están en `main.py:38-67` |
| CHK022 | `ChoferCreate` declara `ConfigDict(extra="forbid")` (`schemas/chofer.py:32`), `ChoferUpdate` lo hereda (`:67-68`); `activo` y `saldo_a_favor` sólo existen en `ChoferRead`, de salida. El test comprueba el 422 al mandar ambos (`test_choferes_api.py:115-134`) |
| CHK024 | `spec.md:3` = `feature/CRUD_choferes`, que es efectivamente la rama del PR #4, mergeada en `a3a8389` (`Merge pull request #4 from LERIDA125/feature/CRUD_choferes`). Al estar mergeada y borrada, ya no figura en `git branch -a` |
| CHK025 | Ninguna de las 6 decisiones abiertas quedó implementada por intuición: DP-01 → `UPDATE activo=false` (`chofer_repo.py:72-74`); DP-02/DP-04 → sin `UNIQUE` en `choferes` y sin `existe_*` en el puerto (`application/choferes/puertos.py:10-12`); DP-03 → `require_rol` (`api/choferes.py:38,118,147`); DP-05 → el saldo no tiene ruta de escritura (`chofer_repo.py:64-65`); DP-06 → no se modelan peones |

Ítems sin marcar y por qué (requieren decisión del Tech Lead):

- **CHK002** — La spec declara 21 criterios de aceptación y hay **4 funciones de test** en total
  (2 unitarios en `tests/unit/test_h3_choferes.py`, 2 de integración en
  `tests/integration/api/test_choferes_api.py`). Quedan sin test: US2.5 (listado sin coincidencias
  devuelve `total = 0`, `spec.md:87-88`), US3.3 (edición idempotente, `spec.md:114-117`), FR-014 /
  SC-007 (baja de un chofer que es `id_chofer_habitual` de un vehículo, `spec.md:212-213`), FR-018
  (contrato OpenAPI, `spec.md:221-222`), la segunda mitad de FR-019 (`actualizado_en` no cambia al
  consultar, `spec.md:223-224`) y los 6 edge cases (`spec.md:160-177`).
  **Además el criterio US1.5 se contradice con el código**: la spec dice que el sistema **"los ignora
  y aplica sus valores por defecto"** (`spec.md:54`) mientras que `ChoferCreate` usa
  `extra="forbid"` y su propio docstring documenta el `422` (`schemas/chofer.py:29, 32`); el test
  asienta el rechazo (`test_choferes_api.py:115-134`). El requisito existe, pero tal como está
  escrito **no es verificable tal cual**: hay que corregir la spec.
- **CHK015** — La validación por cantidad de dígitos está implementada y bien probada: en el dominio
  (`domain/chofer.py:76-81`, cuenta `d.isdigit()` y no la longitud de la cadena) y replicada en el
  schema (`schemas/chofer.py:55-64`); los formatos con `+`, espacios y guiones están cubiertos por
  test (`test_h3_choferes.py:29`). **Pero el contrato de longitud no cierra**: el schema no declara
  `max_length` (`schemas/chofer.py:40-47`) y la columna es `VARCHAR(20)` (`models/chofer.py:21`,
  migración `0003:28`). Un teléfono de 20 dígitos separados por espacios (39 caracteres) pasa el
  schema **y** el dominio y revienta en el `INSERT` con
  `psycopg.errors.DataError: value too long for type character varying(20)`; al no haber handler de
  `DataError`/`IntegrityError` en `main.py:38-67`, sale como **HTTP 500 en vez de 422**. Es el
  **mismo patrón** que `patente` `VARCHAR(10)` vs `max_length=15` en H4 (ver `specs/003-gestion-vehiculos`).
  Nota: `nombre_completo` sí tiene `max_length` que coincide con `VARCHAR(120)` (`schemas/chofer.py:34-39`),
  así que la asimetría es intra-historia.
- **CHK018** — Hay 2 tests unitarios de Aplicación (`test_h3_choferes.py:60-108`, con
  `FakeChoferRepo` en `tests/unit/application/choferes/fakes.py`) que comprimen los 21 criterios de
  aceptación. No hay unitarios del repositorio en sí. Además el doble **aliasea objetos** en vez de
  copiarlos (`fakes.py:16` guarda la misma instancia y `fakes.py:35` la muta in-place), de modo que
  el assert de "actualizar conserva el saldo" (`test_h3_choferes.py:82-88`) termina verificando el
  aliasing del fake y no el contrato del repo. A esto se suma que la migración `0003` **nunca se
  ejercita**: `tests/integration/conftest.py:58` crea el esquema con `Base.metadata.create_all`
  (desde el ORM), nunca con Alembic, así que el backfill, el `NOT NULL` y el `downgrade()` no
  tienen ninguna cobertura.
- **CHK023** — La spec no quedó estable respecto de la implementación:
  1. **US1.5 contradice al código** (`spec.md:54` dice "los ignora", la implementación responde
     `422`): es la misma contradicción que separa CHK002 de CHK022.
  2. El Contrato de API declara **`401` si no hay sesión** (`spec.md:240`) que el código **jamás
     puede producir**: `get_rol_actual` devuelve `ROL_CHOFER` por defecto (`core/dependencias.py:53`),
     que es justamente el stub documentado en DD-3.
  3. US3.1 pide que `actualizado_en` sea **posterior** a `creado_en` (`spec.md:111`), pero
     `func.now()` es timestamp de **transacción** (`chofer_repo.py:67`), que garantiza `>=`; el test
     también afirma `>=` (`test_choferes_api.py:68`).
  4. La spec fija `saldo_a_favor` como **`float`** (`spec.md:250`) mientras el resto del sistema usa
     `Decimal` para dinero (`domain/tipo_vehiculo.py:5, 27-29`); la columna es `NUMERIC(12,2)` y el
     repositorio convierte con `float(orm.saldo_a_favor)` (`chofer_repo.py:15`). H3 es el único campo
     monetario que no usa `Decimal`, y la inconsistencia nace en la spec, no en el código.
  5. La spec sigue en `**Status**: Draft` (`spec.md:7`) pese a estar mergeada en `a3a8389`.
  Según AGENTS.md §9, esto se correg **en la spec**, no parcheando el código.

## Notes

- Los ítems se marcan `[x]` solo tras verificar el criterio contra el código o la spec.
- Un caso marcado como decisión pendiente en la spec se testea con `pytest.mark.skip`, nunca inventando comportamiento.
- Los dos `GET` (`choferes.py:51, 78`) no declaran ninguna dependencia de rol: la lectura está abierta a
  cualquier header, y el plan (`plan.md`, tabla de endpoints) les asigna rol "admin, chofer" y error `403`,
  que el código **no puede producir**. Hay que decidir si el acceso de lectura es abierto por diseño o si falta
  una dependencia.
- `ChoferListado` no está exportado en el consolidado `app/api/schemas/__init__.py` (sí lo está
  `ClienteListado`, en las líneas 4 y 41). Asimetría menor entre historias.
- `FakeChoferRepo.llamadas_desactivar` se declara y acumula (`fakes.py:11, 34`) pero ningún test lo lee. El mismo
  patrón repetido en los 4 fakes del proyecto (`clientes`, `vehiculos`, `tipos_vehiculo`).
