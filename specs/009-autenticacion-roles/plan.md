# Implementation Plan: 009 — Autenticación y autorización por rol

**Branch**: `009-autenticacion-roles` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Status**: Especificado — Ticket 1 reactiva la implementación con alcance ampliado (ver Enmienda).

## Enmienda — Ticket 1 (2026-10-30)

El **Ticket 1 — Autenticación, Multi-Admin y Creación de Usuarios** amplía esta historia:

- Incorpora cuentas `CHOFER` con login y asociación 1:1 a un chofer activo.
- Habilita que un `ADMIN` autenticado cree cuentas `ADMIN` y `CHOFER`; el primer `ADMIN` sigue
  aprovisionándose por CLI.
- Agrega la tabla `roles` y la tabla `usuarios` con `rol_id`, `id_chofer`, `activo` y auditoría.
- Mantiene las rutas operativas del chofer fuera de alcance.
- Mantiene `require_rol` y normaliza la resolución del rol a `admin`/`chofer` en `get_rol_actual`.
- **Corrige la migración**: la nueva migración es `0006_crear_usuarios_rbac.py` con
  `down_revision = "0005"`, porque `0005_cancelacion_servicios.py` ya existe. No se reutiliza
  `0005_crear_usuarios.py`.
- El detalle de modelo, ERD y contrato está en
  [`docs/especificacion-rbac.md`](../../docs/especificacion-rbac.md).

## Resumen

Agregar cuentas autenticables admin separadas de las entidades operativas, login JWT en FastAPI,
reemplazar el stub `X-Rol` dentro de `get_rol_actual` y establecer una sesión server-side en
Next.js mediante cookie `httpOnly`. Cada API request, layout y Server Action protegido vuelve a
verificar usuario y rol; el `proxy.ts` de Next.js solo hace redirección optimista. La autenticación
de choferes se incorpora en el Ticket 1 (ver Enmienda); las rutas operativas del chofer siguen fuera
de alcance.

El cambio habilita a la historia 008 para integrar Servicios sin simular el rol `admin` en el
frontend.

## Revisión de constitución

| Principio | Resultado | Aplicación |
|---|---|---|
| I. Spec antes de código | PASS | Spec y plan aprobados con username, provisión CLI del primer ADMIN, JWT de 30 min y login de chofer incorporado por Ticket 1. |
| II. Capas y puertos | PASS propuesto | Aplicación consume puertos; SQL queda en repositorios; routers no decodifican JWT. |
| III. Seguridad/API como contrato | PASS propuesto | Backend autoriza; OpenAPI documenta Bearer; frontend solo reenvía token desde servidor. |
| IV. Tests primero en reglas críticas | PASS propuesto | Unitarios para autenticación/token y cobertura de integración para login y roles. |
| V. Simplicidad | PASS propuesto | Sin registro público, SSO, MFA ni refresh token en el MVP. |
| Frontend: sesión y roles | PASS propuesto | Cookie `httpOnly`; guards server-side; Server Actions verifican por sí mismas. |
| Desviación por Next.js 16 | Revisada | La convención `middleware.ts` se renombró a `proxy.ts` en Next 16. Proxy solo redirige; no reemplaza autorización en layouts, acciones ni API. |

## Contexto técnico verificado

- `backend/app/core/dependencias.py` declara `get_rol_actual` leyendo `X-Rol`; `require_rol` ya se
  usa en los routers y debe conservar la misma firma/contrato.
- `ChoferORM` contiene nombre, teléfono, activo y saldo, pero no credenciales.
- `backend/app/core/config.py` solo configura DB y CORS; no existe clave JWT.
- No hay paquete JWT/hash en `backend/pyproject.toml`.
- `frontend/src/lib/auth/` no existe; los layouts admin no verifican sesión.
- El proyecto usa Next `16.4.2`; la guía oficial de Next 16 renombra Middleware a Proxy. Proxy hará
  un check optimista de cookie; llamadas a `/auth/me` y permisos se validarán en servidor.
