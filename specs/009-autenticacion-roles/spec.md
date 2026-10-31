# Feature Specification: 009 — Autenticación JWT, Multi-Admin, Auditoría y Portal del Chofer

**Feature Branch**: `009-autenticacion-roles`

**Created**: 2026-10-21 | **Updated**: 2026-10-29

**Status**: Active — En implementación sobre `009-autenticacion-roles`

## Resumen

Esta especificación unifica los 3 tickets evolutivos solicitados por el cliente para el cierre de
seguridad, trazabilidad y operación móvil:

1. **Ticket 1 — Autenticación JWT, Multi-Admin y Creación de Usuarios (`admin` / `chofer`)**:
   - Login con `username` y `password` que emite un token JWT firmado (`HS256`) con `sub` (ID del
     usuario), `rol` (`admin` o `chofer`), `id_chofer` (cuando aplica) y `exp`.
   - Soporte para **múltiples cuentas de Administrador** (varios dueños/encargados operando en
     simultáneo).
   - Creación de cuentas de usuario para **Choferes** exclusivamente por parte de un `admin`
     autenticado (`POST /api/auth/usuarios`), vinculando la cuenta al registro activo de `choferes`
     (`id_chofer`).
   - Protección de `POST /api/choferes` y demás mutaciones administrativas para que solo un token
     con rol `admin` pueda ejecutarlas.

2. **Ticket 2 — Trazabilidad y Auditoría ("El Quién hizo qué")**:
   - Incorporación de las columnas `creado_por_id` y `modificado_por_id` (FK a `usuarios.id`) en
     todas las tablas operativas de SQLAlchemy (`clientes`, `choferes`, `tipos_vehiculo`,
     `vehiculos`, `servicios` y `usuarios`).
   - Los gestores de la Capa de Aplicación reciben automáticamente el `usuario_id` extraído del
     token JWT del usuario autenticado al momento de hacer `INSERT`, `UPDATE`, cambio de estado,
     cancelación o baja lógica (`DELETE`).

3. **Ticket 3 — Vista Restringida del Chofer y Sincronización en Tiempo Real**:
   - En `GET /api/servicios`, si el token pertenece al rol `chofer`, el gestor de Aplicación
     inyecta un filtro obligatorio `WHERE id_chofer = token.id_chofer`, impidiendo que un chofer
     vea servicios de otros choferes o sin asignar.
   - El chofer puede avanzar el estado operativo de sus propios viajes (`confirmado → en curso →
     finalizado`) mediante `PATCH /api/servicios/{id}/estado`, rechazándose con `403` cualquier
     intento sobre un viaje ajeno o transición administrativa (`cobrado`).
   - Portal móvil del chofer (`/chofer`) en Next.js con sincronización automática mediante polling
     en el cliente HTTP (`frontend/src/lib/api/servicios.ts`) cada X segundos para reflejar en
     tiempo real los nuevos viajes asignados por el administrador.

---

## User Scenarios & Testing

### User Story 1 — Autenticación JWT, Multi-Admin y Alta de Usuarios de Chofer (Priority: P1)

Como dueño/administrador de la empresa, quiero iniciar sesión con mi cuenta, dar de alta a otros
administradores (socios/encargados) y crearles credenciales de acceso a los choferes registrados,
para que cada persona ingrese con su propio usuario y rol.

**Acceptance Scenarios**:

1. **Dado** un usuario activo (`admin` o `chofer`) y contraseña correcta, **cuando** envía
   `POST /api/auth/login`, **entonces** recibe un JWT `Bearer` con expiración y los datos de su
   identidad (`id`, `username`, `rol`, `id_chofer`), sin exponer `password_hash`.
2. **Dado** un usuario inexistente, inactivo o con contraseña incorrecta, **cuando** intenta
   iniciar sesión, **entonces** recibe `401 Unauthorized` con mensaje genérico.
3. **Dado** un administrador autenticado con JWT, **cuando** crea otra cuenta con `rol="admin"` en
   `POST /api/auth/usuarios`, **entonces** el nuevo administrador puede iniciar sesión y operar con
   todos los permisos de `admin`.
4. **Dado** un administrador autenticado y un chofer activo (`id_chofer`), **cuando** el
   administrador le crea su cuenta con `rol="chofer"` e `id_chofer` en `POST /api/auth/usuarios`,
   **entonces** el chofer puede iniciar sesión y su token identifica su `id_chofer`.
5. **Dado** un usuario con rol `chofer`, **cuando** intenta ejecutar `POST /api/choferes` o
   `POST /api/auth/usuarios`, **entonces** la API rechaza la operación con `403 Forbidden`.

---

### User Story 2 — Trazabilidad y Auditoría de Operaciones Críticas (Priority: P1)

