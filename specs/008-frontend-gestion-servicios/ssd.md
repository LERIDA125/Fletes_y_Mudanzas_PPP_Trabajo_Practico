# SSD — System Sequence Diagrams (Diagramas de Secuencia del Sistema)
## Historia H8 e Integración General: Servicios, Cotizaciones, Catálogos, Agenda y Operaciones

**Proyecto**: Fletes y Mudanzas Express (MVP 1)  
**Cátedra**: Trabajo Integrador de Prácticas Pre-Profesionales 1 (2026) — Licenciatura en Sistemas, UNLa  
**Rama consolidada**: `main` (integración completa de `008-frontend-gestion-servicios` y `feature/frontend-integracion-ui`)  
**Fecha de actualización**: Octubre 2026  

---

## 1. Arquitectura y Contexto de Integración

El sistema está estructurado como un **monolito modular en capas** (Backend FastAPI + PostgreSQL 16) interactuando con un frontend web responsive en **Next.js 16 (App Router, Turbopack)**, **React 19** y **TypeScript**, comunicados mediante Server Components, Server Actions y validación de esquemas con **React Hook Form + Zod**.

```
[ Usuario / Operador Administrativo ]
         ↕ Interacción UI (RSC + Server Actions + RHF/Zod)
[ Presentación Frontend (Next.js 16) ] ── (Tema Claro/Oscuro anti-FOUC con useSyncExternalStore)
         ↕ REST API JSON (http.ts con fallback backend:8000 / localhost:8000, cache: "no-store")
[ Capa de Presentación Backend (app/api/) ] ── (Validación Pydantic extra="forbid" + require_rol)
         ↕ Inyección de dependencias (Protocols)
[ Capa de Aplicación (app/application/) ] ── (Gestores de Servicios, Clientes, Choferes, Vehículos y Calculadora Strategy)
         ↕ Entidades e invariantes puras
[ Capa de Dominio (app/domain/) ] ── (Máquina de estados de Servicio, reglas de baja y normalización)
         ↕ Repositorios SQLAlchemy
[ Capa de Infraestructura (app/infrastructure/) ] ── (PostgreSQL 16 + Migraciones Alembic 0001..0005)
```

---

## 2. Diagramas de Secuencia del Sistema (SSD)

### SSD-01: Cotización Oficial, Disponibilidad Informativa y Alta de Servicio (Cliente Existente o Nuevo)

