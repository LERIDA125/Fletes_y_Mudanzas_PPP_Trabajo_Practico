# Feature Specification: H3 — Gestión de Choferes

**Feature Branch**: `feature/CRUD_choferes`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "El sistema debe permitir gestionar choferes. Cada chofer tiene un nombre completo, un teléfono, un indicador de activo y un saldo a favor. Se requiere alta, consulta de activos, modificación y baja lógica."

## Out of Scope

- Autenticación del chofer en la aplicación (usuario, contraseña, JWT) — corresponde a la historia de autenticación.
- Licencia de conducir, categoría profesional, vencimiento de documentación y datos personales extendidos.
- Roles de ayudantes/peones (regla todavía no confirmada por el cliente, AGENTS.md §6).
- Asignación de choferes a vehículos (H4, ya resuelta por FK `id_chofer_habitual`).
- Asignación de choferes a servicios y control de agenda/disponibilidad (H5/H6).
- Movimientos que afectan `saldo_a_favor` (anticipos, pagos, rendiciones) — esta historia solo
  persiste y expone el saldo como dato del chofer; su operatoria económica corresponde a H10/H11.
- Historial de cambios (auditoría) de un chofer.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Registrar un chofer nuevo (Priority: P1)

Como administrador de Fletes y Mudanzas Express, quiero dar de alta un chofer con su nombre completo
y su teléfono, para poder después asignarle vehículos y servicios.

**Why this priority**: Sin choferes cargados no se puede asignar un responsable a los vehículos
(H4) ni agendar servicios (H5/H6). Es el mínimo valor entregable por sí solo: un chofer más un
listado ya le sirven al administrador para reemplazar la parte de la planilla donde lleva el
plantel.

**Independent Test**: Completar el formulario de alta con nombre completo y teléfono y verificar
que el chofer queda disponible en el listado, activo y con `saldo_a_favor = 0.0`. Se puede probar
de punta a punta sin ninguna otra historia implementada.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y ningún chofer con el nombre completo "Juan Pérez",
   **cuando** registra un chofer con nombre completo "Juan Pérez" y teléfono "351 555 0100",
   **entonces** el chofer queda registrado y aparece en el listado con esos mismos datos,
   `activo = true` y `saldo_a_favor = 0.0`.
2. **Dado** un administrador autenticado, **cuando** registra un chofer con nombre completo y
   teléfono válidos, **entonces** el sistema asigna un identificador único y las fechas de creación
   y última modificación, y no permite que el usuario defina esos valores.
3. **Dado** un administrador autenticado, **cuando** registra un chofer con el nombre completo vacío
   o con solo espacios, **entonces** el sistema rechaza la operación informando que el nombre
   completo es obligatorio.
4. **Dado** un administrador autenticado, **cuando** registra un chofer con un teléfono que no tiene
   entre 7 y 20 dígitos, **entonces** el sistema rechaza la operación indicando que el teléfono es
   inválido.
5. **Dado** un administrador autenticado, **cuando** intenta definir `saldo_a_favor` o `activo` en
   el alta, **entonces** el sistema los ignora y aplica sus valores por defecto (`0.0` y `true`
   respectivamente).

---

### User Story 2 — Consultar choferes activos (Priority: P1)

Como administrador, quiero listar y buscar choferes por nombre y ver el detalle de uno, viendo
únicamente a los choferes activos, para encontrar rápido los datos del personal disponible sin
recorrer toda la planilla ni cruzarme con los que ya no trabajan.

**Why this priority**: Es la forma más rápida de obtener valor de la historia y es requisito de las
historias de vehículos (H4), agenda (H5) y servicios (H6), que necesitan resolver un chofer por
nombre entre los disponibles.

**Independent Test**: Con al menos tres choferes activos y uno dado de baja, usar el listado,
aplicar un filtro por nombre y abrir el detalle de uno, verificando que el dado de baja no aparece.
No requiere formulario de alta ni de edición.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y 25 choferes activos, **cuando** solicita el listado sin
   filtros, **entonces** recibe los choferes activos ordenados de forma estable y la respuesta
   indica la cantidad total de choferes activos que cumplen el filtro.
