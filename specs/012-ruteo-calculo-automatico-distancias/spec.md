# Feature Specification: 012 — Ruteo y Cálculo Automático de Distancias

**Feature Branch**: `012-ruteo-calculo-automatico-distancias`

**Created**: 2026-10-31

**Status**: Aprobado — backend, frontend y contrato de persistencia implementados; revisión y
aplicación de la migración Alembic pendientes por solicitud del Tech Lead

**Input**: Directiva del Tech Lead para obtener distancias y tiempos de viaje desde un servicio
de mapas de código abierto, sin exponer credenciales en el frontend.

## Resumen ejecutivo

Al registrar un servicio, el administrador envía una búsqueda explícita para cada dirección y
selecciona un resultado de origen y otro de destino. El backend consulta Nominatim para
geocodificarlas y OSRM para calcular la ruta en automóvil; la interfaz muestra la distancia de ida
y el tiempo estimado. El valor de distancia actualiza el campo
existente `distancia_ida_km`, que alimenta la cotización vigente y la reactividad del Motor 011.
Ambos proveedores son consultados exclusivamente desde el backend y no requieren una API key.

La dirección habitual de un cliente nuevo se conserva: no representa el origen ni el destino del
viaje. Los extremos de la ruta se guardan en el servicio para que el recorrido quede asociado al
registro.

## Decisiones propuestas para aprobación

| Tema | Propuesta |
|---|---|
| Proveedores | Nominatim para geocodificación y OSRM para ruteo, mediante sus endpoints públicos. |
| Selección de direcciones | La búsqueda solo se ejecuta al presionar Buscar o Enter; no se consulta Nominatim al tipear. Se exige selección explícita y no se enruta una dirección ambigua. |
| Distancia | Usar la distancia de ida de OSRM; el formulario la carga en `distancia_ida_km`. El cálculo vigente de cotización sigue duplicándola según la regla existente. |
| Edición manual / contingencia | El campo de distancia queda de solo lectura y no hay fallback manual cuando el proveedor falla. El error se informa y se puede reintentar. |
| Persistencia | Guardar las etiquetas elegidas de origen y destino con el servicio. El tiempo de ruta se muestra como estimación y no se persiste en esta historia. |
| Motor 011 | Integrar mediante la actualización del valor observado del formulario, sin agregar una fórmula de precio en el cliente. Su contrato aprobado es un prerrequisito de implementación. |

## Dependencia y alcance existente

El Tech Lead confirmó que la entrada de distancia del motor vigente es
`CotizacionRequest.distancia_ida_km` y que la fórmula está en `EstrategiaPorHoraYKm`. El backend
mantiene la cotización como autoridad: cuando la ruta aplica la distancia calculada, el frontend debe
solicitar de nuevo `POST /api/servicios/cotizar` y presentar el `precio_final` recibido, sin calcular
el precio localmente.

En el código actual no hay un campo llamado `precio_sugerido` ni una solicitud automática de
cotización al cambiar kilómetros: el formulario permite pedirla mediante una acción explícita.
La fase frontend debe implementar el recálculo automático mediante el endpoint existente, evitando
presentar como vigente una cotización previa. Esta historia no cambia la fórmula ni el contrato de
cotización.

El formulario actual usa `distancia_ida_km` (no `km_estimados`) como distancia de ida. La historia
conserva ese contrato para el alta y la cotización del servicio.

## Out of Scope

- Google Maps, proveedores pagos, navegación paso a paso, mapas interactivos o visualización de geometría.
- Cálculo de precio, cambios a tarifas, franquicia o fórmula de cotización.
- Geocodificación o ruteo directamente desde el navegador.
- Persistir coordenadas, geometría completa de la ruta o el tiempo estimado en el servicio.
- Fallback automático a otros proveedores, edición manual de la distancia o cotización si un proveedor no responde.
- Cambiar la dirección habitual del cliente o su comportamiento de alta.
- Cambios a disponibilidad, asignación de vehículos/choferes o autenticación.

## User Scenarios & Testing

### User Story 1 — Seleccionar el recorrido (Priority: P1)

Como administrador, quiero buscar y seleccionar el origen y el destino del servicio para identificar
sin ambigüedad las ubicaciones que se usarán en el cálculo de la ruta.

**Independent Test**: Enviar dos búsquedas explícitas, elegir un resultado para cada extremo y
verificar que el formulario conserva las selecciones y solicita la ruta con sus coordenadas.

**Acceptance Scenarios**:

