# Feature Specification: 015 — Registro y liquidación de rendiciones

**Feature Branch**: `015-rendiciones`

**Created**: 2026-11-03

**Status**: Propuesta — pendiente de aprobación del Tech Lead

**Input**: Directiva para reemplazar el prototipo estático de `/rendiciones` por persistencia real
de la liquidación económica de cada servicio con chofer asignado.

## Resumen

Una rendición registra el cierre económico de un servicio ya prestado: cuánto corresponde pagar al
chofer (`tarifa`), cuánto se le adelantó (`adelanto`), qué gastos informó (combustible, peajes y
otros) y cuánto queda por liquidar (`saldo`). El administrador registra la rendición, la deja en
revisión y finalmente la aprueba.

El `saldo` no se envía desde el cliente: lo calcula el backend como
`tarifa - adelanto - (combustible + peajes + otros)`, redondeado a dos decimales con
`ROUND_HALF_UP`. El `codigo` (`REN-001`, `REN-002`, …) y la `fecha` se derivan del identificador y
del servicio; el chofer también se deriva del servicio para que no pueda quedar inconsistente.

Cada servicio puede tener a lo sumo una rendición. Solo son elegibles los servicios con chofer
asignado y estado `finalizado` o `cobrado` que todavía no tengan rendición.

## Historias de usuario y pruebas

### Historia 1 — Registrar la rendición de un servicio (Prioridad: P1)

Como administrador, quiero registrar la rendición de un servicio finalizado con chofer asignado,
para dejar asentado el adelanto, los gastos informados y el saldo a liquidar.

**Prueba independiente**: crear una rendición sobre un servicio elegible y verificar que el
backend asigna código, fecha y chofer, persiste los importes y calcula el saldo sin aceptar valores
del cliente para los campos derivados.

**Escenarios de aceptación**:

1. **Dado** un servicio `finalizado` o `cobrado` con chofer y sin rendición, **cuando** el
   administrador registra tarifa, adelanto y gastos, **entonces** se crea una rendición en estado
   `pendiente` con `codigo` generado por el sistema, la fecha del servicio y el chofer del servicio.
2. **Dado** una rendición con tarifa 18.500, adelanto 12.000 y gastos 2.500, **cuando** se
   consulta, **entonces** el saldo informado es 4.000.
3. **Dado** un servicio sin chofer, **cuando** se intenta rendir, **entonces** el backend rechaza la
   operación con un error de datos.
4. **Dado** un servicio `pendiente`, `confirmado`, `en curso` o `cancelado`, **cuando** se intenta
   rendir, **entonces** el backend rechaza la operación por conflicto de estado.
5. **Dado** un servicio que ya tiene rendición, **cuando** se intenta rendir de nuevo, **entonces**
   el backend rechaza la operación por conflicto y no crea una segunda fila.
6. **Dado** un cliente que envía `codigo`, `fecha`, `id_chofer`, `saldo` o `gastos_total` en el
   alta, **cuando** se procesa el request, **entonces** esos campos se rechazan por contrato.

### Historia 2 — Consultar y filtrar rendiciones (Prioridad: P1)

Como administrador, quiero ver el listado de rendiciones con sus importes y KPIs, para controlar
qué falta liquidar y qué se aprobó en el mes.

**Prueba independiente**: listar rendiciones con y sin búsqueda, verificando paginación, orden,
importes derivados y resumen global.

**Escenarios de aceptación**:

1. **Dado** rendiciones persistidas, **cuando** se consulta el listado, **entonces** se devuelven
   ordenadas por identificador descendente, con chofer, servicio, fecha, tarifa, adelanto, gastos,
   saldo y estado.
2. **Dado** un texto de búsqueda, **cuando** se lista, **entonces** se filtra por código, chofer,
   razón social del cliente o identificador de servicio, sin distinguir mayúsculas ni acentos.
3. **Dado** el listado, **cuando** se consulta el resumen, **entonces** devuelve el total pendiente
   (suma de saldos en `pendiente` y `en revision`), la cantidad de rendiciones pendientes, el total
   aprobado del mes corriente y el total de gastos informados.
4. **Dado** una rendición, **cuando** se consulta su detalle, **entonces** se devuelve el desglose
   de gastos y el saldo calculado.

### Historia 3 — Cambiar el estado de una rendición (Prioridad: P1)

Como administrador, quiero mover una rendición entre `pendiente`, `en revision` y `aprobada`, para
reflejar el avance del cierre.

**Prueba independiente**: cambiar el estado de una rendición existente y verificar que se persiste
y que un estado inválido se rechaza.

**Escenarios de aceptación**:

1. **Dado** una rendición `pendiente`, **cuando** se la pasa a `en revision` o `aprobada`,
   **entonces** el nuevo estado queda persistido y la respuesta lo refleja.
2. **Dado** una rendición en cualquier estado válido, **cuando** se envía un estado desconocido,
   **entonces** el backend responde con error de validación y no modifica la fila.
3. **Dado** una rendición inexistente, **cuando** se intenta cambiar su estado, **entonces** el
   backend responde 404.

### Historia 4 — Operar la pantalla real de rendiciones (Prioridad: P1)

Como administrador, quiero que `/rendiciones` muestre datos reales y permita registrar y aprobar
rendiciones, para dejar de usar el prototipo con filas hardcodeadas.

