# Requirements Quality Checklist: H4 — Gestión de Vehículos y Tipos de Vehículo

**Purpose**: Verificar la calidad de los requisitos de la historia H4 antes y después de su implementación.
**Created**: 2026-10-21
**Feature**: [spec.md](../spec.md) — [plan.md](../plan.md)
**Historia**: H4 · **Rama**: `feature/H4-gestion-vehiculos` · **Directorio**: `specs/003-gestion-vehiculos`

**Note**: Artefacto de revisión de calidad de requisitos, propiedad del revisor. `[x]` significa que el
criterio fue revisado y satisfecho **en calidad de requisito**; no significa que el trabajo de
implementación esté terminado.
**Estado de la revisión retrospectiva**: 2026-10-21 — los ítems marcados se verificaron contra el
código real de `backend/`; los que quedan sin marcar requieren decisión del Tech Lead.

## A. Claridad y completitud de la spec

- [x] CHK001 Cada User Story tiene criterios de aceptación en formato Dado/Cuando/Entonces
- [x] CHK002 Los criterios de aceptación de la relación vehículo–tipo de vehículo están explícitos
- [x] CHK003 La spec define qué ocurre al dar de baja un tipo de vehículo con vehículos asociados
- [x] CHK004 La spec define qué ocurre al dar de baja un vehículo con servicios asociados
- [x] CHK005 *Out of Scope* delimita explícitamente lo que esta historia NO implementa
- [ ] CHK006 La spec distingue entre "chofer habitual" y "chofer asignado a un servicio"

## B. Trazabilidad

- [x] CHK007 Cada requisito funcional (FR) tiene al menos un endpoint asociado
- [x] CHK008 El plan.md describe las 4 capas con los archivos concretos que crea o modifica
- [ ] CHK009 El tasks.md cubre implementación, tests y documentación
- [x] CHK010 El `**Feature Branch**` declarado en la spec coincide con la rama real del repositorio

## C. Conformidad con la Constitución

- [x] CHK011 No hay reglas de negocio en `app/api/` (Principio II)
- [x] CHK012 La capa de Aplicación no importa SQLAlchemy ni FastAPI; habla solo por puertos (Principio II)
- [x] CHK013 La baja es lógica con flag `activo` y la fila no se borra físicamente (DD-1)
- [ ] CHK014 La unicidad de patente y de descripción se resuelve con clave normalizada `*_key` (DD-2)
- [x] CHK015 La autorización se consume por `require_rol` y ningún handler lee el rol directamente (DD-3)
- [x] CHK016 La modificación es `PUT` completo y repite los campos obligatorios del alta (DD-5)
- [x] CHK017 Las tarifas base por hora y por km del tipo de vehículo NO están hardcodeadas en el código (Principio: tarifas en tabla de configuración)
- [x] CHK018 Las consultas a otras entidades (chofer habitual, tipo de vehículo) van por puertos, no por joins en infraestructura

## D. Criterios de aceptación verificables

- [ ] CHK019 Existe test unitario de la capa de Aplicación por cada criterio de aceptación
- [x] CHK020 Existe test de integración del endpoint contra PostgreSQL real
- [x] CHK021 Los listados devuelven el esquema genérico `Pagina[T]`
- [x] CHK022 Los errores de dominio heredan de la jerarquía base y se traducen a 404 / 409 / 422
- [x] CHK023 Los schemas de escritura usan `extra="forbid"` y no aceptan campos de sistema

## E. Cierre

- [ ] CHK024 La spec quedó estable: cualquier cambio posterior a la implementación está documentado en la spec
- [x] CHK025 Los stubs heredados de esta historia están identificados y su reemplazabilidad es explícita

## Evidencia de la verificación retrospectiva (2026-10-21)

Ítems marcados y dónde se verificó:

| Ítem | Evidencia |
|---|---|
| CHK001 | 8 User Stories, 39 escenarios, todos en Dado/Cuando/Entonces (`spec.md:29-217`) |
| CHK002 | US5.4 y US5.5; FR-014 y FR-015; Edge Case "un vehículo con tipo de vehículo dado de baja debe rechazarse" |
| CHK003 | US4.2, FR-011, y `TipoVehiculoConVehiculos` implementado en `GestorTiposVehiculo.eliminar` |
| CHK004 | US8.2, FR-021, y `VehiculoConServicios` implementado en `GestorVehiculos.eliminar` |
| CHK005 | `## Out of Scope` con 5 exclusiones (`spec.md:11-17`) |
| CHK007 | FR-001..FR-021 mapeados a los 10 endpoints de `app/api/vehiculos.py` y `app/api/tipos_vehiculo.py` |
| CHK008 | `plan.md` §3 y §9 (nuevo documento retrospectivo) |
| CHK010 | Spec declara `feature/H4-gestion-vehiculos`; el merge `f050ee5` (PR #3) viene de esa rama. La rama se borró tras el merge, así que la trazabilidad queda en el merge commit |
| CHK011 | Los 2 routers solo traducen HTTP y delegan; sin `if` de negocio |
| CHK012 | `app/application/vehiculos/` y `app/application/tipos_vehiculo/` no importan `sqlalchemy` ni `fastapi`; hablan por 6 `Protocol` |
| CHK013 | `desactivar()` en ambas entidades + UPDATE Core con `activo=False`; el test de integración asserta que tras el DELETE el GET da 404 |
| CHK015 | `require_rol(ROL_ADMIN)` en `dependencies=[...]` de las 3 rutas de escritura de cada router |
| CHK016 | `VehiculoUpdate(VehiculoCreate)` y `TipoVehiculoUpdate(TipoVehiculoCreate)` no redefinen campos; heredan `extra="forbid"` |
| CHK017 | Las 3 tarifas son columnas `NUMERIC` en `tipos_vehiculo`; no hay constantes de tarifa en el código |
| CHK018 | 6 puertos (`ConsultaTipoVehiculo`, `ConsultaChofer`, `ConsultaServiciosVehiculo`, `ConsultaVehiculosPorTipo` + 2 de repositorio); sin joins entre `vehiculos`, `tipos_vehiculo` y `choferes` |
| CHK020 | `tests/integration/api/test_vehiculos_api.py` con `SELECT` directo contra PostgreSQL |
| CHK021 | `VehiculoListado(Pagina[VehiculoRead])` y `TipoVehiculoListado(Pagina[TipoVehiculoRead])` |
| CHK022 | 8 errores de H4 cuelgan de `RecursoNoEncontrado`/`ConflictoOperacion`/`DatoInvalido`; 4 handlers en `app/main.py` |
| CHK023 | `VehiculoCreate`, `VehiculoUpdate`, `TipoVehiculoCreate` y `TipoVehiculoUpdate` con `ConfigDict(extra="forbid")` |
| CHK025 | `ConsultaServiciosVehiculoVacio` en `app/infrastructure/repositories/consulta_stub.py` con docstring "STUB temporal: devuelve False hasta que exista la historia de Servicios (H6)"; el provider en `dependencias.py` repite la advertencia |

Ítems sin marcar y por qué (requieren decisión del Tech Lead):

- **CHK006** — La distinción existe **implícitamente**: la spec usa siempre "chofer habitual" para el
  campo `id_chofer_habitual` y deja "Asignación de vehículos a servicios (H5/H6)" en *Out of Scope*.
  Pero nunca dice de forma explícita que **el chofer habitual NO es el chofer del servicio**. Basta
  agregar una línea en la spec para evitar un malentendido caro cuando llegue H6.
- **CHK009** — **No existe `tasks.md` para H4.** El código llegó por el commit `5e1a62f` sin commit de
  documentación, a diferencia de H3 (`7fa319e docs(H3): ...`). Tampoco existe `quickstart.md`. El
  `feature.json` de la historia ya refleja esa ausencia en `missing_artifacts`.
- **CHK014** — El requisito funcional **se cumple**, pero por un mecanismo distinto al que presupone
  la redacción del ítem: `descripcion_key` sí es una columna `UNIQUE` aparte (como en DD-2), mientras
  que `patente` no tiene columna `*_key` — se apoya en que `normalizar_patente` guarda el valor en
  mayúsculas y el `UNIQUE` y la búsqueda (`busqueda.upper()`) trabajan sobre esa forma canónica.
  **El ítem debería reformularse**, no el código: conmayúsculas no hay diferencia visual entre el
  dato mostrado y su clave.
- **CHK019** — La suite quedó comprimida a **3 tests unitarios** (`test_h4_dominio`,
  `test_h4_gestor_tipos_vehiculo`, `test_h4_gestor_vehiculos`) y 2 de integración. Los 39 escenarios
  de aceptación de las 8 User Stories no tienen un test por escenario.
- **CHK024** — La spec sigue con `**Status**: Draft` pese a estar implementada y mergeada. Además hay
  **tres divergencias post-implementación no documentadas en la spec**:
  1. La spec dice "la entidad completa de Chofer llega en **H2**" (`spec.md:13, 286, 308`), pero llegó
     como **H3** (`alembic/versions/0003_completar_choferes.py`).
  2. La spec no menciona que H4 creó la **tabla mínima `choferes`** para sostener el FK
     `id_chofer_habitual` — sí está documentado en la migración `0002`, en la `0003` y en el modelo
     ORM, pero no en la spec.
  3. El schema Pydantic acepta `patente` de **6 a 15 caracteres** mientras que la columna es
     `VARCHAR(10)`: una patente de 11 a 15 caracteres pasa la validación y revienta con
     `DataError` de PostgreSQL → **HTTP 500 en lugar de 422**. Es el único punto del backend donde un
     dato inválido produce error de servidor.

## Notes

- Los ítems se marcan `[x]` solo tras verificar el criterio contra el código o la spec.
- La historia dejó stubs para dependencias de historias futuras (servicios, choferes): documentarlos evita que se confundan con comportamiento real.
