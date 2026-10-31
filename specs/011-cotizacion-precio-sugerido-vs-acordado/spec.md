# Feature Specification: 011 — Motor de Cotizaciones: Precio Sugerido vs Precio Acordado

**Feature Branch**: `011-cotizacion-precio-sugerido-vs-acordado`

**Created**: 2026-10-30

**Status**: Draft — pendiente de aprobación del Tech Lead (no se escribe código hasta aprobar)

**Ticket interno**: H7 (motor de cotizaciones). La directiva lo llamó “Ticket 010”; en Spec Kit se
numera **011** porque `specs/010-cierre-viaje-rendicion/` ya pertenece a H10 y la numeración debe ser
única para preservar la trazabilidad spec ↔ rama.

**Depende de**: `008-frontend-gestion-servicios` (servicios y cotización vigente),
`003-gestion-vehiculos` (tarifas por tipo) y `007-frontend-listado-vehiculos` (flota).

**Directiva de origen**: override del Tech Lead del 2026-10-30, consensuado con el equipo, que
confirma la nueva fórmula, habilita los modificadores y aprueba el modelo Precio Sugerido vs Precio
Acordado. Esta spec registra y formaliza esa directiva.

---

## Relación con las reglas anteriores

Esta historia **reemplaza** para servicios nuevos las reglas de cotización de `008`:

| Regla anterior (008) | Regla nueva (011) |
|---|---|
| `distancia_total_km = distancia_ida_km * 2` | Se elimina la duplicación de distancia. |
| Franquicia fija de 10 km | Se elimina la franquicia. Se cobran todos los km estimados. |
| `km_excedente = max(0, total - 10)` | Se elimina el concepto de km excedente. |
| Sin modificadores de servicio | Se agregan ayudante, escalera, zona concurrida y urgencia. |
| El alta recalcula e ignora todo importe del cliente | El alta acepta y persiste `precio_acordado`; el `precio_sugerido` queda como snapshot de auditoría. |
| Alta solo con una cotización vigente confirmada (FR-017 de 008) | El alta no exige una cotización vigente: el operador puede acordar un precio distinto. |

También deja sin efecto, **solo para esta historia**, las notas de `AGENTS.md §6` sobre ayudantes
fuera del cálculo y de `DD-6` sobre ignorar importes del cliente. El plan documenta la actualización
de gobernanza que corresponde.

---

## Resumen ejecutivo

El despachante arma una cotización eligiendo un vehículo, horas estimadas, kilómetros estimados y
cuatro condiciones operativas. El backend calcula un **precio_sugerido** desglosado. En la misma
pantalla, el operador ve el precio final acordado, autocompletado con el sugerido pero editable: si
quiere hacer un descuento o un recargo personalizado al cliente, lo tipea y ese valor es el que se
persiste al dar de alta el servicio.

El backend nunca confía en cálculos del navegador: el sugerido se calcula siempre en Aplicación con
las tarifas y la configuración vigentes en base de datos. Al crear el servicio, el backend vuelve a
calcular el sugerido (para el snapshot) y guarda también el `precio_acordado` enviado por el
operador como importe comercial definitivo.

No se persiste una tabla de cotizaciones: cotizar es una operación de cálculo pura. El único
registro económico persistente es el del `Servicio` creado, con ambos importes y el snapshot de
tarifas/modificadores.

---

## Directiva de negocio aprobada

1. **Fórmula base**: se abandona la franquicia de 10 km. El costo base es
   `horas_estimadas * tarifa_hora_base + km_estimados * tarifa_km_excedente`.
2. **Modificadores fijos**: `requiere_ayudante` y `acceso_escalera` suman un importe fijo cada uno.
3. **Recargos porcentuales**: `zona_concurrida` suma 15% y `urgencia_mismo_dia` suma 20%, ambos
   calculados sobre el subtotal con fijos y **aditivos** entre sí (15% + 20% = 35%, no compuestos).
4. **Modelo Sugerido vs Acordado**: el backend calcula `precio_sugerido`; `POST /api/servicios`
   acepta obligatoriamente `precio_acordado` y persiste ese valor como el importe final del
   servicio.

