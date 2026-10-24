# Implementation Plan: 008 — Backend de Servicios y Cotizaciones

**Branch**: `008-frontend-gestion-servicios` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Status**: Backend implementado con cancelación y consulta de disponibilidad; frontend integrado
para demo local sin login.

## Resumen

El backend implementado ofrece cotización, alta con snapshot calculado en servidor, listado y
cancelación con motivo y hora de finalización.
Construir `/servicios` y el cotizador de dos pasos en Next.js, sin lógica financiera local. La demo
omite login y asume admin solo con configuración dev local explícita; nunca desplegar ese modo.

## Constitution Check

| Principio | Resultado | Aplicación |
|---|---|---|
| I. Spec Before Code | PASS | El alcance frontend y el modo de demo local fueron aprobados. |
| II. Capas y Puertos | PASS | Router delega al gestor; gestor consume Protocols; dominio Python puro; SQL solo en repositorios. |
| III. API como contrato | PASS | Consumir tipos de OpenAPI; importes se presentan desde API y nunca se recalculan. |
| IV. Testing | PASS | Mantener backend cubierto y añadir RTL para listado, cotización, confirmación y errores. |
| V. Simplicidad | PASS | Reusar composición y tokens existentes; añadir solo catálogo, formulario y acciones necesarios. |
| Seguridad | PASS con alcance local | `DEV_ASSUME_ADMIN` requiere `ENVIRONMENT=dev`; fuera de dev la API responde 401. Compose publica puertos en loopback; la UI no envía `X-Rol`. No desplegar este modo. |
| Confirmación de precio | PASS | Aprobado tratar la cotización como estimación y mostrar como definitivo el importe devuelto por el alta, informando que puede variar. |

## Fórmula aprobada y datos

Entradas:

- `horas_estimadas: Decimal`, mínimo 1.
- `distancia_ida_km: Decimal`, mínimo 0.
- `id_tipo_vehiculo: int`, tipo activo.

Cálculo en `app/application/cotizacion/`:

```text
distancia_total_km = distancia_ida_km * 2
km_franquicia = 10
km_excedente = max(0, distancia_total_km - km_franquicia)
subtotal_horas = tarifa_hora_base * horas_estimadas
subtotal_km = tarifa_km_excedente * km_excedente
precio_final = (subtotal_horas + subtotal_km).quantize(0.01, ROUND_HALF_UP)
```

Las dos tarifas se leen de `tipos_vehiculo` en cada cotización/alta. Las entradas tarifarias del
modelo existente son `Numeric(12, 2)`; los valores calculados se representan como `Decimal`.
`distancia_total_km`, `km_excedente`, horas y precio se guardan con precisión suficiente y
validación de rango en Pydantic/dominio. Nunca aceptar desde request valores derivados ni precios.

El alta vuelve a cotizar con las tarifas vigentes y persiste snapshots de tarifa, franquicia,
distancia total, excedente, horas y precio. Cotizar no crea registro persistente y no se garantiza
vigencia de una cotización entre solicitudes.

## Cambios previstos por capa

### Dominio

| Archivo | Responsabilidad |
|---|---|
| `backend/app/domain/servicio.py` | Entidad, fábrica `Servicio.crear` y método `Servicio.cancelar`; valida invariantes, estado inicial `pendiente`, transición a `cancelado`, motivo obligatorio y `hora_fin`. No importa ORM/Pydantic/FastAPI. |
| `backend/app/domain/errores.py` | Agregar errores tipados para servicio/tipo/cliente/chofer/vehículo inválidos, relación vehículo-tipo inconsistente, servicio inexistente, cancelación no permitida y motivo obligatorio, heredando clases HTTP ya manejadas. |

### Aplicación

| Archivo | Responsabilidad |
|---|---|
| `backend/app/application/cotizacion/puertos.py` | Protocol para leer configuración de tarifa por tipo activo. |
| `backend/app/application/cotizacion/estrategias/por_hora_y_km.py` | Estrategia pura con fórmula y `Decimal/ROUND_HALF_UP`; sin lecturas ni constantes de tarifas. La franquicia fija de 10 km es la regla aprobada de esta estrategia. |
| `backend/app/application/cotizacion/calculadora.py` | Caso de uso/selector de la estrategia de cotización, dependiente del puerto de tarifas. |
| `backend/app/application/servicios/puertos.py` | Protocols para repositorio de Servicios y consultas de entidades activas requeridas al alta. |
| `backend/app/application/servicios/gestor_servicios.py` | Métodos `cotizar`, `crear`, `listar` y `cancelar`; validar referencias/asignación tipo-vehículo, delegar la transición al dominio, inyectar la hora del servidor y persistir por puerto. |

