# Implementation Plan: 012 — Ruteo y Cálculo Automático de Distancias

**Branch**: `012-ruteo-calculo-automatico-distancias` | **Date**: 2026-10-31 |
**Spec**: [spec.md](./spec.md)

**Status**: Fases 1 y 3 implementadas; el contrato y el modelo de persistencia de Fase 2 están
implementados. La revisión Alembic y su aplicación quedan para el Tech Lead.

## Summary

Agregar una integración servidor-servidor con Nominatim y OSRM: el backend proxya la búsqueda de
direcciones y el cálculo de rutas, mientras que el formulario envía búsquedas explícitas y selecciona resultados,
muestra distancia/tiempo y aplica la distancia de ida al campo existente `distancia_ida_km`.
El alta guarda las etiquetas de origen y destino con el servicio. No se agrega código de mapas ni
credenciales al navegador, y el backend sigue siendo la autoridad de la cotización oficial.

## Technical Context

| Área | Decisión |
|---|---|
| Proveedores externos | Nominatim Search API para geocodificación y OSRM Route API con perfil fijo `driving`. |
| Credencial | No se requiere API key; ambos servicios se invocan exclusivamente desde el backend. |
| Contrato propio | `POST /api/mapas/direcciones` para sugerencias y `POST /api/mapas/ruta` para una ruta entre coordenadas elegidas. POST mantiene direcciones fuera de la URL. |
| Geocodificación | Nominatim recibe `q`, `format=jsonv2` y un `User-Agent` descriptivo; consultas explícitas serializadas a un máximo de una por segundo y respuestas repetidas cacheadas. No se usa autocomplete. |
| Ruta | OSRM recibe coordenadas `longitud,latitud;longitud,latitud`; backend traduce metros a `distancia_ida_km` y conserva duración en segundos para la respuesta. |
| Cotización | La distancia de ida llena el campo existente `distancia_ida_km`; la fórmula vigente de cotización no cambia. |
| Persistencia | Agregar `origen_direccion` y `destino_direccion` a servicios como `VARCHAR(500)`. Nullable para historial existente; obligatorios y no vacíos en nuevas altas. Sin coordenadas, geometría ni duración persistida. |
| Frontend | `src/lib/api/` + Server Actions existentes; contrato sin cambios y sin llamadas del navegador a proveedores. |
| Dependencia | El Tech Lead confirmó `CotizacionRequest.distancia_ida_km` y `EstrategiaPorHoraYKm`; al aplicar una ruta, el frontend volverá a solicitar la cotización oficial y presentará `precio_final` del backend. |
| Pruebas | Unitarias de aplicación y adaptador con transporte externo simulado; integración FastAPI; Vitest + Testing Library para formulario y flujo reactivo. |

## Constitution Check

| Principio / contrato | Resultado | Aplicación |
|---|---|---|
| I. Spec Before Code | PENDING | No implementar hasta que Tech Lead apruebe este spec y este plan. |
| II. Capas y Puertos | PASS propuesto | Router valida y delega; caso de uso declara Protocol; el adaptador de proveedores vive en Infraestructura; no se consulta SQL desde API o Aplicación. |
| III. API como contrato | PASS | OpenAPI define endpoints y campos; los tipos frontend se generan. El precio sugerido se obtiene del cotizador FastAPI, sin cálculo local. |
| IV. Testing | PASS propuesto | Cubrir criterios de aceptación con unitarios, integración del contrato y pruebas observables de UI. Simular respuestas y fallos externos. |
| V. Simplicidad y trazabilidad | PASS propuesto | Un proveedor y perfil fijo; sin fallback, mapa visual, caché ni abstracción de múltiples proveedores. |
| Backend: configuración | PASS | Los endpoints y el `User-Agent` del cliente son constantes del adaptador; no se configura ni requiere API key. |
| Frontend: datos y renderizado | PASS | Acceso por cliente API/acciones de servidor; ningún componente consulta Nominatim u OSRM ni mantiene una segunda API. |
| Seguridad y privacidad | PASS propuesto | Autorización admin, endpoints externos fijos, límite/caché/timeout, atribución OSM, sin direcciones en logs y errores sanitizados. |

