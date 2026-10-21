# Implementation Plan: 008 — Backend de Servicios y Cotizaciones

**Branch**: `008-frontend-gestion-servicios` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Status**: Backend implementado; frontend aprobado para demo local sin login.

## Resumen

El backend implementado ofrece cotización, alta con snapshot calculado en servidor y listado.
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
| `backend/app/domain/servicio.py` | Entidad y fábrica `Servicio.crear`; valida invariantes, estado inicial `pendiente`, entradas y snapshot. No importa ORM/Pydantic/FastAPI. |
| `backend/app/domain/errores.py` | Agregar errores tipados para servicio/tipo/cliente/chofer/vehículo inválidos y relación vehículo-tipo inconsistente, heredando clases HTTP ya manejadas. |

### Aplicación

| Archivo | Responsabilidad |
|---|---|
| `backend/app/application/cotizacion/puertos.py` | Protocol para leer configuración de tarifa por tipo activo. |
| `backend/app/application/cotizacion/estrategias/por_hora_y_km.py` | Estrategia pura con fórmula y `Decimal/ROUND_HALF_UP`; sin lecturas ni constantes de tarifas. La franquicia fija de 10 km es la regla aprobada de esta estrategia. |
| `backend/app/application/cotizacion/calculadora.py` | Caso de uso/selector de la estrategia de cotización, dependiente del puerto de tarifas. |
| `backend/app/application/servicios/puertos.py` | Protocols para repositorio de Servicios y consultas de entidades activas requeridas al alta. |
| `backend/app/application/servicios/gestor_servicios.py` | Métodos `cotizar`, `crear` y `listar`; validar referencias/asignación tipo-vehículo, llamar calculadora y persistir por puerto. |

### Infraestructura

| Archivo | Responsabilidad |
|---|---|
| `backend/app/infrastructure/models/servicio.py` | ORM `servicios`, FK a cliente/tipo/chofer/vehículo; campos de viaje, snapshot tarifario, precio, estado y auditoría. |
| `backend/app/infrastructure/models/__init__.py` | Registrar `ServicioORM` para metadata de Alembic y tests. |
| `backend/app/infrastructure/repositories/servicio_repo.py` | Persistir servicios; obtener tarifa activa; validar y consultar relaciones; listar con JOINs paginados, total y orden estable; consultas de historial de clientes/vehículos. |
| `backend/alembic/versions/0004_crear_servicios.py` | Migración aditiva enlazada a `0003`, tabla, FKs, constraints, índices y estado inicial de aplicación. |
| `backend/app/infrastructure/repositories/consulta_stub.py` | No usar el stub de “sin servicios” para consultas que ahora pueden responderse. Eliminarlo solo si queda sin referencias; no conservar resultado ficticio. |

Los importes/tarifas usan `Numeric(12, 2)`. Distancias y horas admiten dos decimales y mínimo no
negativo; `horas_estimadas` debe ser ≥ 1. El modelo mantiene el estado como string restringido a
los estados definidos por la máquina del proyecto; el alta siempre persiste `pendiente`. Si el
modelo actual no dispone de catálogo de estados, no crear un catálogo especulativo para esta
historia: usar campo acotado y constraint para los estados definidos. No se exponen transiciones.

### API y composición

| Archivo | Responsabilidad |
|---|---|
| `backend/app/api/schemas/servicio.py` | Reemplazar schemas preliminares con `CotizacionRequest/Read`, `ServicioCreate`, `ServicioRead`, `ServicioListado`; entrada estricta `extra="forbid"`, campos calculados solo en salida. |
| `backend/app/api/servicios.py` | Router `/api/servicios`: `POST /cotizar`, `POST ""` con 201, `GET ""` paginado. Las dos operaciones de escritura/cotización requieren `admin`; handlers solo validan schema/dependencia y delegan. |
| `backend/app/core/dependencias.py` | Construir repositorio/gestor de servicios y calculadora con repositorio de tarifas; reemplazar adaptadores stub de historial de Cliente y servicios por Vehículo por consultas reales, sin dependencias circulares. |
| `backend/app/main.py` | Registrar router de servicios. Los handlers globales actuales traducen errores de dominio a 404/409/422. |

