# Feature Specification: 008 — Backend de Servicios y Cotizaciones

**Feature Branch**: `008-frontend-gestion-servicios`

**Created**: 2026-10-21

**Status**: Backend implementado con cancelación; frontend aprobado para demo local sin login

**Input**: Implementar listado, cotización y alta frontend para `/servicios`. La autenticación se
pospone fuera del MVP; la demo asume admin solo en el entorno local de desarrollo.

## Resumen ejecutivo

La API cotiza un viaje, registra un servicio calculado exclusivamente en backend y devuelve
servicios paginados. La vista `/servicios` permite listar, pedir cotización oficial, mostrar el
importe recibido y crear solo después de una confirmación explícita. El frontend nunca calcula el
precio.

La API backend, sus modelos y la migración ya están implementados. `ServicioCreate` no acepta
precios ni valores derivados del cálculo.

## Decisiones aprobadas

- Alcance actual: frontend Next.js para listar, cotizar y dar de alta mediante la API ya implementada.
- El operador ingresa horas estimadas numéricas, con mínimo de 1 hora.
- El operador ingresa kilómetros de ida. El backend calcula la distancia total como el doble.
- La empresa incluye 10 km de franquicia por viaje. `km_excedente` es
  `max(0, distancia_total_km - 10)`.
- Fórmula: `precio_final = tarifa_hora_base * horas_estimadas + tarifa_km_excedente * km_excedente`.
- Las tarifas se leen del tipo de vehículo activo en la base de datos; no se agregan tarifas
  constantes en código.
- Los cálculos monetarios usan `Decimal`; el precio final se redondea a 2 decimales con
  `ROUND_HALF_UP`, en ARS.
- La cotización es una operación de cálculo no persistida. Al crear, el backend repite el cálculo
  con tarifas vigentes y guarda las tarifas, franquicia y resultados como snapshot. El cliente no
  envía precio, tarifas aplicadas, distancia total, franquicia ni km excedente.
- Cliente y tipo de vehículo deben existir y estar activos. Chofer y vehículo son opcionales; si
  se informan deben existir y estar activos. El vehículo asignado debe corresponder al tipo
  cotizado. No se validan disponibilidad, solapamientos ni márgenes de agenda.
- Todo servicio nuevo inicia en estado `pendiente`. La cancelación es la única transición expuesta
  en esta fase: pasa el servicio a `cancelado`, exige un motivo y registra la hora de finalización.
- Un servicio puede cancelarse desde `pendiente`, `confirmado` o `en curso`. No puede cancelarse
  desde `finalizado`, `cobrado` ni desde un servicio ya `cancelado`.
- Pagos, cuenta corriente y rendiciones quedan fuera de alcance.
- **Excepción de demo aprobada**: sin login en el MVP, el backend asume `admin` solo cuando
  `ENVIRONMENT=dev` y `DEV_ASSUME_ADMIN=true`. En cualquier otro entorno falla cerrado con 401;
  el frontend no manda `X-Rol`. Compose publica frontend/backend solo en `127.0.0.1`. Nunca usar
  este modo en un despliegue, una red compartida o un entorno accesible por terceros.
- El alta del backend recalcula el importe con las tarifas vigentes; no vincula un registro de
  cotización previo. El precio de la respuesta de creación es el importe definitivo persistido.

## Inventario del backend verificado

| Capacidad | Situación |
|---|---|
| Clientes, choferes, vehículos y tipos de vehículo | CRUD/listados existentes; los tipos almacenan `tarifa_hora_base` y `tarifa_km_excedente`. |
| Servicios | No hay tabla, modelo, dominio, repositorio, gestor ni router. Solo hay schemas preliminares. |
| Cotizaciones | No hay endpoint, schema ni calculadora operativa. |
| Pagos, cuenta corriente y rendiciones | Solo existen algunos schemas Pydantic; no hay endpoints ni persistencia. |

## User Scenarios & Testing

### User Story 1 — Cotizar un viaje (Priority: P1)

Como administrador, quiero cotizar un viaje con las tarifas configuradas para conocer el precio
resultante antes de registrar el servicio.