**Contrato Motor 011 confirmado por Tech Lead**: `CotizacionRequest.distancia_ida_km` recibe la
distancia y `EstrategiaPorHoraYKm` calcula la cotización. El formulario actual no dispara una nueva
cotización por sí solo al cambiar el valor; la fase frontend debe conectar la actualización con
`POST /api/servicios/cotizar` y descartar respuestas obsoletas.

**Migración**: tras iniciar PostgreSQL y el backend, generar la revisión desde `backend/` con
`alembic revision --autogenerate -m "persist service route addresses"` y aplicarla con
`alembic upgrade head`. No se incluyó una revisión generada en esta entrega porque su ejecución
queda a cargo del Tech Lead.

## API propuesta

### Buscar direcciones

`POST /api/mapas/direcciones`

Request: `{ "consulta": "calle, localidad, provincia" }`

Response: `{ "opciones": [{ "etiqueta": "...", "longitud": -58.4, "latitud": -34.6 }] }`

- Admin requerido; `consulta` recortada, longitud acotada y cantidad de resultados limitada.
- El adaptador consulta `GET https://nominatim.openstreetmap.org/search` solo tras una acción
  explícita del usuario, con `q`, `format=jsonv2`, `limit=5`, `accept-language=es` y
  `User-Agent: FletesExpressMVP/1.0`.
- Las solicitudes a Nominatim se serializan y se espacian al menos un segundo; las búsquedas
  repetidas se responden desde una caché acotada en memoria.
- La interfaz presenta etiquetas legibles y obliga a seleccionar una opción; no interpreta
  silenciosamente texto libre como ubicación definitiva.

### Calcular ruta

`POST /api/mapas/ruta`

Request: `{ "origen": { "longitud": -58.4, "latitud": -34.6 }, "destino": { ... } }`

Response: `{ "distancia_ida_km": 12.34, "duracion_segundos": 1234.5 }`

- Admin requerido; validar dos coordenadas dentro de rangos geográficos válidos.
- El adaptador llama al endpoint fijo `GET
  https://router.project-osrm.org/route/v1/driving/{coordenadas}` con coordenadas
  `longitud,latitud;longitud,latitud`.
- Lee `routes[0].distance` y `routes[0].duration`; sin ruta o respuesta malformada
  no se emite resultado parcial.
- Distancia: metros / 1000, representada con `Decimal` y redondeada a 0.01 km mediante
  `ROUND_HALF_UP`. Duración: segundos tal como la entrega OSRM; la UI la formatea.
- El payload no acepta URL, perfil, header, clave ni parámetros arbitrarios del proveedor.

### Errores

| Caso | Respuesta propia |
|---|---|
| Payload vacío, coordenadas inválidas o consulta no válida | 422, mensaje de validación sin detalles del proveedor |
| No hay sugerencias o ruta para las ubicaciones | 422 con mensaje funcional explícito |
| Proveedor temporalmente no disponible / timeout | 503 |
| Error inesperado o respuesta malformada del proveedor | 502 |

El backend agrega errores tipados para los proveedores y los traduce mediante el manejo
centralizado de errores. Ningún mensaje debe incluir headers, request crudo o respuesta interna.

## Cambios previstos por capa

### Configuración e infraestructura

| Archivo | Cambio previsto |
|---|---|
| `backend/app/core/config.py` | No agregar configuración de credenciales para mapas. |
| `backend/app/infrastructure/maps/mapas_client.py` | Implementar clientes HTTP para Nominatim y OSRM con URLs fijas, `User-Agent` descriptivo, intervalo público, timeout, validación de estructura y errores tipados. No registrar direcciones, coordenadas ni cuerpos completos. |
| `backend/pyproject.toml` | Promover `httpx` a dependencia de runtime si se usa el cliente HTTP propuesto; hoy figura solo como dependencia opcional de desarrollo. |
| `backend/.env.example` | No requiere variable de entorno para mapas. |