2. **Dado** un administrador autenticado y un chofer "Juan Pérez" activo y otro chofer dado de baja,
   **cuando** solicita el listado sin filtros, **entonces** el resultado incluye a "Juan Pérez" y no
   incluye al chofer dado de baja.
3. **Dado** un administrador autenticado y un chofer "Juan Pérez" activo, **cuando** busca choferes
   con el texto "juan", **entonces** el resultado incluye ese chofer y solo los que coincidan con
   el texto, sin importar mayúsculas ni minúsculas.
4. **Dado** un administrador autenticado y un chofer activo, **cuando** solicita el detalle por su
   identificador, **entonces** recibe nombre completo, teléfono, `activo` y `saldo_a_favor`, junto
   con las fechas de creación y modificación.
5. **Dado** un administrador autenticado, **cuando** busca un texto que no coincide con ningún
   chofer activo, **entonces** recibe un listado vacío con la cantidad total en cero, no un error.
6. **Dado** un administrador autenticado, **cuando** solicita el detalle de un identificador que no
   existe o que corresponde a un chofer dado de baja, **entonces** el sistema responde con un error
   de "chofer no encontrado".

---

### User Story 3 — Modificar un chofer (Priority: P2)

Como administrador, quiero corregir los datos de un chofer ya registrado —por ejemplo, porque cambió
de teléfono o el nombre estaba mal escrito— sin dar de alta un chofer nuevo ni perder su historial.

**Why this priority**: La carga de datos reales siempre tiene errores y cambios de contacto, así que
sin edición el listado se ensucia con duplicados. Viene después del alta porque el problema que
resuelve aparece recién una vez que hay choferes cargados.

**Independent Test**: Editar el teléfono de un chofer existente y verificar que el listado y el
detalle muestran el valor nuevo, y que la fecha de modificación se actualiza.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un chofer con teléfono "351 555 0100", **cuando** actualiza
   su teléfono a "351 555 0199", **entonces** el detalle del chofer muestra el teléfono nuevo y su
   fecha de última modificación es posterior a la de creación.
2. **Dado** un administrador autenticado y un chofer "Juan Perez", **cuando** actualiza su nombre
   completo a "Juan Pérez", **entonces** el detalle del chofer muestra el nombre nuevo.
3. **Dado** un administrador autenticado y un chofer existente, **cuando** guarda la edición con los
   mismos datos que ya tenía, **entonces** la operación se completa correctamente, el chofer conserva
   su identificador, su fecha de creación y su `saldo_a_favor`, y solo se actualiza la fecha de
   modificación.
4. **Dado** un administrador autenticado, **cuando** intenta actualizar un chofer con el nombre
   completo vacío o con un teléfono inválido, **entonces** el sistema rechaza la operación, no la
   guarda y explica qué dato falta.
5. **Dado** un administrador autenticado, **cuando** intenta actualizar un chofer inexistente o dado
   de baja, **entonces** el sistema responde con un error de "chofer no encontrado" y no crea ningún
   registro.
6. **Dado** un administrador autenticado, **cuando** intenta modificar `saldo_a_favor` o `activo` a
   través de la edición de datos, **entonces** el sistema no los modifica (el saldo se mueve por los
   flujos económicos y el estado solo cambia por la baja lógica).

---

### User Story 4 — Dar de baja un chofer (Priority: P3)

Como administrador, quiero dar de baja un chofer que ya no trabaja con Fletes y Mudanzas Express (o
que fue cargado por error), para que no aparezca en la lista de disponibles al asignar vehículos o
agendar servicios, sin perder el historial de servicios que ya realizó.

**Why this priority**: Es la operación menos frecuente y la más delicada, porque un chofer puede estar
referenciado por vehículos y servicios ya realizados. Se implementa como baja lógica (AGENTS.md
§11, DD-1) para no romper la integridad de los datos históricos.

