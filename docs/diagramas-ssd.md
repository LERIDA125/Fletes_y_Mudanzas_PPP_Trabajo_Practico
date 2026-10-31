# Catálogo de Diagramas de Secuencia del Sistema (SSD)

**Proyecto**: Fletes y Mudanzas Express (MVP 1)  
**Cátedra**: Trabajo Integrador de Prácticas Pre-Profesionales 1 (2026) — Licenciatura en Sistemas, UNLa  

Este documento reúne los **10 Diagramas de Secuencia del Sistema (SSD)** correspondientes a todas las Historias de Usuario recopiladas en [`historias-de-usuario.md`](./historias-de-usuario.md).

---

## SSD-01: Gestión de Clientes — Alta, Búsqueda Normalizada, Edición y Baja Protegida (`001` + `005` + `008`)

Cubre `US-001.1`, `US-001.2`, `US-001.3`, `US-001.4`, `US-005.2` y `US-008.7`.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    participant UI as Frontend (/clientes · DialogoCliente / FilaCliente)
    participant SA as Server Actions (clientes/actions.ts)
    participant API as FastAPI (/api/clientes)
    participant Gestor as Aplicación (GestorClientes)
    participant Dom as Dominio (Cliente)
    participant Repo as Infraestructura (ClienteRepo · PostgreSQL)

    rect rgb(235, 245, 255)
    Note over Admin,Repo: 1. Listado Paginado y Búsqueda con Debounce (350 ms / Enter)
    Admin->>UI: Escribe texto en BuscadorClientes ("distribuidora")
    UI->>API: GET /api/clientes?q=distribuidora&page=1
    API->>Gestor: listar(q="distribuidora", page=1, size=20)
    Gestor->>Repo: buscar_activos(q_norm="distribuidora")
    Repo-->>API: 200 OK { items, total, page, size }
    API-->>UI: Renderiza tabla con razón social, teléfono, dirección y badge de cuenta corriente
    end

    rect rgb(235, 255, 240)
    Note over Admin,Repo: 2. Alta y Modificación de Cliente
    Admin->>UI: Abre "+ Nuevo cliente" o "Editar", completa datos (RHF + Zod) y guarda
    UI->>SA: crearClienteAction / editarClienteAction
    SA->>API: POST /api/clientes (o PUT /api/clientes/{id})
    API->>Gestor: crear / modificar
    Gestor->>Dom: Valida longitud (3..120), teléfono (7..20 dígitos) y normaliza razon_social_key
    Gestor->>Repo: Verifica unicidad de razon_social_key
    alt Razón social duplicada
        Repo-->>API: 409 Conflict (RazonSocialDuplicada)
        API-->>UI: Muestra error en el formulario sin perder los datos ingresados
    else Datos válidos y únicos
        Repo-->>API: 201 Created / 200 OK
        SA->>SA: revalidatePath("/clientes", "/servicios")
        SA-->>UI: Cierra modal y refresca listado
    end
    end

    rect rgb(255, 240, 240)
    Note over Admin,Repo: 3. Baja Lógica con Protección de Historial
    Admin->>UI: Clic en "Dar de baja" y confirma en DialogoConfirmacion
    UI->>SA: darDeBajaClienteAction(id)
    SA->>API: DELETE /api/clientes/{id}
    API->>Gestor: eliminar(id)
    Gestor->>Repo: ¿Tiene servicios asociados en tabla servicios?
    alt Tiene servicios asociados
        Repo-->>API: 409 Conflict (ClienteConHistorial)
        API-->>UI: Explica en el diálogo que no se puede dar de baja por tener servicios
    else Sin servicios asociados
        Gestor->>Repo: UPDATE clientes SET activo = false WHERE id = {id}
        Repo-->>API: 204 No Content
        SA-->>UI: Quita al cliente del listado activo
    end
    end
