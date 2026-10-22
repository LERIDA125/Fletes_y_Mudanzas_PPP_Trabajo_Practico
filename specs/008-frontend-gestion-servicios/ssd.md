# SSD — System Sequence Diagrams (Diagramas de Secuencia del Sistema)
## Historia H8: Gestión de Servicios, Cotizaciones, Agenda y Rendiciones

**Proyecto**: Fletes y Mudanzas Express (MVP 1)  
**Cátedra**: Trabajo Integrador de Prácticas Pre-Profesionales 1 (2026) — Licenciatura en Sistemas, UNLa  
**Rama**: `008-frontend-gestion-servicios`  
**Fecha de actualización**: Octubre 2026  

---

## 1. Arquitectura y Contexto de Integración

El sistema está estructurado como un **monolito modular en capas** (Backend FastAPI + PostgreSQL) interactuando con un frontend web responsive en **Next.js 16 (App Router)**, **React 19** y **TypeScript**.

```
[ Usuario / Operador ]
         ↕ HTTP (Fetch / RSC / Server Actions)
[ Presentación (Next.js 16) ] ── (Tema: Modo Claro / Oscuro con useSyncExternalStore)
         ↕ REST API (JSON)
[ API FastAPI (app/api/) ]
         ↕ Inyección de dependencias
[ Capa de Aplicación (app/application/) ] ── (Calculadora, Validador, Gestor de Pagos/Rendición)
         ↕ Entidades y reglas invariantes
[ Capa de Dominio (app/domain/) ]
         ↕ Repositorios
[ Infraestructura (app/infrastructure/) ] ── (PostgreSQL / SQLAlchemy)
```

---

## 2. Diagramas de Secuencia del Sistema (SSD)

### SSD-01: Cotización Oficial y Alta de Servicio

Representa el flujo de cálculo no persistido y la creación definitiva del servicio. El frontend nunca calcula las tarifas oficiales de la empresa: envía parámetros y recibe el cálculo exacto del backend antes de permitir el alta.

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Operador / Admin
    participant UI as Frontend Next.js (/servicios)
    participant API as Backend FastAPI (/api/servicios)
    participant App as Capa de Aplicación (Calculadora)
    participant DB as PostgreSQL (Tipos de Vehículo & Servicios)

    Operador->>UI: Ingresa horas, distancia ida, cliente y tipo vehículo
    Operador->>UI: Clic en "Calcular cotización"
    UI->>API: POST /api/servicios/cotizar { tipo_vehiculo_id, horas_estimadas, distancia_ida_km }
    API->>App: cotizar_servicio(params)
    App->>DB: Obtener tipo de vehículo activo (tarifa_hora_base, tarifa_km_excedente)
    DB-->>App: Retorna tarifas vigentes
    Note over App: distancia_total = ida * 2<br/>km_excedente = max(0, distancia_total - 10)<br/>precio = (tarifa_hora * horas) + (tarifa_km * excedente)
    App-->>API: Retorna ResultadoCotizacion (desglose e importe_total)
    API-->>UI: 200 OK { precio_estimado, horas, km_total, km_excedente, desglose }
    UI-->>Operador: Muestra estimación visual y habilita confirmación
    
    Operador->>UI: Clic en "Confirmar y agendar servicio"
    UI->>API: POST /api/servicios { cliente_id, tipo_vehiculo_id, fecha_servicio, ... }
    API->>App: crear_servicio(datos)
    App->>DB: Validar existencia de cliente y tipo activo
    App->>DB: Insertar servicio (estado="pendiente", snapshot de tarifas)
    DB-->>App: Retorna registro persistido con id
    App-->>API: Retorna ServicioResponse
    API-->>UI: 201 Created { id, estado: "pendiente", precio_total, ... }
    UI-->>Operador: Muestra notificación de éxito y actualiza tabla
```

---

### SSD-02: Agenda Operativa y Planificación Mensual

Representa la visualización del calendario mensual interactivo, la consulta de turnos del día y la planificación de nuevos viajes.

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Operador / Logística
    participant Shell as Layout / Header
    participant Agenda as Vista Agenda (/agenda)
    participant State as Estado React (useMemo / useState)

    Operador->>Shell: Clic en "Agenda" en menú lateral
    Shell->>Agenda: Navega a /agenda
    Agenda->>State: Inicializa vista mensual (Septiembre 2026, día seleccionado=23)
    State-->>Agenda: Renderiza grilla de 31 días con indicadores (libres/asignados)
    Agenda-->>Operador: Muestra calendario + panel lateral "Turnos de hoy (8 turnos)"
    
    Operador->>Agenda: Clic en día 24 en el calendario
    Agenda->>State: setSelectedDay(24)
    State-->>Agenda: Actualiza anillo selector y refresca panel lateral
    Agenda-->>Operador: Muestra turnos programados para el 24 de septiembre
    
    Operador->>Agenda: Clic en "Agendar nuevo turno"
    Agenda-->>Operador: Despliega modal interactivo de turno
    Operador->>Agenda: Completa cliente, origen, destino, chofer y vehículo
    Operador->>Agenda: Clic en "Confirmar turno"
    Agenda->>State: Agrega turno a la planificación
    Agenda-->>Operador: Cierra modal y actualiza contador del día
```

