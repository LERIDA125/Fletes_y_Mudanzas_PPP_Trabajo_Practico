# Implementation Plan: 007 — Listado de Vehículos

**Branch**: `007-frontend-listado-vehiculos` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Status**: Draft — pendiente de aprobación del Tech Lead.

## Summary

La historia agrega una vista de lectura `/vehiculos` y amplía el contrato de lectura para que el
listado entregue datos legibles de sus relaciones. `GET /api/vehiculos` hará un JOIN con
`TipoVehiculo` y un LEFT OUTER JOIN con `Chofer`, devolviendo descripción del tipo, capacidad de
carga y nombre del chofer habitual junto con los campos actuales.

La capacidad de carga se lee del tipo asociado; no se agrega `tara`. El alcance no incluye cambios
de esquema de base de datos, migraciones ni cambios en los payloads u operaciones de alta y
edición. La vista recicla el flujo servidor-primero, los estados, la búsqueda URL/debounce y la
paginación aprobados en 005 y 006.

## Technical Context

| Área | Decisión |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2; capas existentes |
| Frontend | Next.js 16 App Router, React 19, TypeScript estricto, Tailwind v4 |
| Datos iniciales | Server Component que consume `GET /api/vehiculos` mediante `src/lib/api/` |
| Estado de búsqueda/página | URL (`q`, `page`); debounce de 350 ms en el buscador cliente |
| Tipos | Generados desde OpenAPI con el comando existente; no se editan a mano |
| Pruebas | Pytest de integración para el contrato enriquecido; Vitest + Testing Library para la vista |
| Persistencia | Sin cambios; no se crean ni alteran tablas |
| API de escritura | Sin cambios a `POST /api/vehiculos` y `PUT /api/vehiculos/{vehiculo_id}` |
| Responsive / accesibilidad | Mobile-first desde 360 px, WCAG 2.1 AA, foco visible, semántica HTML y reduced motion |

## Constitution Check

| Principio / contrato | Resultado | Acción |
|---|---|---|
| I. Spec Before Code | PASS al aprobarse | No implementar hasta que Tech Lead apruebe este spec y este plan. |
| II. Capas y Puertos | PASS | La consulta JOIN queda en el repositorio; la aplicación conserva la coordinación de lectura y el dominio sigue libre de ORM y datos de presentación. |
| III. Contrato de API | PASS | OpenAPI define la nueva respuesta; el frontend usa el cliente HTTP y tipos generados. No se agrega BFF ni se resuelven relaciones en el navegador. |
| IV. Testing | PASS | Se prueba el contrato enriquecido en integración backend y el comportamiento observable del listado en Vitest. |
| V. Simplicidad y trazabilidad | PASS | Se reutilizan los patrones y utilidades de 005/006; no se agregan dependencias, tablas ni abstracciones sin uso. |
| Frontend: datos/renderizado | PASS | Lectura inicial en Server Component; el componente cliente del buscador solo modifica la URL y no hace fetch. |
| Frontend: sesión/rol | Deficiencia existente | La historia no crea autenticación; la resolución de sesión queda para su historia específica. |
| Frontend: calidad visual | PASS | Se reutiliza el plan de diseño aprobado en 005 y el patrón mobile-first de 006. |

## Cambios previstos

### Backend — enriquecer la lectura sin alterar la persistencia

