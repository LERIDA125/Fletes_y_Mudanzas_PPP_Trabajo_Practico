# Diagramas de Secuencia del Sistema (SSD) — 009: Autenticación, Auditoría y Portal del Chofer

**Rama**: `009-autenticacion-roles` | **Fecha**: 2026-10-29 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Este documento modela los **3 Diagramas de Secuencia del Sistema (SSD)** correspondientes a los tres
tickets de negocio implementados en la historia `009`.

---

## SSD-009-1: Autenticación JWT, Multi-Admin y Creación de Usuarios (`admin` / `chofer`)

**Cubre**:
- Login unificado con emisión de JWT `HS256` (`POST /api/auth/login`).
- Creación de múltiples cuentas de Administrador (Multi-Admin) por un dueño autenticado.
- Creación de usuario y contraseña para un Chofer existente (`POST /api/auth/usuarios`), validando
  que solo el rol `admin` pueda crear choferes (`POST /api/choferes`) y cuentas de acceso.

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

    Note over Admin,DB: 1. Inicio de sesión del Administrador
    Admin->>UI: Ingresa username y password en /login
    UI->>API: POST /api/auth/login {username, password}
    API->>Auth: iniciar_sesion(username, password)
    Auth->>Repo: obtener_por_username(username_key)
    Repo->>DB: SELECT * FROM usuarios WHERE username = :u
    DB-->>Repo: UsuarioORM (rol='admin', activo=true)
    Auth->>Sec: verificar_password(password, password_hash)
    Sec-->>Auth: True (scrypt + compare_digest)
    Auth->>Sec: emitir_token(sub=id, rol='admin', id_chofer=None)
    Sec-->>Auth: access_token (JWT HS256, exp=30m)
    Auth-->>API: TokenAutenticacion(access_token, usuario)
    API-->>UI: 200 OK {access_token, token_type: "bearer", usuario}

    Note over Admin,DB: 2. Alta de segundo Administrador (Multi-Admin)
    Admin->>UI: Completa formulario "Nuevo Administrador" en /usuarios
    UI->>API: POST /api/auth/usuarios (Bearer JWT Admin 1)<br/>{username, password, rol: "admin"}
    API->>API: require_rol("admin") valida JWT y usuario activo
    API->>Auth: crear_usuario(username, password, rol="admin", creado_por_id=Admin1.id)
    Auth->>Sec: hashear_password(password)
    Auth->>Repo: crear(Usuario(rol="admin", creado_por_id=Admin1.id))
    Repo->>DB: INSERT INTO usuarios (..., rol='admin', creado_por_id=1)
    DB-->>Repo: UsuarioORM (id=2)
    API-->>UI: 201 Created UsuarioRead (id=2, rol="admin")

    Note over Admin,DB: 3. Admin registra Chofer y le crea su cuenta de Usuario
    Admin->>UI: Crea chofer (POST /api/choferes) y le asigna usuario en /usuarios
    UI->>API: POST /api/auth/usuarios (Bearer JWT Admin 1)<br/>{username, password, rol: "chofer", id_chofer: 10}
    API->>API: require_rol("admin")
    API->>Auth: crear_usuario(..., rol="chofer", id_chofer=10, creado_por_id=Admin1.id)
    Auth->>Repo: verificar chofer activo (id_chofer=10) y sin usuario previo
    Auth->>Sec: hashear_password(password)
    Auth->>Repo: crear(Usuario(rol="chofer", id_chofer=10, creado_por_id=Admin1.id))
    Repo->>DB: INSERT INTO usuarios (..., rol='chofer', id_chofer=10, creado_por_id=1)
    DB-->>Repo: UsuarioORM (id=3, id_chofer=10)
    API-->>UI: 201 Created UsuarioRead (id=3, rol="chofer", id_chofer=10)

    Note over Chofer,DB: 4. Login del Chofer con las credenciales creadas por el Admin
    Chofer->>UI: Ingresa su username y password en /login
    UI->>API: POST /api/auth/login {username, password}
    API->>Auth: iniciar_sesion(username, password)
    Auth-->>API: JWT con claims {sub: "3", rol: "chofer", id_chofer: 10}
    API-->>UI: 200 OK -> Redirige a /chofer