Representa el flujo completo de extremo a extremo para cotizar un viaje sin persistencia, consultar choferes y vehículos disponibles en la franja horaria elegida y registrar el servicio con snapshot tarifario inmutable (reutilizando o creando un cliente nuevo en la misma transacción).

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Operador / Admin
    participant UI as Frontend (/servicios · FormularioServicio)
    participant SA as Server Actions (servicios/actions.ts)
    participant API as FastAPI (/api/servicios)
    participant Gestor as Aplicación (GestorServicios + Calculadora)
    participant DB as PostgreSQL

    Admin->>UI: Selecciona fecha, hora_inicio, tipo de vehículo, horas y km de ida
    UI->>SA: consultarDisponibilidadAction(fecha, id_tipo_vehiculo, horas_estimadas, hora_inicio)
    SA->>API: GET /api/servicios/disponibilidad?...
    API->>Gestor: consultar_disponibilidad(...)
    Gestor->>DB: Consultar choferes/vehículos activos y servicios no cancelados del día
    DB-->>Gestor: Recursos activos + compromisos del día
    Note over Gestor: Filtra recursos sin solapamiento en [hora_inicio, hora_fin)<br/>y vehículos que coinciden con id_tipo_vehiculo
    Gestor-->>API: DisponibilidadRead { choferes, vehiculos }
    API-->>SA: 200 OK
    SA-->>UI: Actualiza selectores con choferes y vehículos libres

    Admin->>UI: Clic en "Calcular cotización"
    UI->>SA: cotizarServicioAction({ id_tipo_vehiculo, horas_estimadas, distancia_ida_km })
    SA->>API: POST /api/servicios/cotizar
    API->>Gestor: cotizar(params)
    Gestor->>DB: Obtener TipoVehiculo activo (tarifa_hora_base, tarifa_km_excedente)
    DB-->>Gestor: Tarifas vigentes
    Note over Gestor: Estrategia PorHoraYKm:<br/>distancia_total = ida * 2 | franquicia = 10 km<br/>km_excedente = max(0, total - 10)<br/>precio_final = ROUND_HALF_UP(tarifa_hora*horas + tarifa_km*excedente)
    Gestor-->>API: CotizacionRead (desglose + precio_final ARS)
    API-->>SA: 200 OK
    SA-->>UI: Muestra ResumenCotizacion y habilita casilla de confirmación

    Admin->>UI: Elige "Cliente existente" (id_cliente) o "Cliente nuevo" (nuevo_cliente)
    Admin->>UI: Confirma la estimación y envía "Registrar servicio"
    UI->>SA: crearServicioAction(payload sin importes ni campos derivados)
    SA->>API: POST /api/servicios
    API->>Gestor: crear(datos)
    alt Modo nuevo_cliente
        Gestor->>DB: Buscar por razon_social_key
        alt No existe
            Gestor->>DB: Crear Cliente activo
        else Existe activo
            Note over Gestor: Reutiliza id_cliente activo existente
        else Existe inactivo
            Gestor-->>API: Error 409 RazonSocialDuplicada
        end
    end
    Gestor->>DB: Recalcular tarifa vigente y persistir Servicio (estado="pendiente", snapshot tarifario)
    DB-->>Gestor: Servicio persistido con ID
    Gestor-->>API: ServicioRead
    API-->>SA: 201 Created
    SA->>SA: revalidatePath("/servicios", "/clientes", "/agenda", "/")
    SA-->>UI: Muestra precio_total definitivo persistido y refresca tabla
```

---

### SSD-02: Ciclo de Vida del Servicio (Transición de Estado, Cancelación y Eliminación)

Representa las tres operaciones de gestión sobre un servicio ya registrado desde el menú de acciones de cada fila (`FilaServicio`) con sus respectivos diálogos de confirmación (`DialogoConfirmacion`).

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Operador / Admin
    participant Fila as Frontend (FilaServicio + DialogoConfirmacion)
    participant SA as Server Actions (servicios/actions.ts)
    participant API as FastAPI (/api/servicios/{id})
    participant Gestor as Aplicación (GestorServicios)
    participant Dom as Dominio (Servicio)
    participant DB as PostgreSQL

    alt 1. Avance en la Máquina de Estados Ordinaria
        Admin->>Fila: Selecciona siguiente estado (pendiente → confirmado → en curso → finalizado → cobrado)
        Fila->>SA: cambiarEstadoServicioAction(id, nuevoEstado)
        SA->>API: PATCH /api/servicios/{id}/estado { estado }
        API->>Gestor: cambiar_estado(id, estado)
        Gestor->>DB: obtener_por_id(id)
        Gestor->>Dom: servicio.transicionar_a(estado)
        Note over Dom: Valida que sea estrictamente el estado inmediato siguiente
        Gestor->>DB: actualizar(servicio)
        DB-->>API: 200 OK (ServicioRead actualizado)
        API-->>SA: 200 OK
        SA->>SA: revalidatePath("/servicios", "/agenda", "/")
        SA-->>Fila: Actualiza badge de estado en la tabla
    else 2. Cancelación con Motivo y Hora del Servidor
        Admin->>Fila: Clic en "Cancelar servicio" e ingresa motivo (1..255 caracteres)
        Fila->>SA: cancelarServicioAction(id, { motivo })
        SA->>API: PATCH /api/servicios/{id}/cancelar { motivo }
        API->>Gestor: cancelar(id, motivo)
        Gestor->>DB: obtener_por_id(id)
        Gestor->>Dom: servicio.cancelar(motivo, hora_fin=servidor.now().time())
        Note over Dom: Permitido solo desde pendiente, confirmado o en curso.<br/>Desde finalizado/cobrado/cancelado lanza 409 Conflict
        Gestor->>DB: actualizar(estado="cancelado", motivo_cancelacion, hora_fin)
        DB-->>API: 200 OK (ServicioRead con motivo y hora_fin)
        API-->>SA: 200 OK
        SA->>SA: revalidatePath("/servicios", "/agenda", "/")
        SA-->>Fila: Muestra estado "Cancelado" con detalle del motivo y hora
    else 3. Eliminación de Servicio
        Admin->>Fila: Clic en "Eliminar" y confirma en DialogoConfirmacion
        Fila->>SA: eliminarServicioAction(id)
        SA->>API: DELETE /api/servicios/{id}
        API->>Gestor: eliminar(id)
        Gestor->>DB: eliminar(id) (verifica FK dependientes)
        DB-->>API: 204 No Content (o 409 si posee referencias)
        API-->>SA: 204 No Content
        SA->>SA: revalidatePath("/servicios", "/agenda", "/")
        SA-->>Fila: Remueve fila del listado
    end
```

