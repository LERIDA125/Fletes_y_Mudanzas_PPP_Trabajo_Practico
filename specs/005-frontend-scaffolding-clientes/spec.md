# Feature Specification: 005 — Frontend Scaffolding y Listado de Clientes

**Feature Branch**: `005-frontend-scaffolding-clientes`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Scaffolding inicial del proyecto Frontend (Next.js, Tailwind) y una primera vista básica: el Dashboard / Listado de Clientes, consumiendo la API de clientes existente."

## Out of Scope

- Alta, modificación y baja de clientes. Esta historia solo **lee**; los botones de escritura no
  existen todavía porque su comportamiento pertenece al `spec.md` de H1, no a éste.
- Autenticación real, sesiones y guard de rol. El backend todavía consume el rol por un stub de
  header (DD-3), por lo que no hay login que resguardar. El route group `(admin)` se crea por
  estructura; el middleware y la redirección llegan con la historia de autenticación.
- Los módulos de choferes, vehículos, tipos de vehículo, agenda, servicios, cotizaciones, pagos,
  cuenta corriente y rendiciones.
- Un panel con métricas o tarjetas de resumen: la vista es **el listado**, no un dashboard de
  indicadores. Si un futuro spec pide un dashboard, rediseña la ruta en ese spec.
- Alta, edición o eliminación de cualquier entidad desde el navegador.
- Cálculos de negocio de cualquier tipo. Los totales y las cifras los calcula el backend
  (Principio III de la constitución).
- Despliegue a producción y dominio final. Solo se trabaja sobre el entorno de desarrollo local.
- Exportación a Excel/CSV del listado.
- Pruebas end-to-end con Playwright. Se difieren hasta que exista un flujo completo con datos
  sembrables en el entorno de desarrollo; la verificación de esta historia se hace con pruebas
  unitarias de componentes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Scaffolding del proyecto frontend (Priority: P1)

Como equipo de desarrollo, quiero que exista el proyecto frontend andando, con su estructura de
carpetas, sus verificaciones de calidad y sus tipos de API generados desde el backend, para poder
construir encima historias de usuario reales.

**Why this priority**: Es la condición necesaria de las otras dos historias: sin el proyecto no se
renderiza ninguna vista. Además es el único entregable que se puede demostrar de forma
aislada —"el proyecto arranca y las verificaciones están en verde"— y su falla bloquea todo lo
demás. Se ubica antes que el valor de negocio porque no existe frontend previo (greenfield).

**Independent Test**: Clonar el repositorio, instalar dependencias, arrancar el proyecto con un
comando y ejecutar lint, formato, tests unitarios y regeneración de tipos. El resultado esperado
es la pantalla de bienvenida en el navegador y todas las verificaciones en verde, sin necesidad
de las otras dos historias.

**Acceptance Scenarios**:

1. **Dado** el repositorio recién clonado y sin dependencias instaladas, **cuando** el desarrollador
   ejecuta el comando de instalación y luego el de arranque del entorno de desarrollo,
   **entonces** la aplicación responde en el navegador sin errores de compilación.
2. **Dado** el proyecto arrancado, **cuando** el desarrollador ejecuta las verificaciones de lint,
   formato y tests unitarios, **entonces** las tres terminan sin hallazgos y sin tests fallidos.
3. **Dado** el contrato OpenAPI publicado por el backend, **cuando** el desarrollador ejecuta el
   comando documentado de generación de tipos, **entonces** se regenera el archivo de tipos del
   cliente y su contenido es idéntico al versionado en el repositorio.
4. **Dado** un cambio en un schema del backend que modifique el contrato OpenAPI, **cuando** corre
   el proceso de integración continua, **entonces** la verificación de tipos detecta la diferencia
   y el proceso falla antes de aprobar el cambio.
5. **Dado** el proyecto creado, **cuando** se revisa su árbol de archivos, **entonces** la
   estructura de carpetas corresponde exactamente a la que fija la constitución del proyecto.

---

### User Story 2 — Listado de clientes con paginación (Priority: P2)

