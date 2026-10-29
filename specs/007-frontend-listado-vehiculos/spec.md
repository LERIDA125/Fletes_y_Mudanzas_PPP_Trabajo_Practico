# Feature Specification: 007 — Listado de Vehículos

**Feature Branch**: `007-frontend-listado-vehiculos`

**Created**: 2026-10-21

**Status**: Draft — pendiente de aprobación del Tech Lead

**Input**: User description: "Implementar el listado frontend de vehículos. Ajustar el contrato de lectura para que el backend entregue nombres legibles del tipo y del chofer habitual junto con los datos del vehículo."

## Decisión de alcance

El backend enriquecerá la respuesta de `GET /api/vehiculos` con la descripción del tipo de
vehículo, su capacidad de carga y el nombre del chofer habitual. El listado no mostrará IDs de
relaciones como sustituto de nombres legibles.

La capacidad de carga pertenece al tipo de vehículo; **no se agrega una tara**. Esta historia no
requiere migraciones ni cambios en los payloads o en el comportamiento de alta y edición.

## Out of Scope

- Alta, edición y baja de vehículos o tipos de vehículo.
- Detalle de vehículo y otras pantallas de gestión.
- Cambiar la búsqueda existente por patente, el orden estable, los filtros de activos o la
  paginación del backend.
- Modificar tablas, agregar columnas o ejecutar migraciones.
- Cambiar los payloads de `POST /api/vehiculos` o `PUT /api/vehiculos/{vehiculo_id}`.
- Mostrar tarifas, facturación, cotizaciones u otros cálculos de negocio.
- Resolver o emular relaciones mediante llamadas adicionales desde el navegador.
- Autenticación real, middleware de sesión o permisos nuevos.
- Pruebas E2E con Playwright; se cubre el comportamiento con pruebas unitarias de componentes
  y pruebas de integración del contrato de lectura del backend.

## User Scenarios & Testing

### User Story 1 — Consultar la flota (Priority: P1)

Como administrador de Fletes y Mudanzas Express, quiero ver los vehículos activos con su patente,
tipo, capacidad de carga y chofer habitual, para identificar la unidad que necesito sin descifrar
IDs internos.

**Why this priority**: El listado convierte el registro de flota existente en información operativa
legible y reutiliza los datos de tipo y chofer ya persistidos.

**Independent Test**: Con más de 20 vehículos activos, abrir `/vehiculos`, verificar los datos
legibles de una unidad en la primera página, avanzar y retroceder entre páginas, y confirmar que
una unidad con tipo y chofer asociados muestra sus nombres y capacidad.

**Acceptance Scenarios**:

1. **Dado** un administrador y vehículos activos, **cuando** abre `/vehiculos`, **entonces** ve
   por cada fila la patente, la descripción del tipo, la capacidad de carga en kilogramos, el
   nombre del chofer habitual y la fecha de alta.
2. **Dado** un vehículo activo con tipo existente y chofer habitual asignado, **cuando** el
   listado se carga, **entonces** presenta la descripción y capacidad del tipo y el nombre
   completo del chofer, sin presentar sus IDs como sustituto.
3. **Dado** un vehículo activo sin chofer habitual, **cuando** aparece en el listado, **entonces**
   el campo de chofer indica claramente que no tiene uno asignado.
4. **Dado** más vehículos que el tamaño de página, **cuando** se recorre el listado, **entonces**
   se puede avanzar y retroceder, el total y las páginas corresponden a la respuesta del backend,
   y la primera página no lleva un parámetro de página innecesario.
5. **Dado** un usuario en una página posterior, **cuando** filtra por parte de una patente,
   **entonces** el filtro se refleja en la URL, vuelve a la primera página y muestra las
   coincidencias informadas por el backend.
6. **Dado** un criterio de búsqueda que no coincide con vehículos, **cuando** se aplica, **entonces**
   la vista muestra un mensaje vacío que incluye el criterio y permite limpiar la búsqueda.
7. **Dado** que no existen vehículos activos, **cuando** se abre el listado sin criterio,
   **entonces** aparece un mensaje que explica que todavía no hay vehículos, sin mostrar una tabla
   vacía como si fuera un error.