---

## Decisiones aprobadas

- El endpoint de cálculo es `POST /api/cotizaciones/calcular` (rol `admin`). Reemplaza a
  `POST /api/servicios/cotizar`, que se retira del contrato para no tener dos autoridades de
  cálculo. El frontend se migra a la nueva ruta.
- La cotización se identifica por `id_tipo_vehiculo` (categoría activa). El backend lee
  `tarifa_hora_base` y `tarifa_km_excedente` directamente de `tipos_vehiculo`; cotizar no requiere
  que exista ni que se seleccione una unidad de flota.
- Entradas numéricas: `horas_estimadas` ≥ 1, `km_estimados` ≥ 0, con hasta dos decimales.
- Los cuatro modificadores son booleanos y por defecto `false`.
- Las tarifas y los importes/porcentajes de los modificadores se leen de la base de datos. **Nunca**
  se escriben como constantes en el código.
- La configuración de modificadores es única y global (tabla `configuracion_cotizacion`, fila
  singleton): `recargo_ayudante`, `recargo_escalera`, `porcentaje_zona_concurrida` (15.00) y
  `porcentaje_urgencia_mismo_dia` (20.00).
- Los importes son `Decimal`, en ARS, y se redondean a 2 decimales con `ROUND_HALF_UP`. Cada
  componente del desglose se redondea a centavos y el total es la suma de los componentes
  redondeados (regla determinística, testeable).
- `precio_acordado` es obligatorio al crear un servicio, es `Decimal` ≥ 0 y no puede superar la
  precisión monetaria (`Numeric(12, 2)`). El backend **no** lo recalcula ni lo corrige.
- El backend **no** valora si el acordado es “razonable” respecto del sugerido: descuentos y
  recargos manuales son una decisión del despachante. No hay límites ni aprobaciones en esta
  historia.
- La respuesta de creación expone ambos importes: `precio_sugerido` (snapshot calculado) y
  `precio_acordado` (importe persistido como final).
- Cotizar no exige que el servicio tenga cliente, chofer, fecha ni vehículo asignado; solo exige un
  tipo de vehículo activo para resolver la tarifa. En el alta, el selector comercial usa el tipo
  de vehículo y la asignación operativa de una unidad es opcional, disponible según fecha/hora y
  filtrada para pertenecer al tipo seleccionado.
- El alta **no** requiere una cotización vigente previa. El sugerido es informativo; el acordado es
  la fuente comercial. El backend recalcula el sugerido igualmente para el snapshot de auditoría.
- Se mantiene la autorización por `require_rol(ROL_ADMIN)` y el modo demo local de `DD-3`.

## Supuestos temporales y decisiones abiertas

- **Importes fijos de ayudante y escalera**: la directiva aprueba que existan, pero no fijó montos.
  Se modelan en `configuracion_cotizacion` y se cargan en la migración/seed con valores explícitos
  aprobados por el Tech Lead antes de la demo. **No se hardcodean** en Python. Los tests usan
  valores de fixture propios para no depender de los montos productivos. Queda registrado como
  `[Supuesto temporal]` hasta confirmación del cliente.
- **Porcentajes 15% / 20%**: aprobados por la directiva y persistidos como configuración editable
  en base de datos (no como constantes).
- **Categoría vs unidad asignada**: la cotización y el selector comercial usan `id_tipo_vehiculo`;
  no muestran patentes. El alta conserva `id_vehiculo` opcional de 008 para la asignación
  operativa. La UI solo ofrece unidades disponibles del tipo seleccionado y el backend valida que
  la unidad asignada pertenezca a ese tipo.
- **Redondeo**: se adopta la regla “redondear cada componente y sumar” para que el desglose mostrado
  sea exactamente el que se persiste. Si el cliente pide otra convención, se actualiza esta spec.

---

## User Scenarios & Testing

### User Story 1 — Calcular el precio sugerido (Priority: P1)

Como despachante, quiero calcular el precio sugerido de un viaje con la categoría del vehículo y las condiciones
elegidas, para mostrarle un número al cliente antes de acordar el precio final.