---

### SSD-03: Gestión Integral de Catálogos (Clientes, Choferes, Vehículos) y Tarifas por Tipo

Representa el alta, edición completa (`PUT`), baja lógica protegida (`DELETE` con bloqueo `409` ante servicios históricos) y la actualización de tarifas en `/vehiculos` que alimenta al cotizador.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    participant UI as Frontend (/clientes, /choferes, /vehiculos)
    participant Modal as Dialogo (Cliente / Chofer / Vehiculo / PanelTarifas)
    participant SA as Server Actions (actions.ts)
    participant API as FastAPI (/api/...)
    participant Gestor as Aplicación (Gestor correspondiente)
    participant DB as PostgreSQL

    alt Alta o Edición de Registro (Cliente, Chofer o Vehículo)
        Admin->>UI: Clic en "+ Nuevo..." o "Editar" en menú de fila
        UI->>Modal: Abre modal con React Hook Form + Zod
        Admin->>Modal: Completa datos y guarda
        Modal->>SA: crearAction / editarAction
        SA->>API: POST /api/{recurso} o PUT /api/{recurso}/{id}
        API->>Gestor: crear / modificar (normaliza claves y valida invariantes)
        Gestor->>DB: Persistir cambios
        DB-->>API: 201 Created / 200 OK
        API-->>SA: Respuesta validada
        SA->>SA: revalidatePath de vistas afectadas
        SA-->>Modal: Cierra modal y refresca listado (router.refresh)
    else Edición de Tarifas por Tipo de Vehículo (/vehiculos)
        Admin->>UI: Modifica tarifa_hora_base o tarifa_km_excedente en PanelTarifas
        UI->>SA: actualizarTipoVehiculoAction(id, datos)
        SA->>API: PUT /api/tipos-vehiculo/{id}
        API->>Gestor: modificar_tipo_vehiculo(...)
        Gestor->>DB: UPDATE tipos_vehiculo
        DB-->>API: 200 OK
        SA->>SA: revalidatePath("/vehiculos", "/servicios", "/cotizaciones", "/")
        SA-->>UI: Confirma actualización de tarifas vigentes
    else Baja Lógica con Protección de Historial
        Admin->>UI: Clic en "Dar de baja" y confirma en DialogoConfirmacion
        UI->>SA: darDeBajaAction(id)
        SA->>API: DELETE /api/{recurso}/{id}
        API->>Gestor: dar_de_baja(id)
        Gestor->>DB: Verificar si tiene servicios o vehículos asociados
        alt Tiene historial o referencias activas
            DB-->>Gestor: Existen registros asociados
            Gestor-->>API: 409 Conflict (entidad con historial)
            API-->>SA: 409 Conflict con mensaje de negocio
            SA-->>UI: Muestra explicación en el diálogo sin borrar el registro
        else Sin dependencias bloqueantes
            Gestor->>DB: UPDATE activo = False
            DB-->>API: 204 No Content
            SA->>SA: revalidatePath
            SA-->>UI: Oculta registro del listado activo
        end
    end