### Aplicación y API

| Archivo | Cambio previsto |
|---|---|
| `backend/app/application/mapas/puertos.py` | Definir un Protocol para buscar sugerencias y calcular ruta, sin tipos de HTTP ni del proveedor. |
| `backend/app/application/mapas/gestor_mapas.py` | Coordinar búsqueda y cálculo, validar/normalizar entradas de aplicación y convertir errores del proveedor a errores tipados con mensajes seguros. |
| `backend/app/api/schemas/mapa.py` | Definir requests/responses estrictos (`extra="forbid"`), límites de longitud, coordenadas con rangos, opciones y unidades documentadas en OpenAPI. |
| `backend/app/api/mapas.py` | Crear ambos endpoints bajo `/api/mapas`, con `require_rol(ROL_ADMIN)`. Los handlers solo validan el schema y delegan cada operación en un método del gestor. |
| `backend/app/core/dependencias.py` | Proveer adaptador y gestor de mapas desde la configuración existente, permitiendo sustituirlos en pruebas. |
| `backend/app/application/mapas/errores.py` / `backend/app/main.py` | Definir errores tipados de aplicación para configuración/proveedor y traducirlos centralizadamente, preservando los handlers existentes y sin colocar errores de integración en Dominio ni exponer detalles del proveedor. |
| `backend/app/main.py` | Registrar el router de mapas. No cambiar CORS salvo que la revisión detecte un origen frontend faltante. |

### Persistencia del recorrido del servicio

| Archivo | Cambio previsto |
|---|---|
| `backend/app/domain/servicio.py` | Incluir `origen_direccion` y `destino_direccion` en creación/representación del servicio; validar que sean valores no vacíos y acotados, sin importar reglas del proveedor. |
| `backend/app/api/schemas/servicio.py` | Exigir las dos etiquetas en `ServicioCreate` y devolverlas en `ServicioRead`; admitir `null` en lectura para registros históricos. Mantener `extra="forbid"`. |
| `backend/app/infrastructure/models/servicio.py` | Agregar columnas de texto acotadas para ambas direcciones. |
| `backend/alembic/versions/<revision>_direcciones_servicio.py` | Revisión autogenerada después de `0006`; debe agregar columnas nullable para no inventar direcciones históricas e incluir `downgrade()`. |
| `backend/app/infrastructure/repositories/servicio_repo.py` | Mapear las direcciones al persistir y leer el servicio; sin almacenar coordenadas o geometría. |
| Tests backend de servicios | Ajustar altas/fakes/fixtures a los campos requeridos; cubrir servicio histórico con direcciones nulas y alta sin origen/destino. |

### Frontend

| Archivo | Cambio previsto |
|---|---|
| `frontend/src/lib/api/mapas.ts` | Agregar funciones tipadas para búsqueda y ruta usando el cliente autenticado existente; no duplicar URL ni tipos del contrato. |
| `frontend/src/features/servicios/actions.ts` | Exponer acciones de servidor para buscar direcciones y calcular rutas, con errores convertidos al patrón `ResultadoAccion`. |
| `frontend/src/features/servicios/schemas/servicio.ts` | Validar etiquetas de origen/destino requeridas y acotadas; las coordenadas permanecen en el estado tipado de las opciones seleccionadas, no en el payload de alta. |
| `frontend/src/features/servicios/components/formulario-servicio.tsx` | Añadir búsqueda accesible y selección para origen/destino; mostrar estados de búsqueda/cálculo, distancia y tiempo; borrar resultados previos al cambiar selección; actualizar `distancia_ida_km` usando React Hook Form, solicitar una nueva cotización al endpoint existente y presentar su respuesta como precio sugerido. Conservar `direccion_habitual` del alta de cliente nuevo. |
| `frontend/src/features/servicios/types.ts` y `frontend/src/types/openapi.d.ts` | Derivar tipos de OpenAPI y regenerar el archivo generado; no editar tipos generados a mano. |
| Tests Vitest de servicios | Cubrir selección, ruteo exitoso, errores, selección modificada durante una solicitud, invalidación de cotización previa y notificación del contrato del Motor 011. |