**Independent Test**: Invocar `POST /api/cotizaciones/calcular` con un tipo activo, horas, km y
los cuatro flags; verificar el desglose completo y el `precio_sugerido` redondeado.

**Acceptance Scenarios**:

1. **Dado** un tipo de vehículo activo con `tarifa_hora_base = 3000` y
   `tarifa_km_excedente = 150`, **cuando** se cotiza con 2 horas, 10 km y todos los flags en
   `false`, **entonces** `base_horas = 6000`, `base_km = 1500`, `subtotal_base = 7500`, sin fijos ni
   recargos, y `precio_sugerido = 7500.00` ARS.
2. **Dado** la misma base y una configuración con `recargo_ayudante = 500` y
   `recargo_escalera = 300`, **cuando** se cotiza con ambos flags en `true`, **entonces**
   `subtotal_con_fijos = 8300.00` y el desglose muestra esos dos importes por separado.
3. **Dado** `subtotal_con_fijos = 8300`, **cuando** `zona_concurrida = true` y
   `urgencia_mismo_dia = true`, **entonces** el recargo de zona es 1245.00, el de urgencia es
   1660.00, el total de recargos porcentuales es 2905.00 y `precio_sugerido = 11205.00`.
4. **Dado** `zona_concurrida = false`, **cuando** se cotiza, **entonces** el porcentaje y el
   importe de zona aplicados son 0 y no se suman al total.
5. **Dado** horas < 1, km negativo, o un `id_tipo_vehiculo` inexistente/inactivo, **cuando** se
   cotiza, **entonces** la API responde 422 y no devuelve un precio.
6. **Dado** tarifas o importes configurados en cero, **cuando** se cotiza, **entonces** se usan
   esos valores tal cual, sin introducir valores predeterminados en el código.
7. **Dado** un request que incluya campos derivados (`precio_sugerido`, `base_horas`, tarifas, etc.),
   **cuando** se envía, **entonces** la API lo rechaza con 422.

### User Story 2 — Registrar el servicio con el precio acordado (Priority: P1)

Como despachante, quiero registrar el servicio con el precio que acordé con el cliente, para que el
importe comercial final sea exactamente el que negocié y no un recálculo automático.

**Independent Test**: Crear un servicio enviando `precio_acordado` distinto del sugerido; verificar
que se persiste el acordado, que el sugerido queda guardado como snapshot y que la respuesta
devuelve ambos.

**Acceptance Scenarios**:

1. **Dado** datos de viaje y referencias válidas y un `precio_acordado` de 10000, **cuando** se
   crea el servicio, **entonces** el backend calcula el sugerido con la configuración vigente y
   persiste `precio_acordado = 10000` como importe final, junto con el snapshot del sugerido.
2. **Dado** un `precio_acordado` igual al sugerido, **cuando** se crea, **entonces** ambos importes
   quedan iguales y la respuesta lo refleja.
3. **Dado** un request sin `precio_acordado` o con un valor negativo/no finito, **cuando** se crea,
   **entonces** la API responde 422 y no persiste el servicio.
4. **Dado** un request que incluya `precio_sugerido`, tarifas aplicadas, recargos calculados u otros
   campos derivados, **cuando** se envía el alta, **entonces** la API lo rechaza con 422 y no
   persiste.
5. **Dado** un `precio_acordado` que difiere del sugerido en cualquier dirección (descuento o
   recargo), **cuando** se crea, **entonces** el backend no lo ajusta ni lo rechaza por esa
   diferencia.
6. **Dado** que el cálculo del sugerido cambia entre la cotización mostrada y el alta (porque
   cambiaron tarifas o configuración), **cuando** se crea con el acordado, **entonces** se persiste
   el acordado enviado y el sugerido nuevo como snapshot, sin alterar el importe comercial.

### User Story 3 — Formulario reactivo con precio acordado editable (Priority: P1)

Como despachante, quiero un formulario donde el precio sugerido se actualice solo al cambiar
vehículo, horas, km o condiciones, y donde pueda escribir a mano el precio final acordado, para
trabajar rápido en el mostrador sin perder el control del importe.