**Prueba independiente**: renderizar la pantalla con datos del backend, registrar una rendición
desde el modal y aprobar una existente, verificando que el listado y los KPIs se actualizan.

**Escenarios de aceptación**:

1. **Dado** la pantalla `/rendiciones`, **cuando** carga, **entonces** muestra las rendiciones y
   KPIs reales, y el buscador filtra por código, chofer o servicio.
2. **Dado** el modal "Nueva rendición", **cuando** se abre, **entonces** solo ofrece servicios
   elegibles y muestra el chofer derivado del servicio seleccionado.
3. **Dado** un alta válida, **cuando** se guarda, **entonces** la rendición aparece en el listado
   con estado `pendiente` y los KPIs se recalculan.
4. **Dado** el detalle de una rendición no aprobada, **cuando** se pulsa "Aprobar rendición",
   **entonces** el estado pasa a `aprobada` y el KPI de aprobado se actualiza.
5. **Dado** un error del backend (conflicto, datos inválidos o falta de permisos), **cuando** se
   guarda o aprueba, **entonces** la UI muestra un mensaje claro sin cerrar el modal en silencio.

## Requisitos funcionales

- **FR-001**: Todas las rutas de rendiciones MUST exigir rol `admin`.
- **FR-002**: El listado MUST ser paginado (`page`, `size`), ordenado por `id` descendente y
  filtrable por un texto `q` sobre código, chofer, razón social del cliente e identificador de
  servicio.
- **FR-003**: El endpoint de servicios elegibles MUST devolver únicamente servicios con `id_chofer`
  no nulo, estado `finalizado` o `cobrado` y sin rendición asociada.
- **FR-004**: El alta MUST recibir exactamente un `id_servicio` elegible, `tarifa` y `adelanto`
  mayores o iguales a cero, tres gastos mayores o iguales a cero y `observaciones` opcionales de
  hasta 500 caracteres.
- **FR-005**: El backend MUST derivar `id_chofer` y `fecha` del servicio, y `codigo` del
  identificador generado (`REN-{id:03d}`). El cliente no puede enviarlos.
- **FR-006**: El `saldo` MUST calcularse como
  `tarifa - adelanto - (combustible + peajes + otros)` con `Decimal` y `ROUND_HALF_UP` a dos
  decimales. Puede ser negativo cuando los gastos y el adelanto superan la tarifa.
- **FR-007**: Los estados válidos MUST ser `pendiente`, `en revision` y `aprobada`. El cambio de
  estado MUST aceptar cualquiera de esos valores sobre una rendición existente.
- **FR-008**: Un servicio sin chofer MUST rechazarse como dato inválido; un servicio no elegible o
  ya rendido MUST rechazarse como conflicto.
- **FR-009**: El resumen MUST exponer: total pendiente, cantidad pendiente, total aprobado del mes
  corriente y total de gastos informados.
- **FR-010**: La rendición MUST persistirse en PostgreSQL con FK a servicio y chofer, unicidad por
  servicio, checks de importes no negativos y estados válidos, y columnas de auditoría.
- **FR-011**: La migración `0008` MUST crear la tabla y ser reversible sin alterar datos de
  servicios.
- **FR-012**: El seed MUST crear rendiciones de demostración solo para servicios existentes con
  chofer y en estado finalizado.
- **FR-013**: El frontend MUST reemplazar las filas y KPIs hardcodeados por datos del backend y
  MUST usar Server Actions para las mutaciones.

## Entidades y datos derivados

| Campo | Origen | Regla |
|---|---|---|
| `id` | Sistema | Identidad entera. |
| `codigo` | Sistema | `REN-{id:03d}` único. |
| `id_servicio` | Cliente | Servicio elegible; único. |
| `id_chofer` | Servicio | Derivado; nunca enviado por el cliente. |
| `fecha` | Servicio | Fecha del servicio. |
| `tarifa` | Cliente | `>= 0`, dos decimales. |
| `adelanto` | Cliente | `>= 0`, dos decimales. |
| `gasto_combustible`, `gasto_peajes`, `gasto_otros` | Cliente | Cada uno `>= 0`, dos decimales. |
| `gastos_total` | Sistema | Suma de los tres gastos. |
| `saldo` | Sistema | `tarifa - adelanto - gastos_total`. |
| `estado` | Sistema/Cliente | `pendiente`, `en revision` o `aprobada`. |
| `observaciones` | Cliente | Opcional, máximo 500 caracteres. |

## Fuera de alcance

- Generar pagos, movimientos contables o asientos de caja.
- Modificar `choferes.saldo_a_favor` o reutilizar la compensación por cancelación tardía como
  tarifa de la rendición.
- Exportar CSV (el botón del prototipo queda fuera de esta historia).
- Editar o eliminar rendiciones una vez creadas.
- Liquidar servicios sin chofer asignado.

## Criterios de éxito

- El prototipo deja de tener datos hardcodeados y opera contra PostgreSQL.
- El saldo y los totales siempre coinciden con la fórmula aprobada, sin depender del cliente.
- Un servicio no puede rendirse dos veces ni rendirse antes de finalizar.
- Los KPIs reflejan el estado real de las rendiciones y se actualizan tras cada mutación.

## Dependencias

- Servicios y estados de `specs/008-frontend-gestion-servicios/spec.md`.
- Autenticación y roles de `specs/009-autenticacion-roles/spec.md`.
- Choferes y `saldo_a_favor` de `specs/004-gestion-choferes/spec.md`.
