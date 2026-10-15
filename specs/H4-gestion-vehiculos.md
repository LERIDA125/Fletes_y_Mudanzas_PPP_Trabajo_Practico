# Feature Specification: H4 — Gestión de Vehículos y Tipos de Vehículo

**Feature Branch**: `feature/H4-gestion-vehiculos`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "El sistema debe permitir gestionar vehículos y tipos de vehículos. Cada vehículo tiene una patente única, un tipo de vehículo y opcionalmente un chofer habitual. Cada tipo de vehículo define la capacidad de carga y las tarifas base por hora y por kilómetro excedente. Se requiere CRUD completo para ambas entidades."

## Out of Scope

- Gestión completa de choferes (H2) — esta historia solo crea la tabla mínima de choferes para soportar el FK de `id_chofer_habitual`.
- Asignación de vehículos a servicios (H5/H6).
- Historial de asignaciones de choferes a vehículos.
- Fotografías o documentación de vehículos.
- Mantenimiento o inspecciones de vehículos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Registrar un tipo de vehículo (Priority: P1)

Como administrador, quiero dar de alta un tipo de vehículo con su descripción, capacidad de carga y tarifas base, para poder asignarlo a los vehículos y usarlo en la cotización de servicios.

**Why this priority**: Sin tipos de vehículo no se pueden registrar vehículos. Es el prerrequisito de toda la flota y de la calculadora de cotización (H7).

**Independent Test**: Crear un tipo de vehículo, verificar que aparece en el listado y que se puede recuperar por ID.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado, **cuando** registra un tipo de vehículo con descripción "Camioneta 1/2 tonelada", capacidad de carga 500 kg, tarifa hora base $3000 y tarifa km excedente $150,
   **entonces** el tipo de vehículo queda registrado y aparece en el listado con esos datos.
2. **Dado** un administrador autenticado, **cuando** registra un tipo de vehículo sin capacidad de carga o con valor negativo o cero,
   **entonces** el sistema rechaza la operación indicando que la capacidad de carga debe ser positiva.
3. **Dado** un administrador autenticado, **cuando** registra un tipo de vehículo sin tarifa hora base o con valor negativo,
   **entonces** el sistema rechaza la operación indicando que la tarifa hora base no puede ser negativa.
4. **Dado** un administrador autenticado, **cuando** registra un tipo de vehículo sin tarifa km excedente o con valor negativo,
   **entonces** el sistema rechaza la operación indicando que la tarifa km excedente no puede ser negativa.
5. **Dado** un administrador autenticado y un tipo de vehículo ya registrado con descripción "Camioneta 1/2 tonelada",
   **cuando** intenta registrar otro tipo de vehículo con esa misma descripción,
   **entonces** el sistema rechaza la operación indicando que la descripción ya está registrada.
6. **Dado** un administrador autenticado, **cuando** registra un tipo de vehículo con todos los datos válidos,
   **entonces** el sistema asigna un identificador único y las fechas de creación y última modificación.

---

### User Story 2 — Consultar tipos de vehículo (Priority: P1)

Como administrador, quiero listar y buscar tipos de vehículo, y ver el detalle de uno, para encontrar rápido las especificaciones de un tipo de vehículo.

**Why this priority**: Es la forma más rápida de verificar que un tipo de vehículo está bien cargado y es requisito para asignarlo a vehículos.

**Independent Test**: Con al menos tres tipos de vehículo cargados, usar el listado, aplicar un filtro por descripción y abrir el detalle de uno.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y 5 tipos de vehículo registrados, **cuando** solicita el listado sin filtros,
   **entonces** recibe los tipos de vehículo ordenados de forma estable y la respuesta indica la cantidad total.
2. **Dado** un administrador autenticado y un tipo de vehículo "Camioneta 1/2 tonelada" registrado,
   **cuando** busca tipos de vehículo con el texto "Camioneta",
   **entonces** el resultado incluye ese tipo de vehículo y solo los que coincidan con el texto.
3. **Dado** un administrador autenticado y un tipo de vehículo existente, **cuando** solicita el detalle por su identificador,
   **entonces** recibe descripción, capacidad de carga, tarifa hora base, tarifa km excedente y las fechas.
4. **Dado** un administrador autenticado, **cuando** busca un texto que no coincide con ningún tipo de vehículo,
   **entonces** recibe un listado vacío con la cantidad total en cero, no un error.
5. **Dado** un administrador autenticado, **cuando** solicita el detalle de un identificador que no existe,
   **entonces** el sistema responde con un error de "tipo de vehículo no encontrado".

---

### User Story 3 — Modificar un tipo de vehículo (Priority: P2)

Como administrador, quiero corregir los datos de un tipo de vehículo ya registrado —por ejemplo, porque cambió la tarifa— sin dar de alto un tipo nuevo.

