# Requirements Quality Checklist: H13 — Migración de Datos Históricos

**Purpose**: Verificar la calidad de los requisitos de la historia H13 antes y después de su implementación.
**Created**: 2026-10-21
**Feature**: [spec.md](../spec.md) — [plan.md](../plan.md) — [tasks.md](../tasks.md)
**Historia**: H13 · **Rama**: `feature/H13-migracion-datos-historicos` · **Directorio**: `specs/002-migracion-datos-historicos`

**Note**: Artefacto de revisión de calidad de requisitos, propiedad del revisor. `[x]` significa que el
criterio fue revisado y satisfecho **en calidad de requisito**; no significa que el trabajo de
implementación esté terminado.
**Estado de la revisión retrospectiva**: 2026-10-21 — los ítems marcados se verificaron contra el
código real de `backend/scripts/migracion/`; los que quedan sin marcar requieren decisión del Tech Lead.

## A. Claridad y completitud de la spec

- [x] CHK001 El *Input* describe el problema de los datos de origen con detalle suficiente
- [x] CHK002 La spec enumera los problemas concretos del archivo de origen (formatos, prefijos, unidades, monedas)
- [x] CHK003 La spec define el comportamiento esperado ante un dato que no se puede resolver con confianza
- [x] CHK004 *Out of Scope* delimita explícitamente lo que la migración NO hace
- [x] CHK005 La spec define qué se hace con los datos que no pueden mapearse (no se los descarta en silencio)

## B. Trazabilidad

- [x] CHK006 Cada regla de normalización de la spec tiene su contraparte en el código
- [x] CHK007 El plan.md describe el pipeline etapa por etapa con los módulos concretos
- [x] CHK008 El tasks.md cubre implementación, tests y documentación
- [x] CHK009 El quickstart.md explica cómo correr la migración y cómo leer el reporte
- [x] CHK010 El `**Feature Branch**` declarado en la spec coincide con la rama real del repositorio

## C. Conformidad con la Constitución

- [x] CHK011 La migración no inventa reglas de negocio para resolver ambigüedad (Principio I)
- [x] CHK012 Los datos ambiguos quedan señalados para revisión humana, no corregidos por heurística silenciosa
- [x] CHK013 Los catálogos usados por la normalización están en un módulo único y versionable
- [x] CHK014 La migración es idempotente o su reejecución está documentada de forma explícita
- [x] CHK015 Los importes se interpretan con precisión decimal, nunca con `float` binario

## D. Criterios de aceptación verificables

- [ ] CHK016 Existe test unitario por etapa del pipeline
- [ ] CHK017 Existe test de integración que corre el pipeline completo sobre datos de prueba
- [x] CHK018 El reporte de migración enumera los registros descartados o pendientes y su motivo
- [x] CHK019 La carga respeta las entidades del dominio o documenta por qué no

## E. Cierre

- [x] CHK020 El reporte de migración generado queda versionado como evidencia del resultado
- [x] CHK021 Los casos que quedaron sin resolver están listados para el cliente, no archivados en silencio

## Evidencia de la verificación retrospectiva (2026-10-21)

Ítems marcados y dónde se verificó:

| Ítem | Evidencia |
|---|---|
| CHK001 | `## Contexto del repositorio al momento de esta historia` (`spec.md:11-26`) + `**Input**` |
| CHK002 | FR-001..FR-038 (formatos de fecha, códigos, teléfonos, montos, monedas, unidades de carga), sección `### Gaps de mapeo` (`spec.md:358`) y las 20 transformaciones documentadas en `reporte.py` |
| CHK003 | US3 "Saber qué se transformó y qué falta decidir" (`spec.md:106`) + la estructura `ColaDeRevision` con `Motivo` y `Gravedad` |
| CHK004 | `## Out of Scope` (`spec.md:27-42`) |
| CHK005 | `## Plan de implementación` → "Contrato entre los módulos" (`spec.md:438`): todo caso dudoso viaja en la cola de revisión con su valor original intacto |
| CHK006 | Tabla de reglas en `plan.md` §3.2, con el patrón literal de cada una y su archivo (`normalizacion.py`) |
| CHK007 | `plan.md` §3, con el diagrama de las 6 etapas y los 9 módulos (`plan.md` nuevo, retrospectivo) |
| CHK008 | `tasks.md`: 8 fases + "Trazabilidad FR ↔ test (T038)" + Definition of Done |
| CHK009 | `quickstart.md`: los 3 modos, la tabla de parámetros, "Qué se carga y qué no" y "Antes de tomar la base como fuente de verdad" (explica la sección de bloqueantes) |
| CHK010 | Spec declara `feature/H13-migracion-datos-historicos`; la rama existe en `origin` y el merge es `9ce322f` (PR #2) |
| CHK011 | El diseño entero de la historia es "no decidir": `Motivo` con 9 miembros, `Gravedad` con 2, y las funciones de normalización devuelven `(None, motivo)` cuando no saben |
| CHK012 | `ColaDeRevision` con `RevisionHumana(hoja, fila, clave, motivo, gravedad, valor_original, detalle)`; el original **nunca** se sobrescribe |
| CHK013 | `backend/scripts/migracion/catalogos.py` (246 líneas) — único módulo de catálogos; **no importa nada de `app/`** (solo `from __future__` y `typing`) |
| CHK014 | `carga.py` consulta `repo.existe_razon_social(cliente.razon_social_key)` antes de insertar y trata `RazonSocialDuplicada` como "ya existente"; sección `### Idempotencia` de la spec (`spec.md:450`) |
| CHK015 | 50 apariciones de `Decimal` en `backend/scripts/migracion/` (48 usos reales, 2 en `import`), concentradas en `normalizacion.py` (31), `transformacion.py` (8) y `reporte.py` (5). Las **3** apariciones de `float` están en guardas `isinstance(valor, (int, float, Decimal))` (`normalizacion.py:374,433,468`) que convierten **inmediatamente** con `Decimal(str(valor))` — no hay aritmética binaria |
| CHK018 | `reporte.py` genera 8 secciones; la 7ª lista `## Bloqueantes (N)` y `## Para confirmar (N)` con motivo, gravedad y valor original |
| CHK019 | `carga.py` arma la entidad con `Cliente.crear(...)` (API de H1) y escribe por `ClienteRepo`. No redefine ni modifica la entidad `Cliente` |
| CHK020 | `backend/data/reporte_migracion.md` versionado: 10 clientes, 8 móviles, 10 viajes, 37 casos (5 bloqueantes + 32 por confirmar) |
| CHK021 | El reporte versionado es la lista abierta para el cliente, con los 5 casos bloqueantes identificados |

Ítems sin marcar y por qué (requieren decisión del Tech Lead):

- **CHK016** — La suite quedó comprimida a **1 sola función de test**
  (`test_migracion_h13_completa(tmp_path)` en `backend/tests/unit/scripts/migracion/test_migracion.py`),
  que cubre normalización, transformación, reporte, carga e idempotencia en un solo flujo. Los commits
  `14648e6` y `60f9e4f` comprimieron lo que eran 10 archivos de test. **No hay un test por etapa del
  pipeline**, y la tabla de trazabilidad FR↔test del `tasks.md` quedó obsoleta.
- **CHK017** — **No hay test de integración del pipeline completo sobre el Excel real.** El directorio
  `raw-data/` no está en el repo (es el insumo de la cátedra, excluido por `.gitignore`), así que la
  rama `if archivo_excel.exists():` del test **nunca se ejecuta en CI**. En consecuencia, las
  aserciones `10 clientes / 8 móviles / 10 viajes / 37 casos` **no se validan automáticamente**.
  Compensa que el reporte generado sí quedó versionado (CHK020) como evidencia congelada del
  resultado, pero no es un test.

## Notes

- Los ítems se marcan `[x]` solo tras verificar el criterio contra el código o la spec.
- Los datos sucios son parte del problema de negocio: corregirlos sin regla confirmada es automatizar una regla abierta.