### Infraestructura

| Archivo | Responsabilidad |
|---|---|
| `backend/app/infrastructure/models/servicio.py` | ORM `servicios`, FK a cliente/tipo/chofer/vehículo; campos de viaje, snapshot tarifario, precio, estado, `motivo_cancelacion`, `hora_fin` y auditoría. |
| `backend/app/infrastructure/models/__init__.py` | Registrar `ServicioORM` para metadata de Alembic y tests. |
| `backend/app/infrastructure/repositories/servicio_repo.py` | Persistir servicios; obtener por id; actualizar la cancelación; listar con JOINs paginados, total y orden estable; consultas de historial de clientes/vehículos. |
| `backend/alembic/versions/0004_crear_servicios.py` | Migración aditiva enlazada a `0003`, tabla, FKs, constraints, índices y estado inicial de aplicación. |
| `backend/alembic/versions/0005_cancelacion_servicios.py` | Agrega `hora_fin` y `motivo_cancelacion`; amplía el CHECK de estados con `cancelado` y agrega el CHECK de cancelación completa. |
| `backend/app/infrastructure/repositories/consulta_stub.py` | No usar el stub de “sin servicios” para consultas que ahora pueden responderse. Eliminarlo solo si queda sin referencias; no conservar resultado ficticio. |

Los importes/tarifas usan `Numeric(12, 2)`. Distancias y horas admiten dos decimales y mínimo no
negativo; `horas_estimadas` debe ser ≥ 1. El modelo mantiene el estado como string restringido a
los estados definidos por la máquina del proyecto; el alta siempre persiste `pendiente`. Si el
modelo actual no dispone de catálogo de estados, no crear un catálogo especulativo para esta
historia: usar campo acotado y constraint para los estados definidos. No se exponen transiciones.

### API y composición

| Archivo | Responsabilidad |
|---|---|
| `backend/app/api/schemas/servicio.py` | `CotizacionRequest/Read`, `ServicioCreate`, `ServicioCancelar`, `ServicioRead`, `ServicioListado`; entrada estricta `extra="forbid"`, campos calculados solo en salida y `motivo_cancelacion`/`hora_fin` en la lectura. |
| `backend/app/api/servicios.py` | Router `/api/servicios`: `POST /cotizar`, `POST ""` con 201, `GET ""` paginado y `PATCH /{id}/cancelar`. Todas las operaciones requieren `admin`; handlers solo validan schema/dependencia y delegan. |
| `backend/app/core/dependencias.py` | Construir repositorio/gestor de servicios y calculadora con repositorio de tarifas; reemplazar adaptadores stub de historial de Cliente y servicios por Vehículo por consultas reales, sin dependencias circulares. |
| `backend/app/main.py` | Registrar router de servicios. Los handlers globales actuales traducen errores de dominio a 404/409/422. |

Contrato GET: requiere rol admin, `page` default 1, `size` default 20, máximo 100; devuelve `items`,
`total`, `page`, `size`; orden ascendente por ID. Proyección con joins a cliente, tipo y LEFT JOINs
a chofer y vehículo. Cotización devuelve tarifas, inputs, distancia derivada, franquicia,
excedente y precio en ARS.
Alta recalcula tarifa/precio dentro del gestor antes de persistir; request prohíbe datos calculados.

Contrato PATCH: requiere rol admin; body `{"motivo": "..."}` con 1–255 caracteres recortados. El
router delega en `GestorServicios.cancelar`, que busca el servicio, delega la transición en
`Servicio.cancelar` y le inyecta `hora_fin` con la hora del servidor. Responde 200 con el servicio
actualizado; 404 si no existe, 409 si el estado no admite cancelación y 422 si el motivo es inválido.

### Tests