```

---

### SSD-04: Agenda Operativa y Dashboard Conectados al Backend Real

Representa la carga server-side del Dashboard (`/`) y de la Agenda (`/agenda`) consumiendo los servicios, choferes y vehículos reales desde FastAPI.

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Operador / Logística
    participant Page as Server Component (/ o /agenda)
    participant AgendaUI as Client Component (AgendaCliente)
    participant API as FastAPI (/api/servicios, /api/choferes, /api/vehiculos)
    participant DB as PostgreSQL

    Operador->>Page: Navega a "/" (Dashboard) o "/agenda"
    Page->>API: GET /api/servicios?page=1&size=100 (cache: "no-store")
    API->>DB: Consulta servicios con JOINs a cliente, tipo, chofer y vehículo
    DB-->>API: PaginatedServicios
    API-->>Page: Lista de servicios reales con estados e importes
    Page-->>AgendaUI: Hidrata grilla mensual con los servicios reales agrupados por fecha

    Operador->>AgendaUI: Selecciona un día del calendario o filtra por estado
    AgendaUI-->>Operador: Muestra servicios programados para esa fecha, chofer, patente y horario

    Operador->>AgendaUI: Clic en "+ Nuevo servicio"
    AgendaUI->>Page: Navega a /servicios?nuevo=1
    Page-->>Operador: Abre automáticamente el formulario de alta de servicio
```

---

### SSD-05: Conmutación y Persistencia de Modo Oscuro / Modo Claro

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
    alt theme == 'dark' o (sin preferencia y matchMedia dark)
        Head->>DOM: classList.add('dark'), setAttribute('data-theme', 'dark')
    else theme == 'light'
        Head->>DOM: classList.remove('dark'), setAttribute('data-theme', 'light')
    end

    Note over Store: Renderizado de la aplicación
    Store->>DOM: Obtiene snapshot de tema inicial ('dark' o 'light')
    Store-->>Usuario: Renderiza UI con tokens correspondientes

    Usuario->>Store: Clic en botón Sol/Luna en header
    Note over Store: toggleTheme(): next = (current == 'dark' ? 'light' : 'dark')
    Store->>DOM: Modifica clase 'dark' y atributo 'data-theme'
    Store->>LocalStorage: setItem('theme', nextTheme)
    DOM-->>Store: MutationObserver detecta cambio de atributo
    Store-->>Usuario: Actualiza icono del botón y aplica variables CSS sin recarga