**Independent Test**: Con el cliente de API simulado, cambiar un campo y verificar que se dispara el
cálculo; verificar el autocompletado del acordado; editarlo a mano y comprobar que un nuevo cálculo
no lo pisa; enviar el alta con el valor manual.

**Acceptance Scenarios**:

1. **Dado** el formulario abierto con un vehículo, horas y km válidos, **cuando** cambia cualquiera
   de esos valores o un switch, **entonces** tras un debounce se solicita un nuevo cálculo al
   backend y se muestra el desglose recibido.
2. **Dado** que llega un `precio_sugerido` y el operador **no** tocó el campo acordado, **cuando** se
   actualiza el resultado, **entonces** el campo “Precio final acordado” se autocompleta con ese
   valor.
3. **Dado** que el operador editó o borró manualmente el campo acordado, **cuando** llega un nuevo
   cálculo, **entonces** el campo **no** se sobrescribe y conserva el valor escrito por el operador.
4. **Dado** que el operador borra el acordado y quiere escribirlo de cero, **cuando** lo ingresa,
   **entonces** puede hacerlo y el valor se envía tal cual al alta.
5. **Dado** que la cotización falla o está en curso, **cuando** el operador quiere registrar,
   **entonces** puede hacerlo si los campos obligatorios y el acordado son válidos; el alta recalcula
   el sugerido en backend igualmente.
6. **Dado** un formulario inválido (sin vehículo, horas < 1, km < 0 o acordado vacío), **cuando** se
   intenta registrar, **entonces** se muestra el error de forma sin enviar el alta.

### User Story 4 — Cotizador independiente en `/cotizaciones` (Priority: P2)

Como administrador, quiero usar el mismo motor en la sección Cotizaciones para consultar precios sin
dar de alta un servicio.

**Independent Test**: Abrir `/cotizaciones`, cambiar entradas, ver el desglose del backend y
verificar que no se persiste nada.

**Acceptance Scenarios**:

1. **Dado** la sección `/cotizaciones`, **cuando** se completan vehículo, horas, km y flags,
   **entonces** se muestra el mismo desglose que devuelve `POST /api/cotizaciones/calcular`.
2. **Dado** que el usuario cambia una entrada, **entonces** el resultado anterior se invalida y se
   reemplaza por el nuevo cálculo.
3. **Dado** el cotizador independiente, **cuando** se calcula, **entonces** no se crea ningún
   servicio ni registro persistente.

### Edge Cases

- Tipo de vehículo inactivo o inexistente → 422.
- `km_estimados = 0` → permitido; `base_km = 0`; el resto se calcula normalmente.
- Flags todos `false` → no se suman fijos ni porcentajes.
- Porcentajes configurados en 0 → el recargo correspondiente es 0 aunque el flag esté `true`.
- El acordado puede ser 0 (servicio bonificado) y debe persistirse como 0.
- Importes muy grandes que excedan `Numeric(12, 2)` → 422 por validación, nunca error 500.
- Cambio de tarifas/configuración entre la cotización y el alta → el acordado no cambia; el sugerido
  snapshot refleja los valores vigentes al crear.

---

## Functional Requirements

### Backend — cálculo

- **FR-001**: `POST /api/cotizaciones/calcular` MUST requerir rol `admin`, recibir
  `id_tipo_vehiculo`, `horas_estimadas`, `km_estimados` y los cuatro flags booleanos, y devolver el
  desglose completo y `precio_sugerido` en ARS.
- **FR-002**: El request MUST usar `extra="forbid"` y rechazar con 422 cualquier campo derivado o
  de sistema.
- **FR-003**: `horas_estimadas` MUST ser `Decimal` ≥ 1 y `km_estimados` `Decimal` ≥ 0, ambos
  finitos y con hasta dos decimales.
- **FR-004**: El backend MUST resolver el tipo activo y las tarifas `tarifa_hora_base` /
  `tarifa_km_excedente` desde base de datos; MUST NOT usar constantes de
  tarifa.
- **FR-005**: El cálculo MUST usar
  `base_horas = tarifa_hora_base * horas_estimadas`,
  `base_km = tarifa_km_excedente * km_estimados`,
  `subtotal_base = base_horas + base_km`.