- El branch actual `008-frontend-gestion-servicios` tiene cambios backend sin commit, incluida la
  migración `0004`. Esta historia debe iniciar sobre 008 integrado o sobre una rama apilada
  explícitamente; su migración es `0006` descendiente de `0005` (ver Enmienda Ticket 1).

## Contrato API propuesto

| Operación | Entrada | Salida |
|---|---|---|
| `POST /api/auth/login` | JSON `{ username, password }` | `access_token`, `token_type: "bearer"`, `expires_in` |
| `GET /api/auth/me` | `Authorization: Bearer <token>` | `id`, `username`, `rol: "admin"` |

- Credenciales inválidas, cuenta inexistente/inactiva: respuesta genérica `401` con
  `WWW-Authenticate: Bearer`.
- Token ausente/inválido/expirado o sujeto no vigente: `401`.
- Token válido sin rol requerido: `403`.
- No hay endpoint público de registro, ni se devuelven hashes o claims no necesarios.
- El JWT contiene identificador de cuenta y expiración; el rol/estado actual se lee del repositorio
  para que una baja o cambio de rol aplique sin esperar a que expire el token.
- Contrato aprobado: login JSON con username/password, username normalizado, token de 30 minutos,
  sin refresh token.

## Archivos de backend propuestos

| Archivo | Responsabilidad |
|---|---|
| `backend/app/domain/usuario.py` | Entidad pura de Usuario con username, rol, estado y vínculo opcional a chofer; sin SQLAlchemy ni Pydantic. |
| `backend/app/domain/errores.py` | Errores tipados de autenticación/cuenta inválida si las operaciones de aplicación los requieren. |
| `backend/app/application/autenticacion/puertos.py` | Protocolos de repositorio de usuario, verificador de contraseñas y emisor/validador de tokens. |
| `backend/app/application/autenticacion/gestor_autenticacion.py` | Casos de uso de autenticar credenciales y resolver identidad actual; errores genéricos de login. |
| `backend/app/infrastructure/models/usuario.py` | Tabla `usuarios`: username único, hash Argon2, rol `ADMIN`/`CHOFER`, vínculo opcional a chofer, activo y auditoría. |
| `backend/app/infrastructure/models/__init__.py` | Registrar el nuevo ORM para metadata/Alembic. |
| `backend/app/infrastructure/repositories/usuario_repo.py` | Buscar por username/id, crear cuentas `ADMIN`/`CHOFER` y resolver rol/estado sin SQL fuera de Infraestructura. |
| `backend/app/infrastructure/security/password_hasher.py` | Hash y verificación con Argon2 usando `pwdlib[argon2]`; no loguear credenciales/hash. |
| `backend/app/infrastructure/security/jwt_service.py` | Crear/verificar JWT con `PyJWT`, algoritmo fijado y validación estricta de `sub`/`exp`. |
| `backend/app/api/schemas/autenticacion.py` | Schemas estrictos `LoginRequest`, `TokenRead` y `UsuarioActualRead`; nunca exponer hash. |
| `backend/app/api/autenticacion.py` | Router login y `/me`; delegar a Aplicación y publicar contrato Bearer. |
| `backend/app/application/usuarios/gestor_usuarios.py` | Casos de uso de alta, listado, edición y baja lógica; multi-admin, vínculo con chofer y protección del último ADMIN. |
| `backend/app/api/schemas/usuarios.py` | Schemas estrictos `UsuarioCreate`, `UsuarioUpdate` y `UsuarioRead`; nunca exponer hash. |
| `backend/app/api/usuarios.py` | Router ABM de usuarios con `require_rol("admin")`; delega reglas a Aplicación. |
| `backend/app/core/dependencias.py` | Componer repo/gestor; sustituir solo la implementación de `get_rol_actual` para validar Bearer y obtener rol actual desde Aplicación/Infraestructura. |
| `backend/app/core/config.py` | Configurar `JWT_SECRET` como secreto requerido, algoritmo constante y TTL validado. No default productivo. |
| `backend/app/main.py` | Registrar router auth y mantener handlers existentes sin exponer detalles sensibles. |
| `backend/alembic/versions/0006_crear_usuarios_rbac.py` | Migración aditiva de `roles` y `usuarios`, constraints e índice único del username; down revision `0005`. |
| `backend/scripts/crear_usuario.py` | Bootstrap por CLI del primer `ADMIN`; solicitar contraseña interactivamente y no imprimirla ni aceptarla como argumento. |
| `backend/.env.example` | Documentar `JWT_SECRET` solo con marcador de configuración, nunca un secreto reutilizable. |
| `docker-compose.yml` | Requerir secreto de entorno en dev, sin valor de producción embebido en el YAML. |
| `.github/workflows/ci.yml` | Inyectar clave de test desechable solo para CI, no reutilizable en despliegue. |
| `backend/tests/unit/application/autenticacion/` | Casos de uso: usuario activo/inactivo, password válido/inválido, rol y ausencia de enumeración. |
| `backend/tests/unit/infrastructure/security/` | Hash Argon2, no reversibilidad, JWT válido, firma errónea, expiración/claims inválidos. |
| `backend/tests/integration/api/test_autenticacion_api.py` | Login, `/me`, 401/403, X-Rol ignorado, rutas existentes con JWT y roles. |
| `backend/tests/integration/conftest.py` | Crear cuentas de prueba y reemplazar secretos por configuración aislada. |