Como administrador de Fletes y Mudanzas Express, quiero ver en pantalla los clientes dados de alta
con sus datos de contacto, y poder recorrer la lista completa, para reemplazar la planilla de
Excel con la que trabajo hoy.

**Why this priority**: Es el primer valor de negocio que el usuario final percibe: una pantalla
con datos reales del sistema. Depende de la historia 1 pero entrega valor por sí sola —con este
listado el administrador ya puede trabajar— y no necesita ninguna otra historia implementada.

**Independent Test**: Con al menos 25 clientes dados de alta, abrir la vista y verificar que se
muestran los datos de contacto de la primera tanda, que el total informado coincide con los
clientes registrados y que se puede avanzar hasta la última página sin perder registros. No
requiere búsqueda, ni alta, ni edición.

**Acceptance Scenarios**:

1. **Dado** un administrador, 45 clientes dados de alta y ningún filtro aplicado, **cuando** abre
   la vista, **entonces** ve los primeros 20 clientes con razón social, teléfono, dirección
   habitual, indicador de cuenta corriente y fecha de alta, y ve informado que hay 45 en total
   repartidos en 3 páginas.
2. **Dado** la misma situación, **cuando** navega a la página siguiente, **entonces** ve los
   clientes 21 a 40 y la página anterior sigue disponible.
3. **Dado** un administrador y ningún cliente dado de alta, **cuando** abre la vista, **entonces**
   ve un mensaje que explica que todavía no hay clientes y le indica qué hacer, no una pantalla
   en blanco ni un error.
4. **Dado** un administrador, **cuando** el backend no responde o responde con un error,
   **entonces** ve un mensaje que explica qué falló y una acción para reintentar, no un error
   técnico ni una pantalla vacía sin explicación.
5. **Dado** un administrador con la vista cargada, **cuando** intenta ir a una página más allá de
   la última disponible, **entonces** la vista muestra que no hay resultados en esa página y le
   permite volver a una página con datos, sin quedar en un callejón.
6. **Dado** un cliente con razón social de largo máximo, **cuando** se muestra en la lista,
   **entonces** el texto se acomoda sin desbordar el ancho de la pantalla ni tapar otros datos.

---

### User Story 3 — Búsqueda de clientes por razón social (Priority: P3)

Como administrador, quiero escribir parte de la razón social y ver solo los clientes que
coinciden, para localizar uno concreto sin recorrer la lista completa.

**Why this priority**: Acelera el trabajo habitual pero no es imprescindible para usar la vista:
con la paginación de la historia 2 el administrador ya llega a todos los clientes. Se posterga
porque la búsqueda sin listado base no tiene sobre qué operar.

**Independent Test**: Con al menos tres clientes cuyas razones sociales comparten un prefijo,
escribir ese prefijo y verificar que solo quedan los coincidentes; limpiar el criterio y verificar
que vuelve la lista completa. No requiere alta, edición ni detalle.

**Acceptance Scenarios**:

1. **Dado** un administrador con 45 clientes dados de alta y el cliente "Distribuidora del Sur
   S.A." entre ellos, **cuando** escribe "distribu" en el campo de búsqueda, **entonces** solo
   permanecen los clientes cuya razón social coincide, sin distinguir mayúsculas ni minúsculas, y
   el total informado baja a la cantidad de coincidencias.
2. **Dado** un administrador escribiendo en el campo de búsqueda, **cuando** teclea de forma
   continua, **entonces** el sistema no emite una consulta por tecla: el criterio se aplica después
   de una pausa breve de tecleo o al confirmarlo con Enter.
3. **Dado** un administrador que buscó "distribu" y obtuvo resultados, **cuando** copia la dirección
   de la página, la pega en otra pestaña y la abre, **entonces** ve exactamente los mismos
   resultados; al usar el botón "atrás" del navegador recupera la lista completa.
4. **Dado** un administrador que busca un texto que no coincide con ningún cliente, **cuando** se
   aplica el criterio, **entonces** ve un mensaje que incluye el texto buscado e indica que no hay
   coincidencias, con la opción de limpiar la búsqueda.
