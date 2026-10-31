# Feature Specification: 010 — Cierre de Viaje, Prueba de Entrega (POD) y Rendición

**Feature Branch**: `010-cierre-viaje-rendicion`

**Created**: 2026-10-30

**Status**: Draft — Pendiente de aprobación del Tech Lead (no se escribe código hasta aprobar)

**Depende de**: `009-autenticacion-roles` (JWT, rol `chofer`, filtro por `id_chofer`, auditoría)

## Resumen

Ticket H10. Cuando el chofer termina un viaje, lo cierra desde el celular adjuntando la **foto del
remito de papel firmado** y declarando el **monto real cobrado**. El servicio queda operativamente
finalizado y económicamente **pendiente de rendición**. La administración revisa en el panel
**"Caja y Rendiciones"** los viajes de cada chofer, ve la foto en grande y aprueba la rendición
(o la observa), dejando en cero la deuda del chofer por ese viaje.

Se descarta la firma digital en pantalla para el MVP: la foto del remito de papel es más simple,
más robusta y más cercana a la operatoria real de una PyME.

---

## User Scenarios & Testing

### User Story 1 — El chofer cierra el viaje con foto del remito y monto cobrado (Priority: P1)

Como chofer, quiero marcar un viaje como finalizado adjuntando la foto del remito firmado y
declarando el monto real cobrado, para que la administración reciba el comprobante en tiempo real.

**Acceptance Scenarios**:

1. **Dado** un servicio `en curso` asignado al chofer autenticado, **cuando** envía
   `POST /api/servicios/{id}/finalizar` con una imagen válida y `monto_cobrado_real >= 0`,
   **entonces** el servicio pasa a estado `finalizado`, `estado_rendicion = pendiente`, se guardan
   `foto_remito_url`, `monto_cobrado_real`, `hora_fin` (reloj del servidor) y
   `modificado_por_id` del chofer, y responde `200` con el `ServicioRead` actualizado.
2. **Dado** el mismo servicio, **cuando** el chofer envía el cierre **sin imagen**, **entonces**
   responde `422` y el servicio no cambia.
3. **Dado** el mismo servicio, **cuando** el chofer envía el cierre **sin monto** o con monto
   negativo / no numérico, **entonces** responde `422` y el servicio no cambia.
4. **Dado** un monto declarado distinto de `precio_total` (cotización), **cuando** se cierra el
   viaje, **entonces** se acepta y se conservan ambos valores (la diferencia se ve en el panel).
5. **Dado** un servicio asignado a **otro** chofer, **cuando** intenta cerrarlo, **entonces**
   responde `403`.
6. **Dado** un servicio que no está `en curso` (`pendiente`, `confirmado`, `finalizado`, `cobrado`,
   `cancelado`), **cuando** se intenta cerrar, **entonces** responde `409`.
7. **Dado** un archivo que no es imagen (`jpeg`, `png`, `webp`, `heic`) o supera el tamaño máximo
   permitido, **cuando** se envía, **entonces** responde `422` (o `413` por tamaño).
8. **Dado** un chofer, **cuando** intenta pasar a `finalizado` por el endpoint genérico
   `PATCH /api/servicios/{id}/estado`, **entonces** responde `403`/`409` indicando que debe usar el
   cierre con remito (se cierra el atajo que hoy existe desde la historia 009).

### User Story 2 — El administrador revisa y aprueba la rendición (Priority: P1)

Como administrador, quiero un panel para revisar los viajes finalizados de cada chofer, ver la
foto del remito y el dinero declarado, para aprobar la rendición y marcar ese saldo como ingresado
a la caja.

**Acceptance Scenarios**:

1. **Dado** servicios con `estado_rendicion = pendiente`, **cuando** el admin abre
   **"Caja y Rendiciones"** (`/rendiciones`), **entonces** los ve **agrupados por chofer** con:
   cliente, fecha, cotización (`precio_total`), monto declarado, diferencia y botón "Ver remito".
2. **Dado** una fila, **cuando** hace clic en "Ver remito", **entonces** se abre un modal con la
   imagen en tamaño grande.
3. **Dado** una rendición pendiente, **cuando** el admin hace clic en **"Aprobar rendición"**
   (`POST /api/servicios/{id}/rendicion/aprobar`), **entonces** `estado_rendicion = rendido`, se
   registran `rendido_en` y `rendido_por_id`, y el monto deja de sumar en la deuda pendiente del
   chofer (queda en cero para ese viaje).
4. **Dado** una rendición pendiente, **cuando** el admin la **observa** con un comentario
   obligatorio (`POST /api/servicios/{id}/rendicion/observar`), **entonces**
   `estado_rendicion = observado` y el comentario queda visible.
5. **Dado** una rendición ya `rendido`, **cuando** se intenta aprobar u observar otra vez,
   **entonces** responde `409`.
