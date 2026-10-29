# Implementation Plan: 009 — Autenticación JWT, Multi-Admin, Auditoría y Portal del Chofer

**Branch**: `009-autenticacion-roles` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

**Status**: Active

## Resumen Técnico por Ticket

### 1. Autenticación JWT, Multi-Admin y Creación de Usuarios
- **Dominio (`app/domain/usuario.py`)**: Entidad `Usuario` con `username` normalizado
  (`strip().casefold()`), `password_hash`, `rol` (`"admin"` | `"chofer"`), `id_chofer` (obligatorio
  si `rol == "chofer"`, `None` si `rol == "admin"`), `activo`, `creado_por_id` y
  `modificado_por_id`.
- **Seguridad (`app/infrastructure/security/`)**:
  - `password_hasher.py`: Hash y verificación con `hashlib.scrypt` + sal aleatoria de 16 bytes y
    comparación constante con `hmac.compare_digest`.
  - `jwt_service.py`: Emisión y verificación de tokens RFC 7519 `HS256` con validación estricta de
    firma (`hmac.compare_digest`), algoritmo, `sub`, `rol`, `id_chofer` y `exp`.
- **Aplicación (`app/application/autenticacion/`)**:
  - `GestorAutenticacion`: login, obtención de usuario actual, listado de cuentas y creación de
    cuentas `admin` (multi-admin) o `chofer` (validando que `id_chofer` exista y esté activo, y que
    no tenga ya una cuenta asociada).
- **Presentación (`app/api/autenticacion.py` y `app/core/dependencias.py`)**:
  - `POST /api/auth/login`, `GET /api/auth/me`, `GET /api/auth/usuarios`, `POST /api/auth/usuarios`.
  - `get_usuario_actual` resuelve el token `Authorization: Bearer <token>` contra la base de datos.
    En entorno `dev` con `DEV_ASSUME_ADMIN=true` y sin header `Authorization`, mantiene
    compatibilidad con la suite de pruebas existente asumiendo identidad de desarrollo (`id=None`).

### 2. Trazabilidad y Auditoría ("Quién hizo qué")
- **Infraestructura (`alembic/versions/0006_usuarios_auditoria_y_chofer.py` y Modelos ORM)**:
  - Crea la tabla `usuarios`.
  - Añade `creado_por_id` (`INTEGER REFERENCES usuarios(id) ON DELETE SET NULL`) y
    `modificado_por_id` (`INTEGER REFERENCES usuarios(id) ON DELETE SET NULL`) a `clientes`,
    `choferes`, `tipos_vehiculo`, `vehiculos` y `servicios`.
- **Aplicación y Dominio**:
  - `GestorClientes`, `GestorChoferes`, `GestorTiposVehiculo`, `GestorVehiculos`, `GestorServicios`
    y `GestorAutenticacion` reciben `usuario_id: int | None = None` desde los routers y lo
    persisten en `creado_por_id` (en altas) y `modificado_por_id` (en altas, ediciones, cambios de
    estado, cancelaciones y bajas lógicas).

### 3. Vista Restringida del Chofer y Sincronización en Tiempo Real
- **Backend (`app/application/servicios/gestor_servicios.py` y `app/api/servicios.py`)**:
  - `ServicioRepository.listar` y `contar` aceptan `id_chofer: int | None = None`.
  - `GET /api/servicios` admite `ROL_ADMIN` y `ROL_CHOFER` mediante `require_roles(ROL_ADMIN,
    ROL_CHOFER)`. Si el usuario autenticado tiene `rol == "chofer"`, el gestor fuerza
    `id_chofer = usuario_actual.id_chofer`.
  - `PATCH /api/servicios/{id_servicio}/estado` admite `ROL_ADMIN` y `ROL_CHOFER`. Si el usuario es
    `chofer`, verifica que `servicio.id_chofer == usuario_actual.id_chofer` y que el estado destino
    sea operativo (`en curso` o `finalizado`).
- **Frontend (`frontend/src/`)**:
  - `src/lib/api/http.ts` y `src/lib/api/auth.ts`: soporte de token Bearer e identidad de sesión.
  - `src/lib/api/servicios.ts`: función de consulta y hook/utilidad de sincronización periódica
    (polling cada 5 segundos) para el portal del chofer.
  - `src/app/login/page.tsx`: inicio de sesión para administradores y choferes con redirección
    según rol (`/` para admin, `/chofer` para chofer).
  - `src/app/(admin)/usuarios/page.tsx`: panel de gestión de cuentas Multi-Admin y alta de
    credenciales para choferes activos.
  - `src/app/chofer/page.tsx`: portal móvil restringido del chofer con sincronización en tiempo
    real y avance de estado en un toque.