| Archivo | Cambio previsto |
|---|---|
| `backend/app/api/schemas/vehiculo.py` | Ampliar `VehiculoRead` con `descripcion_tipo_vehiculo`, `capacidad_carga_kg` y `nombre_chofer_habitual`. Los valores legibles serán datos de lectura; chofer nullable. Mantener intactos `VehiculoBase`, `VehiculoCreate` y `VehiculoUpdate`, que contienen los campos de entrada actuales. Documentar tipos, nulabilidad y descripción de campos en OpenAPI. |
| `backend/app/infrastructure/repositories/vehiculo_repo.py` | Enriquecer la consulta paginada usada por `listar`: seleccionar vehículo, descripción y capacidad de `TipoVehiculoORM`, y nombre de `ChoferORM`. Usar `JOIN` interno para el tipo obligatorio y `outerjoin` para el chofer opcional. Mapear a una proyección de lectura sin añadir atributos relacionales a la entidad de dominio ni filtrar por `ChoferORM.activo`. Mantener filtro de vehículo activo, filtro por patente, orden estable y `offset/limit`. |
| `backend/app/application/vehiculos/puertos.py` | Ajustar el contrato de lectura del repositorio para expresar la proyección enriquecida que devuelve el listado, manteniendo SQLAlchemy fuera de Aplicación. La operación `contar` conserva el conteo de vehículos que cumplen `q` y no incorpora los JOIN al conteo. |
| `backend/app/application/vehiculos/gestor_vehiculos.py` | Actualizar los tipos de `listar` para transportar la proyección del repositorio y conservar el total y paginación; no agregar reglas de negocio ni afectar registrar/actualizar/eliminar/obtener. |
| `backend/app/api/vehiculos.py` | Serializar las filas enriquecidas en `GET /api/vehiculos` y mantener `page`, `size`, `total`, filtro y límites actuales. No modificar las operaciones ni los payloads POST/PUT. Los nuevos campos de `VehiculoRead` serán opcionales con valor nulo para las respuestas existentes de POST, PUT y detalle, que no forman parte de esta historia; el endpoint de listado siempre los completa salvo el nombre del chofer, nullable por diseño. |
| `backend/tests/integration/api/test_vehiculos_api.py` | Extender la integración contra PostgreSQL para verificar descripción/capacidad del tipo, nombre del chofer, chofer nulo, preservación de un chofer dado de baja, filtro/paginación y conteo sin duplicados. Comprobar además que las operaciones de escritura mantienen sus payloads actuales. |
| `backend/tests/unit/test_h4_vehiculos.py` o tests específicos del repositorio | Ajustar los fakes/tipos afectados por la firma del puerto y cubrir el mapeo de la proyección si la cobertura del repositorio no queda cubierta por la integración. No alterar reglas unitarias de dominio. |

**Decisión de consulta**:

```text
VehiculoORM
  JOIN TipoVehiculoORM
    ON VehiculoORM.id_tipo_vehiculo = TipoVehiculoORM.id
  LEFT OUTER JOIN ChoferORM
    ON VehiculoORM.id_chofer_habitual = ChoferORM.id
  WHERE VehiculoORM.activo = true
    AND (filtro existente por patente, si q está presente)
  ORDER BY VehiculoORM.id
  OFFSET / LIMIT existentes
```

El JOIN al tipo es seguro con el FK obligatorio vigente. El `outerjoin` preserva vehículos sin
chofer; el registro de chofer se conserva en la baja lógica, por lo que no se agrega filtro de
activo para mostrar el nombre asociado. La consulta de conteo no se multiplica por las relaciones.

No se modifican:

- Modelos ORM ni migraciones Alembic.
- `backend/app/domain/vehiculo.py`.
- `VehiculoCreate` / `VehiculoUpdate`, su validación ni los payloads de alta/edición.
- Comportamiento de detalle, alta, edición o baja.

### Frontend — ruta y componentes de lectura