## Archivos de frontend propuestos

| Archivo | Responsabilidad |
|---|---|
| `frontend/src/app/(auth)/login/page.tsx` | Ruta `/login`, formulario y errores de credenciales sin enumeración. |
| `frontend/src/features/auth/schemas/login.ts` | Validación de forma/UX (username y password requeridos), sin lógica de permisos. |
| `frontend/src/features/auth/components/formulario-login.tsx` | Formulario accesible que llama Server Action; no persiste token en estado/localStorage. |
| `frontend/src/features/auth/actions.ts` | Server Actions `iniciarSesion`/`cerrarSesion`; validan respuesta backend y actualizan cookie. |
| `frontend/src/lib/auth/session.ts` | Leer, crear y borrar cookie de sesión con opciones seguras; `server-only`. |
| `frontend/src/lib/auth/guards.ts` | `obtenerUsuarioActual` y `exigirRol`; validar contra `/api/auth/me`, nunca confiar en rol del cliente. |
| `frontend/src/lib/api/servidor.ts` | Wrapper server-only para enviar Bearer desde cookie en requests autenticados. |
| `frontend/src/proxy.ts` | Check optimista de cookie para redirigir a `/login`; no es frontera de autorización. |
| `frontend/src/app/(admin)/layout.tsx` | Exigir rol `admin` antes de renderizar rutas admin. |
| `frontend/src/app/(admin)/usuarios/page.tsx` | Listado y alta de cuentas `ADMIN`/`CHOFER`; solo accesible para ADMIN. |
| `frontend/src/features/usuarios/actions.ts` | Server Actions de alta, edición y baja; revalidan sesión y rol ADMIN. |
| `frontend/src/types/openapi.d.ts` | Generar contrato auth actualizado con `npm run gen:api`; no editar manualmente. |
| `frontend/src/features/auth/**/*.test.tsx` | RTL para formulario, errores y estado accesible. |
| `frontend/tests/auth/**` | Pruebas de guards, cookies y navegación por rol con API simulada. |

## Persistencia y seguridad

- La tabla `usuarios` agrega una FK opcional y única a `choferes.id` (`id_chofer`), pero no altera la tabla `choferes`.
- Username único tras `strip().casefold()`; guardar el valor normalizado para búsquedas y unicidad.
- `password_hash` no se expone por schema ni se registra en logs.
- El secreto JWT se configura externamente; en producción no se permite fallback ni secreto
  conocido. CI usa valor ficticio exclusivo de pruebas.
