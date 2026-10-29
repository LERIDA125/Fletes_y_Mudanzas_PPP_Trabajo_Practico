# Tasks: H8 — Frontend de Gestión de Servicios, Cotizaciones, Agenda y Rendiciones

Desglose de tareas según la metodología Spec Kit (Spec-Driven Development).

---

## Fase 1 — Setup y Prerrequisitos de Interfaz

- [x] **T001**: Instalar dependencias de UI requeridas (`lucide-react`) en `frontend/package.json`.
- [x] **T002**: Crear primitivas de UI reutilizables compatibles con shadcn/ui en `frontend/src/components/ui/` (`card.tsx`, `badge.tsx`, `button.tsx`, `table.tsx`, `separator.tsx`, `avatar.tsx`).
- [x] **T003**: Adaptar la shell de administración (`frontend/src/app/(admin)/admin-shell.tsx`) a la identidad Move.ly (`#2165d5`), con sidebar responsive, logo y soporte.

---

## Fase 2 — Implementación y Conexión de Vistas Operativas

- [x] **T004**: Implementar **Dashboard principal** (`frontend/src/app/(admin)/page.tsx`) con KPIs operativos (`Servicios del día`, `Choferes disponibles`, `Dinero por cobrar`, `Pendiente de rendición`) y tabla de próximos servicios.
- [x] **T005**: Implementar **Agenda mensual interactiva** (`frontend/src/app/(admin)/agenda/page.tsx`) con selector de mes, grilla de 31 días, indicadores de turnos asignados/libres, panel de turnos de hoy y acceso a nuevo servicio.
- [x] **T006**: Implementar **Cotizador comercial** (`frontend/src/app/(admin)/cotizaciones/page.tsx`) conectado al backend para cálculo oficial por tipo de vehículo, horas y kilometraje.
- [x] **T007**: Implementar **Rendiciones y arqueo de choferes** (`frontend/src/app/(admin)/rendiciones/page.tsx`) con métricas financieras, tabla de rendición `#REN-024` y modales de detalle de liquidación y nueva rendición.
- [x] **T008**: **Choferes**: quitar las tarjetas ficticias de disponibilidad y el tarifario sugerido; dejar el listado real con buscador y el alta/edición mediante `DialogoChofer`.
- [x] **T009**: **Vehículos**: quitar las tarjetas ficticias de flota; dejar las tarifas reales por tipo (`PanelTarifas`), el listado real y el alta/edición mediante `DialogoVehiculo`.
- [x] **T010**: Enriquecer **Clientes** (`frontend/src/app/(admin)/clientes/page.tsx`) con badge de clientes activos, alta/edición (`DialogoCliente`) y baja lógica.
- [x] **T011**: Conectar y estilizar **Servicios** (`frontend/src/app/(admin)/servicios/page.tsx`) manteniendo la cotización oficial y el alta contra la API FastAPI.

---

## Fase 3 — Modo Oscuro (Dark Mode) y Accesibilidad

- [x] **T012**: Configurar soporte nativo de modo oscuro en `globals.css` mediante `@custom-variant dark` y tokens CSS adaptables para `--papel`, `--tinta`, `--tinta-media` y `--linea`.
- [x] **T013**: Declarar `<meta name="color-scheme" content="light dark" />` y script inline anti-FOUC en `frontend/src/app/layout.tsx` para sincronizar con preferencias de sistema y `localStorage`.
- [x] **T014**: Implementar el componente selector de tema (botón Sol / Luna) en el header de `admin-shell.tsx` utilizando `useSyncExternalStore` para reaccionar a cambios DOM sin cascading renders.
- [x] **T015**: Aplicar variantes `dark:` en todas las páginas, cards, tablas, modales e inputs asegurando ratios de contraste conformes a WCAG 2.1.

---

## Fase 4 — Documentación y Calidad (SSD & Verificación)

- [x] **T016**: Redactar **SSD (System Sequence Diagrams)** en `specs/008-frontend-gestion-servicios/ssd.md` con diagramas de interacción en sintaxis Mermaid.
- [x] **T017**: Crear `feature.json` y `quickstart.md` en `specs/008-frontend-gestion-servicios/`.
- [x] **T018**: Ejecutar validación completa `npm run verificar` (ESLint 0 errores, Prettier 100%, TypeScript 0 errores, tests de Vitest pasando).