```

---

## SSD-02: Migración Idempotente de Datos Históricos y Reporte de Auditoría (`002` / H13)

Cubre `US-002.1` a `US-002.5`.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador (CLI)
    participant CLI as Script Migración (scripts/migracion)
    participant XLS as Excel Histórico (Caso 2 .xlsx)
    participant Trans as Transformador Puro (Normalizador)
    participant Repo as Infraestructura (ClienteRepo · PostgreSQL)
    participant Rep as Reporte Markdown (reporte_migracion.md)

    Admin->>CLI: Ejecuta importador ETL
    CLI->>XLS: Verifica presencia de hojas (Choferes_y_Moviles, Clientes_Cotizaciones, Registro_Viajes)
    XLS-->>CLI: Entrega filas crudas con número de fila original
    CLI->>Trans: transformar_todo(filas_crudas)
    Note over Trans: Normaliza códigos (CLI-000, MOV-00, VJ-0000),<br/>extrae dígitos de teléfonos, capacidades en kg,<br/>fechas multiformato y separa casos ambiguos a Cola de Revisión
    Trans-->>CLI: Conjuntos normalizados + Cola de Revisión Humana + Gaps de Mapeo

    loop Por cada cliente normalizado
        CLI->>Repo: buscar_por_razon_social_key(key)
        alt Ya existe en PostgreSQL
            Repo-->>CLI: Reconocido (idempotente: no duplica)
        else Nuevo cliente válido
            CLI->>Repo: crear(Cliente(..., tiene_cuenta_corriente=False))
            Repo-->>CLI: Persistido
        end
    end

    CLI->>Rep: Genera reporte_migracion.md (Transformaciones, Revisión Humana, Gaps, Totales)
    Rep-->>Admin: Reporte auditable listo para revisión con el cliente
```

---

## SSD-03: Gestión de Tipos de Vehículo, Tarifas Vigentes y Flota de Vehículos (`003` + `007` + `008`)

Cubre `US-003.1` a `US-003.8`, `US-007.1` y `US-008.7`.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    participant UI as Frontend (/vehiculos · PanelTarifas / DialogoVehiculo)
    participant SA as Server Actions (vehiculos/actions.ts)
    participant API as FastAPI (/api/vehiculos & /api/tipos-vehiculo)
    participant Gestor as Aplicación (GestorVehiculos)
    participant Repo as Infraestructura (VehiculoRepo · PostgreSQL)

    rect rgb(235, 245, 255)
    Note over Admin,Repo: 1. Consulta de Flota Enriquecida con JOINs (US-007.1)
    Admin->>UI: Abre /vehiculos
    UI->>API: GET /api/vehiculos?page=1&q=... y GET /api/tipos-vehiculo
    API->>Gestor: listar_vehiculos(...)
    Gestor->>Repo: SELECT v.*, tv.descripcion, tv.capacidad_carga_kg, c.nombre_completo<br/>FROM vehiculos v JOIN tipos_vehiculo tv LEFT JOIN choferes c
    Note over Repo: El LEFT JOIN preserva el nombre del chofer<br/>aunque haya sido dado de baja lógicamente
    Repo-->>UI: Renderiza PanelTarifas + Tabla de Vehículos con datos legibles
    end

    rect rgb(255, 248, 225)
    Note over Admin,Repo: 2. Actualización de Tarifas por Tipo de Vehículo (US-003.3 / US-008.7)
    Admin->>UI: Edita tarifa_hora_base y tarifa_km_excedente en PanelTarifas
    UI->>SA: actualizarTipoVehiculoAction(id, payload)
    SA->>API: PUT /api/tipos-vehiculo/{id}
    API->>Gestor: modificar_tipo_vehiculo(id, datos)
    Gestor->>Repo: UPDATE tipos_vehiculo (Decimal ROUND_HALF_UP)
    Repo-->>SA: 200 OK
    SA->>SA: revalidatePath("/vehiculos", "/servicios", "/cotizaciones", "/")
    SA-->>UI: Tarifas actualizadas para próximas cotizaciones (sin alterar snapshots pasados)
    end

    rect rgb(235, 255, 240)
    Note over Admin,Repo: 3. Alta, Edición y Baja Lógica de Vehículo (US-003.5 a US-003.8)
    Admin->>UI: Crea/Edita unidad en DialogoVehiculo (patente AAA 123 / AA 123 ABC, tipo, chofer)
    UI->>SA: crearVehiculoAction / editarVehiculoAction
    SA->>API: POST /api/vehiculos (o PUT /api/vehiculos/{id})
    API->>Gestor: Valida formato de patente, unicidad de patente_norm, tipo activo y chofer activo
    Gestor->>Repo: INSERT / UPDATE vehiculos
    Repo-->>UI: 201 Created / 200 OK y refresca listado
    end