**Why this priority**: Las tarifas y capacidades pueden ajustarse con el tiempo. Sin edición habría que dar de baja y crear un nuevo tipo, perdiendo la trazabilidad.

**Independent Test**: Editar la tarifa de un tipo de vehículo existente y verificar que el detalle muestra el valor nuevo.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un tipo de vehículo con tarifa hora base $3000,
   **cuando** actualiza su tarifa hora base a $3500,
   **entonces** el detalle del tipo de vehículo muestra la tarifa nueva.
2. **Dado** un administrador autenticado y un tipo de vehículo "Camioneta 1/2 tonelada",
   **cuando** actualiza su descripción a "Camioneta 3/4 tonelada",
   **entonces** el detalle muestra la descripción nueva.
3. **Dado** un administrador autenticado y un tipo de vehículo "Camioneta 1/2 tonelada" registrado,
   **cuando** intenta actualizar su descripción a la de otro tipo de vehículo ya registrado,
   **entonces** el sistema rechaza la operación indicando que la descripción ya está registrada.
4. **Dado** un administrador autenticado, **cuando** actualiza un tipo de vehículo con datos inválidos,
   **entonces** el sistema rechaza la operación y no se guarda ningún cambio parcial.
5. **Dado** un administrador autenticado, **cuando** actualiza un tipo de vehículo con un identificador que no existe,
   **entonces** el sistema responde con un error de "tipo de vehículo no encontrado".

---

### User Story 4 — Eliminar un tipo de vehículo (Priority: P2)

Como administrador, quiero dar de baja un tipo de vehículo que ya no se usa, para mantener el listado limpio.

**Why this priority**: Permite tipos de vehículo que dejaron de usarse. Viene después del alta y la edición porque el problema aparece recién una vez que hay tipos cargados.

**Independent Test**: Dar de baja un tipo de vehículo y verificar que desaparece del listado.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un tipo de vehículo sin vehículos asociados,
   **cuando** lo da de baja,
   **entonces** el tipo de vehículo desaparece del listado.
2. **Dado** un administrador autenticado y un tipo de vehículo con vehículos asociados,
   **cuando** intenta darlo de baja,
   **entonces** el sistema rechaza la operación indicando que tiene vehículos asociados.
3. **Dado** un administrador autenticado, **cuando** da de baja un tipo de vehículo que ya está dado de baja,
   **entonces** el sistema responde con un error de "tipo de vehículo no encontrado".
4. **Dado** un administrador autenticado, **cuando** da de baja un tipo de vehículo con un identificador que no existe,
   **entonces** el sistema responde con un error de "tipo de vehículo no encontrado".

---

### User Story 5 — Registrar un vehículo (Priority: P1)

Como administrador, quiero dar de alta un vehículo con su patente, tipo de vehículo y opcionalmente un chofer habitual, para poder asignarlo a servicios.

**Why this priority**: Sin vehículos no hay flota. Es el núcleo de esta historia y prerrequisito de la agenda (H5) y los servicios (H6).

**Independent Test**: Crear un vehículo con patente, tipo de vehículo y chofer habitual, y verificar que aparece en el listado.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un tipo de vehículo registrado,
   **cuando** registra un vehículo con patente "ABC 123", tipo de vehículo y sin chofer habitual,
   **entonces** el vehículo queda registrado y aparece en el listado.
2. **Dado** un administrador autenticado y un tipo de vehículo y un chofer registrados,
   **cuando** registra un vehículo con patente "ABC 123", tipo de vehículo y chofer habitual,
   **entonces** el vehículo queda registrado con el chofer asignado.
3. **Dado** un administrador autenticado y un vehículo ya registrado con patente "ABC 123",
   **cuando** intenta registrar otro vehículo con esa misma patente,
   **entonces** el sistema rechaza la operación indicando que la patente ya está registrada.
4. **Dado** un administrador autenticado, **cuando** registra un vehículo con un tipo de vehículo que no existe,
   **entonces** el sistema rechaza la operación indicando que el tipo de vehículo no existe.
5. **Dado** un administrador autenticado, **cuando** registra un vehículo con un chofer habitual que no existe,
   **entonces** el sistema rechaza la operación indicando que el chofer no existe.
6. **Dado** un administrador autenticado, **cuando** registra un vehículo con todos los datos válidos,
   **entonces** el sistema asigna un identificador único y las fechas de creación y última modificación.

---

### User Story 6 — Consultar vehículos (Priority: P1)

Como administrador, quiero listar y buscar vehículos, y ver el detalle de uno, para encontrar rápido los datos de un vehículo.

**Why this priority**: Es la forma más rápida de verificar que un vehículo está bien cargado y es requisito para asignarlo a servicios.