8. **Dado** que la API no responde o devuelve un error, **cuando** se intenta cargar la vista,
   **entonces** aparece un mensaje comprensible y una acción para reintentar, sin filtrar detalles
   técnicos.
9. **Dado** un ancho de pantalla de 360 px y textos largos, **cuando** se muestra el listado,
   **entonces** cada vehículo se lee en una disposición apilada y no hay desplazamiento horizontal.

### User Story 2 — Buscar un vehículo por patente (Priority: P2)

Como administrador, quiero buscar por una parte de la patente para localizar una unidad sin
recorrer todas las páginas.

**Why this priority**: El filtrado reduce el tiempo de consulta en una flota creciente y ya está
soportado por el endpoint.

**Independent Test**: Con varias patentes conocidas, escribir un fragmento, verificar que la URL
contiene `q`, que el criterio se aplica tras una pausa de tecleo o al confirmar y que limpiar la
búsqueda restaura el listado.

**Acceptance Scenarios**:

1. **Dado** un listado cargado, **cuando** el usuario escribe parte de una patente, **entonces** la
   vista aplica el criterio después de una pausa breve de tecleo y no navega por cada pulsación.
2. **Dado** un criterio escrito, **cuando** el usuario confirma con Enter, **entonces** la búsqueda
   se aplica de inmediato y empieza en la primera página.
3. **Dado** un criterio aplicado, **cuando** se recarga o comparte la URL, **entonces** el listado
   conserva criterio y página; la navegación atrás/adelante restaura los criterios anteriores.
4. **Dado** un criterio aplicado, **cuando** el usuario limpia la búsqueda, **entonces** se quitan
   `q` y `page` de la URL y vuelve el listado completo desde la primera página.

## Edge Cases

- El valor `id_chofer_habitual` puede ser nulo: el nombre legible también debe ser nulo y la
  interfaz muestra "Sin chofer habitual".
- Un vehículo con un tipo asociado siempre debe devolver descripción y capacidad de carga. La
  relación de tipo es obligatoria en el modelo actual.
- Un chofer asignado puede darse de baja lógicamente después de asociarse. Como su fila se conserva,
  el listado debe poder seguir mostrando su nombre; la consulta no debe descartar el vehículo por
  el estado `activo` del chofer.
- La paginación fuera del total devuelve cero elementos sin error; la vista ofrece volver al
  listado desde una página con datos.
- El total corresponde al filtro de patente y no se multiplica por los JOIN.
- Los valores numéricos de capacidad se presentan en kg sin recalcular datos de negocio.
- La vista muestra únicamente los vehículos que el endpoint ya considera activos.
- Errores `401` y `403` mantienen los estados diferenciados que ofrece el cliente HTTP compartido.

## Requirements

### Functional Requirements

- **FR-001**: La ruta `/vehiculos` MUST listar vehículos activos obtenidos directamente del
  endpoint `GET /api/vehiculos`.
- **FR-002**: Cada vehículo del listado MUST mostrar patente, descripción del tipo de vehículo,
  capacidad de carga en kg, nombre del chofer habitual (o "Sin chofer habitual") y fecha de alta.
- **FR-003**: Como prerrequisito, `GET /api/vehiculos` MUST incluir los campos legibles
  `descripcion_tipo_vehiculo`, `capacidad_carga_kg` y `nombre_chofer_habitual`, además de los
  campos actuales. La capacidad es la definida en el tipo asociado, no una tara del vehículo.
- **FR-004**: La consulta de lectura MUST obtener descripción y capacidad del tipo y nombre del
  chofer mediante JOINs en el backend; el frontend MUST NOT resolver relaciones mediante
  peticiones adicionales.
- **FR-005**: El JOIN al chofer MUST preservar vehículos sin chofer habitual y vehículos cuyo
  chofer asociado haya sido dado de baja lógicamente.
- **FR-006**: La respuesta paginada MUST conservar `items`, `total`, `page` y `size`, el orden
  estable y el filtro por patente existentes.
- **FR-007**: La vista MUST informar el total de resultados y el número de páginas, y permitir
  navegación anterior/siguiente sin ofrecer acciones inválidas en los extremos.