Contrato GET: requiere rol admin, `page` default 1, `size` default 20, máximo 100; devuelve `items`,
`total`, `page`, `size`; orden ascendente por ID. Proyección con joins a cliente, tipo y LEFT JOINs
a chofer y vehículo. Cotización devuelve tarifas, inputs, distancia derivada, franquicia,
excedente y precio en ARS.
Alta recalcula tarifa/precio dentro del gestor antes de persistir; request prohíbe datos calculados.

### Tests

| Archivo | Cobertura |
|---|---|
| `backend/tests/unit/application/cotizacion/test_calculadora.py` | Fórmula, franquicia cero/positiva, decimales y empates `ROUND_HALF_UP`, validaciones de horas/distancia. |
| `backend/tests/unit/application/servicios/test_gestor_servicios.py` | Tipo/cliente/referencias inválidas, consistencia de vehículo/tipo, estado inicial y snapshots. |
| `backend/tests/unit/infrastructure/test_servicio_repo.py` | Crear, listado estable/paginado, JOINs opcionales, conteo e historial de clientes/vehículos. |
| `backend/tests/integration/api/test_servicios_api.py` | Cotizar y crear como admin, rechazos de rol/validación, resistencia a precio manipulado, respuesta/listado y páginas. |
| Tests existentes de Clientes/Vehículos | Mantener el comportamiento de baja: una vez que hay servicios asociados no se puede dar de baja la entidad. |

`backend/tests/integration/conftest.py` usa `Base.metadata.create_all` y PostgreSQL real; registrar
el modelo nuevo para que la tabla esté disponible en tests. Los tests de API/infraestructura deben
usar la fixture existente de PostgreSQL; unitarios de Aplicación usan fakes y no requieren DB.

## Orden de ejecución

1. Implementar regla/Strategy y tests unitarios puros.
2. Añadir entidad de dominio, ports y gestor con tests unitarios.
3. Crear ORM, migración y repositorio con tests; sustituir únicamente consultas stub relacionadas
   que ahora deban reconocer historial real.
4. Definir schemas y router, cablear dependencias y registrar el router.
5. Ejecutar Ruff, tests unitarios, integración de Servicios y regresión de Clientes/Vehículos.
6. Regenerar el contrato de TypeScript con `npm run gen:api` desde `frontend/`: exporta OpenAPI
   desde FastAPI y actualiza `src/types/openapi.d.ts`. Esto mantiene CI alineado y no implementa
   ni modifica componentes React/Next.js.

## Supuestos de implementación

- El timestamp/auditoría sigue el patrón `TIMESTAMPTZ`, `server_default now()` y `onupdate`.
- El alta acepta fecha programada y hora de inicio opcional según el schema preliminar; si no se
  envían, la API no inventa calendario ni duración de agenda.
- La duración para cotizar es `horas_estimadas`, no se deriva de `hora_inicio`/`hora_fin`.
- Se almacenan snapshots para preservar el precio histórico aunque las tarifas del tipo cambien.
- No se crea una tabla de cotizaciones: crear vuelve a calcular con la tarifa vigente.
- Los estados de esta entrega: servicio nuevo `pendiente`; no hay endpoint para transiciones.

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

## Complejidad / exclusiones

| Elemento | Decisión |
|---|---|
| React Hook Form/Zod/Server Actions | Alcance frontend aprobado; implementación pendiente de resolver autorización. |
| Tabla de cotizaciones | Excluida; cotizar es cálculo no persistido y crear recalcula. |
| Disponibilidad y agenda | Excluidas por falta de regla aprobada; no se agregan validaciones de solapamiento. |
| Pagos, cuenta corriente, rendiciones | Excluidos; no existen operaciones backend listas para integrarse. |