**Independent Test**: Con al menos tres vehículos cargados, usar el listado, aplicar un filtro por patente y abrir el detalle de uno.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y 5 vehículos registrados, **cuando** solicita el listado sin filtros,
   **entonces** recibe los vehículos ordenados de forma estable y la respuesta indica la cantidad total.
2. **Dado** un administrador autenticado y un vehículo "ABC 123" registrado,
   **cuando** busca vehículos con el texto "ABC",
   **entonces** el resultado incluye ese vehículo y solo los que coincidan con el texto.
3. **Dado** un administrador autenticado y un vehículo existente, **cuando** solicita el detalle por su identificador,
   **entonces** recibe patente, tipo de vehículo, chofer habitual y las fechas.
4. **Dado** un administrador autenticado, **cuando** busca un texto que no coincide con ningún vehículo,
   **entonces** recibe un listado vacío con la cantidad total en cero, no un error.
5. **Dado** un administrador autenticado, **cuando** solicita el detalle de un identificador que no existe,
   **entonces** el sistema responde con un error de "vehículo no encontrado".

---

### User Story 7 — Modificar un vehículo (Priority: P2)

Como administrador, quiero corregir los datos de un vehículo ya registrado —por ejemplo, porque cambió de tipo o de chofer habitual— sin dar de alta un vehículo nuevo.

**Why this priority**: Los datos de un vehículo pueden cambiar (cambio de chofer, reasignación de tipo). Sin edición habría que dar de baja y crear un nuevo vehículo.

**Independent Test**: Editar el tipo de vehículo de un vehículo existente y verificar que el detalle muestra el valor nuevo.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un vehículo con tipo "Camioneta 1/2 tonelada",
   **cuando** actualiza su tipo a "Camión 1 tonelada",
   **entonces** el detalle del vehículo muestra el tipo nuevo.
2. **Dado** un administrador autenticado y un vehículo sin chofer habitual,
   **cuando** actualiza su chofer habitual a un chofer registrado,
   **entonces** el detalle del vehículo muestra el chofer asignado.
3. **Dado** un administrador autenticado y un vehículo "ABC 123",
   **cuando** intenta actualizar su patente a la de otro vehículo ya registrado,
   **entonces** el sistema rechaza la operación indicando que la patente ya está registrada.
4. **Dado** un administrador autenticado, **cuando** actualiza un vehículo con datos inválidos,
   **entonces** el sistema rechaza la operación y no se guarda ningún cambio parcial.
5. **Dado** un administrador autenticado, **cuando** actualiza un vehículo con un identificador que no existe,
   **entonces** el sistema responde con un error de "vehículo no encontrado".

---

### User Story 8 — Eliminar un vehículo (Priority: P2)

Como administrador, quiero dar de baja un vehículo que ya no se usa, para mantener el listado limpio.

**Why this priority**: Permite vehículos que dejaron de usarse. Viene después del alta y la edición porque el problema aparece recién una vez que hay vehículos cargados.

**Independent Test**: Dar de baja un vehículo y verificar que desaparece del listado.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un vehículo sin servicios asociados,
   **cuando** lo da de baja,
   **entonces** el vehículo desaparece del listado.
2. **Dado** un administrador autenticado y un vehículo con servicios asociados,
   **cuando** intenta darlo de baja,
   **entonces** el sistema rechaza la operación indicando que tiene servicios asociados.
3. **Dado** un administrador autenticado, **cuando** da de baja un vehículo que ya está dado de baja,
   **entonces** el sistema responde con un error de "vehículo no encontrado".
4. **Dado** un administrador autenticado, **cuando** da de baja un vehículo con un identificador que no existe,
   **entonces** el sistema responde con un error de "vehículo no encontrado".

---

### Edge Cases

- **Caso límite**: Un vehículo con patente repetida pero distinta capitalización ("abc 123" vs "ABC 123") debe rechazarse.
- **Caso límite**: Un tipo de vehículo con descripción repetida pero distinta capitalización ("camioneta" vs "Camioneta") debe rechazarse.
- **Caso límite**: Un vehículo con tipo de vehículo dado de baja debe rechazarse (integridad referencial).
- **Caso límite**: Un vehículo con chofer habitual dado de baja debe rechazarse (integridad referencial).
- **Caso límite**: La patente debe aceptar formatos de patente argentina (AAA 123 para antiguas, AA 123 ABC para nuevas).

## Requirements *(mandatory)*

### Functional Requirements

**Tipos de Vehículo**

