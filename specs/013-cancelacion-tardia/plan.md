# Implementation Plan: 013 — Política de cancelación tardía

**Branch**: `feature/013-cancelacion-tardia` | **Date**: 2026-11-01 | **Spec**:
[spec.md](./spec.md)

**Status**: Aprobado — implementación backend completada; migración pendiente de aplicar y CI final pendiente

## Resumen

Extender la operación de cancelación de servicios para registrar, desde el backend, una retención
equivalente al 30 % del valor total del viaje a favor del chofer asignado cuando falten dos horas
o menos para el inicio programado. La implementación debe preservar la cancelación existente de
H8 y ser atómica, auditable y no duplicable.

El porcentaje se calcula sobre `Servicio.precio_total`. Se persiste `compensacion_chofer` en el
snapshot del servicio, sin crear un pago o movimiento de cuenta corriente/rendición. El umbral usa
`America/Argentina/Buenos_Aires`; sin hora de inicio, sin chofer o con inicio ya pasado se conserva
la cancelación y se registra compensación cero.

## Contexto técnico

| Aspecto | Decisión / estado |
|---|---|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0 y Pydantic v2 |
| Persistencia | PostgreSQL 16 y Alembic; migración `0007` creada con backfill a cero |
| Contrato | OpenAPI de FastAPI; regenerar los tipos de frontend solo si cambia un contrato consumido por UI |
| Pruebas | Pytest unitario para reglas de Aplicación/Dominio e integración de API contra PostgreSQL |
| Alcance | Backend y persistencia de la regla; frontend y flujo de autenticación de clientes fuera de alcance salvo decisión aprobada |
| Estado | Especificación aprobada; backend implementado. No se aplicó la migración a una base de datos. |

## Revisión de Constitución

| Principio | Resultado | Aplicación |
|---|---|---|
| I. Spec Before Code | PASS | Spec y plan aprobados por Tech Lead antes de implementar. |
| II. Capas y Puertos | PASS | La regla temporal/económica vive en Aplicación/Dominio; los repositorios persisten mediante puertos. Los routers validan y delegan. |
| III. API como contrato | PASS | Si el contrato de cancelación o lectura expone la retención, OpenAPI será la fuente y se regenerarán los tipos. |
| IV. Testing | PASS | Cubrir límites del umbral, cálculo, atomicidad, idempotencia/reintentos y casos inválidos. |
| V. Simplicidad y trazabilidad | PASS | Reutilizar la cancelación actual y evitar crear una abstracción contable antes de aprobar el destino del importe. |

## Diseño por capas aprobado

### Aplicación y Dominio

- Extender el caso de uso existente de cancelación sin duplicar la máquina de estados.
- Comparar la hora de cancelación del servidor con `fecha + hora_inicio`; el criterio exacto de
  zona horaria será `America/Argentina/Buenos_Aires`.
- Calcular el 30 % de `precio_total` con `Decimal` y `ROUND_HALF_UP`. Solo aplica si
  `0 <= inicio_programado - ahora <= 2 horas` y hay chofer asignado.
- Sin horario, sin chofer o con inicio pasado, cancelar con snapshot `compensacion_chofer=0`.
- Inyectar el instante actual para que el umbral sea determinista en tests.

### Infraestructura

- `compensacion_chofer` forma parte del modelo ORM y del dominio de Servicio, con valor inicial
  cero y persistencia en la misma actualización atómica que la cancelación.
- La migración `0007_compensacion_chofer_cancelacion_tardia` agrega la columna, aplica backfill a
  cero y puede revertirse. No se ejecutó contra ninguna base de datos.
- No crear ledger, pago ni movimiento de rendición; la columna es únicamente el importe snapshot
  atribuido al chofer asignado al servicio.

### Presentación y contrato

- `PATCH /api/servicios/{id}/cancelar` calcula y devuelve el snapshot en la respuesta.
- `ServicioRead` expone `compensacion_chofer`; los schemas de escritura rechazan ese campo para que
  el cliente no pueda controlar el importe.
- Mantener los permisos existentes hasta que se apruebe un flujo de cancelación iniciada por el
  cliente.

## Archivos y superficies candidatas

| Superficie | Cambio implementado |
|---|---|
| `backend/app/application/servicios/gestor_servicios.py` | Inyecta el instante actual en hora de Buenos Aires y delega la cancelación al dominio. |
| `backend/app/domain/servicio.py` | Calcula y valida el snapshot durante la cancelación. |
| `backend/app/api/schemas/servicio.py` | Expone `compensacion_chofer` en lectura; los requests no admiten el importe. |
| `backend/app/infrastructure/models/servicio.py` y `servicio_repo.py` | Persisten el snapshot junto con estado y motivo en la misma actualización. |
| `backend/alembic/versions/0007_compensacion_chofer_cancelacion_tardia.py` | Migración reversible con backfill a cero para servicios existentes. |
| `backend/tests/unit/` y `backend/tests/integration/` | Cobertura de regla, elegibilidad, persistencia de API, contrato y reintento. |
| `frontend/src/types/openapi.d.ts` | Sincronizado con el campo de respuesta agregado. |

## Estrategia de verificación

1. Los tests focalizados de aplicación y API pasaron (28 tests), incluidos límite exacto,
   elegibilidad, rechazo de importe cliente y persistencia API.
2. Ruff pasó en todo el backend; los tipos OpenAPI se regeneraron, `npm run typecheck` pasó y
   Vitest pasó (96 tests).
3. El test de integración de cancelación pasó (1 test); la cadena Alembic reconoce `0007` como
   `head`.
4. `npm run verificar` no completó porque el chequeo global de Prettier reporta 127 archivos del
   frontend con formato previo no conforme. No se formateó el repositorio fuera de alcance.
5. No se ejecutó upgrade/downgrade ni se aplicó la migración a una base de datos. Completar CI y
   aplicar la migración en el entorno autorizado antes de cerrar formalmente el ticket.

## Alcance no incluido

No se genera un pago ni se modifica cuenta corriente/rendición. El flujo sigue siendo la operación
administrativa de cancelación existente; la directiva no crea un endpoint de cliente.