```

---

### SSD-06: Refactorización — Simetría de Alta/Edición en `/clientes` y Normalización Compartida en Dominio

Representa la consolidación del flujo de alta y edición en `/clientes` (`NuevoCliente` + `DialogoCliente` + `guardarCliente(datos, id?)`) junto con la centralización de las primitivas de normalización de texto y conteo de dígitos en `app/domain/normalizacion.py`.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    participant Btn as NuevoCliente / FilaCliente (/clientes)
    participant Modal as DialogoCliente (cliente?: Cliente)
    participant SA as guardarCliente(datos, id?)
    participant API as FastAPI (POST / PUT /api/clientes)
    participant Dom as Dominio (Cliente + normalizacion.py)
    participant DB as PostgreSQL

    alt 1. Alta Directa desde /clientes (id === undefined)
        Admin->>Btn: Clic en "+ Nuevo cliente"
        Btn->>Modal: Abre DialogoCliente sin cliente inicial (modo alta)
        Admin->>Modal: Completa razón social, teléfono, dirección y cuenta corriente
        Modal->>SA: guardarCliente(valores, undefined)
        SA->>API: POST /api/clientes
        API->>Dom: Cliente.crear(...) -> normalizar_espacios() + normalizar_clave_comparacion() + contar_digitos()
        Dom->>DB: Verifica unicidad de razon_social_key e inserta registro activo
        DB-->>SA: 201 Created
        SA->>SA: revalidatePath("/clientes", "/servicios", "/agenda", "/")
        SA-->>Modal: Cierra modal y refresca listado
    else 2. Edición desde FilaCliente (id !== undefined)
        Admin->>Btn: Clic en "Editar" en el menú de la fila
        Btn->>Modal: Abre DialogoCliente precargado con cliente existente
        Admin->>Modal: Modifica campos y guarda
        Modal->>SA: guardarCliente(valores, cliente.id)
        SA->>API: PUT /api/clientes/{id}
        API->>Dom: cliente.actualizar(...) -> normalizar_espacios() + normalizar_clave_comparacion()
        Dom->>DB: Verifica unicidad excluyendo id actual y actualiza registro
        DB-->>SA: 200 OK
        SA->>SA: revalidatePath("/clientes", "/servicios", "/agenda", "/")
        SA-->>Modal: Cierra modal y refresca listado
    end
```

---

## 3. Matriz de Trazabilidad Actualizada: Vistas vs. Capacidades y Endpoints

| Vista | Ruta | Componentes Clave | Modo Oscuro | Integración con Backend FastAPI |
|---|---|---|---|---|
| **Dashboard** | `/` | `DashboardPage`, KPIs operativos, tabla de viajes y acceso `/servicios?nuevo=1` | Soportado | **100% Real FastAPI** (`GET /api/servicios`, `/api/choferes`, `/api/vehiculos`) |
| **Agenda** | `/agenda` | `PaginaAgenda`, `AgendaCliente`, calendario mensual interactivo y detalle diario | Soportado | **100% Real FastAPI** (`GET /api/servicios`) |
| **Cotizaciones** | `/cotizaciones` | `PaginaCotizaciones`, `Cotizador`, desglose oficial ARS | Soportado | **100% Real FastAPI** (`GET /api/tipos-vehiculo`, `POST /api/servicios/cotizar`) |
| **Servicios** | `/servicios` | `FormularioServicio`, `ListadoServicios`, `FilaServicio`, `DialogoConfirmacion` | Soportado | **100% Real FastAPI** (`GET/POST /api/servicios`, `POST /cotizar`, `GET /disponibilidad`, `PATCH /{id}/estado`, `PATCH /{id}/cancelar`, `DELETE /{id}`) |
| **Choferes** | `/choferes` | `ListadoChoferes`, `FilaChofer`, `DialogoChofer`, `BuscadorChoferes` | Soportado | **100% Real FastAPI** (`GET/POST /api/choferes`, `PUT/DELETE /api/choferes/{id}`) |
| **Vehículos y Tarifas** | `/vehiculos` | `PanelTarifas`, `ListadoVehiculos`, `FilaVehiculo`, `DialogoVehiculo` | Soportado | **100% Real FastAPI** (`GET/POST /api/vehiculos`, `PUT/DELETE /api/vehiculos/{id}`, `GET/PUT /api/tipos-vehiculo/{id}`) |
| **Clientes** | `/clientes` | `ListadoClientes`, `FilaCliente`, `DialogoCliente`, `BuscadorClientes` | Soportado | **100% Real FastAPI** (`GET/POST /api/clientes`, `PUT/DELETE /api/clientes/{id}`) |
| **Rendiciones** | `/rendiciones` | `PaginaRendiciones`, modales de arqueo y liquidación | Soportado | Prototipo interactivo financiero (pendiente historia de backend de rendiciones) |
| **Shell Global** | Todas | `AdminShell`, sidebar responsive, selector Sol/Luna | Soportado | Layout transversal |
