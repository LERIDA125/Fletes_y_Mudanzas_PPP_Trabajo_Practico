# Implementation Plan: 013 — Política de cancelación tardía

**Branch**: `feature/013-cancelacion-tardia` | **Date**: 2026-11-01 | **Spec**:
[spec.md](./spec.md)

**Status**: Implementación local completada; migración pendiente de aplicar y CI/aprobación pendientes

## Resumen

Extender la operación de cancelación de servicios para registrar, desde el backend, una retención
equivalente al 30 % del valor total del viaje a favor del chofer asignado cuando falten dos horas
o menos para el inicio programado. Además del snapshot de compensación, se acredita el mismo
importe en `choferes.saldo_a_favor`. La implementación debe preservar la cancelación existente de
H8 y confirmar la cancelación, el snapshot y el saldo de forma atómica.

El porcentaje se calcula sobre `Servicio.precio_total`. Se persiste `compensacion_chofer` en el
snapshot del servicio y se incrementa el saldo del chofer asignado, sin crear un pago ni movimiento
de rendición. El umbral usa `America/Argentina/Buenos_Aires`; sin hora de inicio, sin chofer o con
inicio ya pasado se conserva la cancelación y se registra compensación cero.

## Contexto técnico

| Aspecto | Decisión / estado |
|---|---|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0 y Pydantic v2 |
| Persistencia | PostgreSQL 16 y Alembic; migración `0007` creada con backfill a cero |
| Contrato | OpenAPI de FastAPI; regenerar los tipos de frontend solo si cambia un contrato consumido por UI |
| Pruebas | Pytest unitario para reglas de Aplicación/Dominio e integración de API contra PostgreSQL |
| Alcance | Backend y persistencia de la regla; frontend y flujo de autenticación de clientes fuera de alcance salvo decisión aprobada |
| Estado | Enmienda de alcance aprobada e implementada localmente. No se aplicó la migración a una base de datos; CI y aprobación siguen pendientes. |

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
- Si la compensación es positiva, el gestor obtiene el chofer asignado mediante el puerto de
  choferes, suma el importe a `saldo_a_favor` y prepara la actualización del servicio. La lectura
  del servicio para cancelar toma un bloqueo de fila; así, cancelaciones concurrentes no pueden
  acreditar dos veces. Los dos repositorios comparten la `Session` de la request; la actualización
  del chofer confirma una sola transacción que incluye también el servicio. Si falla el commit, no
  queda persistido ninguno de los cambios.
- Para una cancelación sin compensación se conserva la actualización normal del servicio. La
  escritura del saldo solo se realiza cuando la cancelación produjo una compensación positiva.
- La migración `0007_compensacion_chofer_cancelacion_tardia` agrega la columna, aplica backfill a
  cero y puede revertirse. No se ejecutó contra ninguna base de datos.
- No crear ledger, pago ni movimiento de rendición; el snapshot del servicio y el saldo a favor del
  chofer conservan la trazabilidad de la compensación.

### Presentación y contrato

- `PATCH /api/servicios/{id}/cancelar` calcula y devuelve el snapshot en la respuesta.
- `ServicioRead` expone `compensacion_chofer`; los schemas de escritura rechazan ese campo para que
  el cliente no pueda controlar el importe.
- Mantener los permisos existentes hasta que se apruebe un flujo de cancelación iniciada por el
  cliente.

## Archivos y superficies candidatas

| Superficie | Cambio implementado |
|---|---|
| `backend/app/application/servicios/gestor_servicios.py` | Inyecta el instante actual, delega el cálculo al dominio y coordina la acreditación del saldo con los repositorios. |
| `backend/app/domain/servicio.py` | Calcula y valida el snapshot durante la cancelación. |
| `backend/app/api/schemas/servicio.py` | Expone `compensacion_chofer` en lectura; los requests no admiten el importe. |
| `backend/app/infrastructure/models/servicio.py`, `servicio_repo.py` y `chofer_repo.py` | Persisten snapshot, estado, motivo y saldo del chofer en una única transacción de la `Session` compartida. |
| `backend/alembic/versions/0007_compensacion_chofer_cancelacion_tardia.py` | Migración reversible con backfill a cero para servicios existentes. |
| `backend/tests/unit/` y `backend/tests/integration/` | Cobertura de regla, elegibilidad, persistencia del snapshot y saldo, atomicidad, contrato y reintento. |
| `backend/tests/unit/test_h8_servicios_api.py` | Comprueba que el saldo persistido del chofer aumenta exactamente por el snapshot acreditado. |
| `frontend/src/types/openapi.d.ts` | Sincronizado con el campo de respuesta agregado. |

## Estrategia de verificación

1. Verificar los tests focalizados de aplicación y API: cálculo en el umbral, rechazo de importe
   cliente, saldo acreditado exactamente una vez y persistencia del snapshot.
2. Verificar que ambas actualizaciones se confirman mediante una sola transacción y que un fallo
   de persistencia revierte tanto la cancelación como el saldo.
3. Ejecutar Ruff y la suite backend relevante; confirmar que la cadena Alembic reconoce `0007` como
   `head`.
4. No ejecutar upgrade/downgrade ni aplicar la migración a una base de datos sin autorización.

## Alcance no incluido

No se genera un pago ni se modifica la rendición. La compensación sí incrementa
`choferes.saldo_a_favor`. El flujo sigue siendo la operación administrativa de cancelación
existente; la directiva no crea un endpoint de cliente.