- **FR-006**: El cálculo MUST sumar `recargo_ayudante` si `requiere_ayudante` y
  `recargo_escalera` si `acceso_escalera`, obteniendo `subtotal_con_fijos`.
- **FR-007**: El cálculo MUST aplicar `porcentaje_zona_concurrida` si `zona_concurrida` y
  `porcentaje_urgencia_mismo_dia` si `urgencia_mismo_dia`, en forma **aditiva** sobre
  `subtotal_con_fijos`; los recargos son independientes y no se componen.
- **FR-008**: Los importes y porcentajes de los modificadores MUST leerse de la tabla de
  configuración en base de datos; MUST NOT estar hardcodeados, salvo los valores aprobados que se
  cargan en la migración/seed.
- **FR-009**: Cada componente monetario MUST redondearse a 2 decimales con `ROUND_HALF_UP`; el
  `precio_sugerido` MUST ser la suma de los componentes redondeados.
- **FR-010**: La respuesta MUST incluir, como mínimo: tipo, descripción del tipo, horas,
  km, tarifas, `base_horas`, `base_km`, `subtotal_base`, `recargo_ayudante`,
  `recargo_escalera`, `subtotal_con_fijos`, porcentaje e importe de zona, porcentaje e importe de
  urgencia, `total_recargos_porcentuales`, `precio_sugerido` y `moneda = "ARS"`.
- **FR-011**: Un tipo inexistente o inactivo, horas/km inválidos o configuración inválida
  MUST responder 422 y no un precio.
- **FR-012**: Cotizar MUST NOT persistir nada ni requerir cliente, chofer, fecha o asignación de
  vehículo.

### Backend — alta

- **FR-013**: `POST /api/servicios` MUST requerir `precio_acordado` (`Decimal` ≥ 0, no finito
  prohibido, máximo `12,2`) y persistirlo como importe comercial final.
- **FR-014**: El alta MUST recalcular el `precio_sugerido` en backend con las mismas reglas de
  cálculo vigentes y persistirlo como snapshot, junto con tarifas, flags y recargos aplicados.
- **FR-015**: El alta MUST NOT aceptar `precio_sugerido`, tarifas aplicadas, recargos, subtotales
  ni otros campos derivados; el schema MUST usar `extra="forbid"`.
- **FR-016**: El alta MUST NOT modificar, corregir ni rechazar `precio_acordado` por su diferencia
  con el sugerido.
- **FR-017**: El alta MUST conservar las validaciones de 008 sobre cliente, chofer, vehículo, tipo,
  fecha, hora, estado inicial `pendiente` y cliente nuevo/existente.
- **FR-018**: Si se informa `id_vehiculo`, MUST pertenecer al `id_tipo_vehiculo` indicado y estar
  activo; si no se informa, el servicio MUST poder crearse igual (vehículo opcional).
- **FR-019**: La entidad `Servicio` MUST validar que ambos importes son `Decimal` finitos y no
  negativos, y que las columnas heredadas de 008 quedan consistentes.
- **FR-020**: La respuesta y el listado MUST exponer `km_estimados`, `precio_sugerido`,
  `precio_acordado`, los cuatro flags y los recargos aplicados, manteniendo compatibilidad de
  lectura con las columnas históricas que aún se muestran.

### Contrato y capas

- **FR-021**: El router de cotizaciones MUST validar rol y payload y delegar en un único método de
  Aplicación; MUST NOT contener fórmulas ni consultas SQL.
- **FR-022**: La estrategia de cálculo MUST ser intercambiable (patrón Strategy) y residir en
  `app/application/cotizacion/`.
- **FR-023**: La capa de Aplicación MUST leer tarifas y configuración únicamente por puertos
  (`Protocol`); MUST NOT importar SQLAlchemy, FastAPI ni Pydantic.
- **FR-024**: El dominio MUST seguir siendo Python puro y no depender de Pydantic/ORM.
- **FR-025**: `POST /api/servicios/cotizar` MUST retirarse del contrato y del frontend; MUST NOT
  quedar una segunda autoridad de cálculo activa.