**Independent Test**: Invocar `POST /api/servicios/cotizar` con tipo, horas y kilómetros de ida;
verificar kilómetros totales, franquicia, tarifas aplicadas y precio redondeado.

**Acceptance Scenarios**:

1. **Dado** un tipo activo con tarifas configuradas, **cuando** se envían horas ≥ 1 y distancia de
   ida ≥ 0, **entonces** el backend duplica la distancia y devuelve el cálculo desglosado junto al
   precio final ARS redondeado a 2 decimales con `ROUND_HALF_UP`.
2. **Dado** un recorrido total de hasta 10 km, **cuando** se cotiza, **entonces** los kilómetros
   excedentes son 0.
3. **Dado** un recorrido total superior a 10 km, **cuando** se cotiza, **entonces** solo se cobran
   kilómetros por encima de la franquicia de 10 km.
4. **Dado** horas menores a 1, distancia negativa o un tipo inexistente/inactivo, **cuando** se
   cotiza, **entonces** se devuelve error y no un precio.
5. **Dado** tarifas configuradas en cero, **cuando** se cotiza, **entonces** se usan esos valores
   sin introducir tarifas predeterminadas en el código.

### User Story 2 — Registrar un servicio cotizado (Priority: P1)

Como administrador, quiero registrar un servicio y que el backend calcule y guarde su precio junto
con los datos y tarifas usados, sin confiar en importes enviados por el cliente.

**Independent Test**: Crear con parámetros de viaje válidos y verificar que el precio se calcula
en el servidor, el estado inicial es `pendiente` y la respuesta coincide con el registro.

**Acceptance Scenarios**:

1. **Dado** cliente y tipo activos y datos de viaje válidos, **cuando** el administrador crea el
   servicio, **entonces** se guardan sus referencias, entradas, snapshot de tarifas, total y estado
   `pendiente`.
2. **Dado** un body que incluya campos de precio calculado o tarifas, **cuando** se envía el alta,
   **entonces** la API lo rechaza y no persiste el servicio.
3. **Dado** un cliente/tipo inexistente o inactivo, o asignaciones inválidas/incompatibles,
   **cuando** se crea, **entonces** la API devuelve error explícito y no persiste.
4. **Dado** una falla al persistir, **cuando** se crea, **entonces** no queda un servicio parcial.

### User Story 3 — Consultar servicios (Priority: P1)

Como administrador, quiero consultar servicios paginados con datos legibles del cliente, tipo,
estado y recursos asignados.

**Independent Test**: Crear servicios con recursos asignados y no asignados, consultar páginas y
verificar nombres descriptivos, orden estable y total.

**Acceptance Scenarios**:

1. **Dado** más registros que el tamaño de página, **cuando** se consulta, **entonces** página,
   tamaño y total son correctos con orden estable.
2. **Dado** servicios sin chofer o vehículo, **cuando** se listan, **entonces** los nombres son
   nulos sin fallar el JOIN ni eliminar la fila.
3. **Dado** page/size inválidos, **cuando** se consulta, **entonces** FastAPI devuelve 422.

### User Story 4 — Gestionar servicios desde la pantalla admin (Priority: P1, propuesta)

Como administrador, quiero consultar servicios y registrar uno nuevo desde `/servicios`, para
revisar datos y precio antes de confirmar el alta sin que el navegador calcule importes.

**Independent Test**: Con autorización admin disponible, verificar listado paginado, cotización
remota, confirmación, alta, revalidación y errores usando API simulada.

**Acceptance Scenarios**:

1. **Dado** que existe autorización admin y hay servicios, **cuando** abro `/servicios`, **entonces**
   veo datos legibles, precio devuelto por API y navegación paginada.
2. **Dado** que el listado carga, no tiene resultados o falla, **cuando** cambia el estado de la
   solicitud, **entonces** se muestra el estado accesible correspondiente y una opción de reintento
   para errores recuperables.