- **FR-008**: El criterio `q` y el número de página MUST vivir en la URL; al cambiar el criterio se
  vuelve a la primera página. La búsqueda se aplica con debounce de 350 ms o al confirmar con
  Enter.
- **FR-009**: El listado MUST distinguir carga, ausencia inicial de datos, ausencia de coincidencias,
  página fuera de rango y error de servicio. Los estados de error MUST ofrecer reintento y los
  vacíos por búsqueda MUST permitir limpiar el criterio.
- **FR-010**: Los datos MUST presentarse con el vocabulario del dominio, sin exponer mensajes
  técnicos ni IDs de relaciones como información principal.
- **FR-011**: La interfaz MUST ser mobile-first, usable desde 360 px sin desplazamiento horizontal,
  accesible por teclado, con foco visible y estados anunciados; MUST respetar `prefers-reduced-motion`.
- **FR-012**: Las fechas MUST usar formato `dd/mm/aaaa` en la zona `America/Argentina/Buenos_Aires`.
- **FR-013**: El frontend MUST consumir tipos generados desde OpenAPI y no MUST definir manualmente
  el contrato de `VehiculoRead`.
- **FR-014**: Los campos de alta/edición y el comportamiento de `POST` y `PUT` MUST permanecer sin
  cambios; esta historia MUST NOT agregar columnas ni migraciones.
- **FR-015**: La presentación MUST limitarse a formatear los valores recibidos; no MUST calcular
  capacidad ni derivar cifras de negocio.

## Key Entities

- **Vehículo listado**: proyección de lectura de un vehículo activo con `id`, `patente`,
  `id_tipo_vehiculo`, `id_chofer_habitual`, `descripcion_tipo_vehiculo`,
  `capacidad_carga_kg`, `nombre_chofer_habitual` y `creado_en`. Los IDs existentes se conservan
  para compatibilidad, aunque la vista prioriza los valores legibles.
- **Tipo de vehículo**: entidad existente. La descripción y la capacidad de carga se leen de la
  fila asociada; no se modifica su persistencia.
- **Chofer habitual**: entidad existente y relación opcional. La interfaz muestra el nombre
  asociado o el estado sin asignación.

## Brief de diseño

- **Audiencia**: administradores que consultan la flota desde escritorio y teléfonos.
- **Trabajo principal**: reconocer una unidad por patente y comprender de inmediato qué tipo es,
  cuánto puede cargar y quién la conduce habitualmente.
- **Dirección visual**: se conserva el sistema aprobado en 005: papel frío `#F7F8FA`, tinta
  `#15181D`, tinta secundaria `#5C6575`, líneas `#E1E5EA`, señal `#1E4AA8` y alerta `#B42318`.
  La banda superior de identidad es el único gesto de alto contraste.
- **Tipografía**: Archivo, con la patente como dato de reconocimiento prioritario; capacidad con
  cifras tabulares y unidad explícita.
- **Layout**: tabla compacta en escritorio con patente, tipo/capacidad, chofer y alta; en celular,
  cada fila se apila con etiquetas visibles, sin tarjetas decorativas ni scroll horizontal.
- **Principio**: optimizar la identificación de unidades; los identificadores técnicos no compiten
  con los nombres que necesita el usuario.

## Success Criteria

- **SC-001**: Con 45 vehículos, todos son alcanzables mediante la paginación del endpoint y el
  total coincide con la cantidad que cumple el filtro.
- **SC-002**: El 100% de las filas del listado muestra descripción y capacidad del tipo correcto; el
  nombre del chofer corresponde a la relación o se indica explícitamente su ausencia.
- **SC-003**: En 360 px de ancho se pueden leer todos los datos de una fila sin scroll horizontal.
- **SC-004**: Un administrador localiza un vehículo con una búsqueda por patente en menos de
  5 segundos sin recorrer la lista completa.
- **SC-005**: Los errores y estados vacíos nunca dejan la página sin explicación ni acción
  apropiada.
- **SC-006**: Cambios incompatibles entre el OpenAPI del backend y los tipos frontend generan una
  diferencia detectable al regenerar los tipos.

