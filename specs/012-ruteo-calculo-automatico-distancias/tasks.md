# Tasks: Ticket 012 — Ruteo y Cálculo Automático de Distancias

**Feature Branch**: `012-ruteo-calculo-automatico-distancias`

**Spec**: [spec.md](./spec.md)

**Plan**: [plan.md](./plan.md)

**Status**: Backend, frontend, contratos y pruebas implementados. La revisión Alembic está
presente en el worktree, pendiente de revisión y aplicación por el Tech Lead; no se ejecutó Alembic.

## Format: `[ID] [P?] [Story] Description`

- `[P]` = puede ejecutarse en paralelo con otra task del mismo grupo.
- `[US1]` selección de direcciones; `[US2]` cálculo de ruta; `[US3]` alta/persistencia.

## Phase 1: Backend — proxy de direcciones y rutas

- [x] **T001** [P] [US1] Retirar la configuración de `ORS_API_KEY` y declarar `httpx` como
  dependencia de runtime para los proveedores públicos sin credenciales.
- [x] **T002** [US1] Definir schemas estrictos para consulta, coordenadas, sugerencias y ruta;
  validar longitud de consulta y rangos geográficos.
- [x] **T003** [US1] Definir el puerto de Aplicación, sus tipos de resultado y errores seguros de
  disponibilidad/respuesta inválida/ruta no encontrada.
- [x] **T004** [P] [US1, US2] Implementar adaptadores Nominatim/OSRM con endpoints fijos,
  `User-Agent` descriptivo, timeout, límite de sugerencias y validación de respuesta.
- [x] **T005** [US1, US2] Implementar `GestorMapas` y publicar `POST /api/mapas/direcciones` y
  `POST /api/mapas/ruta`, ambos protegidos por rol `admin` e inyectados por dependencias.
- [x] **T006** [US2] Convertir metros a kilómetros usando `Decimal` y `ROUND_HALF_UP` a dos
  decimales; devolver `distancia_ida_km` y `duracion_segundos`.
- [x] **T007** [US1, US2] Traducir errores externos a HTTP seguro sin exponer direcciones,
  respuestas crudas ni credenciales.
- [x] **T008** [US1, US2] Probar autorización, payloads, errores sin credenciales, timeout,
  respuesta sin ruta, coordenadas de sugerencias, redondeo y contrato OpenAPI.
- [x] **T009** [US1, US2] Validar suite unitaria backend, Ruff y formato de los módulos nuevos.

## Phase 2: Backend — persistir las direcciones del servicio

- [x] **T010** [P] [US3] Agregar origen/destino a `Servicio`, schemas, ORM y repositorio; mantener
  nulas las direcciones de registros históricos y exigir ambas en altas nuevas.
- [ ] **T011** [US3] Generar y revisar una migración Alembic aditiva y reversible con el comando
  documentado; su ejecución queda pendiente por solicitud del Tech Lead.
- [x] **T012** [US3] Probar alta, lectura y compatibilidad de servicios históricos sin direcciones.

## Phase 3: Frontend — selección, ruta y cotización vigente

- [x] **T013** [P] [US1] Añadir cliente API y Server Actions para consultar los endpoints de mapas.
- [x] **T014** [US1] Implementar búsqueda accesible enviada explícitamente y selección de
  origen/destino en el formulario; conservar intacta la dirección habitual del cliente nuevo.
- [x] **T015** [US2] Mostrar distancia y duración, actualizar `distancia_ida_km` al completar ruta,
  e invalidar ruta/distancia/cotización al cambiar una selección.
- [x] **T016** [US2] Al aplicar kilómetros, solicitar una nueva cotización mediante
  `POST /api/servicios/cotizar` y presentar el `precio_final` recibido; no calcular precio local.
- [x] **T017** [US2] Probar éxito, errores, reintento, respuestas obsoletas, invalidación de ruta y
  actualización del precio sugerido con Vitest y Testing Library.
- [x] **T018** [US1] Regenerar tipos OpenAPI y actualizar la documentación de configuración y uso
  al completar las fases aprobadas.
- [x] **T019** [US1] Retirar autocomplete al tipear para respetar la política de Nominatim público;
  documentar el límite/caché, atribuir OpenStreetMap y probar el envío explícito.
