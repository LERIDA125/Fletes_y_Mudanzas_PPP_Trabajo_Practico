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
- [x] **T005**: Implementar **Agenda mensual interactiva** (`frontend/src/app/(admin)/agenda/page.tsx`) con selector de mes, grilla de 31 días, indicadores de turnos asignados/libres, panel de turnos de hoy y modal de nuevo turno.
- [x] **T006**: Implementar **Cotizador comercial** (`frontend/src/app/(admin)/cotizaciones/page.tsx`) con cálculo en tiempo real por tipo de camión, kilometraje, extras (escaleras, embalaje), desglose y cotizaciones recientes.
- [x] **T007**: Implementar **Rendiciones y arqueo de choferes** (`frontend/src/app/(admin)/rendiciones/page.tsx`) con métricas financieras, tabla de rendición `#REN-024` y modales de detalle de liquidación y nueva rendición.
- [x] **T008**: Integrar tarjetas de disponibilidad y tarifario sugerido en **Choferes** (`frontend/src/app/(admin)/choferes/page.tsx`) preservando la conexión con el backend real y el buscador con debounce.
- [x] **T009**: Integrar tarjetas de estado de flota y kilometraje en **Vehículos** (`frontend/src/app/(admin)/vehiculos/page.tsx`) preservando el listado backend.
- [x] **T010**: Enriquecer **Clientes** (`frontend/src/app/(admin)/clientes/page.tsx`) con badge de clientes activos y tokens visuales.
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
- [x] **T018**: Ejecutar validación completa `npm run verificar` (ESLint 0 errores, Prettier 100%, TypeScript 0 errores, 52 tests de Vitest pasando).