| Archivo | Cobertura |
|---|---|
| `backend/tests/unit/application/cotizacion/test_calculadora.py` | Fórmula, franquicia cero/positiva, decimales y empates `ROUND_HALF_UP`, validaciones de horas/distancia. |
| `backend/tests/unit/application/servicios/test_gestor_servicios.py` | Tipo/cliente/referencias inválidas, consistencia de vehículo/tipo, estado inicial, snapshots y cancelación con hora inyectada, motivo obligatorio y estados no cancelables. |
| `backend/tests/unit/infrastructure/test_servicio_repo.py` | Crear, listado estable/paginado, JOINs opcionales, conteo e historial de clientes/vehículos. |
| `backend/tests/integration/api/test_servicios_api.py` | Cotizar y crear como admin, rechazos de rol/validación, resistencia a precio manipulado, respuesta/listado, páginas y cancelación (200, 404, 409, 422) contra PostgreSQL. |
| Tests existentes de Clientes/Vehículos | Mantener el comportamiento de baja: una vez que hay servicios asociados no se puede dar de baja la entidad. |

`backend/tests/integration/conftest.py` usa `Base.metadata.create_all` y PostgreSQL real; registrar
el modelo nuevo para que la tabla esté disponible en tests. Los tests de API/infraestructura deben
usar la fixture existente de PostgreSQL; unitarios de Aplicación usan fakes y no requieren DB.

## Orden de ejecución

1. Implementar regla/Strategy y tests unitarios puros.
2. Añadir entidad de dominio, ports y gestor con tests unitarios.
3. Crear ORM, migración y repositorio con tests; sustituir únicamente consultas stub relacionadas
   que ahora deban reconocer historial real.
4. Agregar campos y constraint de cancelación al ORM y la migración `0005`; implementar
   `obtener_por_id` y `actualizar` en el repositorio.
5. Definir schemas y router, cablear dependencias y registrar el endpoint de cancelación.
6. Ejecutar Ruff, tests unitarios, integración de Servicios y regresión de Clientes/Vehículos.
7. Regenerar el contrato de TypeScript con `npm run gen:api` desde `frontend/`: exporta OpenAPI
   desde FastAPI y actualiza `src/types/openapi.d.ts`. Esto mantiene CI alineado y no implementa
   ni modifica componentes React/Next.js.

## Supuestos de implementación

- El timestamp/auditoría sigue el patrón `TIMESTAMPTZ`, `server_default now()` y `onupdate`.
- El alta acepta fecha programada y hora de inicio opcional según el schema preliminar; si no se
  envían, la API no inventa calendario ni duración de agenda.
- La duración para cotizar es `horas_estimadas`, no se deriva de `hora_inicio`/`hora_fin`.
- Se almacenan snapshots para preservar el precio histórico aunque las tarifas del tipo cambien.
- No se crea una tabla de cotizaciones: crear vuelve a calcular con la tarifa vigente.
- Estados válidos: `pendiente`, `confirmado`, `en curso`, `finalizado`, `cobrado`, `cancelado`.
  El alta inicia en `pendiente`; la única transición expuesta es la cancelación.
- Cancelación: se permite desde `pendiente`, `confirmado` o `en curso`; desde `finalizado`,
  `cobrado` o `cancelado` responde 409. El motivo es obligatorio (1–255, recortado) y `hora_fin` se
  inyecta con la hora local del servidor; el request no puede enviar hora ni estado.
- `hora_fin` es `TIME` para alinearse con el ERD y con `hora_inicio`; la fecha del servicio sigue en
  `fecha`. No se agrega una columna de timestamp de cancelación en esta fase.
- La base refuerza la consistencia con un CHECK: `cancelado` implica motivo no vacío y `hora_fin`.

## Enmienda Frontend — propuesta

### Ruta y composición

Crear `frontend/src/app/(admin)/servicios/page.tsx` como Server Component siguiendo la
composición de `/choferes` y `/vehiculos`: leer `searchParams`, renderizar navegación/cabecera,
Suspense, estados, tabla y paginación. Criterios `page` y `size` viven en URL; `q` se omite hasta
que el backend ofrezca filtro de servicios.

### Archivos de frontend propuestos