- **FR-026**: El OpenAPI MUST declarar el nuevo endpoint y los nuevos campos; los tipos del
  frontend MUST regenerarse con `npm run gen:api`.

### Frontend

- **FR-027**: El formulario MUST estar disponible como componente reutilizable y usarse tanto en el
  modal de “Nuevo Servicio” como en `/cotizaciones`.
- **FR-028**: El formulario MUST incluir selector de tipo de vehículo activo, horas, km y cuatro
  switches (ayudante, escalera, zona concurrida, urgencia). La unidad asignada, si se elige, MUST
  ser una unidad disponible del tipo seleccionado; el selector comercial no MUST mostrar patentes.
- **FR-029**: Cada cambio en esos campos MUST disparar un cálculo al backend con debounce; el fetch
  MUST originarse desde la capa de acciones/cliente API, nunca desde un `useEffect` ni desde un
  componente haciendo `fetch` directo.
- **FR-030**: El campo “Precio final acordado” MUST ser un `<input type="number">` editable y
  autocompletarse con `precio_sugerido` solo mientras el operador no lo haya editado manualmente.
- **FR-031**: Una vez que el operador edita o borra el acordado, los cálculos posteriores MUST NOT
  sobrescribirlo.
- **FR-032**: El envío del alta MUST incluir `precio_acordado` con el valor final del campo y MUST
  NOT incluir campos derivados.
- **FR-033**: La UI MUST mostrar el desglose devuelto por el backend; MUST NOT recalcular importes
  en el navegador.
- **FR-034**: Zod MUST validar forma y límites de UX (tipo de vehículo requerido, horas ≥ 1, km ≥ 0,
  acordado requerido ≥ 0); MUST NOT duplicar la fórmula ni las reglas de tarifa.
- **FR-035**: La UI MUST manejar estados de cálculo en curso, error y resultado obsoleto, sin
  bloquear el alta por un fallo del cálculo informativo.
- **FR-036**: La estética MUST reutilizar los tokens y componentes existentes, respetar WCAG 2.1 AA,
  mobile-first, formato `es-AR` y ARS con `Intl.NumberFormat`.

---

## API Contract

### `POST /api/cotizaciones/calcular` — admin

Request (ejemplo):

```json
{
  "id_tipo_vehiculo": 3,
  "horas_estimadas": "2.00",
  "km_estimados": "10.00",
  "requiere_ayudante": false,
  "acceso_escalera": false,
  "zona_concurrida": true,
  "urgencia_mismo_dia": true
}
```

Response (ejemplo con tarifas 3000/150, fijos 500/300 y 15% + 20%):

```json
{
  "id_tipo_vehiculo": 3,
  "descripcion_tipo_vehiculo": "Camión chico",
  "horas_estimadas": "2.00",
  "km_estimados": "10.00",
  "tarifa_hora_base": "3000.00",
  "tarifa_km_excedente": "150.00",
  "base_horas": "6000.00",
  "base_km": "1500.00",
  "subtotal_base": "7500.00",
  "requiere_ayudante": false,
  "recargo_ayudante": "0.00",
  "acceso_escalera": false,
  "recargo_escalera": "0.00",
  "subtotal_con_fijos": "7500.00",
  "zona_concurrida": true,
  "porcentaje_zona_concurrida": "15.00",
  "importe_recargo_zona_concurrida": "1125.00",
  "urgencia_mismo_dia": true,
  "porcentaje_urgencia_mismo_dia": "20.00",
  "importe_recargo_urgencia_mismo_dia": "1500.00",
  "total_recargos_porcentuales": "2625.00",
  "precio_sugerido": "10125.00",
  "moneda": "ARS"
}
```

> Los importes del ejemplo usan fijos en 0 para mostrar que el desglose es derivable. Con fijos
> 500/300 el `subtotal_con_fijos` sería 8300 y el `precio_sugerido` 11205.

Errores: 401/403 por autorización, 422 por payload inválido o tipo inactivo.

### `POST /api/servicios` — admin (cambio de contrato)

Request: conserva `id_cliente` o `nuevo_cliente`, `id_tipo_vehiculo`, `id_chofer` opcional,
`id_vehiculo` opcional, `fecha`, `hora_inicio`, `horas_estimadas`, y agrega:

- `km_estimados` (reemplaza `distancia_ida_km`),
- `requiere_ayudante`, `acceso_escalera`, `zona_concurrida`, `urgencia_mismo_dia`,
- `precio_acordado` (obligatorio).

Los campos calculados siguen prohibidos (`extra="forbid"`). El backend recalcula el sugerido y
persiste ambos importes.

Response: servicio con `km_estimados`, `precio_sugerido`, `precio_acordado`, flags, recargos
aplicados, estado y auditoría.

### Endpoints retirados

- `POST /api/servicios/cotizar`: se elimina. El frontend y los tests migran a
  `POST /api/cotizaciones/calcular`.

---

## Modelo de datos

### Nueva tabla `configuracion_cotizacion` (singleton, fila `id = 1`)

| Campo | Tipo | Nulable | Regla |
|---|---|---|---|
| `id` | `INTEGER` identity | No | Singleton; solo una fila activa. |
| `recargo_ayudante` | `NUMERIC(12,2)` | No | Importe fijo ARS ≥ 0. |
| `recargo_escalera` | `NUMERIC(12,2)` | No | Importe fijo ARS ≥ 0. |
| `porcentaje_zona_concurrida` | `NUMERIC(5,2)` | No | 0–100; valor aprobado 15.00. |
| `porcentaje_urgencia_mismo_dia` | `NUMERIC(5,2)` | No | 0–100; valor aprobado 20.00. |
| `creado_en` / `actualizado_en` | `TIMESTAMPTZ` | No | Auditoría del patrón vigente. |

La migración crea la fila singleton con los valores aprobados. El backend debe rechazar una
configuración ausente o inválida con 422, nunca asumir valores por defecto en Python.

### Cambios en `servicios`

| Campo | Cambio | Regla |
|---|---|---|
| `distancia_ida_km` | Renombrado a `km_estimados` | Km directos, ≥ 0, sin duplicación ni franquicia. |
| `precio_total` | Renombrado a `precio_acordado` | Importe final ingresado por el operador, ≥ 0. |
| `precio_sugerido` | Nuevo `NUMERIC(12,2)` | Snapshot calculado al crear, ≥ 0. |
| `requiere_ayudante`, `acceso_escalera`, `zona_concurrida`, `urgencia_mismo_dia` | Nuevos `BOOLEAN` | `false` por defecto. |
| `recargo_ayudante_aplicado`, `recargo_escalera_aplicado` | Nuevos `NUMERIC(12,2)` | Importes snapshot, ≥ 0. |
| `importe_recargo_zona_aplicado`, `importe_recargo_urgencia_aplicado` | Nuevos `NUMERIC(12,2)` | Importes snapshot, ≥ 0. |
| `porcentaje_zona_aplicado`, `porcentaje_urgencia_aplicado` | Nuevos `NUMERIC(5,2)` | Porcentajes snapshot, 0–100. |
| `distancia_total_km`, `km_franquicia`, `km_excedente` | Heredadas de 008 | Se conservan por historial; no participan del cálculo. En servicios nuevos: `distancia_total_km = km_estimados`, `km_franquicia = 0`, `km_excedente = 0`. |

Migración `0007_cotizacion_sugerido_vs_acordado` (siguiente libre después de `0006`):

- Crear `configuracion_cotizacion` y su fila singleton.
- Renombrar columnas preservando datos.
- Agregar columnas nuevas con `nullable` → backfill → `NOT NULL` donde aplique.
- Backfill de servicios históricos: `precio_sugerido = precio_acordado` (el importe que se cobró) y
  flags/recargos en `false`/`0`.
- Declarar `downgrade()`.

---

## Frontend Contract

- El componente reutilizable vive en `frontend/src/features/cotizaciones/` y se monta en:
  - el modal de “Nuevo Servicio” (`features/servicios/components/formulario-servicio.tsx`),
  - la página `/cotizaciones` (`features/cotizaciones/components/cotizador.tsx`).
- La acción de servidor y el cliente tipado se agregan en `features/cotizaciones/actions.ts` y
  `lib/api/cotizaciones.ts`.
