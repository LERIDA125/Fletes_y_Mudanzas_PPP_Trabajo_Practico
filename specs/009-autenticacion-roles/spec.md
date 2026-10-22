# Feature Specification: 009 — Autenticación y autorización por rol

**Feature Branch**: `009-autenticacion-roles`

**Created**: 2026-10-21

**Status**: Paused — fuera del MVP actual; decisiones conservadas para retomar luego

**Input**: Historia de autenticación aprobada inicialmente, pausada por prioridad de producto para
completar el MVP local de Servicios sin login.

## Resumen

Incorporar inicio/cierre de sesión para administradores, reemplazar el stub `X-Rol` por identidad
autenticada en la API y proteger las rutas `(admin)` de Next.js. El backend será la autoridad de
autenticación y permisos. Next.js conservará el JWT en una cookie `httpOnly` y lo reenviará a la
API desde el servidor; ningún rol privilegiado llegará desde código cliente.

La propuesta conserva las rutas actuales que usan `require_rol(rol)`: cambia la resolución del rol,
no la declaración de permisos en cada router.

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
  `admin`.
- La autenticación de Chofer queda diferida a una historia posterior; esta entrega no crea el grupo
  `(chofer)` ni cuentas para ese rol.
- **Cuenta admin**: identidad autenticable separada de las entidades operativas; username, hash de
  contraseña, rol `admin`, estado activo y auditoría.
- No existe registro público ni UI de administración de cuentas. La cuenta admin se provisiona
  por comando CLI interactivo.

### Decisiones aprobadas

| Decisión | Resolución aprobada |
|---|---|
| Identificador de acceso | `username` normalizado con `strip().casefold()` para cuentas `admin`; no reutilizar teléfono. |
| Asociación con Chofer | Ninguna en esta fase; la autenticación de choferes queda fuera de alcance. |
| Provisión inicial | Comando local interactivo para crear cuentas `admin`; sin signup público ni credenciales por defecto. |
| Contraseña | Hash Argon2; nunca persistir ni registrar la contraseña en claro. |
| Token | JWT de acceso firmado con algoritmo fijo; `sub` identifica la cuenta, el backend consulta estado y rol actuales. |
| Sesión web | JWT en cookie `httpOnly`, `sameSite=lax`, `secure` en producción; llamadas API con Bearer desde el servidor Next. |
| Renovación | Sin refresh token en esta versión; al expirar, volver a iniciar sesión. JWT de 30 minutos. |
| Recuperación de contraseña | Fuera de alcance; cambio/reset mediante provisión administrativa fuera de la UI. |
| Baja de cuenta | Desactivar cuenta admin bloquea el siguiente request autenticado. |

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
- **FR-008**: El sistema MUST impedir el alta pública de cuentas. Las cuentas `admin` se crean
  únicamente por CLI restringida e interactiva.
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

- Registro público, administración de usuarios desde una pantalla, recuperación/cambio de
  contraseña, MFA, SSO/OAuth externo.
- Refresh tokens, lista de revocación o cierre remoto de todas las sesiones, salvo decisión del
  Tech Lead.
- Rehacer permisos de negocio de cada endpoint; las rutas existentes continúan declarando roles
  con `require_rol`.
- Autenticación de choferes, creación del grupo `(chofer)`, y pantallas operativas de chofer.
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

- El identificador para la cuenta admin es username, no email ni teléfono.
- Se almacena una entidad `Usuario` separada; los datos de contacto de `Chofer` no se modifican.
- No hay registro público ni UI de gestión de cuentas; las cuentas admin se provisionan por CLI.
- El JWT de acceso dura 30 minutos y no tiene refresh en esta versión.
- Al desactivar usuario o cambiar rol, el cambio aplica al siguiente request mediante lookup del
  usuario vigente.
