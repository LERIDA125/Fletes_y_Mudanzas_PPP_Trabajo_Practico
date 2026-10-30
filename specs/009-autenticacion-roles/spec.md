# Feature Specification: 009 — Autenticación y autorización por rol

**Feature Branch**: `009-autenticacion-roles`

**Created**: 2026-10-21

**Status**: Especificado — Ticket 1 reactiva el alcance con Multi-Admin y creación de usuarios (ver Enmienda)

**Input**: Historia de autenticación aprobada inicialmente, pausada por prioridad de producto para
completar el MVP local de Servicios sin login.

## Resumen

Incorporar inicio/cierre de sesión para administradores, reemplazar el stub `X-Rol` por identidad
autenticada en la API y proteger las rutas `(admin)` de Next.js. El backend será la autoridad de
autenticación y permisos. Next.js conservará el JWT en una cookie `httpOnly` y lo reenviará a la
API desde el servidor; ningún rol privilegiado llegará desde código cliente.

La propuesta conserva las rutas actuales que usan `require_rol(rol)`: cambia la resolución del rol,
no la declaración de permisos en cada router.

## Enmienda — Ticket 1 (2026-10-30): Multi-Admin y creación de usuarios

Esta enmienda amplía la historia para cubrir el **Ticket 1 — Autenticación, Multi-Admin y Creación
de Usuarios**. El detalle técnico completo (modelo de datos, ERD, contrato API y criterios de
aceptación) vive en [`docs/especificacion-rbac.md`](../../docs/especificacion-rbac.md).

### Cambios de alcance

| Tema | Decisión anterior | Decisión vigente |
|---|---|---|
| Autenticación de choferes | Diferida a una historia posterior | **Incluida**: login y cuenta de usuario para `CHOFER`; rutas operativas del chofer siguen diferidas. |
| Alta de cuentas | Solo CLI para `admin`; sin UI de gestión | Primer `ADMIN` por CLI; las cuentas siguientes las crea un `ADMIN` autenticado vía API/UI. |
| Multi-admin | No explicitado | **Soportado**: N cuentas `ADMIN` activas. |
| Asociación Usuario–Chofer | Ninguna en esta fase | **Obligatoria** para rol `CHOFER`: 1 cuenta ↔ 1 chofer activo. |
| Roles persistidos | Contrato `admin`/`chofer` sin tabla | Tabla `roles` con códigos `ADMIN`/`CHOFER`. |
| Migración | `0005_crear_usuarios.py` | `0006_crear_usuarios_rbac.py` (la `0005` ya está ocupada por cancelación). |

### Reglas incorporadas

- **BR-001**: solo existen los roles `ADMIN` y `CHOFER`.
- **BR-002**: pueden coexistir múltiples `ADMIN` activos.
- **BR-003**: solo un `ADMIN` autenticado puede crear cuentas de usuario; un `CHOFER` no puede.
- **BR-004**: toda cuenta `CHOFER` se vincula a exactamente un chofer existente y activo; un chofer
  tiene como máximo una cuenta.
- **BR-005**: toda cuenta `ADMIN` tiene `id_chofer = NULL`.
- **BR-006**: no hay registro público; el primer `ADMIN` se aprovisiona por CLI.
- **BR-011**: no se puede desactivar ni degradar la última cuenta `ADMIN` activa (`409`).
- **BR-014**: una cuenta `CHOFER` solo se autentica mientras su chofer siga activo.

### Requisitos funcionales adicionales

- **FR-017**: el sistema MUST admitir múltiples cuentas `ADMIN` activas sin asumir un administrador
  único.
- **FR-018**: `POST /api/usuarios`, `PUT /api/usuarios/{id}` y `DELETE /api/usuarios/{id}` MUST
  exigir rol `ADMIN`; un `CHOFER` MUST recibir `403`.
- **FR-019**: el alta de una cuenta `CHOFER` MUST exigir un `id_chofer` activo y libre, y MUST
  rechazar con `409`/`422` los casos inconsistentes.
- **FR-020**: el sistema MUST impedir el registro público y MUST mantener la provisión CLI para el
  primer administrador.
- **FR-021**: la API MUST impedir la baja o degradación de la última cuenta `ADMIN` activa.
- **FR-022**: el login de `CHOFER` MUST validar que el chofer asociado siga activo y MUST responder
  `401` genérico si no lo está.