---

## Fase 5 — Cambio de requisitos: cancelación de servicios

- [x] **T019**: Actualizar `spec.md` con el modelo de cancelación, el estado `cancelado`, la regla de negocio y los criterios de aceptación.
- [x] **T020**: Actualizar `plan.md` con el impacto por capas, la migración `0005` y la estrategia de tests.
- [x] **T021**: Agregar `hora_fin` y `motivo_cancelacion` al ORM y al schema Pydantic; ampliar el CHECK de estados y agregar el CHECK de cancelación completa en migración `0005`.
- [x] **T022**: Implementar `Servicio.cancelar` en Dominio y `GestorServicios.cancelar` con motivo obligatorio y hora inyectada.
- [x] **T023**: Implementar `PATCH /api/servicios/{id}/cancelar` y las operaciones `obtener_por_id`/`actualizar` del repositorio.
- [x] **T024**: Cubrir el flujo con tests unitarios y de integración (cancelación válida, motivo inválido, servicio inexistente, estado no cancelable).
- [x] **T025**: Ejecutar Ruff y la suite de tests del backend.

---

## Fase 6 — Enmienda de integración frontend (demo)

- [x] **T026**: Actualizar `spec.md` y `plan.md` con disponibilidad informativa, alta con cliente nuevo y el resto del alcance de integración.
- [x] **T027**: Implementar `GET /api/servicios/disponibilidad` en puertos, gestor, repositorios y router; documentar el supuesto temporal de solapamiento.
- [x] **T028**: Permitir `id_cliente` **o** `nuevo_cliente` en `POST /api/servicios`, creando o reutilizando el cliente activo por razón social normalizada.
- [x] **T029**: Resolver la URL de la API por entorno en `frontend/src/lib/api/http.ts` y documentar `API_URL` / `NEXT_PUBLIC_API_URL`.
- [x] **T030**: Agregar alta y edición de choferes y vehículos con diálogos conectados a la API y revalidación.
- [x] **T031**: Exponer la edición de tarifas por tipo de vehículo en `/vehiculos` y revalidar las vistas dependientes.
- [x] **T032**: Conectar `/cotizaciones` al backend y eliminar el cálculo local de importes.
- [x] **T033**: Integrar cliente nuevo y selección de recursos disponibles en el formulario de `/servicios`, incluida la apertura con `?nuevo=1`.
- [x] **T034**: Cubrir backend con tests de cliente nuevo y disponibilidad; actualizar tests RTL del formulario y listado.
- [x] **T035**: Desacoplar el encabezado y los modales de la carga de catálogos, reintentar hosts en servidor y pedir catálogos al abrir cada diálogo.
- [x] **T036**: Ejecutar `npm run verificar` con todas las suites en verde.

---

## Fase 7 — Ciclo de Vida de Servicios y ABM Completo en UI (Integración Final)

- [x] **T037**: Implementar `PATCH /api/servicios/{id}/estado` y `DELETE /api/servicios/{id}` en backend y conectarlos en `FilaServicio` con `DialogoConfirmacion`.
- [x] **T038**: Agregar acciones de edición y baja lógica con confirmación (`DialogoConfirmacion`) en `FilaCliente`, `FilaChofer` y `FilaVehiculo`, mostrando errores de negocio (`409 Conflict`) cuando existen servicios asociados.
- [x] **T039**: Conectar **Agenda** (`/agenda/page.tsx` + `agenda-cliente.tsx`) y **Dashboard** (`/page.tsx`) a los datos reales de `/api/servicios`, `/api/choferes` y `/api/vehiculos`.
- [x] **T040**: Actualizar `backend/scripts/seed.py` con datos realistas de clientes, flota, tarifas y servicios en distintos estados y fechas.
- [x] **T041**: Ampliar cobertura de tests a **44 tests unitarios de backend** (`pytest tests/unit`) y **80 tests de frontend en 12 suites** (`vitest`), y actualizar `AGENTS.md` y `ssd.md`.
