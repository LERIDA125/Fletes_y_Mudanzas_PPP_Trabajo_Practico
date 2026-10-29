# Documentación de Ingeniería — Fletes y Mudanzas Express (MVP 1)

**Cátedra**: Trabajo Integrador de Prácticas Pre-Profesionales 1 (2026) — Licenciatura en Sistemas, UNLa  
**Metodología**: Spec-Driven Development (Spec Kit) + Arquitectura en Capas (Monolito Modular)  

Esta carpeta centraliza todas las **Historias de Usuario**, los **Diagramas de Secuencia del Sistema (SSD)** y los **Diagramas de Arquitectura, Dominio, Base de Datos y Estados** generados a partir de las especificaciones (`/specs/001` a `/specs/009`) y de la implementación consolidada en `main`.

---

## Índice de Documentos

1. **[`historias-de-usuario.md`](./historias-de-usuario.md)**  
   Recopilación completa de las **31 Historias de Usuario** del proyecto organizadas por módulo (`001` a `009`), con sus criterios de aceptación en formato *Dado / Cuando / Entonces*, reglas de negocio, casos límite y estado de implementación.

2. **[`diagramas-ssd.md`](./diagramas-ssd.md)**  
   Catálogo de **10 Diagramas de Secuencia del Sistema (SSD)** en formato Mermaid que modelan las interacciones de punta a punta entre el actor, el frontend Next.js 16 (Server Components + Server Actions), la API FastAPI, la Capa de Aplicación, el Dominio y PostgreSQL.

3. **[`diagramas-arquitectura-y-dominio.md`](./diagramas-arquitectura-y-dominio.md)**  
   Diagramas estructurales y de comportamiento del sistema:
   - Arquitectura en 4 capas (Presentación, Aplicación, Dominio, Infraestructura).
   - Diagrama Entidad-Relación (ERD) de PostgreSQL (migraciones `0001` a `0005`).
   - Diagrama de Clases del Dominio y Patrón *Strategy* de Cotización (`PorHoraYKm`).
   - Máquina de Estados explícita de `Servicio` (`pendiente → confirmado → en curso → finalizado → cobrado` y `cancelado`).
   - Flujo de Integración Continua (GitHub Actions CI) y Orquestación Docker Compose.

---

## Resumen General de Módulos y Especificaciones

| Spec ID | Historia / Módulo | Rama Original | Estado en `main` | Tests Asociados |
|---|---|---|---|---|
| **001 (H1)** | Gestión de Clientes (Backend CRUD + Normalización) | `feature/H1-gestion-clientes` | Implementado | Unit + Integración API |
| **002 (H13)** | Migración Idempotente de Datos Históricos (ETL Excel) | `feature/H13-migracion-datos-historicos` | Implementado | Unit ETL + Reporte MD |
| **003 (H4)** | Gestión de Vehículos y Tipos de Vehículo con Tarifas | `feature/H4-gestion-vehiculos` | Implementado | Unit + Integración API |
| **004 (H3)** | Gestión de Choferes y Saldo a Favor | `feature/CRUD_choferes` | Implementado | Unit + Integración API |
| **005** | Frontend Scaffolding (Next.js 16) y Listado de Clientes | `005-frontend-scaffolding-clientes` | Implementado | Vitest + RTL |
| **006** | Frontend Listado y Búsqueda de Choferes | `006-frontend-listado-choferes` | Implementado | Vitest + RTL |
| **007** | Frontend Listado de Vehículos y Enriquecimiento JOIN | `007-frontend-listado-vehiculos` | Implementado | Unit Repo + Vitest |
| **008 (H8)** | Servicios, Cotizador Oficial, Disponibilidad, Cancelación, ABM UI, Agenda, Dashboard y Modo Oscuro | `008-frontend-gestion-servicios` / `feature/frontend-integracion-ui` | Implementado | 44 Unit Backend + 80 Vitest Frontend |
| **009** | Autenticación Admin (Argon2 + JWT `httpOnly`) y Roles | `009-autenticacion-roles` | Especificado (Pausado para MVP demo) | Contrato diseñado |