5. **Dado** un administrador con un criterio de búsqueda activo en la página 3, **cuando** escribe
   un texto nuevo, **entonces** la búsqueda se aplica desde la página 1, no desde la página 3.

---

### Edge Cases

- **El backend no responde, o responde con error de red**: se muestra un estado de error con
  acción de reintento; nunca una pantalla vacía sin explicación.
- **El backend responde `401` o `403`**: se muestra un mensaje de sesión expirada o de sin
  permisos respectivamente, diferenciado del error genérico, conforme al contrato de integración
  de la constitución.
- **El backend responde con un error `404`, `409` o `422` en una lectura**: situación que el
  contrato de la API no contempla para este listado; se trata como error del servicio con
  reintento.
- **La página pedida queda más allá del total disponible**: el backend devuelve la página vacía
  sin error; la vista informa que no hay resultados en esa página y permite volver a una con datos.
- **Total igual a cero sin criterio de búsqueda**: estado vacío orientado a la acción (no hay
  clientes dados de alta).
- **Total igual a cero con criterio de búsqueda**: estado vacío que repite el criterio buscado e
  invita a limpiarlo.
- **Un solo cliente**: la paginación no ofrece navegación porque hay una sola página.
- **Razón social, dirección o teléfono con largo máximo**: el texto se ajusta al contenedor sin
  desbordar ni superponerse a otras columnas.
- **Espacios sobrantes o caracteres especiales en los datos**: se muestran tal como los devolvió
  el backend, sin normalizarlos visualmente.
- **Cambio de tamaño de pantalla**: en pantalla angosta cada cliente se presenta apilado y legible,
  sin desplazamiento horizontal.
- **El usuario activa la reducción de movimiento**: la interfaz no reproduce animaciones.

## Requirements *(mandatory)*

### Functional Requirements

**Scaffolding (historia 1)**

- **FR-001**: El sistema frontend MUST arrancar con un único comando documentado y servir la
  aplicación en el navegador durante el desarrollo, sin errores de compilación.
- **FR-002**: El sistema frontend MUST respetar la estructura de carpetas que fija la constitución
  (`src/app`, `src/features`, `src/lib`, `src/components/ui`, `src/styles`, `src/types`).
- **FR-003**: El sistema frontend MUST ejecutar localmente y en cada solicitud de incorporación las
  verificaciones de lint, formato y tests unitarios, y éstas MUST terminar sin hallazgos.
- **FR-004**: El sistema MUST generar los tipos del cliente de la API desde el contrato OpenAPI
  publicado por el backend, con un comando documentado, y MUST versionar el resultado en el
  repositorio.
- **FR-005**: El proceso de integración continua MUST regenerar los tipos y MUST fallar si el
  resultado difiere de los tipos versionados, de modo que ninguna diferencia entre backend y
  frontend llegue a producción sin detectarse.
- **FR-006**: El sistema frontend MUST usar TypeScript en modo estricto; ningún `any` está
  permitido sin una justificación escrita junto al código.
- **FR-007**: El gestor de paquetes del proyecto frontend MUST ser **npm**. La constitución delega
  esta elección en el spec de la primera historia de frontend; se elige npm porque ya viene con
  Node.js, así el equipo de cuatro integrantes no depende de instalar ni sincronizar un gestor
  adicional.
- **FR-008**: El sistema frontend MUST definir y hacer revisar el plan de tokens de diseño (color,
  tipografía y layout) **antes** de escribir la primera línea de componente, conforme a la
  constitución.
- **FR-009**: Toda pantalla MUST cumplir WCAG 2.1 nivel AA como mínimo: foco visible, contraste
  suficiente, navegación completa por teclado y respeto de `prefers-reduced-motion`.
- **FR-010**: El sistema frontend MUST ser mobile-first: la vista MUST ser usable en un teléfono
  con una sola mano y sin desplazamiento horizontal.

**Listado (historia 2)**

- **FR-011**: La vista MUST mostrar por cada cliente su razón social, su teléfono, su dirección
  habitual, el indicador de si tiene cuenta corriente y su fecha de alta.