- El algoritmo queda fijado en código/config validada; el token no puede seleccionar el algoritmo.
- Lookup de usuario activo/rol vigente en cada request evita que un JWT con claims obsoletos
  mantenga permisos.
- No hay registro público. La CLI crea el primer `ADMIN`; las cuentas siguientes las crea un `ADMIN` autenticado. Toda contraseña se toma con `getpass` o se recibe por el canal seguro del alta.
- No hay refresh token en esta versión. Logout invalida la sesión del navegador borrando
  cookie, pero JWT capturado puede usarse hasta expiración; revisar si esto es aceptable.
- Las llamadas web a endpoints protegidos salen desde Server Components/Actions; el navegador no
  recibe ni envía `X-Rol` y no accede al JWT.
- Cada Server Action revalida usuario/rol aunque la ruta y Proxy ya lo hayan verificado.

## Pruebas y verificación

1. Unit tests de password, JWT y casos de uso de autenticación y usuarios sin PostgreSQL,
   incluyendo multi-admin, vínculo con chofer y protección del último ADMIN.
2. Integración API cubre login, cuenta inactiva, `GET /me`, expiración, roles, alta de usuarios,
   conflictos de username/chofer y rechazo de `X-Rol` spoofed.
3. Regresión: los endpoints existentes admin con `require_rol` responden para JWT admin válido y
   deniegan requests anónimos; actualizar fixtures que antes usaban `X-Rol`.
4. Frontend: tests de cookie flags, guards por rol, Server Actions, login fallido/sin respuesta,
   logout y rutas redirigidas.
5. Verificar con `ruff check`, `pytest` unit/integration disponible, exportación OpenAPI y
   `npm run verificar` desde `frontend/`.
6. Probar manualmente login admin con cuenta creada por CLI. No registrar credenciales de prueba
   en `.env.example`, CI logs ni documentación.

## Orden propuesto

1. Asegurar que 008 está integrado o acordar branch apilado; `0006` depende de la migración `0005`.
2. Implementar entidad/puertos/casos de uso y pruebas unitarias.
3. Añadir ORM, migración y repositorio; implementar hash/token y tests.
4. Crear endpoints login/me y ABM de usuarios, cambiar `get_rol_actual` manteniendo `require_rol` y
   probar todas las rutas protegidas.
5. Crear comando de bootstrap y ajustar configuración/compose/CI.
6. Implementar cookie, Server Actions, guard server-side y Proxy; proteger layouts, agregar la
   pantalla `/usuarios` y regenerar tipos OpenAPI.
7. Ejecutar pruebas completas, verificar login admin y confirmar que `X-Rol` no concede acceso.

## Decisiones aprobadas y dependencias

| Riesgo/decisión | Resolución aprobada |
|---|---|
| No existe identidad de usuario ni email en Chofer | Cuenta admin separada con username y contraseña. |
| Admin inicial y altas de cuentas | Primer `ADMIN` por CLI; altas posteriores por API/UI de un `ADMIN`; sin registro público. |
| Robo/expiración de JWT tras logout | Access token 30 min, sin refresh; baja/rol se consulta en DB por request. |
| Autenticación de choferes | Incluida por Ticket 1: login y cuenta `CHOFER` vinculada a chofer; rutas operativas del chofer siguen diferidas. |
| Ramas/migraciones | Empezar 009 después de integrar 008; migración 0006 depende de 0005 (Ticket 1). |
| Header X-Rol en OpenAPI | Retirarlo al cambiar `get_rol_actual`; todos los clientes admin deben autenticarse. |

## Referencias técnicas

- [Next.js Authentication guide](https://nextjs.org/docs/app/guides/authentication)
- [Next.js Proxy convention](https://nextjs.org/docs/app/api-reference/file-conventions/proxy)
- [FastAPI OAuth2/JWT guide](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
