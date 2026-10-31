# Tasks: 011 — Motor de Cotizaciones: Precio Sugerido vs Precio Acordado

**Feature**: [spec.md](./spec.md) · [plan.md](./plan.md)
**Branch**: `011-cotizacion-precio-sugerido-vs-acordado`
**Status**: Phases 1 and 5 implemented; Phases 2–4 and 6 pending.
**Input**: Directiva del Tech Lead del 2026-10-30 y aprobación formal de `spec.md` + `plan.md`.

## Reglas de ejecución

- Un task = un cambio revisable. Los tests van en el mismo commit que el comportamiento.
- No se marca `[x]` hasta que el task esté implementado **y** verificado.
- Los tasks de una fase pueden paralelizarse solo si no comparten archivos.
- Commits convencionales con prefijo de historia: `feat(H7)`, `test(H7)`, `docs(H7)`.

---

## Phase 0 — Gobernanza y preparación

**Goal**: desbloquear la implementación y dejar el rastro documental antes del código.

- [x] T001 Confirmar aprobación del Tech Lead sobre `spec.md` + `plan.md`.
- [x] T002 Corregir la rama local a `011-cotizacion-precio-sugerido-vs-acordado` (regla `<NNN>-<slug>`).
- [x] T003 Enmendar `.specify/memory/constitution.md` a v3.0.0 (MAJOR): fórmula nueva, modificadores y modelo sugerido/acordado.
- [x] T004 Actualizar `AGENTS.md` §2, §3, §4, §6, §8 y §11 (DD-6 + DD-10).
- [x] T005 Registrar la decisión en Engram y dejar `feature.json` en `status: "specified"`.

**Checkpoint**: la historia ya no tiene bloqueos de gobernanza.

---

## Phase 1 — Base de datos y persistencia (MVP data slice)

**Goal**: tabla de configuración, esquema de servicios y migración `0007` listos para `alembic upgrade head`.

- [x] T010 Crear `backend/app/domain/configuracion_cotizacion.py` con `ConfiguracionCotizacion` validada.
- [x] T011 Agregar `ConfiguracionCotizacionInvalida` a `backend/app/domain/errores.py`.
- [x] T012 Crear `backend/app/infrastructure/models/configuracion_cotizacion.py` (singleton + constraints).
- [x] T013 Actualizar `backend/app/infrastructure/models/servicio.py`:
  - renombrar `distancia_ida_km` → `km_estimados`;
  - renombrar `precio_total` → `precio_acordado`;
  - agregar `precio_sugerido`, flags y snapshots;
  - actualizar constraints.
- [x] T014 Registrar `ConfiguracionCotizacionORM` en `backend/app/infrastructure/models/__init__.py`.
- [x] T015 Crear `backend/app/infrastructure/repositories/configuracion_cotizacion_repo.py`.
- [x] T016 Adaptar `backend/app/infrastructure/repositories/servicio_repo.py` al esquema renombrado, con shim temporal para la fase 1.
- [x] T017 Crear `backend/alembic/versions/0007_cotizacion_sugerido_vs_acordado.py`:
  - tabla `configuracion_cotizacion` + fila singleton (`30000`, `15000`, `15.00`, `20.00`);
  - renombres de columnas;
  - columnas nuevas + backfill de históricos;
  - constraints;
  - `downgrade()` completo.
- [ ] T018 Aplicar `alembic upgrade head` y `alembic downgrade -1 && alembic upgrade head` en la base de desarrollo (lo ejecuta el Tech Lead). Validado en DB scratch `fletes_migracion_test`.
- [x] T019 Ejecutar `ruff check app` y los tests unitarios existentes.

**Checkpoint**: esquema y migración listos; la app sigue operando con el flujo anterior gracias al shim.

---

## Phase 2 — Dominio

**Goal**: entidades y value objects puros para la nueva cotización.

- [ ] T020 Crear `backend/app/domain/cotizacion.py` con `CotizacionCalculada` y sus invariantes.
- [ ] T021 Refactorizar `backend/app/domain/servicio.py`:
  - `km_estimados`, `precio_acordado`, `precio_sugerido`;
  - flags y snapshots;
  - `crear(..., cotizacion: CotizacionCalculada, precio_acordado: Decimal)`;
  - validaciones y compatibilidad de columnas heredadas.
- [ ] T022 Tests de dominio: `backend/tests/unit/test_h7_cotizacion_dominio.py`.