| Archivo | Cambio previsto |
|---|---|
| `frontend/src/app/(admin)/vehiculos/page.tsx` | Crear la ruta como Server Component siguiendo `app/(admin)/page.tsx` y `app/(admin)/choferes/page.tsx`: leer `searchParams`, llamar al cliente API, manejar `ErrorApi`, Suspense, rango de página, total y resumen de filas. Añadir enlace de navegación a Vehículos en la cabecera del listado. |
| `frontend/src/lib/api/vehiculos.ts` | Crear el servicio de lectura paginada con `q`, `page`, `size` y el tamaño por defecto del endpoint. Usar el cliente `request` compartido. |
| `frontend/src/features/vehiculos/types.ts` | Exportar tipos derivados de OpenAPI; no duplicar modelos manualmente. |
| `frontend/src/features/vehiculos/components/listado-vehiculos.tsx` | Crear tabla semántica con caption accesible y encabezados para patente, tipo/capacidad, chofer habitual y alta; adaptar a fila apilada en móvil siguiendo clientes/choferes. |
| `frontend/src/features/vehiculos/components/fila-vehiculo.tsx` | Presentar patente, descripción, capacidad recibida del backend, nombre del chofer o "Sin chofer habitual" y fecha formateada. No traducir IDs ni calcular capacidad. |
| `frontend/src/features/vehiculos/components/buscador-vehiculos.tsx` | Reutilizar patrón de 006 con debounce de 350 ms, Enter inmediato, limpieza, sincronización con URL e inicio de búsqueda en página 1. Etiqueta y placeholder referidos a patente. |
| `frontend/src/features/vehiculos/components/paginacion.tsx` | Adaptar los enlaces de páginas de 006 y conservar el criterio `q` en cada URL. Ocultar navegación cuando solo hay una página. |
| `frontend/src/features/vehiculos/components/cabecera-listado.tsx` | Encabezado, total y número de páginas con vocabulario "Vehículos". |
| `frontend/src/features/vehiculos/components/estados/cargando.tsx` | Estado de carga anunciado, con filas de reserva que no causen scroll horizontal. |
| `frontend/src/features/vehiculos/components/estados/vacio.tsx` | Diferenciar listado sin vehículos y búsqueda sin coincidencias; permitir limpiar la búsqueda. |
| `frontend/src/features/vehiculos/components/estados/error.tsx` | Traducir clases de error del cliente HTTP y ofrecer reintento mediante `router.refresh()`. |
| `frontend/src/types/openapi.d.ts` | Regenerar como salida del contrato actualizado. Nunca editar manualmente. |
| `frontend/tests/listado-vehiculos.test.tsx` | Probar datos por fila, semántica/estado sin chofer y adaptación de contenido accesible. |
| `frontend/tests/buscador-vehiculos.test.tsx` | Probar debounce, Enter, limpieza, URL y reinicio de página. |
| `frontend/tests/paginacion-vehiculos.test.tsx` | Probar límites, enlaces y conservación de búsqueda. |

Se reutilizan `fechaCorta`, `totalPaginas`, `primeraFilaDeLaPagina`, `ultimaFilaDeLaPagina`,
`ErrorApi`, el cliente HTTP y los tokens existentes. No se introduce una capa de caché cliente ni
un segundo fetch para resolver relaciones.

## Contrato de lectura propuesto

`GET /api/vehiculos` conserva la envoltura paginada y agrega a cada item:

| Campo | Tipo OpenAPI esperado | Origen |
|---|---|---|
| `descripcion_tipo_vehiculo` | `string` | `tipos_vehiculo.descripcion` |
| `capacidad_carga_kg` | `number` | `tipos_vehiculo.capacidad_carga_kg` |
| `nombre_chofer_habitual` | `string \| null` | `choferes.nombre_completo` |

Los campos existentes, incluidos los IDs, permanecen por compatibilidad. Para no cambiar las
respuestas de POST, PUT y detalle en esta historia, los campos añadidos al schema compartido se
declaran opcionales/nullables en esas respuestas; el GET paginado completa descripción y capacidad
para cada resultado. La lista no depende de nombres de campos de otras respuestas.

## Pruebas y verificación

1. Backend unitarios dirigidos para el gestor/puerto afectado.
2. Integración backend contra PostgreSQL para validar el contrato JSON y los JOINs, incluyendo
   chofer nullable e inactivo y exactitud del total.
3. Regenerar tipos con `npm run gen:api` después de modificar el OpenAPI y revisar el diff.
4. Frontend: `npm test` con los tests nuevos y existentes, `npm run lint`,
   `npm run format:check` y `npm run typecheck`.
5. Validación manual a 360 px y escritorio: búsqueda compartible, paginación, vacío, error y filas
   largas.

## Suposiciones y riesgos

- Las claves foráneas y tablas actuales (`vehiculos.id_tipo_vehiculo` obligatorio y
  `vehiculos.id_chofer_habitual` nullable) se mantienen como fuente de relaciones.
- Un chofer dado de baja permanece en la tabla; la lectura por el FK conserva su nombre histórico.
- La ampliación de `VehiculoRead` es aditiva. Los nuevos valores son nulos en operaciones fuera del
  alcance y están completos en el endpoint de listado, salvo el chofer opcional.
- No se filtran tipos inactivos en el JOIN: el tipo asociado se conserva por la relación existente,
  y las reglas de ciclo de vida actuales evitan su baja mientras haya vehículos activos.

## Complexity Tracking

No se solicitan excepciones a la constitución. La proyección relacional es necesaria para separar
datos de presentación de la entidad de dominio; no añade persistencia ni dependencias.