1. **Dado** un administrador y una búsqueda válida, **cuando** la envía explícitamente,
   **entonces** recibe opciones legibles con coordenadas desde el backend y puede seleccionar una.
2. **Dado** que no hay sugerencias para una búsqueda, **cuando** termina la consulta, **entonces**
   la interfaz informa que no encontró coincidencias y no calcula una ruta.
3. **Dado** que se modifica una dirección después de seleccionarla, **cuando** cambia el texto,
   **entonces** se invalida la selección previa, la ruta y la distancia asociadas a ella.
4. **Dado** que el proveedor no responde, **cuando** se envía una búsqueda,
   **entonces** la interfaz informa que no se pudo completar la búsqueda, sin mostrar credenciales
   ni detalles internos.

### User Story 2 — Calcular y aplicar la ruta (Priority: P1)

Como administrador, quiero obtener la distancia y el tiempo estimado entre las ubicaciones elegidas
para cotizar el servicio con kilómetros de ida calculados automáticamente.

**Independent Test**: Enviar al backend dos ubicaciones seleccionadas y verificar que devuelve la
distancia y duración de OSRM; comprobar que `distancia_ida_km` recibe la distancia devuelta.

**Acceptance Scenarios**:

1. **Dado** un origen y un destino seleccionados, **cuando** ambos están disponibles, **entonces**
   la interfaz consulta `POST /api/mapas/ruta` y muestra distancia de ida y tiempo estimado.
2. **Dado** una respuesta de ruta válida, **cuando** se completa el cálculo, **entonces** se
   actualiza `distancia_ida_km` con la distancia de ida redondeada a dos decimales y se notifica
   al Motor 011 mediante el mecanismo reactivo existente.
3. **Dado** que se cambia el origen o destino tras calcular la ruta, **cuando** cambia cualquiera
   de las selecciones, **entonces** se descartan el resultado y la cotización anteriores; no se
   puede registrar el servicio con kilómetros de una ruta distinta.
4. **Dado** que OSRM no encuentra una ruta, **cuando** se calcula, **entonces** la interfaz muestra
   un error recuperable y no permite usar una distancia anterior ni registrar el servicio.
5. **Dado** una demora o error del proveedor, **cuando** termina la solicitud, **entonces** se
   informa el fallo y se permite reintentar sin exponer el error crudo del proveedor.
6. **Dado** que una respuesta anterior llega después de que se cambiaron las ubicaciones,
   **cuando** la interfaz procesa las respuestas, **entonces** ignora el resultado obsoleto.

### User Story 3 — Registrar el servicio con el recorrido (Priority: P1)

Como administrador, quiero que el servicio conserve las ubicaciones seleccionadas junto con la
distancia aplicada para poder identificar el recorrido cotizado.

**Independent Test**: Crear un servicio válido con origen, destino y distancia calculada; consultar
el registro y verificar que devuelve las dos direcciones y la distancia de ida.

**Acceptance Scenarios**:

1. **Dado** un servicio nuevo, **cuando** se confirma el alta, **entonces** el backend valida y
   persiste origen, destino y distancia de ida en la misma operación.
2. **Dado** un alta sin origen o destino seleccionado, **cuando** se intenta confirmar,
   **entonces** la API la rechaza y no crea un registro parcial.
3. **Dado** un servicio histórico creado antes de esta migración, **cuando** se consulta,
   **entonces** sigue siendo legible y sus direcciones de ruta aparecen nulas.

## Requirements

### Functional Requirements

- **FR-001**: La API MUST ofrecer `POST /api/mapas/direcciones` para buscar sugerencias de
  direcciones y `POST /api/mapas/ruta` para calcular una ruta entre dos ubicaciones seleccionadas.
- **FR-002**: Ambos endpoints MUST requerir el rol `admin`, validar el payload y delegar la
  operación a un único método de Aplicación.
- **FR-003**: El backend MUST consultar Nominatim (`https://nominatim.openstreetmap.org/search`)
  para geocodificar y OSRM (`https://router.project-osrm.org/route/v1/driving/`) para calcular
  rutas. No MUST requerir credenciales. Las búsquedas Nominatim MUST enviar un `User-Agent`
  descriptivo, MUST respetar el límite de una solicitud por segundo y MUST cachear consultas
  repetidas. La interfaz MUST esperar una acción explícita del usuario antes de buscar y MUST NOT
  implementar autocomplete consultando Nominatim mientras se tipea.
- **FR-004**: La búsqueda MUST devolver un conjunto acotado de sugerencias con etiqueta legible y
  coordenadas validadas. La interfaz MUST requerir que el operador seleccione una sugerencia para
  cada extremo antes de calcular la ruta.