```

---

## SSD-04: Gestión de Choferes Activos y Saldo de Cuenta Corriente (`004` + `006` + `008`)

Cubre `US-004.1` a `US-004.4`, `US-006.1` y `US-008.7`.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    participant UI as Frontend (/choferes · DialogoChofer / FilaChofer)
    participant SA as Server Actions (choferes/actions.ts)
    participant API as FastAPI (/api/choferes)
    participant Gestor as Aplicación (GestorChoferes)
    participant Repo as Infraestructura (ChoferRepo · PostgreSQL)

    Admin->>UI: Abre /choferes o filtra por nombre en BuscadorChoferes
    UI->>API: GET /api/choferes?q=...&page=1
    API->>Gestor: listar_choferes_activos(...)
    Gestor->>Repo: SELECT * FROM choferes WHERE activo = true AND nombre_completo ILIKE %q%
    Repo-->>UI: Muestra choferes activos con teléfono y saldo_a_favor en ARS

    Admin->>UI: Clic en "+ Nuevo chofer" o "Editar" en menú de fila
    UI->>SA: crearChoferAction / editarChoferAction
    SA->>API: POST /api/choferes (o PUT /api/choferes/{id})
    API->>Gestor: Valida nombre (3..120) y teléfono (7..20 dígitos); inicializa saldo_a_favor = 0.0
    Gestor->>Repo: Persistir chofer
    Repo-->>SA: 201 Created / 200 OK
    SA->>SA: revalidatePath("/choferes", "/vehiculos", "/servicios", "/")
    SA-->>UI: Actualiza tabla de choferes

    Admin->>UI: Clic en "Dar de baja" y confirma en DialogoConfirmacion
    UI->>SA: darDeBajaChoferAction(id)
    SA->>API: DELETE /api/choferes/{id}
    API->>Gestor: dar_de_baja(id)
    Gestor->>Repo: UPDATE choferes SET activo = false (conserva saldo e historial)
    Repo-->>UI: 204 No Content y desaparece del listado de activos
```

---

## SSD-05: Cotización Oficial en Dos Pasos, Disponibilidad Informativa y Alta de Servicio (`008`)

Cubre `US-008.1`, `US-008.2` y `US-008.3`.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Operador / Admin
    participant UI as Frontend (/servicios · FormularioServicio)
    participant SA as Server Actions (servicios/actions.ts)
    participant API as FastAPI (/api/servicios)
    participant Gestor as Aplicación (GestorServicios + Calculadora Strategy)
    participant DB as PostgreSQL

    Admin->>UI: Selecciona fecha, hora_inicio, id_tipo_vehiculo, horas_estimadas y distancia_ida_km
    UI->>SA: consultarDisponibilidadAction(fecha, id_tipo_vehiculo, horas_estimadas, hora_inicio)
    SA->>API: GET /api/servicios/disponibilidad
    API->>Gestor: consultar_disponibilidad(...)
    Gestor->>DB: Obtiene choferes activos, vehículos activos del tipo y viajes no cancelados del día
    Note over Gestor: Excluye recursos con solapamiento en [hora_inicio, hora_inicio + horas)<br/>o comprometidos en un servicio sin hora_inicio en esa fecha
    Gestor-->>UI: Filtra desplegables de Chofer y Vehículo con unidades libres

    Admin->>UI: Clic en "Calcular cotización"
    UI->>SA: cotizarServicioAction({ id_tipo_vehiculo, horas_estimadas, distancia_ida_km })
    SA->>API: POST /api/servicios/cotizar
    API->>Gestor: cotizar(...)
    Gestor->>DB: Lee tarifa_hora_base y tarifa_km_excedente del TipoVehiculo activo
    Note over Gestor: Estrategia PorHoraYKm:<br/>distancia_total_km = distancia_ida_km * 2<br/>km_excedente = max(0, distancia_total_km - 10)<br/>precio_final = ROUND_HALF_UP(tarifa_hora * horas + tarifa_km * km_excedente)
    Gestor-->>UI: Muestra ResumenCotizacion (desglose y precio_final ARS) y habilita confirmación

    Note over Admin,UI: Si el operador altera tipo, horas o distancia, la cotización se invalida

    Admin->>UI: Elige "Cliente existente" (id_cliente) o "Cliente nuevo" (nuevo_cliente), confirma y envía
    UI->>SA: crearServicioAction(payload sin precios ni importes derivados)
    SA->>API: POST /api/servicios (extra="forbid")
    API->>Gestor: crear(datos)
    alt Se envió nuevo_cliente
        Gestor->>DB: Busca por razon_social_key (reutiliza si está activo, crea si no existe, 409 si está inactivo)
    end
    Gestor->>DB: Recalcula con tarifas vigentes e inserta Servicio (estado="pendiente" + snapshot tarifario)
    DB-->>SA: 201 Created (ServicioRead con precio_total definitivo)
    SA->>SA: revalidatePath("/servicios", "/clientes", "/agenda", "/")
    SA-->>UI: Presenta confirmación e importe definitivo y actualiza el listado