## Flujo y consistencia del formulario

1. El administrador escribe una búsqueda y presiona Buscar o Enter; la UI consulta el endpoint
   backend y descarta respuestas obsoletas. No se envían consultas mientras tipea.
2. El administrador selecciona una sugerencia para origen y otra para destino.
3. Con las dos selecciones vigentes, la UI solicita la ruta al backend.
4. Al recibir una respuesta válida, actualiza `distancia_ida_km`, muestra el tiempo estimado e
   invalida cualquier cotización que no coincida con los datos actuales.
5. Si cambia un extremo, se limpian selección, ruta, distancia aplicada y cotización asociada; el
   servicio no se puede guardar hasta calcular la nueva ruta.
6. En el alta se envían las etiquetas seleccionadas y la distancia. El backend guarda las
   direcciones y vuelve a calcular el precio con el contrato de cotización vigente; no confía en un
   `precio_sugerido` del navegador.

La actualización programática debe notificar a React Hook Form y provocar una nueva solicitud de
cotización al backend. Los tests deben confirmar que un resultado anterior no reemplaza el precio
de la ruta vigente y que el valor presentado proviene de `CotizacionRead.precio_final`.

## Migración, pruebas y documentación

- No hay cambios en fórmulas, tarifas o snapshots de precio; la nueva distancia sigue siendo de
  ida y el backend conserva la regla actual de distancia total.
- Migración aditiva y reversible; direcciones históricas quedan `NULL` y altas nuevas requieren
  ambos extremos.
- Pruebas unitarias de Aplicación con un fake del puerto; adaptador probado con transporte HTTP
  simulado (incluyendo User-Agent, límite/caché Nominatim, timeout, no results, no route, 4xx/5xx
  y payload malformado).
- Pruebas de integración API para autorización, validación, shape de respuesta y mapeo de errores,
  con proveedor reemplazado por dependencia de prueba; no llamar a proveedores reales en CI.
- Pruebas del alta aseguran rollback/ausencia de alta parcial si la validación de direcciones falla.
- Vitest + Testing Library prueba el comportamiento observable del formulario y la invalidación
  de respuestas atrasadas; verifica que no se consulta hasta enviar la búsqueda y que se atribuyen
  los datos de OpenStreetMap.
- El límite y la caché son por proceso; despliegues con varios workers o réplicas necesitan un
  limitador y caché compartidos antes de escalar el uso del servidor público.
- Regenerar OpenAPI/types al cambiar los contratos; no se necesita configuración de mapas.

## Complexity Tracking

| Excepción / costo adicional | Justificación |
|---|---|
| Segundo endpoint de mapas para buscar sugerencias | Necesario para que el operador seleccione ubicaciones inequívocas antes de calcular la ruta. |
| Migración de servicios | El origen y destino seleccionados deben sobrevivir al alta; filas históricas permanecen válidas con columnas nullable. |
| Adaptador externo y errores tipados | Aísla Nominatim/OSRM, permite tests deterministas y evita filtrar detalles internos. |

## Next Step

Revisar la revisión Alembic existente
`backend/alembic/versions/418d1b224011_persist_service_route_addresses.py`. Una vez aprobada,
aplicarla desde la raíz del repositorio con `docker compose exec backend alembic upgrade head`.
No se ejecutó Alembic durante esta implementación.

## Referencias técnicas

- [Nominatim Search API](https://nominatim.org/release-docs/latest/api/Search/)
- [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)
- [OSRM HTTP API](https://project-osrm.org/docs/v5.24.0/api/)