**Independent Test**: Dar de baja un chofer y verificar que deja de aparecer en el listado de activos
y que su detalle ya no está disponible, pero que el registro sigue existiendo en la base de datos con
`activo = false`.

**Acceptance Scenarios**:

1. **Dado** un administrador autenticado y un chofer activo, **cuando** lo da de baja, **entonces** el
   chofer deja de aparecer en el listado de activos y su detalle ya no está disponible.
2. **Dado** un administrador autenticado, **cuando** da de baja un chofer, **entonces** el registro
   permanece en la base de datos con `activo = false` (no se borra físicamente) y conserva su
   identificador, su fecha de creación y su `saldo_a_favor`.
3. **Dado** un administrador autenticado y un chofer ya dado de baja, **cuando** intenta darlo de baja
   otra vez, **entonces** el sistema responde con un error de "chofer no encontrado".
4. **Dado** un administrador autenticado, **cuando** da de baja un chofer con un identificador que no
   existe, **entonces** el sistema responde con un error de "chofer no encontrado".

---

### Edge Cases

- **Nombre con solo espacios**: el nombre completo se considera vacío y el alta o la modificación se
  rechaza.
- **Teléfono con formato heterogéneo**: se aceptan `351 555 0100`, `+54 9 351 555 0100`,
  `0351-555-0100`; el sistema no exige un formato único, pero sí una cantidad mínima de dígitos
  (7 a 20).
- **Teléfono compartido por dos choferes**: se permite, un teléfono no es único.
- **Nombre repetido entre dos choferes**: se permite; el nombre completo no es un identificador de
  negocio y pueden existir homónimos.
- **Texto con caracteres o emojis**: se aceptan, no se rechaza el registro por eso.
- **Nombre completo muy extenso**: se acepta hasta el largo máximo definido; más largo se rechaza.
- **`saldo_a_favor` negativo**: se permite el valor (representa un saldo en contra del chofer);
  esta historia no impone que sea no negativo.
- **Baja de un chofer que es chofer habitual de un vehículo o tiene servicios asociados**: se permite
  la baja lógica; el historial y las referencias quedan intactos (SC-007).
- **Operaciones simultáneas sobre el mismo chofer**: la última actualización válida gana, sin dejar el
  chofer en un estado intermedio inválido.
- **Listado sin resultados**: devuelve lista vacía con total en cero, no un error.
- **Paginación más allá del total disponible**: devuelve la página pedida vacía, sin error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir registrar un chofer con los datos requeridos: nombre completo y
  teléfono.
- **FR-002**: El sistema MUST exigir el nombre completo en el alta: no puede ser nulo ni quedar vacío
  una vez normalizados los espacios sobrantes.
- **FR-003**: El sistema MUST validar el nombre completo con una longitud entre 3 y 120 caracteres,
  una vez normalizados los espacios sobrantes.
- **FR-004**: El sistema MUST validar el teléfono como un texto de 7 a 20 dígitos, admitiendo espacios,
  guiones y el prefijo internacional `+`, y NO MUST exigir un formato único (AGENTS.md §11, DD-4).
- **FR-005**: El sistema MUST asignar al chofer un identificador único y las fechas de creación y última
  modificación; el usuario NO MUST poder informarlos.
- **FR-006**: El sistema MUST inicializar `activo` en `true` y `saldo_a_favor` en `0.0` al registrar un
  chofer, sin permitir que el usuario los defina en el alta.
- **FR-007**: El sistema MUST permitir consultar el listado de choferes **activos** con orden estable,
  paginado, e indicar en la respuesta la cantidad total de choferes activos que cumplen el filtro.
  Los choferes dados de baja MUST NOT aparecer en el listado.
- **FR-008**: El sistema MUST permitir filtrar el listado por texto de búsqueda que coincida, sin
  distinguir mayúsculas y minúsculas, con parte del nombre completo del chofer.