| Archivo | Responsabilidad |
|---|---|
| `frontend/src/app/(admin)/servicios/page.tsx` | Listado server-rendered paginado y estados, acorde a patrón de rutas admin existente. |
| `frontend/src/lib/api/servicios.ts` | Cliente tipado para listar, cotizar y catálogos auxiliares, desde OpenAPI. Las solicitudes deberán usar la identidad autorizada acordada, no inventar headers privilegiados. |
| `frontend/src/features/servicios/types.ts` | Reexportar `ServicioRead`, `ServicioListado`, `CotizacionRequest`, `CotizacionRead` y entidades relacionadas generadas. |
| `frontend/src/features/servicios/schemas/servicio.ts` | Zod para forma, campos requeridos, horas ≥ 1 y distancia ≥ 0; no calcular el precio ni simular disponibilidad. |
| `frontend/src/features/servicios/actions.ts` | Server Actions para cotizar/crear, propagar sesión y traducir errores; revalidar `/servicios` tras creación exitosa. |
| `frontend/src/features/servicios/components/listado-servicios.tsx` | Tabla semántica adaptable, precio, fecha/estado y datos legibles del contrato. |
| `frontend/src/features/servicios/components/fila-servicio.tsx` | Presentación de cliente, tipo, fecha, asignaciones, estado e importe emitidos por API. |
| `frontend/src/features/servicios/components/paginacion.tsx` | Paginación enlazada a URL según patrón 005/006. |
| `frontend/src/features/servicios/components/estados/{cargando,vacio,error}.tsx` | Estados consistentes con sistema existente. |
| `frontend/src/features/servicios/components/formulario-servicio.tsx` | Client Component con React Hook Form + Zod; flujo de cotización y confirmación; invalida cotización al cambiar campos relevantes. |
| `frontend/src/features/servicios/components/resumen-cotizacion.tsx` | Mostrar desglose y precio del backend con `Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" })`. |
| `frontend/tests/servicios*.test.tsx` | RTL de importe, cotización obsoleta, errores, doble paso y refresco de listado. |
| `frontend/src/types/openapi.d.ts` | Actualizar solo con `npm run gen:api`; no editar manualmente. |
| `frontend/package.json` / `package-lock.json` | Agregar React Hook Form y Zod tras aprobar plan, solo si se confirma que no están disponibles ya. |

### Flujo propuesto

1. RHF recoge cliente, tipo, fecha/hora, horas, distancia de ida y asignaciones opcionales.
2. Zod valida campos/formatos y límites, sin reproducir reglas de tarifa.
3. La acción de cotizar envía `id_tipo_vehiculo`, `horas_estimadas` y `distancia_ida_km`; la UI
   presenta exactamente desglose y `precio_final` recibidos de API.
4. Toda edición de tipo, horas o distancia invalida el resultado y bloquea el alta hasta recalcular.
5. Tras confirmación visible, la acción de alta envía datos operativos (no precio, km total,
   franquicia ni excedente); después de éxito se muestra el `precio_total` definitivo devuelto y
   se revalida la ruta.
6. Si las tarifas cambiaron entre cotizar y crear, el backend puede persistir un precio distinto
   al mostrado antes de enviar. La UI identifica la cotización como estimación e informa el importe
   definitivo recibido tras crear; nunca afirma que el importe anterior quedó reservado.

La API requiere admin en las rutas de Servicios. Para esta demo local, el backend asume admin solo
con `ENVIRONMENT=dev` y `DEV_ASSUME_ADMIN=true`; en cualquier otro entorno rechaza con 401. La
interfaz no envía `X-Rol`. Docker Compose publica los puertos 3000/8000 en `127.0.0.1`; no usar
esta configuración en una red compartida o despliegue.

### Brief visual propuesto

- **Trabajo**: coordinador identifica rápidamente fecha, cliente, recursos y precio final.
- **Paleta**: conservar los tokens existentes `--tinta`, `--papel`, `--linea`, `--senal`,
  `--alerta`; no introducir colores hexadecimales nuevos.
- **Tipografía**: Archivo existente; números tabulares para horas/importes, sin introducir otra
  familia tipográfica.
- **Layout**: título alineado a la izquierda; crear servicio en panel desplegable “Nuevo servicio”
  antes de tabla, para que el listado siga siendo la superficie principal. La cotización se
  presenta en el mismo flujo del formulario con desglose visible y acción explícita de confirmar.
- **Composición**: tabla densa en escritorio con filas apiladas en móvil, misma escala de espacio
  y foco visible del admin actual; ninguna tarjeta repetida como adorno.
- **Accesibilidad**: WCAG 2.1 AA, teclado, mensajes asociados a inputs, foco al resultado/error y
  `prefers-reduced-motion`.

La dirección conserva las decisiones visuales de 005/006 en vez de introducir otra paleta o
tipografía para una pantalla perteneciente a la misma aplicación.