### Trazabilidad de la enmienda

- Se actualizó *Usuarios y alcance propuesto* para incluir cuentas `CHOFER`, multi-admin y alta
  administrativa de cuentas.
- Se amplió la tabla *Decisiones aprobadas* con la asociación Usuario–Chofer y la provisión inicial.
- **FR-008** mantiene la prohibición de registro público, pero el alta posterior ya no se limita a la
  CLI.
- *Fuera de alcance* ahora excluye solo las pantallas y rutas operativas del chofer; el login de
  chofer sí queda incluido.
- La migración `0005_crear_usuarios.py` del plan original se reemplaza por `0006_crear_usuarios_rbac.py`.

## Situación actual verificada

| Área | Estado actual |
|---|---|
| Backend | `get_rol_actual` confía en `X-Rol` y usa `chofer` por defecto; no valida identidad. |
| API | No hay router de login ni endpoint de perfil autenticado. |
| Datos | Existe `ChoferORM` sin email, usuario ni contraseña; no hay entidad `Usuario`. |
| Frontend | No existe `src/lib/auth/`, formulario de login, proxy ni guard de rol. |
| Sesión | No hay emisión, validación, expiración o revocación de tokens. |
| Roles | El contrato del proyecto define `admin` y `chofer`; las rutas API ya declaran `require_rol`. |

## Usuarios y alcance propuesto

- **Administrador**: accede a las rutas del grupo `(admin)` y a operaciones API que requieren
  `admin`; pueden coexistir múltiples administradores activos.
- **Chofer**: cuenta autenticable vinculada 1:1 a un chofer activo. En este ticket accede a login y
  perfil; no se crea el grupo `(chofer)` ni pantallas operativas de chofer.
- **Cuenta de usuario**: identidad autenticable separada de las entidades operativas; username,
  hash de contraseña, rol `ADMIN`/`CHOFER`, vínculo opcional a chofer, estado activo y auditoría.
- No existe registro público. El primer `ADMIN` se aprovisiona por CLI; las cuentas siguientes las
  crea un `ADMIN` autenticado vía API/UI.

### Decisiones aprobadas

| Decisión | Resolución aprobada |
|---|---|
| Identificador de acceso | `username` normalizado con `strip().casefold()`; no reutilizar teléfono. |
| Asociación con Chofer | Obligatoria para `CHOFER` (1 cuenta ↔ 1 chofer activo); `ADMIN` no se vincula a chofer. |
| Provisión inicial | CLI interactiva para el primer `ADMIN`; las cuentas siguientes las crea un `ADMIN` autenticado. Sin signup público ni credenciales por defecto. |
| Contraseña | Hash Argon2; nunca persistir ni registrar la contraseña en claro. |
| Token | JWT de acceso firmado con algoritmo fijo; `sub` identifica la cuenta, el backend consulta estado y rol actuales. |
| Sesión web | JWT en cookie `httpOnly`, `sameSite=lax`, `secure` en producción; llamadas API con Bearer desde el servidor Next. |
| Renovación | Sin refresh token en esta versión; al expirar, volver a iniciar sesión. JWT de 30 minutos. |
| Recuperación de contraseña | Fuera de alcance; cambio/reset mediante provisión administrativa fuera de la UI. |
| Baja de cuenta | Desactivar una cuenta bloquea el siguiente request autenticado; no se puede desactivar ni degradar el último `ADMIN` activo. |

## User Scenarios & Testing

### User Story 1 — Iniciar sesión (Priority: P1)

Como administrador con cuenta activa, quiero iniciar sesión con mis credenciales para acceder a
las funciones administrativas.

**Independent Test**: Crear una cuenta admin de prueba, autenticar con credenciales válidas y
verificar token/identidad; comprobar que credenciales inválidas no revelan si el usuario existe.

**Acceptance Scenarios**:

1. **Dado** un usuario activo y contraseña correcta, **cuando** inicia sesión, **entonces** recibe
   un JWT de acceso con expiración y la identidad autenticada, sin datos de contraseña.
2. **Dado** usuario inexistente, inactivo o contraseña incorrecta, **cuando** intenta iniciar
   sesión, **entonces** recibe el mismo error `401` genérico.