3. **Dado** entradas válidas, **cuando** solicito cotización, **entonces** la UI muestra el
   desglose y precio recibido de `POST /api/servicios/cotizar`, sin cálculo local.
4. **Dado** una cotización visible para entradas actuales, **cuando** el usuario la confirma,
   **entonces** puede enviar el alta; si cambia tipo, horas o distancia, la confirmación se invalida
   y debe obtener una cotización nueva.
5. **Dado** que el alta tiene éxito, **cuando** la API responde, **entonces** la pantalla presenta
   el `precio_total` definitivo de la respuesta y revalida el listado.
6. **Dado** que una llamada devuelve 401/403 o error de validación/servicio, **cuando** se procesa,
   **entonces** se muestra un mensaje explícito y se preservan los datos que el usuario ingresó.
7. **Dado** que no existe sesión/autorización admin en el frontend, **cuando** se intenta usar la
   ruta, **entonces** no se simula un rol privilegiado; el gate de autorización permanece visible.

### User Story 5 — Cancelar un servicio (Priority: P1)

Como administrador, quiero cancelar un servicio registrando el motivo y la hora de finalización,
para dejar trazabilidad de una cancelación sin borrar el registro ni su historial.

**Independent Test**: Crear un servicio, invocar `PATCH /api/servicios/{id}/cancelar` con un motivo
válido y verificar que queda en estado `cancelado`, con motivo y hora de finalización persistidos.

**Acceptance Scenarios**:

1. **Dado** un servicio en `pendiente`, `confirmado` o `en curso`, **cuando** se cancela con motivo,
   **entonces** pasa a `cancelado` y se guardan el motivo y la hora de finalización del servidor.
2. **Dado** un body sin motivo, con motivo vacío o solo espacios, **cuando** se cancela, **entonces**
   la API responde 422 y el servicio no cambia.
3. **Dado** un servicio `finalizado`, `cobrado`, ya `cancelado` o inexistente, **cuando** se intenta
   cancelar, **entonces** la API responde 409 (o 404 si no existe) y no modifica el registro.
4. **Dado** que la cancelación se completa, **cuando** se consulta el listado, **entonces** el
   servicio aparece con estado `cancelado`, su motivo y su hora de finalización.

## Modelo de datos de Servicio (actualizado)

| Campo | Tipo | Nulable | Regla |
|---|---|---|---|
| `hora_fin` | `TIME` | Sí | Se completa únicamente al cancelar, con la hora del servidor. |
| `motivo_cancelacion` | `VARCHAR(255)` | Sí | Obligatorio al cancelar; se recorta y no puede quedar vacío. |
| `estado` | `VARCHAR(20)` | No | Valores válidos: `pendiente`, `confirmado`, `en curso`, `finalizado`, `cobrado`, `cancelado`. |

La base de datos refuerza la consistencia: si `estado = 'cancelado'`, entonces
`motivo_cancelacion` no es nulo ni vacío y `hora_fin` no es nulo.

## Functional Requirements

- **FR-001**: `POST /api/servicios/cotizar` MUST aceptar tipo de vehículo, horas estimadas y
  kilómetros de ida, y devolver distancia total, franquicia aplicada, tarifas y precio final.
- **FR-002**: `horas_estimadas` MUST ser numérico y ≥ 1; `distancia_ida_km` MUST ser numérica y
  ≥ 0.
- **FR-003**: El backend MUST resolver las tarifas vigentes desde un tipo de vehículo activo en DB.
- **FR-004**: El cálculo MUST usar `distancia_total_km = distancia_ida_km * 2`,
  `km_excedente = max(0, distancia_total_km - 10)` y
  `precio_final = tarifa_hora_base * horas_estimadas + tarifa_km_excedente * km_excedente`.
- **FR-005**: El precio MUST calcularse con `Decimal` y redondeo `ROUND_HALF_UP` a dos decimales
  ARS.
- **FR-006**: `POST /api/servicios` MUST recalcular el precio en backend y MUST NOT aceptar precio,
  tarifas aplicadas, distancia total, franquicia ni kilómetros excedentes como datos de entrada.