- **FR-005**: El ruteo MUST usar un perfil fijo de automóvil y una URL externa configurada en
  código/configuración del servidor; el request del usuario MUST NOT controlar host, URL ni perfil
  del proveedor.
- **FR-006**: La respuesta de ruta MUST incluir `distancia_ida_km` y `duracion_segundos` tomados de
  la ruta devuelta por OSRM. La distancia MUST convertirse de metros a kilómetros y redondearse a
  dos decimales con `Decimal` y `ROUND_HALF_UP`.
- **FR-007**: El formulario MUST conservar las etiquetas de origen y destino seleccionadas,
  mostrar el tiempo como estimación y actualizar `distancia_ida_km` al recibir la ruta. El
  comportamiento MUST quedar invalidado al editar cualquiera de las ubicaciones.
- **FR-008**: La actualización programática de `distancia_ida_km` MUST disparar una nueva solicitud
  al cotizador existente (`POST /api/servicios/cotizar`) y presentar su `precio_final` como precio
  sugerido vigente. El frontend MUST NOT implementar una fórmula de precio local.
- **FR-009**: El alta del servicio MUST persistir las direcciones elegidas. La lectura del servicio
  MUST devolverlas; las filas históricas pueden tener ambos valores nulos.
- **FR-010**: Las fallas de geocodificación, ruteo, timeout y disponibilidad del
  proveedor MUST producir errores explícitos y seguros. Los detalles internos, credenciales y
  respuestas crudas MUST NOT filtrarse al cliente.
- **FR-011**: Las direcciones y coordenadas consultadas MUST usarse solo para la búsqueda/ruta y no
  MUST registrarse en logs de aplicación ni persistirse como coordenadas/geometría.
- **FR-012**: El frontend MUST consumir la API FastAPI mediante los módulos existentes de
  `src/lib/api/` y acciones de servidor; MUST NOT agregar un BFF de Next.js ni llamar a los
  proveedores desde el
  navegador.

### Non-Functional Requirements

- Las solicitudes a ambos proveedores MUST tener timeout explícito y límite de cantidad de
  sugerencias. Las solicitudes a Nominatim MUST respetar el límite público de una solicitud por
  segundo; las respuestas de búsqueda repetidas MUST servirse desde caché.
- Las coordenadas MUST validarse dentro de los rangos de longitud y latitud antes de enviarse al
  proveedor.
- La interfaz MUST ser usable por teclado, anunciar estados de carga/error y mantener WCAG 2.1 AA.
- La interfaz MUST atribuir los datos de OpenStreetMap con un enlace visible a su aviso de copyright.
- El cálculo MUST ser una consulta sin persistencia ni caché de respuesta de ruta.

## Edge Cases

- Dirección demasiado corta/larga, coordenadas no finitas o fuera de rango: rechazar antes de
  consultar proveedores.
- Nominatim responde sin coincidencias, o OSRM sin ruta, con datos incompletos, con 4xx/5xx o
  tras el timeout: no devolver una distancia parcial o previa.
- El usuario cambia una selección durante una búsqueda o cálculo: descartar la respuesta obsoleta.
- El proveedor puede variar sus resultados y tiempos: la distancia y duración son estimaciones, no
  promesas de recorrido o tiempo real.
- Los servicios ya persistidos no tienen origen ni destino; la migración no debe inventar valores.
- El formulario actual no recalcula automáticamente al cambiar `distancia_ida_km`; la fase
  frontend debe conectar explícitamente ese cambio con el endpoint oficial de cotización.

## Success Criteria

- **SC-001**: Para dos ubicaciones seleccionadas con ruta disponible, el formulario muestra la
  distancia de ida en km y duración recibidas por el backend.
- **SC-002**: El alta guarda las direcciones seleccionadas y la distancia utilizada; servicios
  anteriores siguen consultables sin cambios de datos inventados.
- **SC-003**: Los proveedores públicos se consultan desde el backend, con `User-Agent`
  identificable para Nominatim y sin credenciales en configuración, bundles o requests del
  navegador.
- **SC-004**: Un cambio de ubicación no puede dejar vigente una distancia/cotización de la ruta
  anterior y una ruta aplicada dispara una nueva cotización mediante el endpoint backend existente.

## Next Step

El spec y el plan están aprobados. Revisar la implementación del proxy backend y, tras su aprobación,
continuar con persistencia del recorrido y la integración frontend descrita.