```

---

## SSD-009-2: Trazabilidad y Auditoría ("El Quién hizo qué")

**Cubre**:
- Extracción automática del `usuario.id` desde el token JWT en la capa de Presentación/Aplicación.
- Persistencia de `creado_por_id` y `modificado_por_id` en todas las tablas operativas (`clientes`,
  `choferes`, `tipos_vehiculo`, `vehiculos`, `servicios`, `usuarios`) al crear, editar, cambiar
  estado, cancelar o dar de baja lógica.

```mermaid
sequenceDiagram
    autonumber
    actor AdminA as Admin 1 (id=1)
    actor AdminB as Admin 2 (id=2)
    participant API as FastAPI Router (Presentación)
    participant Dep as get_usuario_actual (Dependencia JWT)
    participant Gestor as Gestor de Aplicación (Clientes/Servicios/etc.)
    participant Dom as Entidad de Dominio
    participant Repo as Repositorio SQLAlchemy
    participant DB as PostgreSQL

    Note over AdminA,DB: 1. Creación de registro (INSERT con auditoría de creador)
    AdminA->>API: POST /api/servicios (Authorization: Bearer <JWT sub=1>)
    API->>Dep: Resolver identidad desde Bearer JWT
    Dep->>DB: SELECT id, username, rol, activo FROM usuarios WHERE id = 1
    DB-->>Dep: UsuarioAutenticado(id=1, rol="admin")
    API->>Gestor: crear(..., usuario_id=1)
    Gestor->>Dom: Servicio.crear(..., creado_por_id=1, modificado_por_id=1)
    Gestor->>Repo: crear(servicio)
    Repo->>DB: INSERT INTO servicios (..., creado_por_id=1, modificado_por_id=1)
    DB-->>Repo: ServicioORM (id=50, creado_por_id=1, modificado_por_id=1)
    Repo-->>API: ServicioListadoItem
    API-->>AdminA: 201 Created {id_servicio: 50, creado_por_id: 1, modificado_por_id: 1}

    Note over AdminB,DB: 2. Modificación / Cambio de estado / Baja lógica por otro usuario (UPDATE)
    AdminB->>API: PATCH /api/servicios/50/estado (Authorization: Bearer <JWT sub=2>)<br/>{"estado": "confirmado"}
    API->>Dep: Resolver identidad desde Bearer JWT
    Dep-->>API: UsuarioAutenticado(id=2, rol="admin")
    API->>Gestor: cambiar_estado(id_servicio=50, estado="confirmado", usuario_id=2)
    Gestor->>Repo: obtener_por_id(50)
    Repo-->>Gestor: Servicio(id=50, creado_por_id=1, modificado_por_id=1)
    Gestor->>Dom: servicio.transicionar_a("confirmado", modificado_por_id=2)
    Gestor->>Repo: actualizar(servicio)
    Repo->>DB: UPDATE servicios SET estado='confirmado', modificado_por_id=2, actualizado_en=now() WHERE id=50
    DB-->>Repo: ServicioORM (id=50, creado_por_id=1, modificado_por_id=2)
    Repo-->>API: ServicioListadoItem
    API-->>AdminB: 200 OK {id_servicio: 50, estado: "confirmado", creado_por_id: 1, modificado_por_id: 2}