3. **Dado** un administrador activo, **cuando** consulta su identidad, **entonces** recibe su rol
   `admin` y su username, sin campos de autenticación sensibles.

### User Story 2 — Rechazar solicitudes no autenticadas y aplicar roles (Priority: P1)

Como responsable del sistema, quiero que la API valide tokens firmados y aplique el rol persistido
para que un cliente no pueda obtener permisos enviando un header arbitrario.

**Independent Test**: Invocar rutas protegidas sin token, con token inválido/expirado, con usuario
inactivo y con roles válidos pero insuficientes; verificar códigos `401` y `403`.

**Acceptance Scenarios**:

1. **Dado** una ruta protegida, **cuando** no se envía Bearer token o el token es inválido/expiró,
   **entonces** la API responde `401` con `WWW-Authenticate: Bearer`.
2. **Dado** un usuario autenticado sin el rol requerido, **cuando** accede a una ruta, **entonces**
   la API responde `403`.
3. **Dado** un request que envía `X-Rol: admin` sin JWT válido, **cuando** intenta acceder a una
   operación admin, **entonces** la API rechaza el request.
4. **Dado** un usuario que fue desactivado o cuyo rol cambió después de emitir el JWT, **cuando**
   usa un token aún no expirado, **entonces** la API aplica el estado/rol actual de la base y no
   conserva permisos obsoletos.
5. **Dado** una ruta con `require_rol("admin")` o `require_rol("chofer")`, **cuando** cambia el
   mecanismo de autenticación, **entonces** se mantiene la declaración de permisos del router.

### User Story 3 — Mantener y cerrar sesión en Next.js (Priority: P1)

Como administrador autenticado, quiero que mi sesión se conserve de forma segura y que las rutas
admin me redirijan correctamente, pudiendo cerrar la sesión desde cualquier pantalla protegida.

**Independent Test**: Probar login/logout con Server Actions, inspeccionar flags de cookie y
validar acceso/redirección admin con pruebas de integración de componentes/rutas.

**Acceptance Scenarios**:

1. **Dado** un login exitoso, **cuando** Next.js recibe el JWT, **entonces** lo guarda en cookie
   `httpOnly`, `sameSite=lax`, `secure` en producción y con expiración no mayor a la del token.
2. **Dado** un navegador sin sesión, **cuando** navega a una ruta protegida, **entonces** se
   redirige a `/login` sin ejecutar operaciones privilegiadas.
3. **Dado** una sesión admin, **cuando** abre una ruta protegida, **entonces** el layout valida la
   identidad con la API y la API vuelve a aplicar su propia autorización.
4. **Dado** un Server Action llamado directamente, **cuando** el usuario no tiene sesión o el rol
   requerido, **entonces** el action rechaza la operación aunque el layout haya protegido la página.
5. **Dado** que el usuario cierra sesión, **cuando** termina la acción, **entonces** se borra la
   cookie y las rutas protegidas dejan de ser accesibles desde la aplicación.
6. **Dado** un token expirado o revocado por desactivación, **cuando** la aplicación obtiene la
   identidad, **entonces** limpia la sesión y redirige a login con un mensaje claro.

### Edge Cases

- `JWT_SECRET` ausente, débil o inválido: la aplicación no debe arrancar con una clave de
  producción por defecto.
- Token con algoritmo distinto al configurado, firma incorrecta, `sub` inválido o expiración
  ausente: rechazar con `401`, sin fallback a `X-Rol`.
- Cuenta `admin` inactiva: rechazar login y requests existentes con token.
- Si la API está caída durante `GET /auth/me`, no convertir el error de conexión en una identidad
  válida ni dejar pasar rutas protegidas.
- Logout borra la cookie de Next; un JWT copiado puede seguir siendo válido hasta su expiración
  salvo que se apruebe revocación server-side.

## Functional Requirements

- **FR-001**: La API MUST autenticar cuentas activas con `username` y contraseña y emitir un token
  firmado con expiración.
- **FR-002**: Las contraseñas MUST guardarse únicamente como hash Argon2, comparado con una función
  de verificación resistente a timing.
- **FR-003**: La API MUST incluir endpoint autenticado para devolver identidad admin y username sin
  exponer el hash.
- **FR-004**: `get_rol_actual` MUST validar Bearer JWT y resolver usuario activo y rol vigente;
  `X-Rol` MUST dejar de conceder permisos.