- **FR-009**: El sistema MUST permitir consultar el detalle de un chofer activo por su identificador,
  devolviendo nombre completo, teléfono, `activo`, `saldo_a_favor` y las fechas de creación y
  modificación. Un chofer dado de baja MUST NOT exponerse en el detalle.
- **FR-010**: El sistema MUST permitir modificar el nombre completo y el teléfono de un chofer
  existente, conservando su identificador, su fecha de creación y su `saldo_a_favor`.
- **FR-011**: El sistema MUST rechazar toda alta o modificación con datos requeridos incompletos o
  inválidos, informando cuál fue el dato rechazado y no persistiendo ningún cambio parcial.
- **FR-012**: El sistema MUST NOT permitir modificar `saldo_a_favor` ni `activo` a través de la
  operación de modificación de datos del chofer.
- **FR-013**: El sistema MUST implementar la baja de un chofer como baja lógica: el registro permanece
  en la base de datos con `activo = false` y deja de aparecer en el listado y en el detalle, sin
  borrarse físicamente (AGENTS.md §11, DD-1).
- **FR-014**: El sistema MUST conservar intactos los servicios, vehículos y demás registros que
  referencian a un chofer dado de baja (SC-007).
- **FR-015**: El sistema MUST responder con un error de "chofer no encontrado" ante consultas,
  modificaciones o bajas sobre un identificador inexistente o ya dado de baja, y MUST NOT crear
  registros implícitos.
- **FR-016**: El sistema MUST persistir los datos del chofer en la base de datos de forma persistente,
  de modo que la información sobreviva a un reinicio del servidor.
- **FR-017**: El sistema MUST restringir el alta, la modificación y la baja de choferes al rol `admin`;
  el rol `chofer` MAY ONLY consultar el listado y el detalle (AGENTS.md §11, DD-3).
- **FR-018**: El sistema MUST exponer la gestión de choferes de forma documentada en el contrato
  OpenAPI/Swagger, incluidos los códigos de respuesta de éxito y de error.
- **FR-019**: El sistema MUST registrar la fecha de la última modificación cada vez que un chofer se
  actualiza, y MUST NOT modificarla al consultar.

### Contrato de API

Recursos y endpoints (los nombres exactos pueden ajustarse en `/plan`, el comportamiento es el
especificado arriba):

| Método | Ruta | Rol | Resultado |
|---|---|---|---|
| `GET` | `/api/choferes` | admin, chofer | Listado paginado de choferes activos, con total y filtro opcional por texto |
| `GET` | `/api/choferes/{id}` | admin, chofer | Detalle del chofer activo |
| `POST` | `/api/choferes` | admin | `201` con el chofer creado |
| `PUT` | `/api/choferes/{id}` | admin | `200` con el chofer actualizado |
| `DELETE` | `/api/choferes/{id}` | admin | `204` sin cuerpo (baja lógica) |

Errores esperados: `400`/`422` con detalle por campo cuando falla una validación, `401` si no hay
sesión, `403` si el rol no tiene permiso, `404` si el identificador no existe o el chofer ya está dado
de baja.

### Key Entities

- **Chofer**: persona que conduce los vehículos de Fletes y Mudanzas Express. Atributos:
  - `id` (entero, PK auto-incremental, asignado por el sistema).
  - `nombre_completo` (texto, obligatorio, 3–120 caracteres).
  - `telefono` (texto, 7–20 dígitos, sin formato único — DD-4).
  - `activo` (booleano, por defecto `true`; soporta la baja lógica — DD-1).
  - `saldo_a_favor` (float, por defecto `0.0`; saldo económico a favor del chofer).
  - `creado_en` y `actualizado_en` (fechas de auditoría, asignadas por el sistema).

  Se relaciona con los vehículos de los que es chofer habitual (H4) y con los servicios que realiza
  (H6). Su `saldo_a_favor` se mueve por los flujos económicos de H10/H11, no por esta historia.