- **FR-012**: La vista MUST informar la cantidad total de clientes que cumplen el filtro y la
  cantidad total de páginas resultante.
- **FR-013**: La cantidad total de páginas MUST calcularse en el cliente a partir del total y del
  tamaño de página que informa el backend. Ésta es aritmética de presentación sobre valores que
  envía el backend, no un cálculo de negocio (Principio III).
- **FR-014**: La vista MUST permitir avanzar y retroceder entre páginas, y MUST deshabilitar la
  navegación cuando no corresponde (primera página hacia atrás, última página hacia adelante).
- **FR-015**: La vista MUST presentar de forma diferenciada los estados de carga, de lista vacía
  y de error, y en el estado de error MUST ofrecer una acción de reintento.
- **FR-016**: Los mensajes de los estados vacío y de error MUST usar el vocabulario del dominio y
  MUST explicar qué ocurrió y qué puede hacer el usuario, sin exponer mensajes técnicos.
- **FR-017**: La vista MUST mostrar las fechas en formato `dd/mm/aaaa` y, cuando haya importes en
  el futuro, la moneda en pesos argentinos formateada con `Intl.NumberFormat`. En esta historia no
  se muestran importes.
- **FR-018**: El sistema MUST mostrar los datos tal como los devuelve el backend, sin normalizar
  mayúsculas, minúsculas ni espacios para su presentación.
- **FR-019**: El listado MUST mostrar únicamente clientes activos, que es lo único que el backend
  devuelve en este listado; no MUST existir una columna de estado porque sería un valor constante.
- **FR-020**: La vista MUST ser navegable íntegramente por teclado y los estados vacío y de error
  MUST ser anunciados por lector de pantalla.

**Búsqueda (historia 3)**

- **FR-021**: La vista MUST permitir buscar clientes por parte de la razón social, sin distinguir
  mayúsculas ni minúsculas, delegando el criterio en el backend.
- **FR-022**: El criterio de búsqueda y el número de página MUST vivir en la dirección de la
  página, de modo que la vista se pueda compartir, recargar y navegar con los botones del
  navegador conservando los mismos resultados.
- **FR-023**: El sistema NO MUST emitir una consulta por tecla; el criterio se aplica tras una
  pausa breve de tecleo o al confirmarlo con Enter.
- **FR-024**: Al aplicar un criterio de búsqueda nuevo el sistema MUST volver a la página 1.
- **FR-025**: Una búsqueda sin coincidencias MUST mostrar un estado vacío específico que repita el
  criterio buscado y permita limpiarlo; NO MUST presentarse como un error.

### Key Entities

- **Cliente**: entidad ya persistida por el backend. Esta historia solo **lee** una proyección de
  ella: identificador, razón social, teléfono, dirección habitual, indicador de cuenta corriente,
  indicador de alta/baja, fecha de alta y fecha de última modificación. El listado expone razón
  social, teléfono, dirección habitual, cuenta corriente y fecha de alta. No se modifican
  atributos de esta historia; los demás módulos del sistema (servicios, cotizaciones,
  rendiciones) referencian a este cliente pero quedan fuera de alcance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con 45 clientes dados de alta, el 100% de ellos es alcanzable desde la vista
  recorriendo las páginas; ninguno queda fuera de alcance por un límite de paginación.
- **SC-002**: Un administrador localiza un cliente conocido escribiendo parte de su razón social
  y leyendo el resultado en menos de 5 segundos, sin recorrer la lista completa.
- **SC-003**: La vista es usable en un teléfono de 360 píxeles de ancho con una sola mano, sin
  desplazamiento horizontal y con todos los campos de cada cliente visibles.
- **SC-004**: Ante una falla del backend, el 100% de los intentos muestra un mensaje que explica
  la falla y ofrece reintentar; en ningún caso se muestra una pantalla vacía sin explicación ni un
  mensaje técnico sin traducir.
- **SC-005**: El equipo arranca el proyecto frontend con un comando y observa lint, formato y
  tests en verde en menos de 10 minutos desde una instalación limpia.