```

---

## SSD-06: Ciclo de Vida del Servicio — Máquina de Estados, Cancelación con Motivo y Eliminación (`008`)

Cubre `US-008.4`, `US-008.5` y `US-008.6`.

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

    alt 1. Avance de Estado Ordinario (US-008.4)
        Admin->>Fila: Abre menú de acciones y confirma avanzar al siguiente estado
        Fila->>SA: cambiarEstadoServicioAction(id, estadoSiguiente)
        SA->>API: PATCH /api/servicios/{id}/estado { estado }
        API->>Gestor: cambiar_estado(id, estado)
        Gestor->>DB: obtener_por_id(id)
        Gestor->>Dom: servicio.transicionar_a(estado)
        Note over Dom: Secuencia estricta:<br/>pendiente → confirmado → en curso → finalizado → cobrado
        Gestor->>DB: actualizar(servicio)
        DB-->>Fila: 200 OK y refresca badge de estado
    else 2. Cancelación con Motivo Obligatorio y Hora del Servidor (US-008.5)
        Admin->>Fila: Clic en "Cancelar servicio", escribe motivo (1..255 chars) y confirma
        Fila->>SA: cancelarServicioAction(id, { motivo })
        SA->>API: PATCH /api/servicios/{id}/cancelar { motivo }
        API->>Gestor: cancelar(id, motivo)
        Gestor->>DB: obtener_por_id(id)
        Gestor->>Dom: servicio.cancelar(motivo, hora_fin=servidor.now().time())
        Note over Dom: Solo permitido desde pendiente, confirmado o en curso.<br/>Si está finalizado, cobrado o cancelado responde 409 Conflict
        Gestor->>DB: UPDATE servicios SET estado='cancelado', motivo_cancelacion=..., hora_fin=...
        DB-->>Fila: 200 OK (muestra estado Cancelado, motivo y hora_fin)
    else 3. Eliminación con Confirmación (US-008.6)
        Admin->>Fila: Clic en "Eliminar" y confirma en DialogoConfirmacion
        Fila->>SA: eliminarServicioAction(id)
        SA->>API: DELETE /api/servicios/{id}
        API->>Gestor: eliminar(id)
        Gestor->>DB: DELETE FROM servicios WHERE id = {id}
        DB-->>Fila: 204 No Content (o 409 Conflict si tiene referencias dependientes)
    end
```

---

## SSD-07: Agenda Operativa Mensual, Cotizador Comercial y Dashboard en Tiempo Real (`008`)