## Enmienda de alcance aprobada — integración de la demo

Esta sección reemplaza el alcance “solo listado + cotizador” de la propuesta anterior. Fue
aprobada para cerrar la integración punta a punta de la demo y queda registrada en
`spec.md` (*Enmienda de alcance*, FR-026 a FR-033).

### Resolución de la API en el frontend

- `frontend/src/lib/api/http.ts` resuelve la base en servidor con `API_URL` y en navegador con
  `NEXT_PUBLIC_API_URL`. Si `API_URL` falta o no responde, el servidor reintenta contra
  `http://backend:8000` (nombre del servicio en Docker Compose) y luego
  `http://localhost:8000`; el navegador solo usa la URL pública y cae a localhost. Los
  reintentos son solo ante fallos de red: nunca ante una respuesta HTTP de error ni ante un
  timeout de un `POST` (para no duplicar altas). Normaliza barras finales, aplica timeout de
  10 s por intento y usa `cache: "no-store"` en toda lectura de datos.
- `frontend/.env.example` documenta ambas variables. Docker Compose ya publica
  `API_URL=http://backend:8000` y `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- El encabezado de `/choferes`, `/vehiculos` y `/servicios` no espera a la API: el botón de
  alta y su diálogo se renderizan siempre. `/vehiculos` y el formulario de servicio piden sus
  catálogos recién al abrir el modal y muestran el error dentro del diálogo si la API falla;
  el listado y las tarifas conservan su propio estado de error sin ocultar la acción.
- Los errores de FastAPI se traducen a `ErrorApi` con clase (`sin-respuesta`,
  `sesion-expirada`, `sin-permisos`, `error-de-servicio`) y se extrae `detail`, incluida la
  lista de errores de validación. Las acciones de servidor devuelven mensajes explícitos.
- El frontend sigue sin enviar `X-Rol`; la demo local depende de `ENVIRONMENT=dev` y
  `DEV_ASSUME_ADMIN=true` en el backend.

### Disponibilidad informativa

- Nuevo endpoint `GET /api/servicios/disponibilidad` con `fecha`, `id_tipo_vehiculo`,
  `horas_estimadas` y `hora_inicio` opcional. Devuelve `id_tipo_vehiculo`, `fecha`,
  `hora_inicio`, `hora_fin`, `choferes` y `vehiculos` activos y libres.
- El cálculo vive en `GestorServicios` y se apoya en puertos de repositorio; el router solo
  valida y delega. Los recursos se filtran por solapamiento con servicios no cancelados del
  día.
- **Supuesto temporal** (pendiente de confirmación del cliente, AGENTS.md §6): se comparan
  ventanas `[hora_inicio, hora_inicio + horas_estimadas)`; si el servicio pedido o uno
  existente del día no informa `hora_inicio`, el recurso se considera ocupado todo el día. No
  se aplica margen entre servicios.
- El alta **no** bloquea solapamientos: la consulta es informativa y el backend sigue
  aceptando cualquier combinación válida. La UI limpia una asignación que deja de estar
  disponible cuando cambian fecha, hora, tipo u horas.

### Alta con cliente nuevo

- `POST /api/servicios` acepta exactamente uno de `id_cliente` o `nuevo_cliente`; ambos o
  ninguno responden 422. `nuevo_cliente` usa el schema `ClienteCreate`.
- Si se envía `nuevo_cliente`, el backend normaliza la razón social con la misma regla de
  H1 (`razon_social_key`), reutiliza un cliente activo equivalente o crea uno nuevo y lo
  vincula al servicio antes de persistirlo. Un registro inactivo con la misma razón social
  responde 409.
- La UI ofrece un selector “Cliente existente / Cliente nuevo”. En modo nuevo valida razón
  social, teléfono (7–20 dígitos) y dirección; el payload envía `nuevo_cliente` y nunca
  `id_cliente`. Tras crear se revalidan `/servicios`, `/clientes`, `/agenda` y `/`.

### Gestión de choferes y vehículos

- `/choferes` incorpora `+ Nuevo chofer` y edición por fila mediante `DialogoChofer`
  (`POST /api/choferes` y `PUT /api/choferes/{id}`).
- `/vehiculos` incorpora `+ Nuevo vehículo` y edición por fila mediante `DialogoVehiculo`
  (`POST /api/vehiculos` y `PUT /api/vehiculos/{id}`), con catálogos de tipos y choferes
  habituales.
- Ambos diálogos usan React Hook Form + Zod, muestran errores de servidor sin cerrar el
  formulario, cierran solo tras éxito y llaman `router.refresh()`; las acciones revalidan las
  rutas afectadas.
- Se eliminaron tarjetas y tarifarios ficticios de ambas pantallas.

### Tarifas por tipo de vehículo

- `PanelTarifas` en `/vehiculos` edita `descripcion`, `capacidad_carga_kg`,
  `tarifa_hora_base` y `tarifa_km_excedente` del `TipoVehiculo` activo mediante
  `PUT /api/tipos-vehiculo/{id}`. Es la única fuente de tarifas del cotizador.
- Tras guardar se revalidan `/vehiculos`, `/servicios`, `/cotizaciones` y `/`.

### Cotizador real

- `/cotizaciones` deja de calcular localmente. La página carga los tipos activos en servidor y
  `Cotizador` llama a `POST /api/servicios/cotizar` a través de una Server Action.
- Solo se muestran los valores devueltos (`descripcion_tipo_vehiculo`, horas, distancia total,
  km excedente, tarifas y `precio_final`). No se multiplican ni suman importes en el
  navegador. Cambiar cualquier entrada borra el resultado anterior.

### Archivos de la enmienda

| Archivo | Responsabilidad |
|---|---|
| `frontend/src/lib/api/http.ts` | Base URL por entorno, timeout, `no-store` y traducción de errores. |
| `frontend/src/lib/api/servicios.ts` | Listar, cotizar, crear, catálogos y `consultarDisponibilidad`. |
| `frontend/src/lib/api/choferes.ts` / `vehiculos.ts` | Altas, ediciones y actualización de tarifas. |
| `frontend/src/features/servicios/schemas/servicio.ts` | Zod del formulario, incluido el modo cliente nuevo. |
| `frontend/src/features/servicios/actions.ts` | Cotizar, disponibilidad y alta con revalidación. |
| `frontend/src/features/servicios/components/formulario-servicio.tsx` | Alta, cliente nuevo, disponibilidad y apertura por `?nuevo=1`. |
| `frontend/src/features/choferes/components/dialogo-chofer.tsx` | Alta/edición de chofer. |
| `frontend/src/features/vehiculos/components/dialogo-vehiculo.tsx` | Alta/edición de vehículo. |
| `frontend/src/features/vehiculos/components/panel-tarifas.tsx` | Edición de tarifas por tipo. |
| `frontend/src/features/cotizaciones/components/cotizador.tsx` | Cotizador conectado al backend. |
| `frontend/src/app/(admin)/{choferes,vehiculos,servicios,cotizaciones}/page.tsx` | Cableado server-rendered y acceso directo desde Dashboard. |
| `frontend/src/types/openapi.d.ts` | `ServicioCreate` con `nuevo_cliente`, `DisponibilidadRead` y el path de disponibilidad. |

### Tests de la enmienda

- `backend/tests/unit/application/servicios`: creación/reutilización de cliente, rechazo de
  duplicado inactivo y filtrado por solapamiento.
- `backend/tests/unit/test_h8_servicios_api.py`: alta con `nuevo_cliente`, exclusión mutua y
  endpoint de disponibilidad.
- `frontend/tests/servicios.test.tsx`: cotización, confirmación, alta con cliente existente y
  nuevo, invalidación y errores.
- `frontend/tests/listado-vehiculos.test.tsx`: listado con catálogos y acciones mockeadas.
- Pendiente recomendado: RTL de `DialogoChofer`, `DialogoVehiculo`, `PanelTarifas` y del
  filtrado de disponibilidad con recursos excluidos.

## Complejidad / exclusiones

| Elemento | Decisión |
|---|---|
| React Hook Form/Zod/Server Actions | Implementados; la autorización de la demo se resuelve con `ENVIRONMENT=dev` + `DEV_ASSUME_ADMIN=true`, sin JWT. |
| Tabla de cotizaciones | Excluida; cotizar es cálculo no persistido y crear recalcula. |
| Disponibilidad y agenda | Consulta informativa implementada (FR-026, FR-029). El alta no bloquea solapamientos ni se define margen entre servicios: regla pendiente del cliente. |
| Pagos, cuenta corriente, rendiciones | Excluidos; no existen operaciones backend listas para integrarse. |