- **FR-005**: Token ausente, malformado, firma inválida, expirado, sujeto inexistente o usuario
  inactivo MUST dar `401`; identidad válida con rol insuficiente MUST dar `403`.
- **FR-006**: La verificación MUST fijar algoritmo de firma permitido y exigir claims de sujeto y
  expiración. La clave MUST provenir de configuración segura, nunca de un default compartido.
- **FR-007**: La API MUST conservar las dependencias `require_rol(rol)` existentes para evitar
  cambios dispersos en los routers.
- **FR-008**: El sistema MUST impedir el alta pública de cuentas. El primer `ADMIN` se crea por CLI
  restringida e interactiva; las cuentas siguientes las crea un `ADMIN` autenticado.
- **FR-009**: La UI MUST almacenar el JWT en cookie `httpOnly`; el token no debe estar en
  `localStorage`, `sessionStorage` ni accesible al JavaScript del navegador.
- **FR-010**: Las llamadas Next.js a API protegida MUST ejecutarse desde el servidor y propagar el
  Bearer token de la cookie; no leer `X-Rol` del cliente.
- **FR-011**: `proxy.ts` puede hacer redirección optimista por presencia de sesión. Cada layout,
  Server Action y acceso a datos protegido MUST validar sesión y rol de nuevo en servidor; la API
  permanece como frontera de seguridad.
- **FR-012**: La cookie MUST usar `httpOnly`, `sameSite=lax`, `secure` en producción, `path=/` y
  expiración alineada con el token.
- **FR-013**: Los errores de login MUST ser genéricos para no revelar existencia/estado de usuario.
- **FR-014**: Logout MUST borrar la cookie de sesión. La revocación inmediata de JWT queda sujeta a
  la decisión abierta sobre refresh/blacklist.
- **FR-015**: La configuración MUST documentar variables nuevas en `.env.example`, Docker Compose
  y CI sin incluir secretos reales.
- **FR-016**: OpenAPI MUST documentar login, perfil actual y esquema Bearer; el frontend MUST
  regenerar `openapi.d.ts` mediante el script existente.

## Fuera de alcance

- Registro público, roles dinámicos, recuperación/cambio de contraseña, MFA, SSO/OAuth externo.
- Refresh tokens, lista de revocación o cierre remoto de todas las sesiones, salvo decisión del
  Tech Lead.
- Rehacer permisos de negocio de cada endpoint; las rutas existentes continúan declarando roles
  con `require_rol`.
- Creación del grupo `(chofer)` y pantallas operativas de chofer; el login de chofer sí está incluido.
- Reanudar la UI de Servicios; esta puede integrarse una vez que la autenticación admin esté lista.

## Criterios de éxito

- **SC-001**: `X-Rol: admin` por sí solo no permite acceder a ninguna operación que requiere admin.
- **SC-002**: Todos los endpoints actuales protegidos para `admin` aceptan un JWT admin válido y
  rechazan sin token, token inválido o expirado.
- **SC-003**: Las cuentas inactivas o el cambio de rol se reflejan en el siguiente request
  autenticado.
- **SC-004**: Ninguna contraseña se persiste en claro, aparece en respuesta, log o mensaje de
  error.
- **SC-005**: Next.js conserva el JWT solo en cookie `httpOnly`; los guards y Server Actions
  vuelven a comprobar rol y bloquean acceso cruzado.
- **SC-006**: Pytest, Ruff, tests frontend, lint, format y typecheck pasan; OpenAPI/tipos reflejan
  el contrato de autenticación.
- **SC-007**: `/servicios` puede consumir endpoints protegidos solo tras completar esta historia y
  recibir un usuario `admin` autenticado.

## Decisiones aprobadas

- El identificador de acceso es username, no email ni teléfono.
- Se almacena una entidad `Usuario` separada; los datos de contacto de `Chofer` no se modifican.
- No hay registro público. El primer `ADMIN` se provisiona por CLI; las cuentas siguientes las crea un `ADMIN` autenticado y la pantalla `/usuarios` está restringida a ese rol.
- El JWT de acceso dura 30 minutos y no tiene refresh en esta versión.
- Al desactivar usuario o cambiar rol, el cambio aplica al siguiente request mediante lookup del
  usuario vigente.
