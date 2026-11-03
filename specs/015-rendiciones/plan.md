# Implementation Plan: 015 — Registro y liquidación de rendiciones

**Branch**: `015-rendiciones` | **Date**: 2026-11-03 | **Spec**: [spec.md](./spec.md)

**Status**: Propuesta — pendiente de aprobación del Tech Lead antes de escribir código

## Resumen

Agregar la historia de rendiciones como un vertical slice completo sobre el monolito modular:
entidad de Dominio con estados y cálculo de saldo, puerto y gestor de Aplicación, modelo y
repositorio SQLAlchemy, migración `0008`, router admin-only con cuatro endpoints y reemplazo del
prototipo estático de `/rendiciones` por Server Components + Server Actions.

La rendición se apoya en el servicio ya persistido: de ahí toma chofer y fecha, y la elegibilidad
exige que el servicio tenga chofer y esté `finalizado` o `cobrado`. El backend calcula `codigo`,
`gastos_total` y `saldo`; el contrato de alta rechaza cualquier intento de enviarlos.

## Contexto técnico

| Aspecto | Decisión |
|---|---|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, `Decimal` |
| Persistencia | PostgreSQL 16; Alembic `0008_crear_rendiciones` con `down_revision = "0007"` |
| Contrato | OpenAPI de FastAPI; regenerar `src/types/openapi.d.ts` |
| Pruebas | Pytest unitario con fakes + API contra PostgreSQL; Vitest + RTL en frontend |
| Auth | `require_rol(ROL_ADMIN)` en todas las rutas |
| Frontend | Next.js 16 App Router, Server Actions y `requestAutenticado` |

## Revisión de Constitución

| Principio | Resultado | Aplicación |
|---|---|---|
| I. Spec Before Code | PASS | Este plan y la spec se aprueban antes de implementar. |
| II. Capas y Puertos | PASS | Reglas en Dominio/Aplicación; el router solo valida y delega; SQLAlchemy queda en Infraestructura. |
| III. API como contrato | PASS | Endpoints y schemas Pydantic documentados en OpenAPI; tipos regenerados. |
| IV. Testing | PASS | Se cubren cálculo, elegibilidad, unicidad, transición, contrato y UI. |
| V. Simplicidad y trazabilidad | PASS | Una tabla, cuatro endpoints, sin ledger ni pagos; auditoría estándar del proyecto. |

## Diseño por capas

### Dominio — `backend/app/domain/rendicion.py`

- Constantes `ESTADOS_RENDICION = ("pendiente", "en revision", "aprobada")`, `OBSERVACIONES_MAX = 500`.
- Entidad `Rendicion` con `id`, `codigo`, `id_servicio`, `id_chofer`, `fecha`, `tarifa`,
  `adelanto`, `gasto_combustible`, `gasto_peajes`, `gasto_otros`, `observaciones`, `estado` y
  auditoría.
- `crear(...)` valida importes finitos y no negativos, observaciones y estado inicial
  `pendiente`.
- Propiedades `gastos_total` y `saldo` con `Decimal` y `ROUND_HALF_UP`.
- `cambiar_estado(estado, modificado_por_id)` valida contra `ESTADOS_RENDICION`.
- Errores nuevos en `backend/app/domain/errores.py`: `RendicionNoEncontrada` (404),
  `ServicioNoRendible` (409), `ServicioYaRendido` (409) y `RendicionInvalida` (422).

### Aplicación — `backend/app/application/rendiciones/`

- `puertos.py`: `RendicionRepository` con `crear`, `obtener_por_id`, `listar`, `contar`, `resumen`,
  `actualizar` y `existe_para_servicio`; `ConsultaServiciosRendibles` con `listar_elegibles` y
  `obtener_para_rendir`.
- `gestor_rendiciones.py`:
  - `registrar(...)`: obtiene el servicio, valida elegibilidad y chofer, construye la entidad y
    delega la persistencia.
  - `listar(...)`: devuelve página + resumen.
  - `obtener(...)`.
  - `cambiar_estado(...)`.
  - `listar_servicios_elegibles(...)`.

