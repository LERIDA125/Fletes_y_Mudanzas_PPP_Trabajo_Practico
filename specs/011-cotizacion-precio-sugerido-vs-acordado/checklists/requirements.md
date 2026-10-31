# Requirements Quality Checklist: H7 — Precio Sugerido vs Precio Acordado

**Purpose**: Verificar la calidad de los requisitos de la historia H7 antes de la implementación.
**Created**: 2026-10-30
**Feature**: [spec.md](../spec.md) — [plan.md](../plan.md)
**Historia**: H7 · **Rama objetivo**: `011-cotizacion-precio-sugerido-vs-acordado`
**Directorio**: `specs/011-cotizacion-precio-sugerido-vs-acordado`

**Note**: Artefacto de revisión de calidad de requisitos, propiedad del revisor. `[x]` significa
que el criterio fue revisado y satisfecho **en calidad de requisito**; no significa que el trabajo
de implementación esté terminado. El plan y el código todavía no existen en la rama objetivo.

## A. Claridad y completitud de la spec

- [x] CHK001 La spec tiene un resumen ejecutivo que explica el flujo de negocio de punta a punta
- [x] CHK002 Cada User Story tiene criterios de aceptación en formato Dado/Cuando/Entonces
- [x] CHK003 La fórmula base está escrita sin ambigüedad, sin franquicia y sin duplicar distancia
- [x] CHK004 Los cuatro modificadores tienen tipo, condición de aplicación y efecto explícitos
- [x] CHK005 La spec distingue con claridad `precio_sugerido` (calculado) de `precio_acordado` (ingresado)
- [x] CHK006 La spec define qué pasa si el acordado difiere del sugerido (no se ajusta ni rechaza)
- [x] CHK007 La regla de redondeo es determinística y verificable (`ROUND_HALF_UP`, 2 decimales)
- [x] CHK008 *Out of Scope* delimita cotizaciones persistidas, aprobaciones de descuento y H10
- [x] CHK009 La relación de supersesión con 008 está explícita y justificada
- [ ] CHK010 Los montos fijos de ayudante y escalera están confirmados por el cliente (hoy: supuesto temporal)

## B. Trazabilidad

- [x] CHK011 Cada requisito funcional (FR) tiene un endpoint, una capa o un test asociado
- [x] CHK012 El plan describe las 4 capas con archivos concretos que crea o modifica
- [x] CHK013 El plan identifica la migración Alembic siguiente (`0007`) y su `downgrade()`
- [x] CHK014 El plan declara el impacto breaking en API, OpenAPI, frontend y tests
- [x] CHK015 El `feature.json` refleja el estado real y los artefactos faltantes
- [ ] CHK016 El `tasks.md` descompone implementación, tests y documentación
- [ ] CHK017 El `ssd.md` incluye el flujo cálculo → autocompletado → alta (si el equipo lo exige)
- [x] CHK018 La rama objetivo coincide exactamente con el directorio del spec

## C. Conformidad con la Constitución

- [x] CHK019 No hay reglas de negocio ni aritmética en `app/api/` (Principio II)
- [x] CHK020 La Aplicación habla con la persistencia solo por puertos `Protocol` (Principio II)
- [x] CHK021 El Dominio no importa SQLAlchemy, FastAPI ni Pydantic (Principio II)
- [x] CHK022 Las tarifas y los importes/porcentajes de modificadores se leen de la base, no de constantes
- [x] CHK023 La fórmula se implementa como estrategia intercambiable, no como `if/else` en el router
- [x] CHK024 El frontend no recalcula cifras: muestra el desglose de la API (Principio III)
- [x] CHK025 El `precio_acordado` se justifica como dato de entrada comercial, no como cálculo derivado
- [x] CHK026 El contrato se regenera desde OpenAPI y se versiona el resultado (Principio III)
- [x] CHK027 Hay un test de Aplicación previsto por cada escenario de aceptación (Principio IV)
- [x] CHK028 El plan declara la enmienda de constitución necesaria antes de implementar (Principio IV/Governance)
- [ ] CHK029 La enmienda de constitución fue aprobada y versionada (v3.0.0 propuesta)
- [ ] CHK030 `AGENTS.md §2/§4/§6/§11` fue actualizado con la nueva fórmula y el nuevo modelo de precios

## D. Criterios de aceptación verificables

- [x] CHK031 El caso de referencia 11205.00 es reproducible y está en spec + plan + tests previstos
- [x] CHK032 Los flags en `false` producen un total sin fijos ni porcentajes
- [x] CHK033 Los porcentajes son aditivos (no compuestos) y el plan lo hace explícito
- [x] CHK034 Un vehículo/tipo inactivo o un payload con campos derivados responde 422
- [x] CHK035 El alta persiste el acordado exactamente y guarda el sugerido como snapshot
- [x] CHK036 El autocompletado del acordado se desactiva tras la primera edición manual
- [x] CHK037 Un fallo del cálculo no bloquea el alta si los campos son válidos
- [x] CHK038 Los servicios históricos conservan su importe final y reciben un sugerido de backfill
- [ ] CHK039 Existe test unitario de Aplicación por cada criterio de aceptación
- [ ] CHK040 Existe test de integración de `/api/cotizaciones/calcular` y del alta contra PostgreSQL
- [ ] CHK041 Existe test RTL del autocompletado, la edición manual y el payload del alta

## E. Riesgos y cierre

- [x] CHK042 El retiro de `POST /api/servicios/cotizar` está identificado como breaking change
- [x] CHK043 El renombre `precio_total` → `precio_acordado` y `distancia_ida_km` → `km_estimados` está documentado
- [x] CHK044 La validación `max_digits=12` evita un 500 por importe fuera de rango
- [x] CHK045 El plan conserva las columnas históricas de 008 para no perder trazabilidad
- [ ] CHK046 La spec quedó estable tras la implementación y cualquier divergencia está registrada
- [ ] CHK047 El PR declara el impacto en cada principio de la constitución y pasa el Constitution Check final

## F. Decisiones abiertas para el Tech Lead

- **CHK010** — Los importes fijos de `recargo_ayudante` y `recargo_escalera` no fueron definidos en
  la directiva. Se implementan como configuración en base de datos y quedan `[Supuesto temporal]`.
  El Tech Lead debe aprobar los valores de la fila singleton antes de la demo.
- **CHK016 / CHK017** — `tasks.md` y `ssd.md` no se redactaron todavía porque el gate de
  implementación está pendiente. Se completan después de la aprobación de `spec.md` + `plan.md`.
- **CHK029 / CHK030** — La enmienda de constitución y la actualización de `AGENTS.md` son
  **bloqueantes**: sin ellas, la historia automatiza una regla que la v2.0.0 lista como no
  confirmada y rompe el contrato de API sin registro de gobernanza.
- **CHK039–CHK041** — Los tests son requisito de la fase de implementación; no pueden marcarse
  antes de escribir el código.
- **CHK046 / CHK047** — Se verifican al cierre, no en la etapa de especificación.

## Notes

- Este checklist es forward-looking: a diferencia del de H4, todavía no hay código contra el cual
  verificar. Los ítems marcados se validaron contra `spec.md`, `plan.md`, la constitución y el
  código vigente de 008.
- El cambio de fórmula es una decisión de negocio confirmada por el Tech Lead, pero su
  formalización documental sigue el flujo de gobernanza de la constitución.