- **FR-007**: La persistencia MUST guardar cliente, tipo, asignaciones, fecha/hora programada,
  entradas, tarifas aplicadas, distancia total, franquicia, kilómetros excedentes, precio y estado
  inicial `pendiente`.
- **FR-008**: Cliente y tipo deben estar activos; chofer y vehículo son opcionales pero, si se
  informan, deben estar activos. El vehículo asignado debe pertenecer al tipo indicado.
- **FR-009**: `GET /api/servicios` MUST ser paginado, de orden estable y devolver nombres legibles
  relacionados; las asignaciones opcionales no deben eliminar filas.
- **FR-010**: Cotizar, alta y listado MUST declararse en OpenAPI y requieren rol `admin`. En la
  demo local se asume admin solo con la bandera dev explícita; fuera de dev la API rechaza sin
  autenticación implementada.
- **FR-011**: Cada router MUST delegar la operación a un único método de Aplicación y no contener
  reglas de negocio ni consultas SQL.
- **FR-012**: Los repositorios MUST ser el único acceso a SQLAlchemy; Dominio/Aplicación no
  importan SQLAlchemy, FastAPI ni Pydantic.
- **FR-013**: El frontend MUST NOT ser la autoridad de cálculos financieros; precios y tarifas se
  obtienen de la API.
- **FR-014 (propuesta frontend)**: `/servicios` MUST listar datos y precios devueltos por la API,
  con estados de carga, vacío, error y paginación usando el patrón visual aprobado de 005/006.
- **FR-015 (propuesta frontend)**: El formulario MUST usar React Hook Form + Zod para validación
  inmediata de forma y límites; Zod MUST NOT duplicar cotización, tarifas ni reglas del dominio.
- **FR-016 (propuesta frontend)**: Al pedir cotización, la UI MUST llamar
  `POST /api/servicios/cotizar` y mostrar `precio_final` devuelto por backend junto con su
  desglose y moneda. No se muestra un precio calculado localmente.
- **FR-017 (propuesta frontend)**: La creación MUST permanecer deshabilitada hasta que exista una
  cotización válida para los campos actuales y el usuario la haya revisado/confirmado visualmente.
  Si cambian tipo, horas o distancia, la cotización anterior se invalida y se exige cotizar otra vez.
- **FR-018 (propuesta frontend)**: La mutación de alta MUST ejecutarse por Server Action, enviar
  solo entradas de negocio y referencias, manejar errores sin perder los valores y revalidar
  `/servicios` tras éxito. La respuesta de creación, no la cotización anterior, confirma el importe
  finalmente persistido.
- **FR-019 (decisión aprobada; demo local)**: El backend MUST asumir `admin` solo con
  `ENVIRONMENT=dev` y `DEV_ASSUME_ADMIN=true`. No aceptar `X-Rol` como autorización fuera de ese
  modo y el frontend MUST NOT enviar dicho header.
- **FR-020 (decisión aprobada; cotización)**: La cotización se presenta como estimación; el alta
  puede recalcular un importe distinto con las tarifas vigentes. La interfaz debe advertirlo y
  presentar el importe definitivo devuelto por la respuesta de creación.
- **FR-021**: `PATCH /api/servicios/{id}/cancelar` MUST requerir rol `admin`, recibir únicamente
  `motivo` y delegar la operación a un método de Aplicación.
- **FR-022**: La cancelación MUST exigir un `motivo` no vacío de hasta 255 caracteres; el backend
  MUST recortar espacios y rechazar un motivo vacío con 422.
- **FR-023**: Al cancelar, el backend MUST registrar `hora_fin` con la hora del servidor y persistir
  `estado = 'cancelado'`, `motivo_cancelacion` y `hora_fin` en una sola operación.
- **FR-024**: La cancelación MUST permitirse solo desde `pendiente`, `confirmado` o `en curso`.
  Desde `finalizado`, `cobrado` o `cancelado` MUST responder 409; si el servicio no existe, 404.
- **FR-025**: La respuesta de cancelación y el listado MUST exponer `motivo_cancelacion` y
  `hora_fin`, nulos mientras el servicio no esté cancelado.