---

### SSD-03: Arqueo Financiero y Rendición de Choferes

Representa el proceso de liquidación de viajes, verificación de gastos informados (peajes, combustible) y cierre de saldos.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    participant View as Vista Rendiciones (/rendiciones)
    participant Modal as Modal Detalle / Liquidación
    participant Data as Registros de Liquidación

    Admin->>View: Accede a /rendiciones
    View->>Data: Carga KPIs financieros ($50.000 pendientes, $186.500 aprobados)
    View-->>Admin: Presenta métricas y tabla de rendiciones (#REN-024 a #REN-020)
    
    Admin->>View: Clic en "Ver detalle" de #REN-024 (Carlos Méndez)
    View->>Modal: Abre modal de detalle con tarifa $18.500 y adelanto $12.000
    Modal-->>Admin: Muestra desglose de gastos informados ($2.500) y saldo ($4.000)
    
    Admin->>Modal: Clic en "Aprobar rendición"
    Modal->>Data: Marca rendición como "Aprobada" y actualiza saldo de chofer
    Modal-->>View: Notifica actualización de estado
    View-->>Admin: Cambia badge a verde ("Aprobada") y descuenta de pendientes
```

---

### SSD-04: Conmutación y Persistencia de Modo Oscuro / Modo Claro

Representa el ciclo de vida del tema visual, evitando el parpadeo de contenido desalineado (FOUC) y garantizando la sincronización con React 19 mediante `useSyncExternalStore`.

```mermaid
sequenceDiagram
    autonumber
    actor Usuario as Usuario
    participant Head as Script Inline <head>
    participant Store as useSyncExternalStore (React 19)
    participant DOM as document.documentElement
    participant LocalStorage as Almacenamiento Local (browser)

    Note over Head: Carga inicial de la página (anti-FOUC)
    Head->>LocalStorage: getItem('theme')
    alt theme == 'dark' o (sin preference y matchMedia dark)
        Head->>DOM: classList.add('dark'), setAttribute('data-theme', 'dark')
    else theme == 'light'
        Head->>DOM: classList.remove('dark'), setAttribute('data-theme', 'light')
    end

    Note over Store: Renderizado de la aplicación
    Store->>DOM: Obtiene snapshot de tema inicial ('dark' o 'light')
    Store-->>Usuario: Renderiza UI con colores correspondientes
    
    Usuario->>Store: Clic en botón Sol/Luna en header
    Note over Store: toggleTheme(): next = (current == 'dark' ? 'light' : 'dark')
    Store->>DOM: Modifica clase 'dark' y atributo 'data-theme'
    Store->>LocalStorage: setItem('theme', nextTheme)
    DOM-->>Store: MutationObserver detecta cambio de atributo
    Store-->>Usuario: Actualiza icono del botón y aplica variables CSS sin recarga
```

---

## 3. Matriz de Trazabilidad: Vistas vs. Capacidades

| Vista | Ruta | Componentes Clave | Modo Oscuro | Integración Backend |
|---|---|---|---|---|
| **Dashboard** | `/` | `DashboardPage`, `StatusBadge`, KPIs | Soportado (`dark:bg-[#111c2e]`) | Mockup operativo de alta fidelidad |
| **Agenda** | `/agenda` | `PaginaAgenda`, Calendario 31 días, Turnos de hoy | Soportado | Interactivo local |
| **Cotizaciones** | `/cotizaciones` | `PaginaCotizaciones`, Calculadora, Desglose total | Soportado | Interactivo comercial |
| **Servicios** | `/servicios` | `FormularioServicio`, `ListadoServicios`, `Paginacion` | Soportado | **100% Real FastAPI** (`/api/servicios`) |
| **Choferes** | `/choferes` | `ListadoChoferes`, `BuscadorChoferes`, Disponibilidad | Soportado | **100% Real FastAPI** (`/api/choferes`) |
| **Vehículos** | `/vehiculos` | `ListadoVehiculos`, `BuscadorVehiculos`, Tarjetas Flota | Soportado | **100% Real FastAPI** (`/api/vehiculos`) |
| **Clientes** | `/clientes` | `ListadoClientes`, `BuscadorClientes`, Header badge | Soportado | **100% Real FastAPI** (`/api/clientes`) |
| **Rendiciones** | `/rendiciones` | `PaginaRendiciones`, Modales Arqueo y Liquidación | Soportado | Interactivo financiero |
| **Shell** | Todas | `AdminShell`, Sidebar responsive, Theme Toggle | Soportado | Shell global |
