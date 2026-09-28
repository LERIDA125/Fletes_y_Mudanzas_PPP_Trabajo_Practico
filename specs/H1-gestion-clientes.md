# Feature Specification: H1 — Gestión de Clientes

**Feature Branch**: `feature/H1-gestion-clientes`

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "El sistema debe permitir registrar, modificar, eliminar y consultar clientes. Los datos requeridos son razón social, teléfono, dirección habitual y un indicador booleano de si el cliente tiene cuenta corriente."

## Out of Scope

- Datos fiscales del cliente (CUIT, CUIL, condiciones frente a AFIP) — se agrupan en H2.
- Gestión de contactos asociados al cliente (varios teléfonos, correos, personas de contacto).
- Cuenta corriente propiamente dicha (saldo, movimientos, imputación de pagos) — corresponde a H10.
- Exportación a Excel/CSV e importación masiva de clientes.
- Historial de cambios (auditoría de modificaciones) de un cliente.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Registrar un cliente nuevo (Priority: P1)

Como administrador de Fletes y Mudanzas Express, quiero dar de alta un cliente con su razón social,
teléfono, dirección habitual y la indicación de si tiene cuenta corriente, para poder después
cotizarle y agendarle servicios.

**Why this priority**: Sin el alta de clientes no existe ningún otro flujo del sistema (servicios,
cotizaciones, agenda y rendiciones arrancan siempre desde un cliente). Es el mínimo valor
entregable por sí solo: un cliente más un listado ya le sirven al administrador para reemplazar
la planilla de Excel.

**Independent Test**: Completar el formulario de alta con los cuatro datos requeridos y verificar
que el cliente queda disponible en el listado. Se puede probar de punta a punta sin ninguna otra
historia implementada.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y ningún cliente con la razón social "Distribuidora del Sur S.A.",
   **cuando** registra un cliente con razón social "Distribuidora del Sur S.A.", teléfono "351 555 0100",
   dirección habitual "Av. Colón 1250, Córdoba" e indicador de cuenta corriente en `true`,
   **entonces** el cliente queda registrado y aparece en el listado con esos mismos datos y con
   `tiene_cuenta_corriente = true`.
2. **Dado** un administrador autenticado, **cuando** registra un cliente con `tiene_cuenta_corriente` en `false`,
   **entonces** el cliente queda registrado con ese indicador en `false`.
3. **Dado** un administrador autenticado, **cuando** registra un cliente con razón social, teléfono,
   dirección habitual e indicador de cuenta corriente completos, **entonces** el sistema asigna
   un identificador único y las fechas de creación y última modificación, y no permite que el
   usuario defina esos valores.
4. **Dado** un administrador autenticado y un cliente ya registrado con la razón social "Distribuidora del Sur S.A.",
   **cuando** intenta registrar otro cliente con esa misma razón social,
   **entonces** el sistema rechaza la operación indicando que la razón social ya está registrada
   y no se persiste un segundo cliente.

---

### User Story 2 — Consultar clientes (Priority: P1)

Como administrador, quiero listar y buscar clientes por razón social, y ver el detalle de un
cliente, para encontrar rápido los datos de un destinatario sin recorrer toda la planilla.

**Why this priority**: Es la forma más rápida de obtener valor de la historia y es requisito de las
historias de cotizaciones y agenda, que necesitan resolver un cliente por nombre.

**Independent Test**: Con al menos tres clientes cargados, usar el listado, aplicar un filtro por
razón social y abrir el detalle de uno. No requiere formulario de alta ni de edición.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y 25 clientes registrados, **cuando** solicita el listado
   sin filtros, **entonces** recibe los clientes ordenados de forma estable y la respuesta indica
   la cantidad total de clientes que cumplen el filtro.
2. **Dado** un administrador autenticado y un cliente "Distribuidora del Sur S.A." registrado,
   **cuando** busca clientes con el texto "Distribuidora", **entonces** el resultado incluye ese
   cliente y solo los que coincidan con el texto, sin importar mayúsculas ni minúsculas.
3. **Dado** un administrador autenticado y un cliente existente, **cuando** solicita el detalle por
   su identificador, **entonces** recibe razón social, teléfono, dirección habitual,
   `tiene_cuenta_corriente` y las fechas de creación y modificación.