Como socio administrador, quiero que cada alta, modificación, cambio de estado, cancelación o baja
lógica registre qué usuario la ejecutó (`creado_por_id` y `modificado_por_id`), para auditar quién
creó, modificó o dio de baja cada registro cuando operan múltiples usuarios.

**Acceptance Scenarios**:

1. **Dado** el Administrador A autenticado (`id=1`), **cuando** crea un cliente, chofer, tipo de
   vehículo, vehículo o servicio, **entonces** el registro persiste `creado_por_id = 1` y
   `modificado_por_id = 1`.
2. **Dado** un registro creado por el Administrador A (`id=1`), **cuando** el Administrador B
   (`id=2`) lo modifica, cancela o da de baja lógica, **entonces** `creado_por_id` se mantiene en
   `1` y `modificado_por_id` se actualiza a `2`.
3. **Dado** un viaje asignado al Chofer C (usuario `id=3`), **cuando** el Chofer C avanza el estado
   del viaje a `en curso`, **entonces** el servicio conserva el `creado_por_id` del administrador
   que lo agendó y actualiza `modificado_por_id = 3`.

---

### User Story 3 — Vista Restringida del Chofer y Sincronización en Tiempo Real (Priority: P1)

Como chofer autenticado desde mi celular, quiero ver únicamente mis viajes asignados, recibir en
tiempo real los nuevos viajes que el administrador me asigne sin recargar manualmente la página, y
actualizar el estado de mi viaje en curso.

**Acceptance Scenarios**:

1. **Dado** un chofer autenticado con `id_chofer = 10`, **cuando** consulta `GET /api/servicios`,
   **entonces** el gestor filtra obligatoriamente por `id_chofer = 10` y devuelve solo sus propios
   viajes, ocultando los de otros choferes y los no asignados.
2. **Dado** un chofer autenticado con `id_chofer = 10`, **cuando** avanza el estado de su propio
   servicio de `confirmado` a `en curso` o de `en curso` a `finalizado`, **entonces** el cambio se
   persiste con `200 OK` y registra su `modificado_por_id`.
3. **Dado** un chofer autenticado con `id_chofer = 10`, **cuando** intenta cambiar el estado de un
   servicio asignado a otro chofer (`id_chofer = 20`) o pasar un servicio a `cobrado`, **entonces**
   la API rechaza la operación con `403 Forbidden`.
4. **Dado** el portal móvil `/chofer` abierto en el navegador, **cuando** el cliente HTTP ejecuta
   el ciclo de sincronización periódica (polling cada X segundos), **entonces** cualquier viaje
   nuevo o actualizado por el administrador aparece automáticamente en pantalla.

---

## Functional Requirements

- **FR-001**: La API MUST autenticar cuentas activas (`admin` y `chofer`) mediante
  `POST /api/auth/login` comparando contraseñas con hash resistente a ataques de timing (`scrypt` +
  `hmac.compare_digest`) y emitir un JWT `HS256` con expiración.
- **FR-002**: La tabla `usuarios` MUST permitir múltiples cuentas con `rol='admin'` (`id_chofer IS
  NULL`) y cuentas con `rol='chofer'` vinculadas unívocamente a un chofer (`id_chofer IS NOT NULL`,
  `UNIQUE`).
- **FR-003**: Solo un usuario con rol `admin` MUST poder crear cuentas de usuario (`POST
  /api/auth/usuarios`), listar usuarios (`GET /api/auth/usuarios`) y registrar choferes (`POST
  /api/choferes`).
- **FR-004**: Los modelos ORM `ClienteORM`, `ChoferORM`, `TipoVehiculoORM`, `VehiculoORM`,
  `ServicioORM` y `UsuarioORM` MUST incluir las columnas `creado_por_id` y `modificado_por_id`
  referenciando `usuarios.id`.
- **FR-005**: Los gestores de Aplicación MUST asignar `creado_por_id` y `modificado_por_id` al
  crear, y actualizar `modificado_por_id` al modificar, cambiar estado, cancelar o dar de baja
  lógica.
- **FR-006**: `GET /api/servicios` MUST permitir los roles `admin` y `chofer`; cuando el usuario es
  `chofer`, `GestorServicios.listar` MUST aplicar el filtro `WHERE id_chofer = usuario.id_chofer`.
- **FR-007**: `PATCH /api/servicios/{id}/estado` MUST permitir que un `chofer` avance únicamente
  sus propios servicios asignados hacia `en curso` o `finalizado`, denegando con `403` servicios
  ajenos o el estado `cobrado`.
- **FR-008**: El frontend MUST incluir la pantalla `/login`, la gestión de usuarios multi-admin y
  choferes en `/usuarios`, y el portal móvil `/chofer` con refresco automático periódico (polling).