Cubre `US-008.8`.

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Operador / Logística
    participant Browser as Navegador (Next.js App Router)
    participant RSC as Server Components (/, /agenda, /cotizaciones)
    participant HTTP as Cliente HTTP (lib/api/http.ts)
    participant API as FastAPI (/api/...)

    Operador->>Browser: Accede al Dashboard (/) o Agenda (/agenda)
    Browser->>RSC: Renderizado en servidor (SSR dinámico)
    RSC->>HTTP: request("/api/servicios?page=1&size=100", cache: "no-store")
    alt Red Docker activa
        HTTP->>API: Conecta a http://backend:8000
    else Ejecución local fuera de Docker
        HTTP->>API: Fallback automático a http://localhost:8000
    end
    API-->>RSC: Retorna servicios, choferes y vehículos reales
    RSC-->>Operador: Hidrata KPIs del día y calendario mensual con viajes agrupados por fecha

    Operador->>Browser: Navega a /cotizaciones, elige tipo, horas y km de ida
    Browser->>API: Server Action -> POST /api/servicios/cotizar
    API-->>Browser: Devuelve desglose oficial ARS calculado por el backend
```

---

## SSD-08: Arqueo Financiero y Rendición de Choferes (`008`)

Cubre el flujo interactivo de liquidación en `/rendiciones` (`US-008.8`).

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    participant View as Vista Rendiciones (/rendiciones)
    participant Modal as Modal Detalle / Liquidación
    participant State as Estado de Arqueo Financiero

    Admin->>View: Accede a /rendiciones
    View->>State: Carga KPIs financieros y tabla de rendiciones (#REN-024 a #REN-020)
    View-->>Admin: Presenta métricas de recaudación, gastos y saldos pendientes

    Admin->>View: Clic en "Ver detalle" de #REN-024
    View->>Modal: Abre desglose de tarifa cobrada, adelantos y gastos (peajes/combustible)
    Admin->>Modal: Clic en "Aprobar rendición"
    Modal->>State: Marca rendición como "Aprobada" y actualiza saldo neto
    State-->>View: Actualiza indicadores y badge de estado a verde
```

---

## SSD-09: Conmutación de Modo Oscuro / Claro sin FOUC (`008`)

Cubre `US-008.8` (Accesibilidad y Tema Visual con React 19).

```mermaid
sequenceDiagram
    autonumber
    actor Usuario as Usuario
    participant Head as Script Inline <head> (layout.tsx)
    participant Store as useSyncExternalStore (admin-shell.tsx)
    participant DOM as document.documentElement
    participant LS as localStorage

    Note over Head: Antes del primer pintado del navegador (Anti-FOUC)
    Head->>LS: getItem("theme")
    alt theme == "dark" o (sin preferencia y prefers-color-scheme: dark)
        Head->>DOM: classList.add("dark"), setAttribute("data-theme", "dark")
    else theme == "light"
        Head->>DOM: classList.remove("dark"), setAttribute("data-theme", "light")
    end

    Store->>DOM: Lee snapshot inicial sin causar hydration mismatch
    Usuario->>Store: Clic en botón Sol / Luna del encabezado
    Store->>DOM: Alterna clase "dark" y atributo "data-theme"
    Store->>LS: setItem("theme", nuevoTema)
    DOM-->>Store: MutationObserver notifica a useSyncExternalStore
    Store-->>Usuario: Re-renderiza icono y aplica tokens CSS instantáneamente
```

---

## SSD-10: Autenticación Admin con Argon2, JWT en Cookie `httpOnly` y Guardas por Rol (`009`)

Cubre `US-009.1`, `US-009.2` y `US-009.3` (especificado en `/specs/009-autenticacion-roles/ssd.md`).