### Decisiones pendientes de confirmación con el cliente

Estos puntos no están confirmados por el cliente. La historia se implementa con los supuestos
temporales indicados y, si el cliente decide distinto, se actualiza primero esta sección y luego el
código (AGENTS.md §2 y §5):

- **DP-01 — Alcance de la baja**: se asume baja lógica (el chofer queda inactivo y desaparece del
  listado y del detalle) en lugar de borrado físico, para no romper el historial de servicios y las
  referencias de vehículos. **[Supuesto temporal]**
- **DP-02 — Unicidad del nombre**: se asume que el nombre completo NO es único y pueden existir
  homónimos; solo se distingue a los choferes por su identificador. **[Supuesto temporal]**
- **DP-03 — Permisos**: se asume que el rol `admin` hace el alta, la modificación y la baja, y que el
  rol `chofer` solo consulta (AGENTS.md §11, DD-3). **[Supuesto temporal]**
- **DP-04 — Dato identificatorio del chofer**: se asume que el teléfono es el único dato de contacto y
  que no se exige documento, CUIL ni licencia de conducir en esta historia. **[Supuesto temporal]**
- **DP-05 — Origen y signo de `saldo_a_favor`**: se asume que el saldo puede ser negativo (representa
  un saldo en contra del chofer) y que esta historia solo lo persiste y lo expone; la regla que lo
  mueve se define en H10/H11. **[Supuesto temporal]**
- **DP-06 — Rol de ayudantes/peones**: no se modela en esta historia; la regla sigue abierta
  (AGENTS.md §6) y se resolverá en una historia posterior. **[Supuesto temporal]**

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los criterios de aceptación de esta spec tienen al menos un test automatizado
  que los cubre y pasa en verde.
- **SC-002**: Un administrador que nunca vio el sistema registra un chofer válido y lo encuentra en el
  listado en menos de 2 minutos, sin ayuda externa.
- **SC-003**: Buscar un chofer por nombre devuelve el resultado correcto en menos de 2 segundos con
  1.000 choferes cargados.
- **SC-004**: El sistema no permite bajo ninguna circunstancia registrar ni modificar un chofer con
  datos requeridos incompletos o inválidos.
- **SC-005**: Un chofer cargado desde el sistema aparece correctamente en el listado y en el detalle
  desde otro dispositivo/navegador, confirmando que los datos se persistieron.
- **SC-006**: El 100 % de los endpoints nuevos quedan documentados en Swagger y son invocables
  siguiendo solo esa documentación.
- **SC-007**: Un chofer dado de baja conserva intactos los servicios y vehículos que lo referencian, y
  su registro sigue existiendo en la base de datos con `activo = false`.
- **SC-008**: Ningún chofer dado de baja aparece en el listado ni puede consultarse por detalle.

## Assumptions

- El sistema de autenticación JWT y los roles `admin` / `chofer` ya están disponibles (o se
  reimplementan en otra historia); esta historia solo consume el rol del usuario autenticado
  (AGENTS.md §11, DD-3).
- Existe una tabla mínima de choferes creada en H4 para soportar el FK `id_chofer_habitual` de
  vehículos; esta historia la completa con los campos de negocio (`nombre_completo`, `telefono`,
  `saldo_a_favor`) mediante una migración Alembic.
- Los usuarios acceden al sistema desde navegador de escritorio o tablet; la interfaz es responsive
  según AGENTS.md §1.
- La base de datos es PostgreSQL y las migraciones se gestionan con Alembic, según AGENTS.md §3.
- El volumen inicial es de decenas o cientos de choferes, no de millones; la paginación alcanza para el
  volumen del MVP.
- La modificación se hace por `PUT` completo (AGENTS.md §11, DD-5): el body repite los campos
  obligatorios (nombre completo y teléfono) para que el dominio siempre valide un chofer entero.
- Los horarios y zonas horarias no afectan a esta historia.
