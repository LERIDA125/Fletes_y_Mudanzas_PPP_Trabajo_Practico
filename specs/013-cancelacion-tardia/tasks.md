# Tasks: Ticket 013 — Política de cancelación tardía

**Input**: [spec.md](./spec.md) y [plan.md](./plan.md)

**Estado del ticket**: Implementación y pruebas locales completadas; cierre formal pendiente de CI/aprobación. La migración `0007` está creada y no aplicada.

## Fase 0 — Documentación y decisiones

- [x] **T001**: Redactar la especificación del 30 % de retención cuando falten dos horas o menos.
- [x] **T002**: Documentar el plan preliminar por capas, persistencia y pruebas.
- [x] **T003**: Registrar preguntas pendientes y mantener bloqueado el código hasta aprobación.
- [x] **T004**: Obtener aprobación del Tech Lead para `spec.md` y `plan.md`.
- [x] **T005**: Definir `precio_total`, zona `America/Argentina/Buenos_Aires`, compensación cero sin horario/chofer o con inicio pasado, snapshot en Servicio sin asiento contable y redondeo `ROUND_HALF_UP`.
- [x] **T006**: Actualizar `spec.md` y `plan.md` con las decisiones aprobadas antes de implementar.

## Fase 1 — Backend

- [x] **T007**: Añadir tests unitarios para cancelación con más de dos horas y dentro de la ventana, incluyendo precisión de límite y no elegibilidad.
- [x] **T008**: Extender cancelación en dominio/aplicación con reloj inyectable y cálculo del 30 % sobre `precio_total`.
- [x] **T009**: Persistir `compensacion_chofer` como snapshot, asociado al chofer asignado, en la actualización atómica de cancelación.
- [x] **T010**: Exponer el snapshot en `ServicioRead`; mantenerlo fuera de los schemas de escritura.
- [x] **T011**: Crear migración Alembic con backfill a cero para servicios históricos (creada, aún no aplicada).
- [x] **T012**: Añadir tests de API/persistencia para umbral, falta de chofer/horario, inicio pasado y reintentos.
- [x] **T013**: Regenerar tipos OpenAPI y ejecutar Ruff, suite unitaria backend, integración de cancelación y validaciones frontend afectadas.
- [ ] **T014**: Actualizar documentación relacionada y marcar el ticket completo solo después de aceptación y CI verde.

## Validación realizada

- [x] Tests focalizados de aplicación y API: 28 passed.
- [x] Suite unitaria backend: 53 passed; integración de cancelación: 1 passed.
- [x] Ruff completo, regeneración OpenAPI, typecheck y suite frontend (96 passed).
- [ ] `npm run verificar` completo: detenido por el chequeo global de Prettier, que reporta 127 archivos sin formato; no se reformateó contenido ajeno al ticket.
- [x] La cadena Alembic reconoce `0007` como revisión `head`; no se ejecutó la migración.