4. **Dado** un administrador autenticado, **cuando** busca un texto que no coincide con ningún
   cliente, **entonces** recibe un listado vacío con la cantidad total en cero, no un error.
5. **Dado** un administrador autenticado, **cuando** solicita el detalle de un identificador que no
   existe, **entonces** el sistema responde con un error de "cliente no encontrado".

---

### User Story 3 — Modificar un cliente (Priority: P2)

Como administrador, quiero corregir los datos de un cliente ya registrado —por ejemplo, porque
cambió de teléfono o de domicilio— sin dar de alta un cliente nuevo ni perder su historial.

**Why this priority**: La carga de datos reales siempre tiene errores y cambios de contacto, así
que sin edición el listado se ensucia con duplicados. Viene después del alta porque el problema
que resuelve aparece recién una vez que hay clientes cargados.

**Independent Test**: Editar el teléfono de un cliente existente y verificar que el listado y el
detalle muestran el valor nuevo, y que la fecha de modificación se actualiza.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un cliente con teléfono "351 555 0100",
   **cuando** actualiza su teléfono a "351 555 0199", **entonces** el detalle del cliente muestra
   el teléfono nuevo y su fecha de última modificación es posterior a la de creación.
2. **Dado** un administrador autenticado y un cliente con `tiene_cuenta_corriente` en `false`,
   **cuando** cambia ese indicador a `true`, **entonces** el detalle del cliente muestra la
   cuenta corriente habilitada.
3. **Dado** un administrador autenticado y un cliente existente, **cuando** guarda la edición con
   los mismos datos que ya tenía, **entonces** la operación se completa correctamente, el cliente
   conserva su identificador y su fecha de creación, y solo se actualiza la fecha de modificación.
4. **Dado** un administrador autenticado, **cuando** intenta actualizar la razón social de un cliente
   a una razón social que ya pertenece a otro cliente, **entonces** el sistema rechaza la operación
   y el cliente original queda intacto.
5. **Dado** un administrador autenticado, **cuando** intenta actualizar un cliente con razón social,
   teléfono o dirección habitual vacíos, **entonces** el sistema rechaza la operación, no la guarda
   y explica qué dato falta.
6. **Dado** un administrador autenticado, **cuando** intenta actualizar un cliente inexistente,
   **entonces** el sistema responde con un error de "cliente no encontrado" y no crea ningún registro.

---

### User Story 4 — Eliminar un cliente (Priority: P3)

Como administrador, quiero dar de baja un cliente que ya no se usa (por ejemplo, uno cargado por
error o una empresa que dejó de trabajar con Fletes y Mudanzas Express), para que no aparezca en
la lista de disponibles al cotizar o agendar un servicio.

**Why this priority**: Es la operación menos frecuente y la más delicada, porque un cliente puede
estar referenciado por servicios ya realizados. La resolución definitiva de la política de bajas
depende de reglas que el cliente todavía no confirmó (ver "Decisiones pendientes").

**Independent Test**: Dar de baja un cliente sin historial y verificar que deja de aparecer en el
listado, y que el detalle ya no lo expone.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un cliente sin servicios asociados, **cuando** elimina
   ese cliente, **entonces** el cliente deja de aparecer en el listado y su detalle ya no está
   disponible.
2. **Dado** un administrador autenticado y un cliente con servicios asociados, **cuando** intenta
   eliminarlo, **entonces** el sistema rechaza la operación, explica que el cliente tiene historial
   asociado y el cliente permanece en el sistema.
3. **Dado** un administrador autenticado, **cuando** elimina un cliente que ya estaba dado de baja,
   **entonces** la operación se completa sin error y el estado del cliente no cambia.

### Edge Cases

- **Razón social repetida**: se rechaza el alta y la modificación con el mismo texto, ignorando
  mayúsculas, minúsculas, espacios de sobra y diferencias de acentuación.
- **Teléfono con formato heterogéneo**: se aceptan `351 555 0100`, `+54 9 351 555 0100`,
  `0351-555-0100`; el sistema no exige un formato único, pero sí una cantidad mínima de dígitos.
- **Teléfono compartido por dos clientes**: se permite, un teléfono no es único.
- **Campos con solo espacios**: se consideran vacíos y la operación se rechaza.
- **Texto con caracteres o emojis**: se aceptan, no se rechaza el registro por eso.
- **Dirección habitual muy extensa**: se acepta hasta el largo máximo definido; más largo se rechaza.
- **Borrado de un cliente que tiene cotizaciones o rendiciones asociadas**: no se permite; se
  prioriza la integridad de los datos históricos.