- **FR-001**: El sistema MUST permitir registrar un tipo de vehículo con descripción, capacidad de carga en kg, tarifa hora base y tarifa km excedente.
- **FR-002**: La descripción de un tipo de vehículo MUST ser única y tener entre 3 y 80 caracteres.
- **FR-003**: La capacidad de carga en kg MUST ser un número positivo mayor a cero.
- **FR-004**: La tarifa hora base MUST ser un número decimal no negativo.
- **FR-005**: La tarifa km excedente MUST ser un número decimal no negativo.
- **FR-006**: El sistema MUST asignar un identificador único y las fechas de creación y última modificación al registrar un tipo de vehículo.
- **FR-007**: El sistema MUST permitir listar tipos de vehículo con paginación y búsqueda por descripción.
- **FR-008**: El sistema MUST permitir ver el detalle de un tipo de vehículo por su identificador.
- **FR-009**: El sistema MUST permitir actualizar los datos de un tipo de vehículo, validando que la descripción no se repita con otro tipo de vehículo.
- **FR-010**: El sistema MUST permitir dar de baja un tipo de vehículo que no tenga vehículos asociados.
- **FR-011**: El sistema MUST rechazar la baja de un tipo de vehículo que tenga vehículos asociados.

**Vehículos**

- **FR-012**: El sistema MUST permitir registrar un vehículo con patente, tipo de vehículo y opcionalmente un chofer habitual.
- **FR-013**: La patente de un vehículo MUST ser única y tener formato de patente argentina (AAA 123 o AA 123 ABC).
- **FR-014**: El tipo de vehículo de un vehículo MUST existir y estar activo.
- **FR-015**: El chofer habitual de un vehículo, si se especifica, MUST existir y estar activo.
- **FR-016**: El sistema MUST asignar un identificador único y las fechas de creación y última modificación al registrar un vehículo.
- **FR-017**: El sistema MUST permitir listar vehículos con paginación y búsqueda por patente.
- **FR-018**: El sistema MUST permitir ver el detalle de un vehículo por su identificador.
- **FR-019**: El sistema MUST permitir actualizar los datos de un vehículo, validando que la patente no se repita con otro vehículo.
- **FR-020**: El sistema MUST permitir dar de baja un vehículo que no tenga servicios asociados.
- **FR-021**: El sistema MUST rechazar la baja de un vehículo que tenga servicios asociados.

### Contrato de API

**Tipos de Vehículo**

| Método | Ruta | Rol | Resultado |
|---|---|---|---|
| POST | /api/tipos-vehiculo | admin | 201 Created |
| GET | /api/tipos-vehiculo | admin, chofer | 200 OK |
| GET | /api/tipos-vehiculo/{id} | admin, chofer | 200 OK |
| PUT | /api/tipos-vehiculo/{id} | admin | 200 OK |
| DELETE | /api/tipos-vehiculo/{id} | admin | 204 No Content |

**Vehículos**

| Método | Ruta | Rol | Resultado |
|---|---|---|---|
| POST | /api/vehiculos | admin | 201 Created |
| GET | /api/vehiculos | admin, chofer | 200 OK |
| GET | /api/vehiculos/{id} | admin, chofer | 200 OK |
| PUT | /api/vehiculos/{id} | admin | 200 OK |
| DELETE | /api/vehiculos/{id} | admin | 204 No Content |

### Key Entities

- **TipoVehiculo**: id_tipo_vehiculo, descripcion, capacidad_carga_kg, tarifa_hora_base, tarifa_km_excedente, activo, creado_en, actualizado_en.
- **Vehiculo**: id_vehiculo, patente, id_tipo_vehiculo (FK a TipoVehiculo), id_chofer_habitual (FK a Chofer, nullable), activo, creado_en, actualizado_en.
- **Chofer** (mínimo para FK): id, activo. La entidad completa llega en H2.

### Decisiones pendientes de confirmación con el cliente

- **DP-01**: Formato exacto de patente aceptado (por ahora: AAA 123 o AA 123 ABC). **[Supuesto temporal]**
- **DP-02**: Si un vehículo puede cambiar de chofer habitual libremente o si hay restricciones de agenda. **[Supuesto temporal]**
- **DP-03**: Si la baja de un vehículo debe verificar servicios asociados (por ahora: sí, con stub que devuelve False hasta H6). **[Supuesto temporal]**

### Success Criteria *(mandatory)*

- **SC-001**: El CRUD completo de tipos de vehículo funciona correctamente con validaciones de negocio.
- **SC-002**: El CRUD completo de vehículos funciona correctamente con validaciones de negocio.
- **SC-003**: Las búsquedas por descripción y patente funcionan correctamente.
- **SC-004**: Las bajas lógicas funcionan correctamente y no permiten bajas con dependencias.

### Measurable Outcomes

- 100% de cobertura de tests unitarios sobre la capa de Aplicación para tipos de vehículo y vehículos.
- Todos los criterios de aceptación de la spec están cubiertos por tests.

### Assumptions

- La tabla de choferes existe mínimamente (solo id y activo) para soportar el FK de `id_chofer_habitual`. La entidad completa llega en H2.
- La verificación de servicios asociados a un vehículo para permitir la baja es un stub que devuelve False hasta la historia de servicios (H6).