```

---

## SSD-009-3: Vista Restringida del Chofer y Sincronización en Tiempo Real

**Cubre**:
- Filtrado estricto `WHERE id_chofer = token.id_chofer` en `GET /api/servicios` cuando el token es
  de rol `chofer`.
- Sincronización automática periódica (polling cada 5 segundos en `frontend/src/lib/api/servicios.ts`)
  para que el chofer vea en su pantalla móvil los viajes que el administrador le asigna en tiempo
  real.
- Actualización de estado operativa (`confirmado → en curso → finalizado`) por el propio chofer con
  validación de pertenencia (`servicio.id_chofer == usuario.id_chofer`).

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

    Note over Chofer,DB: 1. Apertura del Portal Móvil y filtrado obligatorio por id_chofer
    Chofer->>Portal: Abre /chofer en su dispositivo móvil
    Portal->>Http: listarMisServicios() (inicia polling cada 5s)
    Http->>API: GET /api/servicios (Authorization: Bearer <JWT rol="chofer", id_chofer=10>)
    API->>API: require_roles("admin", "chofer") -> detecta rol="chofer"
    API->>Gestor: listar(offset=0, limit=50, id_chofer=10)
    Gestor->>Repo: contar(id_chofer=10) + listar(offset=0, limit=50, id_chofer=10)
    Repo->>DB: SELECT ... FROM servicios WHERE id_chofer = 10 ORDER BY id
    DB-->>Repo: Filas exclusivas del chofer 10
    Repo-->>API: items, total
    API-->>Portal: 200 OK {items: [viajes del chofer 10], total}

    Note over Admin,DB: 2. El Administrador asigna un nuevo viaje al Chofer 10
    Admin->>API: POST /api/servicios (Bearer JWT Admin)<br/>{id_chofer: 10, estado: "pendiente", ...}
    API->>Gestor: crear(..., id_chofer=10, usuario_id=Admin.id)
    Gestor->>Repo: crear(servicio)
    Repo->>DB: INSERT INTO servicios (..., id_chofer=10, creado_por_id=1)
    DB-->>API: 201 Created (id_servicio=77)

    Note over Chofer,DB: 3. Sincronización automática en tiempo real (Tick de Polling)
    loop Cada 5 segundos en segundo plano
        Portal->>Http: Tick de sincronización automática
        Http->>API: GET /api/servicios (Bearer JWT Chofer 10)
        API->>Gestor: listar(..., id_chofer=10)
        Gestor->>Repo: SELECT ... WHERE id_chofer = 10
        Repo-->>API: Incluye el nuevo viaje #77
        API-->>Portal: 200 OK -> Actualiza lista en vivo sin recargar la página
    end

    Note over Chofer,DB: 4. El Chofer actualiza el estado de su propio viaje
    Chofer->>Portal: Toca botón "Iniciar viaje (En curso)" en viaje #77
    Portal->>Http: cambiarEstadoServicioChofer(77, "en curso")
    Http->>API: PATCH /api/servicios/77/estado (Bearer JWT Chofer 10)<br/>{"estado": "en curso"}
    API->>Gestor: cambiar_estado(id_servicio=77, estado="en curso", usuario_actual=Chofer10)
    Gestor->>Repo: obtener_por_id(77)
    Repo-->>Gestor: Servicio #77 (id_chofer=10)
    Gestor->>Gestor: Verifica servicio.id_chofer == 10 y estado permitido para chofer
    Gestor->>Repo: actualizar(servicio con estado="en curso", modificado_por_id=3)
    Repo->>DB: UPDATE servicios SET estado='en curso', modificado_por_id=3 WHERE id=77
    DB-->>API: 200 OK ServicioRead
    API-->>Portal: 200 OK -> Refresca tarjeta del viaje en vivo
```

---

## Matriz de Trazabilidad (Historia 009)

| Ticket | SSD | Endpoints / Componentes | Reglas de Negocio Verificadas |
|---|---|---|---|
| **1. Autenticación, Multi-Admin y Usuarios** | `SSD-009-1` | `POST /api/auth/login`, `GET /api/auth/me`, `GET /api/auth/usuarios`, `POST /api/auth/usuarios`, `/login`, `/usuarios` | Hash `scrypt`, JWT `HS256`, múltiples cuentas `admin`, alta de cuenta `chofer` exclusiva por `admin`, protección `403` en `POST /api/choferes`. |
| **2. Trazabilidad y Auditoría** | `SSD-009-2` | `ClienteORM`, `ChoferORM`, `TipoVehiculoORM`, `VehiculoORM`, `ServicioORM`, `UsuarioORM`, Gestores de Aplicación | Columnas `creado_por_id` y `modificado_por_id` pobladas automáticamente desde el token JWT en altas, modificaciones, cambios de estado, cancelaciones y bajas lógicas. |
| **3. Vista Restringida del Chofer y Tiempo Real** | `SSD-009-3` | `GET /api/servicios`, `PATCH /api/servicios/{id}/estado`, `frontend/src/lib/api/servicios.ts`, `/chofer` | Filtro obligatorio `WHERE id_chofer = token.id_chofer`, bloqueo `403` sobre viajes ajenos, polling automático cada 5s en el portal móvil del chofer. |