### Infraestructura

- `models/rendicion.py`: tabla `rendiciones` con PK `Identity()`, FK a `servicios.id` y
  `choferes.id` (`ondelete="RESTRICT"`), `codigo` `String(16)` único, `fecha` `Date`,
  importes `Numeric(12,2)`, `estado` `String(20)`, `observaciones` `String(500)`, auditoría
  `TIMESTAMPTZ` y FKs a `usuarios`.
- Restricciones: `UNIQUE(id_servicio)`, `UNIQUE(codigo)`, checks de importes no negativos,
  estado válido y observaciones de hasta 500 caracteres; índice por `estado`.
- `repositories/rendicion_repo.py`: mapeo dominio ↔ ORM, listado con joins a `servicios`,
  `choferes` y `clientes` para devolver nombres; consulta de elegibles con `NOT EXISTS` sobre
  rendiciones; resumen con `SUM` condicional.
- `models/__init__.py` y `db/bootstrap.py`: registrar el modelo y sumar `rendiciones` a
  `_TABLAS_AUDITORIA`.
- `scripts/seed.py`: borrar rendiciones antes de servicios y crear demostraciones para dos o tres
  servicios finalizados con chofer.

### Presentación — `backend/app/api/`

- `schemas/rendicion.py`:
  - `GastosInformados` (`combustible`, `peajes`, `otros`, default 0, `ge=0`).
  - `RendicionCreate` (`extra="forbid"`): `id_servicio`, `tarifa`, `adelanto`,
    `gastos_informados`, `observaciones`.
  - `RendicionEstadoUpdate`: `estado` como `Literal`.
  - `RendicionRead`: campos derivados y nombres de chofer/cliente/servicio.
  - `RendicionListado(Pagina[RendicionRead])` + `ResumenRendiciones`.
  - `ServicioElegibleRead`.
- `api/rendiciones.py`, prefijo `/api/rendiciones`, `tags=["rendiciones"]`:
  - `GET ""` → listado paginado con `q`, `page`, `size`.
  - `GET "/servicios-elegibles"` → servicios rendibles.
  - `POST ""` → 201.
  - `PATCH "/{rendicion_id}/estado"` → cambio de estado.
- Registrar el router en `main.py`.
- `core/dependencias.py`: `get_repo_rendiciones`, `get_consulta_servicios_rendibles` y
  `get_gestor_rendiciones`.

### Migración

- `backend/alembic/versions/0008_crear_rendiciones.py` con `revision = "0008"` y
  `down_revision = "0007"`; `create_table`, constraints e índices; `downgrade` elimina la tabla.
- No se ejecuta `upgrade` contra bases reales sin autorización; el entorno de integración usa
  `Base.metadata.create_all`.

### Frontend

- `src/lib/api/rendiciones.ts`: `listarRendiciones`, `listarServiciosElegibles`,
  `crearRendicion`, `cambiarEstadoRendicion`, usando `requestAutenticado`.
- `src/features/rendiciones/types.ts`: re-export de tipos generados.
- `src/features/rendiciones/actions.ts`: `guardarRendicion` y `aprobarRendicion` con
  `ResultadoAccion`, `revalidatePath("/rendiciones")` y mapeo de errores a mensajes.
- `src/app/(admin)/rendiciones/page.tsx`: Server Component que carga datos y delega la
  interactividad a componentes cliente; conserva el diseño visual actual, reemplaza filas y KPIs
  por datos reales; el modal de alta usa un `<select>` de servicios elegibles y muestra el chofer
  derivado; el detalle muestra el desglose de gastos y el botón de aprobar.

## Contratos principales

```text
GET /api/rendiciones?q=&page=1&size=20
→ { items: RenderRendicion[], total, page, size, resumen: {...} }

GET /api/rendiciones/servicios-elegibles
→ ServicioElegibleRead[]

POST /api/rendiciones
{ id_servicio, tarifa, adelanto, gastos_informados: { combustible, peajes, otros }, observaciones? }
→ 201 RendicionRead

PATCH /api/rendiciones/{id}/estado
{ estado: "pendiente" | "en revision" | "aprobada" }
→ RendicionRead
```