## API Contract

### `POST /api/servicios/cotizar` — admin

Entrada: `id_tipo_vehiculo`, `horas_estimadas`, `distancia_ida_km`.

Salida: datos de entrada, `distancia_total_km`, `km_franquicia` (10), `km_excedente`,
`tarifa_hora_base`, `tarifa_km_excedente`, `precio_final`, `moneda` (`ARS`).

### `POST /api/servicios` — admin

Entrada: `id_cliente`, `id_tipo_vehiculo`, `id_chofer` opcional, `id_vehiculo` opcional, fecha y
hora programadas opcionales, `horas_estimadas`, `distancia_ida_km`. Los campos calculados están
prohibidos por validación estricta (`extra="forbid"`). El backend vuelve a consultar tarifas,
calcula y persiste el snapshot (incluida franquicia de 10 km); no se conserva una cotización
temporal ni se acepta precio desde el request.

Salida: servicio con ID, asociaciones y nombres legibles, datos del viaje, tarifas snapshot,
importe ARS, estado y auditoría.

### `GET /api/servicios` — admin

Query params `page` (default 1, mínimo 1) y `size` (default 20, 1–100). Respuesta `items`, `total`,
`page`, `size`; orden ascendente estable por ID. Incluye cliente, tipo, estado, nombre de chofer y
patente de vehículo; nombres de asignaciones opcionales pueden ser nulos. Cada item incluye
`motivo_cancelacion` y `hora_fin` (nulos si el servicio no fue cancelado).

### `PATCH /api/servicios/{id}/cancelar` — admin

Entrada: `motivo` (string, 1–255, se recorta; obligatorio). No se acepta `hora_fin` ni `estado`
desde el request. El backend inyecta la hora de finalización y persiste la cancelación.

Salida: el servicio actualizado con `estado = 'cancelado'`, `motivo_cancelacion`, `hora_fin` y
auditoría. Errores: 404 si el servicio no existe, 409 si no es cancelable, 422 si el motivo es
inválido.

## Out of Scope

- La autenticación JWT y el login quedan fuera del MVP. El modo demo local no equivale a
  autenticación ni debe desplegarse.
- Edición, baja y transiciones de estado distintas de la cancelación.
- Disponibilidad/calendario, prevención de solapamientos y margen entre servicios.
- Pagos, medios de cobro, cuenta corriente, saldos y rendiciones.
- Login, JWT y gestión de cuentas; se posponen a la historia 009.
- Una tabla persistida de cotizaciones o vigencia/aceptación de ofertas.

## Success Criteria

- **SC-001**: Con tarifa $3.000/h, tarifa $150/km, 2 horas y 15 km de ida, la API devuelve 30 km
  totales, 20 km excedentes y $9.000,00 ARS.
- **SC-002**: Con 4 km de ida, la API devuelve 8 km totales y 0 km excedentes.
- **SC-003**: Un alta no puede alterar precio/tarifas desde el request y guarda un snapshot
  calculado íntegramente en backend.
- **SC-004**: `GET /api/servicios` devuelve páginas ordenadas y asociaciones legibles sin N+1.
- **SC-005**: Ruff, tests backend y exportación OpenAPI validan los tres endpoints y sus schemas.
- **SC-006**: `/servicios` funciona sin login solo en demo local con modo dev explícito; fuera de
  dev las rutas protegidas responden 401 y Compose publica puertos en loopback.
- **SC-007 (propuesto)**: Sin sesión administrativa, no se envían operaciones con privilegios
  desde la UI ni se simula autorización mediante un header hardcodeado.
- **SC-008 (propuesto)**: Los campos del cotizador cambian y el estado de cotización se invalida
  automáticamente; no puede confirmarse una cotización correspondiente a entradas anteriores.
- **SC-009**: Cancelar un servicio persistido devuelve 200 con `estado = 'cancelado'`, un
  `motivo_cancelacion` recortado y `hora_fin` no nulo; repetir la cancelación devuelve 409 y no
  altera el registro original.