6. **Dado** un usuario con rol `chofer`, **cuando** intenta aprobar u observar, **entonces**
   responde `403`.

### User Story 3 — El chofer ve el estado de sus rendiciones (Priority: P3)

Como chofer, quiero ver en mi portal cuáles viajes ya fueron rendidos y cuáles fueron observados,
para saber si tengo que corregir algo.

**Acceptance Scenarios**:

1. **Dado** un viaje finalizado propio, **cuando** el chofer abre su portal, **entonces** la
   tarjeta muestra la etiqueta "Pendiente de rendición", "Rendido" u "Observado" (con el
   comentario del admin si fue observado).

---

## Requisitos Funcionales

- **FR-001**: El cierre del viaje por parte del chofer exige imagen del remito **y** monto cobrado;
  sin ambos, no hay transición a `finalizado`.
- **FR-002**: El estado operativo y el económico son ejes **independientes**: `estado`
  (máquina existente) y `estado_rendicion` (`pendiente` → `rendido` | `observado`).
- **FR-003**: `monto_cobrado_real` es `Numeric(12, 2)`, operado con `Decimal` y `ROUND_HALF_UP`
  (convención del proyecto). Puede ser igual o distinto de `precio_total`; `precio_total` (snapshot
  de la cotización) **no se modifica nunca**.
- **FR-004**: `hora_fin` del cierre se toma del reloj del servidor (igual que en cancelación).
- **FR-005**: La imagen se guarda mediante un **puerto de almacenamiento** intercambiable; la base
  solo persiste la URL (o *data URL* en el modo MVP, ver Decisiones pendientes).
- **FR-006**: Tipos aceptados: `image/jpeg`, `image/png`, `image/webp`, `image/heic`. Tamaño
  máximo del archivo recibido por el backend: **4 MB** (límite práctico del body en Vercel
  Serverless ≈ 4.5 MB). El frontend comprime/redimensiona la foto antes de enviarla.
- **FR-007**: Solo el chofer asignado puede cerrar su viaje; solo un `admin` puede aprobar u
  observar rendiciones.
- **FR-008**: Todas las operaciones registran auditoría (`modificado_por_id`) según la historia 009.
- **FR-009**: La deuda pendiente de un chofer = suma de `monto_cobrado_real` de sus servicios con
  `estado_rendicion = pendiente` (u `observado`). Al aprobar, ese viaje deja de sumar.
- **FR-010**: La vista `/rendiciones` deja de ser un prototipo con datos hardcodeados y pasa a
  consumir datos reales (se conserva el diseño visual actual del equipo).

## Entidades afectadas

- **Servicio** (tabla `servicios`) — columnas nuevas:
  - `foto_remito_url` `TEXT NULL`
  - `monto_cobrado_real` `NUMERIC(12,2) NULL`
  - `estado_rendicion` `VARCHAR(20) NULL` con `CHECK IN ('pendiente','rendido','observado')`
  - `observacion_rendicion` `VARCHAR(255) NULL`
  - `rendido_en` `TIMESTAMPTZ NULL`, `rendido_por_id` `INTEGER NULL FK usuarios.id`
  - `CHECK`: si `estado_rendicion IS NOT NULL` ⇒ `foto_remito_url` y `monto_cobrado_real` no nulos.

> [!NOTE]
> El ticket menciona un estado operativo "Completado". Para no romper la máquina de estados vigente
> (DD-7) se **mapea a `finalizado`**, que es exactamente ese significado. El estado `cobrado`
> sigue existiendo para el cobro al cliente y no se mezcla con la rendición del chofer.

## Decisiones pendientes del cliente / Tech Lead

1. **[Pendiente] Almacenamiento de la foto**: Base64 en la base (MVP) vs. Vercel Blob / Cloudinary /
   S3. Ver análisis en `plan.md` §3. Propuesta: puerto intercambiable con **Base64 como default** y
   adaptador de nube que se activa solo si existe la credencial en el entorno.
2. **[Pendiente] ¿El admin puede cerrar un viaje sin remito?** (ej. chofer sin batería). Propuesta
   MVP: el admin también usa `/finalizar` (con foto opcional para admin) — **requiere confirmación**.
   Hasta confirmar, se testea con `pytest.mark.skip`.
3. **[Pendiente] ¿Se puede re-subir el remito de un viaje `observado`?** Propuesta: sí, el chofer
   vuelve a enviar foto/monto y pasa de `observado` a `pendiente`.

## Success Criteria

- **SC-001**: Un chofer puede cerrar un viaje desde el celular en menos de 30 segundos (abrir
  cámara, sacar foto, confirmar monto).
- **SC-002**: Ningún servicio queda `finalizado` por un chofer sin foto y monto.
- **SC-003**: El admin ve el remito nuevo en `/rendiciones` sin recargar manualmente (polling ≤ 15 s).
- **SC-004**: Los 48 tests unitarios de backend y 96 de frontend existentes siguen en verde.