### SSD-10.1 — Autenticación JWT, Multi-Admin y Creación de Usuarios (`admin` / `chofer`)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador (Dueño 1)
    actor Chofer as Chofer
    participant UI as Frontend Next.js (/login, /usuarios)
    participant API as FastAPI (/api/auth, /api/choferes)
    participant Auth as GestorAutenticacion
    participant Sec as PasswordHasher + JWTService
    participant Repo as UsuarioRepo + ChoferRepo
    participant DB as PostgreSQL

    Admin->>UI: Ingresa username y password en /login
    UI->>API: POST /api/auth/login {username, password}
    API->>Auth: iniciar_sesion(username, password)
    Auth->>Repo: obtener_por_username(username_key)
    Repo->>DB: SELECT * FROM usuarios WHERE username = :u
    Auth->>Sec: verificar_password(password, password_hash)
    Auth->>Sec: emitir_token(sub=id, rol='admin', id_chofer=None)
    API-->>UI: 200 OK {access_token, token_type: "bearer", usuario}

    Admin->>UI: Crea nuevo Administrador (Multi-Admin) o cuenta de Chofer en /usuarios
    UI->>API: POST /api/auth/usuarios (Bearer JWT Admin 1)<br/>{username, password, rol, id_chofer}
    API->>API: require_rol("admin")
    API->>Auth: crear_usuario(..., creado_por_id=Admin1.id)
    Auth->>Sec: hashear_password(password)
    Auth->>Repo: INSERT INTO usuarios (..., creado_por_id=1)
    API-->>UI: 201 Created UsuarioRead

    Chofer->>UI: Inicia sesión con su usuario creado por el Admin
    UI->>API: POST /api/auth/login {username, password}
    API-->>UI: 200 OK JWT {sub, rol: "chofer", id_chofer} -> Redirige a /chofer
```

### SSD-10.2 — Trazabilidad y Auditoría ("El Quién hizo qué")

```mermaid
sequenceDiagram
    autonumber
    actor AdminA as Admin 1 (id=1)
    actor AdminB as Admin 2 (id=2)
    participant API as FastAPI Router
    participant Dep as get_usuario_actual (JWT)
    participant Gestor as Gestor de Aplicación
    participant Repo as Repositorio SQLAlchemy
    participant DB as PostgreSQL

    AdminA->>API: POST /api/servicios (Bearer JWT sub=1)
    API->>Dep: Resolver usuario autenticado (id=1)
    API->>Gestor: crear(..., usuario_id=1)
    Gestor->>Repo: crear(servicio con creado_por_id=1, modificado_por_id=1)
    Repo->>DB: INSERT INTO servicios (..., creado_por_id=1, modificado_por_id=1)
    API-->>AdminA: 201 Created {creado_por_id: 1, modificado_por_id: 1}

    AdminB->>API: PATCH /api/servicios/50/estado (Bearer JWT sub=2)
    API->>Dep: Resolver usuario autenticado (id=2)
    API->>Gestor: cambiar_estado(50, "confirmado", usuario_id=2)
    Gestor->>Repo: actualizar(servicio con modificado_por_id=2)
    Repo->>DB: UPDATE servicios SET estado='confirmado', modificado_por_id=2 WHERE id=50
    API-->>AdminB: 200 OK {creado_por_id: 1, modificado_por_id: 2}
```

### SSD-10.3 — Vista Restringida del Chofer y Sincronización en Tiempo Real

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    actor Chofer as Chofer (id_chofer=10, user_id=3)
    participant Portal as Portal Móvil Chofer (/chofer)
    participant Http as Cliente HTTP + Polling (lib/api/servicios.ts)
    participant API as FastAPI (/api/servicios)
    participant Gestor as GestorServicios
    participant Repo as ServicioRepo
    participant DB as PostgreSQL

    Chofer->>Portal: Abre /chofer en su celular
    Portal->>Http: Inicia polling cada 5s contra GET /api/servicios
    Http->>API: GET /api/servicios (Bearer JWT rol="chofer", id_chofer=10)
    API->>Gestor: listar(offset=0, limit=50, id_chofer=10)
    Gestor->>Repo: SELECT ... FROM servicios WHERE id_chofer = 10
    Repo->>DB: Consulta filtrada estrictamente por id_chofer=10
    API-->>Portal: 200 OK (solo viajes asignados al Chofer 10)

    Admin->>API: POST /api/servicios {id_chofer: 10, ...}
    API-->>Admin: 201 Created

    Portal->>Http: Siguiente tick automático (5s)
    Http->>API: GET /api/servicios (Bearer JWT Chofer 10)
    API-->>Portal: 200 OK -> Muestra el nuevo viaje asignado en tiempo real

    Chofer->>Portal: Avanza estado a "en curso" / "finalizado"
    Portal->>Http: PATCH /api/servicios/{id}/estado (Bearer JWT Chofer 10)
    API->>Gestor: Verifica servicio.id_chofer == 10 y actualiza modificado_por_id=3
    API-->>Portal: 200 OK ServicioRead
```