## Archivos afectados

| Archivo | Cambio |
|---|---|
| `backend/app/domain/rendicion.py` | Nuevo: entidad, estados y saldo. |
| `backend/app/domain/errores.py` | Nuevos errores de rendición. |
| `backend/app/application/rendiciones/puertos.py` | Nuevo: puertos. |
| `backend/app/application/rendiciones/gestor_rendiciones.py` | Nuevo: reglas de negocio. |
| `backend/app/infrastructure/models/rendicion.py` | Nuevo: ORM. |
| `backend/app/infrastructure/models/__init__.py` | Registrar el modelo. |
| `backend/app/infrastructure/repositories/rendicion_repo.py` | Nuevo: persistencia y consultas. |
| `backend/app/infrastructure/db/bootstrap.py` | Modelo y auditoría. |
| `backend/alembic/versions/0008_crear_rendiciones.py` | Nueva migración. |
| `backend/app/api/schemas/rendicion.py` | Nuevos schemas. |
| `backend/app/api/rendiciones.py` | Nuevo router. |
| `backend/app/main.py` | Incluir router. |
| `backend/app/core/dependencias.py` | Factories y DI. |
| `backend/scripts/seed.py` | Datos de demostración. |
| `backend/tests/unit/domain/test_rendicion.py` | Cálculo y validaciones. |
| `backend/tests/unit/application/rendiciones/` | Gestor con fakes. |
| `backend/tests/unit/test_h15_rendiciones_api.py` | Contrato y códigos HTTP. |
| `backend/tests/integration/test_rendiciones.py` | Persistencia, unicidad y resumen. |
| `frontend/src/lib/api/rendiciones.ts` | Cliente HTTP. |
| `frontend/src/features/rendiciones/types.ts` | Tipos. |
| `frontend/src/features/rendiciones/actions.ts` | Server Actions. |
| `frontend/src/features/rendiciones/components/` | Tabla, modales y formulario. |
| `frontend/src/app/(admin)/rendiciones/page.tsx` | Pantalla real. |
| `frontend/tests/rendiciones.test.tsx` | Flujo de listado, alta y aprobación. |
| `frontend/src/types/openapi.d.ts` | Regenerado con `npm run gen:api`. |

## Estrategia de verificación

1. `pytest tests/unit` con foco en saldo, estados, elegibilidad y unicidad.
2. `pytest tests/integration` para alta real, duplicado (`409`), servicio sin chofer (`422`),
   listado con resumen y cambio de estado.
3. `ruff check app tests`.
4. `npm run verificar` en `frontend` (lint, format, typecheck y Vitest).
5. `npm run gen:api` sin diff inesperado y `npm run build` si el tiempo lo permite.
6. Prueba manual de `/rendiciones`: alta, búsqueda, detalle y aprobación con backend real.

## Riesgos y decisiones abiertas

- **Tarifa**: se recibe como importe libre porque el modelo de servicios no tiene una “tarifa del
  chofer” separada de `precio_total`. `compensacion_chofer` no se reutiliza porque representa una
  retención por cancelación tardía.
- **Saldo negativo**: se permite para reflejar que el chofer debe devolver dinero; la UI lo
  muestra con signo. Si el cliente prefiere bloquearlo, se ajusta la spec antes de codificar.
- **Transiciones**: el PATCH acepta cualquier estado válido, sin máquina de transiciones, porque la
  directiva no definió restricciones. Si se exige un flujo estricto, se agrega antes de implementar.
- **Exportar CSV**: el botón queda deshabilitado o fuera de alcance en esta historia.

## Alcance no incluido

No se crean pagos, movimientos de caja, asientos contables ni cambios en `saldo_a_favor`. No se
editan ni eliminan rendiciones. No se modifica la máquina de estados de servicios.