**Checkpoint**: dominio nuevo probado sin ORM.

---

## Phase 3 — Aplicación

**Goal**: cálculo, configuración y alta con doble importe, todo por puertos.

- [ ] T030 Extender `backend/app/application/cotizacion/puertos.py` con `ConsultaConfiguracionCotizacion`.
- [ ] T031 Crear `backend/app/application/cotizacion/estrategias/por_hora_km_modificadores.py`.
- [ ] T032 Eliminar `backend/app/application/cotizacion/estrategias/por_hora_y_km.py`.
- [ ] T033 Refactorizar `backend/app/application/cotizacion/calculadora.py`.
- [ ] T034 Crear `backend/app/application/cotizacion/cotizador_servicios.py`.
- [ ] T035 Actualizar `backend/app/application/servicios/gestor_servicios.py` (alta y snapshot).
- [ ] T036 Tests unitarios: estrategia, calculadora, cotizador y alta.

**Checkpoint**: `pytest tests/unit` en verde con la fórmula nueva.

---

## Phase 4 — API y contrato

**Goal**: endpoint canónico y contrato OpenAPI nuevo.

- [ ] T040 Crear `backend/app/api/schemas/cotizacion.py`.
- [ ] T041 Crear `backend/app/api/cotizaciones.py`.
- [ ] T042 Actualizar `backend/app/api/schemas/servicio.py`.
- [ ] T043 Retirar `POST /api/servicios/cotizar` de `backend/app/api/servicios.py`.
- [ ] T044 Actualizar `backend/app/core/dependencias.py` y `backend/app/main.py`.
- [ ] T045 Tests de integración: `test_cotizaciones_api.py` y actualización de `test_servicios_api.py`.
- [ ] T046 Exportar OpenAPI y verificar que la ruta vieja ya no existe.

**Checkpoint**: contrato nuevo con integración contra PostgreSQL en verde.

---

## Phase 5 — Frontend

**Goal**: panel reutilizable, cálculo reactivo y acordado editable.

- [x] T050 Zod y tipos de cotización en `frontend/src/features/cotizaciones/`.
- [x] T051 Cliente API `frontend/src/lib/api/cotizaciones.ts`.
- [x] T052 Server Action `frontend/src/features/cotizaciones/actions.ts`.
- [x] T053 Crear `formulario-cotizacion.tsx` con debounce y estado de edición manual.
- [x] T054 Integrar el panel en `formulario-servicio.tsx` y `cotizador.tsx`.
- [x] T055 Actualizar schemas, listados, portal chofer y `resumen-cotizacion.tsx`.
- [x] T056 Tests RTL: `cotizaciones.test.tsx` y actualización de `servicios.test.tsx` / `portal-chofer.test.tsx`.

**Checkpoint**: `npm run verificar` en verde.

---

## Phase 6 — Sincronización y cierre

- [ ] T060 `npm run gen:api` sin diff.
- [ ] T061 `npm run build`.
- [ ] T062 Actualizar `checklists/requirements.md` con la evidencia de implementación.
- [ ] T063 Actualizar `ssd.md` / `quickstart.md` si el equipo los incorpora.
- [ ] T064 Revisión cruzada + CI completo (4 jobs) + `feature.json` en `status: "implemented"`.

---

## Dependencias críticas

| Task | Depende de |
|---|---|
| T012–T017 | T010, T011 |
| T018 | T017 (y PostgreSQL disponible) |
| T020–T022 | T010, T011 |
| T030–T036 | T020–T022 |
| T040–T046 | T030–T036 |
| T050–T056 | T040–T046 + `npm run gen:api` |
| T060–T064 | T050–T056 |

## Notas de implementación

- **Valores fijos del MVP**: `recargo_ayudante = 30000.00` y `recargo_escalera = 15000.00`.
  Se cargan en la fila singleton de la migración, no como constantes Python.
- **Históricos**: se conservan `distancia_total_km`, `km_franquicia` y `km_excedente` con su
  valor original; solo las altas nuevas usan `km_estimados`, `0` y `0`.
- **Shim de Fase 1**: hasta completar Fase 2/3, `servicio_repo` mapea `km_estimados` y
  `precio_acordado` a los nombres viejos del dominio y completa `precio_sugerido = precio_acordado`.
  El shim se elimina en T021/T035.