- El selector comercial consume los tipos activos de `/api/tipos-vehiculo` y cotiza mediante
  `id_tipo_vehiculo`. El selector operativo de unidad consume disponibilidad y filtra cualquier
  opción que no pertenezca a ese tipo.
- Disparo reactivo: cada cambio de tipo de vehículo, horas, km o flags programa un cálculo con debounce
  (~350 ms) mediante temporizador en un `ref`, evitando `useEffect` para fetches.
- Máquina de estado del acordado:
  1. Al abrir/limpiar el formulario: `editado_manualmente = false`.
  2. Llega `precio_sugerido`: si `editado_manualmente = false`, autocompletar el campo.
  3. El operador escribe o borra el campo: `editado_manualmente = true`.
  4. Nuevos cálculos con `editado_manualmente = true`: no sobrescriben.
  5. El alta envía siempre el valor actual del campo como `precio_acordado`.
- Un fallo o demora del cálculo no bloquea el alta si los campos obligatorios y el acordado son
  válidos; se informa el estado del cálculo y que el backend recalculará el sugerido.

---

## Out of Scope

- Persistir cotizaciones, ofertas, vigencias o aceptaciones.
- Aprobaciones, topes o auditoría de descuentos/recargos manuales.
- Fórmulas por tipo de servicio distintas de la estrategia aprobada.
- Rol de chofer en la cotización; sigue siendo una operación `admin`.
- Liquidación, pagos, cuenta corriente y rendiciones (H10).
- Migración de datos históricos a la nueva fórmula: los servicios existentes conservan su
  snapshot original y se backfillean para lectura.
- Autenticación real; se mantiene el modo demo local de `DD-3`.

## Success Criteria

- **SC-001**: `POST /api/cotizaciones/calcular` devuelve exactamente el desglose y
  `precio_sugerido` del ejemplo aprobado (11205.00 con 2 h, 10 km, fijos 500/300 y 15% + 20%).
- **SC-002**: Con flags en `false`, el sugerido es la suma de horas y km, sin franquicia ni
  duplicación.
- **SC-003**: Un `id_tipo_vehiculo` inactivo, horas/km inválidos o payload con campos derivados responde
  422 y no devuelve precio.
- **SC-004**: El alta persiste `precio_acordado` exactamente como se envió y guarda el sugerido
  calculado en el mismo registro.
- **SC-005**: Un alta con `precio_acordado` distinto del sugerido no es rechazado ni ajustado.
- **SC-006**: La UI autocompleta el acordado y deja de hacerlo después de la primera edición manual,
  verificado con RTL.
- **SC-007**: El desglose mostrado en UI coincide con la respuesta de la API; no hay cálculo
  financiero en el navegador.
- **SC-008**: Ruff, `pytest tests/unit`, integración contra PostgreSQL, `npm run verificar` y
  regeneración de OpenAPI pasan sin diff.
- **SC-009**: Los servicios históricos siguen legibles: conservan su importe final y obtienen un
  `precio_sugerido` de backfill igual al cobrado.

---

## Breaking changes y migración

- **Contrato**: se retira `POST /api/servicios/cotizar`; `distancia_ida_km` pasa a `km_estimados`;
  `precio_total` pasa a `precio_acordado`; se agregan `precio_sugerido`, flags y recargos en la
  lectura. El frontend, los tipos generados y los tests se actualizan en el mismo PR.
- **Base de datos**: la migración `0007` renombra columnas con preservación de datos y agrega
  columnas nuevas; no borra historia. `downgrade()` revierte los cambios.
- **Gobernanza**: el plan incluye la actualización de `AGENTS.md §6/§11` y el registro de la
  enmienda de constitución que formaliza la directiva del Tech Lead. Sin esa actualización, la
  implementación no se considera cerrada.

---

## Governance

Esta spec nace de una directiva explícita del Tech Lead y queda sujeta a su aprobación antes de
escribir código. Cualquier cambio posterior a la fórmula, a los modificadores o a la semántica de
`precio_acordado` MUST actualizar primero esta spec y el `plan.md`, y recién después el código,
conforme al Principio I de la constitución.
