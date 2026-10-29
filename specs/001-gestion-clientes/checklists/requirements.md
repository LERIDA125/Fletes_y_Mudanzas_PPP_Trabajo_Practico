# Requirements Quality Checklist: H1 — Gestión de Clientes

**Purpose**: Verificar la calidad de los requisitos de la historia H1 antes y después de su implementación.
**Created**: 2026-10-21
**Feature**: [spec.md](../spec.md) — [plan.md](../plan.md) — [tasks.md](../tasks.md)
**Historia**: H1 · **Rama**: `feature/H1-gestion-clientes` · **Directorio**: `specs/001-gestion-clientes`

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
- [x] CHK005 El *Input* de la spec describe el pedido del usuario sin imponer decisiones de implementación

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
- [x] CHK014 La unicidad y la búsqueda de razón social usan la clave normalizada `razon_social_key` (DD-2)
- [x] CHK015 La autorización se consume por `require_rol` y ningún handler lee el rol directamente (DD-3)
- [x] CHK016 La modificación es `PUT` completo y repite los campos obligatorios del alta (DD-5)
- [x] CHK017 `actualizado_en` se fuerza explícitamente en el repositorio (el `onupdate` no dispara solo)
- [x] CHK018 Las fechas de auditoría son `TIMESTAMPTZ` con `server_default now()`

## D. Criterios de aceptación verificables

- [ ] CHK019 Existe test unitario de la capa de Aplicación por cada criterio de aceptación
- [x] CHK020 Existe test de integración del endpoint contra PostgreSQL real
- [x] CHK021 El listado devuelve el esquema genérico `Pagina[ClienteRead]`
- [x] CHK022 Los errores de dominio heredan de la jerarquía base y se traducen a 404 / 409 / 422
- [x] CHK023 Los schemas de escritura usan `extra="forbid"` y no aceptan campos de sistema

## E. Cierre

- [ ] CHK024 La spec quedó estable: cualquier cambio posterior a la implementación está documentado en la spec
- [ ] CHK025 No quedó en el código ninguna regla de negocio que la spec deje como pendiente

## Evidencia de la verificación retrospectiva (2026-10-21)

Ítems marcados y dónde se verificó:

| Ítem | Evidencia |
|---|---|
| CHK001 | 4 User Stories, 18 escenarios, todos en formato Dado/Cuando/Entonces (`spec.md:36-141`) |
| CHK003 | `## Out of Scope` con 5 exclusiones (`spec.md:11-17`) |
| CHK004 | DP-01..DP-05, todas con `[Supuesto temporal]` (`spec.md:233-250`) |
| CHK005 | `**Input**` con descripción del usuario, sin decisiones técnicas (`spec.md:9`) |
| CHK006 | FR-001..FR-020 mapeados a los 5 endpoints de `app/api/clientes.py` |
| CHK007 | `plan.md` §3 y §9 (nuevo documento retrospectivo) |
| CHK008 | `tasks.md`: 62 tareas en 7 fases, con "Evidencia de Phase 7" y T057/T058/T061 |
| CHK009 | `quickstart.md`: prerrequisitos, opción A (Docker) y B (local), los 5 endpoints, errores esperados |
| CHK010 | Spec declara `feature/H1-gestion-clientes`; `git branch --show-current` devuelve lo mismo |
| CHK011 | `app/api/clientes.py` solo traduce HTTP y delega; sin `if` de negocio |
| CHK012 | `app/application/clientes/` no importa `sqlalchemy` ni `fastapi`; habla por `Protocol` |
| CHK013 | `Cliente.desactivar()` + `ClienteRepo.desactivar`; el test de integración asserta `activo IS false` y que la fila sigue en la base |
| CHK014 | `Cliente.razon_social_key` (property) → columna `VARCHAR(120) UNIQUE`; búsqueda con `contains(normalizar_razon_social(...))` |
| CHK015 | `require_rol(ROL_ADMIN)` en `dependencies=[...]` de las 3 rutas de escritura; los handlers no leen el header |
| CHK016 | `ClienteUpdate(ClienteCreate)` no redefine campos; hereda `extra="forbid"` |
| CHK017 | `cliente_repo.py:79-83` — `orm.actualizado_en = func.now()` forzado a mano, con el comentario de la lección |
| CHK018 | `DateTime(timezone=True)` + `server_default=func.now()` en el modelo y en la migración `0001` |
| CHK020 | `tests/integration/api/test_clientes_api.py` con `SELECT` directo contra PostgreSQL |
| CHK021 | `class ClienteListado(Pagina[ClienteRead])` |
| CHK022 | `ClienteNoEncontrado`/`RazonSocialDuplicada`/`ClienteConHistorial` cuelgan de la jerarquía base; 4 handlers en `app/main.py:38-67` |
| CHK023 | `ClienteCreate` y `ClienteUpdate` con `ConfigDict(extra="forbid")` |

Ítems sin marcar y por qué (requieren decisión del Tech Lead):

- **CHK002** — Dos criterios de aceptación no tienen test: US3.1 y US3.3 (la fecha de modificación es
  posterior a la de creación / se refresca al guardar datos idénticos) y el listado sin coincidencias
  devolviendo `total = 0`. La regla de la fecha está implementada (`cliente_repo.py:79-83`) pero sin
  cobertura.
- **CHK019** — La suite quedó comprimida a **2 tests unitarios** (`test_h1_dominio`,
  `test_h1_gestor_clientes`) y 2 de integración. El criterio "un test por criterio de aceptación"
  (SC-001) no se sostiene: 18 escenarios de aceptación se cubren con 4 funciones de test.
- **CHK024** — La spec sigue con `**Status**: Draft` pese a estar implementada y mergeada. Además,
  la divergencia entre el supuesto de la spec ("el sistema de autenticación JWT ya está disponible",
  `spec.md:274`) y la implementación real (stub `X-Rol`, DD-3) está documentada en AGENTS.md pero no
  en la spec.
- **CHK025** — **FR-015 es inerte en producción**: `HistorialClienteRepoVacio.tiene_historial` devuelve
  siempre `False`, así que ninguna baja queda bloqueada por historial. La regla está implementada y
  testeada en `GestorClientes.eliminar`; lo que falta es el dato, no la regla. Se cierra cambiando
  **solo** la inyección en `app/core/dependencias.py` cuando exista la historia de Servicios.

## Notes

- Los ítems se marcan `[x]` solo tras verificar el criterio contra el código o la spec.
- Un caso marcado como decisión pendiente en la spec se testea con `pytest.mark.skip`, nunca inventando comportamiento.