- **Operaciones simultáneas sobre el mismo cliente**: la última actualización válida gana, sin
  dejar el cliente en un estado intermedio inválido.
- **Listado sin resultados**: devuelve lista vacía con total en cero, no un error.
- **Paginación más allá del total disponible**: devuelve la página pedida vacía, sin error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir registrar un cliente con los cuatro datos requeridos:
  razón social, teléfono, dirección habitual e indicador booleano de cuenta corriente.
- **FR-002**: El sistema MUST exigir los cuatro datos requeridos en el alta: ninguno puede ser nulo
  ni quedar vacío. El indicador de cuenta corriente es obligatorio y su valor por defecto, si el
  usuario no lo elige explícitamente, es `false`.
- **FR-003**: El sistema MUST generar el identificador del cliente y sus fechas de creación y
  última modificación; el usuario no puede informarlos.
- **FR-004**: El sistema MUST validar que la razón social no esté ya registrada, comparando el
  texto sin distinguir mayúsculas, minúsculas, acentos ni espacios sobrantes.
- **FR-005**: El sistema MUST validar el teléfono como un texto de 7 a 20 dígitos, admitiendo
  espacios, guiones y el prefijo internacional `+`, y NO MUST exigir un formato único.
- **FR-006**: El sistema MUST validar que la razón social tenga entre 3 y 120 caracteres y que la
  dirección habitual entre 5 y 250 caracteres, una vez normalizados los espacios sobrantes.
- **FR-007**: El sistema MUST permitir consultar el listado de clientes con orden estable,
  paginado, e indicar en la respuesta la cantidad total de clientes que cumplen el filtro.
- **FR-008**: El sistema MUST permitir filtrar el listado por texto de búsqueda que coincida, sin
  distinguir mayúsculas y minúsculas, con parte de la razón social del cliente.
- **FR-009**: El sistema MUST permitir consultar el detalle de un cliente por su identificador,
  devolviendo razón social, teléfono, dirección habitual, indicador de cuenta corriente y fechas
  de creación y modificación.
- **FR-010**: El sistema MUST permitir modificar los cuatro datos requeridos de un cliente
  existente, conservando su identificador y su fecha de creación.
- **FR-011**: El sistema MUST rechazar toda alta o modificación con datos requeridos incompletos o
  inválidos, informando cuál fue el dato rechazado y no persistiendo ningún cambio parcial.
- **FR-012**: El sistema MUST rechazar toda modificación que leave la razón social del cliente
  igual a la de otro cliente.
- **FR-013**: El sistema MUST rechazar toda alta o modificación que violate las reglas de unicidad,
  formato o longitud definidas, devolviendo un mensaje asociado al campo responsable.
- **FR-014**: El sistema MUST dar de baja un cliente sin servicios asociados, de modo que deje de
  aparecer en el listado y no pueda consultarse su detalle.
- **FR-015**: El sistema MUST rechazar la baja de un cliente con servicios, cotizaciones o
  rendiciones asociadas, informando la existencia del historial y sin alterar los datos del cliente.
- **FR-016**: El sistema MUST responder con un error de "cliente no encontrado" ante consultas,
  modificaciones o bajas sobre un identificador inexistente, y MUST NOT crear registros implícitos.
- **FR-017**: El sistema MUST persistir los datos del cliente en la base de datos de forma
  persistente, de modo que la información sobreviva a un reinicio del servidor.
- **FR-018**: El sistema MUST restringir el alta, la modificación y la baja de clientes al rol
  `admin`; el rol `chofer` MAY ONLY consultar el listado y el detalle.
- **FR-019**: El sistema MUST exponer la gestión de clientes de forma documentada en el contrato
  OpenAPI/Swagger, incluidos los códigos de respuesta de éxito y de error.
- **FR-020**: El sistema MUST registrar la fecha de la última modificación cada vez que un cliente
  se actualiza, y MUST NOT modificarla al consultar.

### Contrato de API

Recursos y endpoints (los nombres exactos pueden ajustarse en `/plan`, el comportamiento es el
especificado arriba):

