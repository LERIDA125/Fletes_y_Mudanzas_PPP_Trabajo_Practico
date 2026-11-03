# Feature Specification: 013 — Política de cancelación tardía

**Feature Branch**: `feature/013-cancelacion-tardia`

**Created**: 2026-11-01

**Status**: Enmienda aprobada e implementada localmente; migración/CI pendientes

**Input**: Directiva de Tech Lead para aplicar una retención automática al cancelar un servicio
cuando restan dos horas o menos para su inicio.

## Resumen

Al cancelarse un servicio con dos horas o menos hasta su inicio programado, se debe retener
automáticamente el 30 % del valor total del viaje a favor del chofer asignado. La regla es una
ampliación de la cancelación existente de H8; no reemplaza sus estados permitidos, el motivo
obligatorio ni la hora de finalización registrada por el servidor.

La base de cálculo es el `precio_total` persistido. La compensación queda registrada como snapshot
en el servicio y se acredita al `saldo_a_favor` del chofer asignado. La actualización del servicio
y del saldo es atómica; la acreditación no representa un pago ni un movimiento de rendición. La
comparación temporal usa `America/Argentina/Buenos_Aires`.

## Historias de usuario y pruebas

### Historia 1 — Aplicar la retención por cancelación tardía (Prioridad: P1)

Como responsable de la operación, quiero que una cancelación realizada cuando faltan dos horas o
menos para el inicio registre una compensación del 30 % y la acredite al saldo a favor del chofer,
para aplicar la política aprobada y conservar trazabilidad económica.

**Prueba independiente**: cancelar un servicio válido con chofer asignado dentro del umbral y
verificar que el servicio queda cancelado, se registra una sola compensación por el importe
calculado por el backend y el saldo del chofer aumenta por ese importe.

**Escenarios de aceptación**:

1. **Dado** un servicio cancelable, con inicio programado y chofer asignado, **cuando** se cancela
   faltando exactamente dos horas, **entonces** se registra una compensación del 30 % del valor
   total del viaje y se acredita ese importe al saldo del chofer.
2. **Dado** un servicio cancelable con chofer asignado, **cuando** se cancela faltando menos de dos
   horas, **entonces** se aplica la misma regla, el cálculo lo realiza el backend y el saldo del
   chofer aumenta por el importe calculado.
3. **Dado** un servicio cancelable con chofer asignado, **cuando** se cancela faltando más de dos
   horas, **entonces** esta regla de cancelación tardía no agrega una retención.
4. **Dado** que se concreta la cancelación tardía, **cuando** se vuelve a intentar cancelarla,
   **entonces** se conserva el rechazo definido por la operación de cancelación existente y no se
   duplica la compensación ni el incremento de saldo.
5. **Dado** un servicio sin hora de inicio programada o sin chofer asignado, **cuando** se cancela,
   **entonces** la cancelación se permite y el snapshot de compensación es cero.
6. **Dado** un servicio cuya hora programada ya pasó, **cuando** se cancela, **entonces** no se
   considera una cancelación dentro de la ventana previa y no se aplica compensación.

## Requisitos funcionales

- **FR-001**: Para una cancelación realizada con un tiempo restante menor o igual a dos horas hasta
  el inicio programado, el sistema MUST calcular una compensación equivalente al 30 % del valor
  total del viaje a favor del chofer asignado.
- **FR-002**: El porcentaje y el umbral MUST aplicarse en el backend; el cliente no puede enviar ni
  alterar el importe retenido.
- **FR-003**: El registro de la cancelación, la compensación snapshot y la acreditación del saldo
  MUST ser atómico. Una cancelación rechazada o fallida no debe dejar una compensación ni un saldo
  parcialmente actualizado.
- **FR-004**: Una misma cancelación no puede generar más de una compensación o acreditación. Se conservan las
  respuestas y restricciones de la operación existente para servicios ya cancelados.
- **FR-005**: La cancelación MUST mantener las reglas vigentes de H8: solo se permite desde
  `pendiente`, `confirmado` o `en curso`; exige un motivo no vacío de hasta 255 caracteres y
  registra `hora_fin` desde el servidor.
- **FR-006**: El sistema MUST conservar la trazabilidad del servicio, del chofer beneficiario, del
  importe y del momento de cancelación. El importe y beneficiario se guardan en el snapshot del
  servicio; el mismo importe se acredita en `choferes.saldo_a_favor`. No se crea un pago ni un
  movimiento de rendición.
- **FR-007**: La comparación del tiempo restante MUST usar `America/Argentina/Buenos_Aires` y
  considerar elegible únicamente `0 <= inicio_programado - ahora <= 2 horas`.
- **FR-008**: Si falta `hora_inicio` o `id_chofer`, la cancelación sigue permitida y la compensación
  es cero.
- **FR-009**: Si el inicio programado ya pasó, no se aplica compensación por cancelación tardía.
- **FR-010**: El cálculo monetario MUST redondearse a dos decimales con `ROUND_HALF_UP`.
- **FR-011**: La acreditación MUST actualizar el saldo del chofer asignado exactamente una vez por
  cancelación tardía y en la misma transacción de base de datos que cancela el servicio.

## Fuera de alcance

- Cambiar los estados o motivos válidos de cancelación de H8.
- Pagar dinero al chofer o crear/modificar movimientos de rendición. La compensación acredita el
  saldo a favor del chofer, pero no representa un pago o una liquidación.
- Modificar frontend, permisos o autenticación de clientes sin aprobación expresa.
- Definir otras penalidades, cargos o políticas para cancelaciones fuera del umbral.

## Criterios de éxito

- Las cancelaciones dentro del umbral aplican exactamente el 30 % sobre la base económica aprobada,
  lo atribuyen al chofer asignado y acreditan ese importe en su saldo a favor.
- Ninguna cancelación inválida o reintentada produce una retención duplicada o parcial.
- La cancelación, el snapshot y el saldo del chofer se confirman juntos o se revierten juntos.
- Los servicios sin horario o chofer asignado y los servicios cuyo inicio ya pasó se cancelan sin
  compensación; el snapshot identifica el importe atribuido al chofer cuando corresponde.

## Dependencias

- Contrato de cancelación y máquina de estados de `specs/008-frontend-gestion-servicios/spec.md`.
- El flujo actual es administrativo; no se incorpora un rol ni endpoint de cliente para cancelar.