- **SC-006**: Ninguna diferencia entre el contrato del backend y los tipos del frontend se
  incorpora a la rama principal sin que el proceso de integración la detecte.
- **SC-007**: Con el criterio de búsqueda en la dirección de página, abrir ese enlace en una
  segunda pestaña reproduce exactamente los mismos resultados.
- **SC-008**: Todas las acciones de la vista son alcanzables con teclado solo y los estados de
  carga, vacío y error son anunciados por un lector de pantalla.

## Brief de diseño

> Requerido por la constitución: el diseño parte de este brief y de un plan de tokens revisado
> **antes** de escribir la primera línea de componente. El plan de tokens (valores concretos de
> color, tipografía y layout) vive en `plan.md`.

- **Quién lo usa**: el personal administrativo de la empresa desde un escritorio, y el chofer desde
  un celular en la calle, con una mano. Esta historia construye la vista del administrador, pero
  se aplica sobre ella desde el inicio el criterio mobile-first porque el rol de chofer llega
  después sobre esta misma base.
- **Qué reemplaza**: una planilla de Excel. Quien mira la pantalla **ya conoce a los clientes** por
  nombre. El trabajo de la página es **encontrar y confirmar**, no explorar ni descubrir.
- **Trabajo concreto de la página**: localizar un cliente rápido, ver de un vistazo si tiene
  cuenta corriente, y saber cuántos clientes hay en total.
- **Vocabulario**: razón social, teléfono, dirección habitual, cuenta corriente, cliente dado de
  baja. El vocabulario del dominio, no el de software genérico ("nombre", "balance", "inactivo").
  El texto de la interfaz es consistente de punta a punta: si el botón dice "Limpiar búsqueda", el
  mensaje relacionado dice "Búsqueda limpiada".
- **Tono**: operativo, denso pero legible, como un manifiesto de carga bien compuesto. No es una
  pantalla de marketing y no tiene nada que vender.
- **Idioma y formatos**: `es-AR`, fechas `dd/mm/aaaa`, moneda ARS cuando haya importes (no los hay
  en esta vista).
- **Accesibilidad**: WCAG 2.1 AA, foco visible, navegación por teclado, lector de pantalla,
  `prefers-reduced-motion`.
- **Una sola cosa memorable**: la lista misma, compuesta con la disciplina de un registro
  impreso. No se agregan adornos ni elementos decorativos que no aporten información.

## Assumptions

- El gestor de paquetes del proyecto frontend es **npm**; la constitución delega expresamente esta
  elección en el spec de la primera historia de frontend (ver FR-007).
- La vista se publica en la raíz `/` del entorno de administrador. Cuando un futuro spec agregue
  un dashboard con métricas, ese spec decide si el listado se traslada a una ruta propia.
- El endpoint de lectura de clientes no exige rol, conforme a DD-3 (el rol todavía se resuelve por
  un stub de cabecera hasta la historia de autenticación). Por eso esta historia puede construirse
  sin login.
- El route group `(admin)` se crea desde esta historia por estructura, pero el middleware y la
  redirección por sesión se implementan en la historia de autenticación. El guard de rol del
  frontend es experiencia de usuario, nunca una frontera de seguridad: la autorización real la
  aplica el backend.
- El backend devuelve **únicamente clientes activos** en el listado (el repositorio filtra por
  `activo`), por lo que no existe columna de estado que mostrar (ver FR-019).
- El repositorio de datos de desarrollo puede arrancar sin clientes dados de alta, porque no existe
  un cargador de datos de demostración; el estado vacío es parte del alcance y no una carencia.
- La versión de cada tecnología del stack frontend debe verificarse contra la documentación oficial
  vigente antes de implementar: la constitución fija versiones mayores ratificadas sin acceso a la
  documentación y exige corregirlas por enmienda si la verificación las contradice.
- El backend sigue exponiendo su contrato en OpenAPI con la ruta por defecto de FastAPI; ésa es la
  fuente de verdad de la que se generan los tipos (FR-004, FR-005).
- La búsqueda por razón social se delega en el filtro que ya expone el backend; el frontend no
  implementa un filtro propio sobre los datos recibidos.