| Método | Ruta | Rol | Resultado |
|---|---|---|---|
| `GET` | `/api/clientes` | admin, chofer | Listado paginado con total, filtro opcional por texto |
| `GET` | `/api/clientes/{id}` | admin, chofer | Detalle del cliente |
| `POST` | `/api/clientes` | admin | `201` con el cliente creado |
| `PUT` | `/api/clientes/{id}` | admin | `200` con el cliente actualizado |
| `DELETE` | `/api/clientes/{id}` | admin | `204` sin cuerpo |

Errores esperados: `400`/`422` con detalle por campo cuando falla una validación, `401` si no hay
sesión, `403` si el rol no tiene permiso, `404` si el identificador no existe, `409` si la razón
social ya está registrada o el cliente tiene historial asociado a la baja.

### Key Entities

- **Cliente**: persona o empresa que contrata servicios de fletes y mudanzas. Atributos: razón
  social (texto, identificador de negocio, único), teléfono (texto de contacto), dirección
  habitual (texto), indicador de cuenta corriente (booleano), estado activo (booleano, interno a
  la baja), identificador (sistema), fecha de creación y fecha de última modificación (sistema).
  Se relaciona con los servicios que se le contratan y, si tiene cuenta corriente habilitada, con
  sus movimientos de cuenta corriente (historia posterior).

### Decisiones pendientes de confirmación con el cliente

Estos puntos no están confirmados por el cliente. La historia se implementa con los supuestos
temporales indicados y, si el cliente decide distinto, se actualiza primero esta sección y luego
el código (AGENTS.md §2 y §5):

- **DP-01 — Alcance de la baja**: se asume baja lógica (el cliente queda inactivo y desaparece del
  listado) en lugar de borrado físico, para no romper el historial de servicios, cotizaciones y
  rendiciones. **[Supuesto temporal]**
- **DP-02 — Unicidad de la razón social**: se asume que no puede haber dos clientes con la misma
  razón social. **[Supuesto temporal]**
- **DP-03 — Permisos**: se asume que el rol `admin` hace el alta, la modificación y la baja, y que
  el rol `chofer` solo consulta. **[Supuesto temporal]**
- **DP-04 — Telefónos y correos múltiples**: se asume un único teléfono como dato requerido. Los
  contactos múltiples se confirman con H2 (datos del cliente). **[Supuesto temporal]**
- **DP-05 — Identificación fiscal**: se asume que el CUIT/CUIL no es obligatorio en esta historia.
  En la planilla de Excel es un campo muy usado, así que conviene confirmarlo antes de implementar.
  **[Supuesto temporal]**

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los criterios de aceptación de esta spec tienen al menos un test
  automatizado que los cubre y pasa en verde.
- **SC-002**: Un administrador que nunca vio el sistema registra un cliente válido y lo encuentra en
  el listado en menos de 2 minutos, sin ayuda externa.
- **SC-003**: Buscar un cliente por razón social devuelve el resultado correcto en menos de 2
  segundos con 1.000 clientes cargados.
- **SC-004**: El sistema no permite bajo ninguna circunstancia registrar, modificar ni dar de baja un
  cliente con datos requeridos incompletos, inválidos o duplicados.
- **SC-005**: Un cliente cargado desde el sistema aparece correctamente en el listado y en el
  detalle desde otro dispositivo/navegador, confirmando que los datos se persistieron.
- **SC-006**: El 100 % de los endpoints nuevos quedan documentados en Swagger y son invocables
  siguiendo solo esa documentación.
- **SC-007**: Un cliente dado de baja conserva intactos los servicios, cotizaciones y rendiciones
  que lo referencian.

## Assumptions

- El sistema de autenticación JWT y los roles `admin` / `chofer` ya están disponibles (o se
  reimplementan en otra historia); esta historia solo consume el rol del usuario autenticado.
- Los usuarios acceden al sistema desde navegador de escritorio o tablet; la interfaz es responsive
  según AGENTS.md §1.
- La base de datos es PostgreSQL y las migraciones se gestionan con Alembic, según AGENTS.md §3.
- El volumen inicial es de cientos de clientes, no de millones; la paginación alcanza para el
  volumen del MVP.
- Los horarios y zonas horarias no afectan a esta historia.
- El texto de los datos del cliente se muestra tal como se carga, sin normalización mayúscula /
  minúscula, salvo la comparación por búsqueda y unicidad.
