# Recopilación de Historias de Usuario (SSD & Especificaciones)

**Proyecto**: Fletes y Mudanzas Express (MVP 1)  
**Metodología**: Spec-Driven Development (Spec Kit)  
**Fuente de verdad**: `/specs/001` a `/specs/009` consolidadas en `main`  

---

## Módulo 001 (H1) — Gestión de Clientes

> **Objetivo del módulo**: Reemplazar la planilla de clientes por un padrón persistente con unicidad de razón social normalizada (`razon_social_key`), validación flexible de teléfono (7 a 20 dígitos) y baja lógica con protección de historial.

### US-001.1 — Registrar un cliente nuevo (Prioridad: P1)
- **Como** administrador de Fletes y Mudanzas Express,
- **quiero** dar de alta un cliente con su razón social, teléfono, dirección habitual y la indicación de si tiene cuenta corriente,
- **para** poder después cotizarle y agendarle servicios.
- **Criterios de Aceptación**:
  1. **Dado** un administrador autenticado y ningún cliente con la razón social `"Distribuidora del Sur S.A."`, **cuando** registra un cliente con razón social `"Distribuidora del Sur S.A."`, teléfono `"351 555 0100"`, dirección habitual `"Av. Colón 1250, Córdoba"` y `tiene_cuenta_corriente = true`, **entonces** el cliente queda registrado con `activo = true` y aparece en el listado (`201 Created`).
  2. **Dado** un administrador autenticado, **cuando** registra un cliente con `tiene_cuenta_corriente = false`, **entonces** queda registrado con ese indicador en `false`.
  3. **Dado** un alta válida, **cuando** se persiste, **entonces** el sistema asigna `id` autogenerado, `creado_en` y `actualizado_en` sin permitir que el cliente los informe.
  4. **Dado** un cliente ya registrado con `"Distribuidora del Sur S.A."`, **cuando** se intenta registrar otro con la misma razón social (ignorando mayúsculas, acentos y espacios extra), **entonces** el sistema rechaza la operación con `409 Conflict` (`RazonSocialDuplicada`).

### US-001.2 — Consultar y buscar clientes (Prioridad: P1)
- **Como** administrador o chofer,
- **quiero** listar y buscar clientes activos por razón social y ver el detalle de un cliente,
- **para** encontrar rápido los datos de un destinatario sin recorrer toda la planilla.
- **Criterios de Aceptación**:
  1. **Dado** 25 clientes activos registrados, **cuando** se solicita `GET /api/clientes`, **entonces** devuelve la página ordenada de forma estable junto con `total`, `page` y `size`.
  2. **Dado** el cliente `"Distribuidora del Sur S.A."`, **cuando** se busca con `q=distribuidora`, **entonces** devuelve las coincidencias sin distinguir mayúsculas, minúsculas ni acentos.
  3. **Dado** un cliente activo existente, **cuando** se consulta `GET /api/clientes/{id}`, **entonces** devuelve sus datos completos y fechas de auditoría.
  4. **Dado** un texto sin coincidencias, **cuando** se busca, **entonces** devuelve `items: []` y `total: 0` (`200 OK`).
  5. **Dado** un `id` inexistente o dado de baja, **cuando** se consulta su detalle, **entonces** responde `404 Not Found`.

### US-001.3 — Modificar un cliente (Prioridad: P2)
- **Como** administrador,
- **quiero** corregir los datos de un cliente ya registrado (teléfono, dirección, razón social o cuenta corriente),
- **para** mantener el padrón actualizado sin duplicar clientes ni perder su historial.
- **Criterios de Aceptación**:
  1. **Dado** un cliente existente, **cuando** se envía `PUT /api/clientes/{id}` con datos válidos, **entonces** actualiza los campos y `actualizado_en`, conservando `id` y `creado_en`.
  2. **Dado** un intento de cambiar la razón social a una que ya pertenece a otro cliente, **entonces** responde `409 Conflict` y conserva el registro original intacto.
  3. **Dado** un intento de edición con campos vacíos o longitud fuera de rango (razón social 3–120 caracteres, dirección 5–250 caracteres, teléfono 7–20 dígitos), **entonces** responde `422 Unprocessable Entity`.

### US-001.4 — Dar de baja un cliente con protección de historial (Prioridad: P3)
- **Como** administrador,
- **quiero** dar de baja lógicamente a un cliente que ya no opera con la empresa,
- **para** que no aparezca en los selectores de nuevos servicios sin romper los viajes históricos.
- **Criterios de Aceptación**:
  1. **Dado** un cliente activo sin servicios asociados, **cuando** se invoca `DELETE /api/clientes/{id}`, **entonces** pasa a `activo = false`, responde `204 No Content` y desaparece del listado activo.
  2. **Dado** un cliente con servicios asociados en la base de datos, **cuando** se intenta dar de baja, **entonces** el sistema rechaza la operación con `409 Conflict` explicando que posee historial asociado.

---

## Módulo 002 (H13) — Migración de Datos Históricos (ETL desde Excel)

> **Objetivo del módulo**: Importar los datos históricos de `Caso 2 Fletes_Mudanzas_Express_Datos.xlsx` de forma idempotente, sin inventar reglas de negocio ante celdas ambiguas y generando un reporte auditable en Markdown.

### US-002.1 — Cargar los clientes históricos sin duplicar (Prioridad: P1)
- **Como** administrador,
- **quiero** cargar automáticamente los clientes de la hoja `Clientes_Cotizaciones`,
- **para** empezar a operar sin tipear la planilla manualmente.
- **Criterios de Aceptación**:
  1. **Dado** el archivo Excel con 10 filas en `Clientes_Cotizaciones` y prefijos inconsistentes (`"CLI-101"`, `"102"`), **cuando** corre la migración, **entonces** los 10 clientes se cargan una sola vez mediante `ClienteRepo`.
  2. **Dado** teléfonos con símbolos (`"+54 9 11 9876-5432"`), **cuando** se migran, **entonces** se normalizan y validan sin perder los dígitos.
  3. **Dado** notas libres en `Historial_Pagos` (`"Paga a 30 días"`), **cuando** se migran, **entonces** no se fuerzan a booleanos sin confirmación y se preservan íntegras en el reporte.

### US-002.2 — Ejecutar la migración de forma idempotente (Prioridad: P1)
- **Como** administrador,
- **quiero** poder correr el script de migración múltiples veces sin duplicar clientes,
- **para** recuperar el proceso ante cualquier corrección en la planilla.
- **Criterios de Aceptación**:
  1. **Dado** una base con los 10 clientes ya cargados, **cuando** el script se ejecuta nuevamente, **entonces** reconoce cada cliente por su `razon_social_key`, agrega `0` nuevos y mantiene el total en `10`.
  2. **Dado** una fila ilegible o inválida, **cuando** corre el script, **entonces** omite y reporta esa fila sin abortar la carga de las filas válidas.

### US-002.3 — Generar reporte de transformaciones, casos humanos y gaps (Prioridad: P1)
- **Como** administrador,
- **quiero** un reporte en `backend/data/reporte_migracion.md` que detalle qué se transformó y qué requiere decisión humana,
- **para** auditar cada supuesto sin esconder datos ambiguos.
- **Criterios de Aceptación**:
  1. **Dado** una corrida del importador, **entonces** el reporte documenta transformaciones aplicadas, cola de revisión humana (citando hoja, fila original y valor textual) y columnas sin destino en el modelo actual (*gaps de mapeo*).

### US-002.4 — Preservar el texto original de campos libres (Prioridad: P1)
- **Como** administrador,
- **quiero** que las celdas con texto libre (`"En taller hasta el martes"`, `"Archivadores pesados"`, `"Anotado en la libreta"`) conserven su texto original en el reporte,
- **para** no perder información operativa al estructurar los datos.

### US-002.5 — Pre-normalizar móviles, choferes y viajes sin acoplar a la base (Prioridad: P2)
- **Como** administrador,
- **quiero** que la transformación normalice códigos (`MOV-00`, `CLI-000`, `VJ-0000`), capacidades en kg, fechas en múltiples formatos y cruce de choferes por nombre sin requerir base de datos,
- **para** que la lógica ETL sea testeable en aislamiento.

---

## Módulo 003 (H4) — Gestión de Vehículos y Tipos de Vehículo

> **Objetivo del módulo**: Administrar el catálogo de tipos de vehículo (capacidad en kg, tarifa por hora base y tarifa por km excedente) y las unidades físicas de la flota (patente normalizada única, tipo asociado y chofer habitual opcional).

### US-003.1 — Registrar un tipo de vehículo con tarifas (Prioridad: P1)
- **Como** administrador,
- **quiero** dar de alta un tipo de vehículo con descripción, capacidad de carga en kg, tarifa hora base y tarifa km excedente,
- **para** categorizar la flota y alimentar la calculadora oficial de cotizaciones.
- **Criterios de Aceptación**:
  1. **Dado** datos válidos (`descripcion="Camioneta Mediana"`, `capacidad_carga_kg=1500`, `tarifa_hora_base=18000`, `tarifa_km_excedente=650`), **cuando** se envía `POST /api/tipos-vehiculo`, **entonces** se persiste con `201 Created`.
  2. **Dado** capacidad `<= 0` o tarifas `< 0`, **entonces** se rechaza con `422`.
  3. **Dado** una descripción ya existente (`descripcion_key` normalizada), **entonces** se rechaza con `409 Conflict`.

### US-003.2 — Consultar y buscar tipos de vehículo (Prioridad: P1)
- **Como** administrador o chofer,
- **quiero** listar tipos de vehículo activos paginados, filtrar por descripción y consultar su detalle,
- **para** conocer las capacidades y tarifas vigentes.

### US-003.3 — Modificar un tipo de vehículo y actualizar sus tarifas (Prioridad: P2)
- **Como** administrador,
- **quiero** actualizar la descripción, capacidad o tarifas de un tipo de vehículo existente (`PUT /api/tipos-vehiculo/{id}`),
- **para** ajustar precios frente a la inflación sin recrear el tipo ni alterar servicios históricos ya cerrados.

### US-003.4 — Dar de baja un tipo de vehículo (Prioridad: P2)
- **Como** administrador,
- **quiero** dar de baja lógicamente un tipo de vehículo sin unidades asociadas (`DELETE /api/tipos-vehiculo/{id}`),
- **para** depurar el catálogo rechazando con `409 Conflict` si aún tiene vehículos asignados.

### US-003.5 — Registrar un vehículo en la flota (Prioridad: P1)
- **Como** administrador,
- **quiero** registrar un vehículo con su patente argentina (`AAA 123` o `AA 123 ABC`), su tipo de vehículo activo y opcionalmente su chofer habitual activo,
- **para** asignarlo a los servicios de flete y mudanza.
- **Criterios de Aceptación**:
  1. **Dado** patente válida y tipo activo, **cuando** se registra con o sin `id_chofer_habitual`, **entonces** se guarda normalizando `patente_norm` y devuelve `201 Created`.
  2. **Dado** una patente repetida (con o sin espacios/minúsculas), **entonces** responde `409 Conflict`.
  3. **Dado** un tipo de vehículo o chofer habitual inexistente o inactivo, **entonces** responde `404`/`422`.

### US-003.6 — Consultar y buscar vehículos por patente (Prioridad: P1)
- **Como** administrador o chofer,
- **quiero** listar los vehículos activos paginados y buscar por fragmento de patente (`GET /api/vehiculos?q=...`),
- **para** ubicar rápidamente una unidad de la flota.

### US-003.7 — Modificar un vehículo (Prioridad: P2)
- **Como** administrador,
- **quiero** modificar la patente, el tipo o el chofer habitual de un vehículo (`PUT /api/vehiculos/{id}`),
- **para** reflejar reasignaciones de flota.

### US-003.8 — Dar de baja un vehículo con protección de servicios (Prioridad: P2)
- **Como** administrador,
- **quiero** dar de baja lógicamente un vehículo que dejó de operar (`DELETE /api/vehiculos/{id}`),
- **para** quitarlo de la flota activa, bloqueando con `409 Conflict` si tiene servicios asociados.

---

## Módulo 004 (H3) — Gestión de Choferes

> **Objetivo del módulo**: Gestionar el plantel de choferes activos con su nombre completo, teléfono validado y saldo a favor en cuenta corriente (`saldo_a_favor`).

### US-004.1 — Registrar un chofer nuevo (Prioridad: P1)
- **Como** administrador,
- **quiero** dar de alta un chofer con su nombre completo (3–120 caracteres) y su teléfono (7–20 dígitos),
- **para** asignarle vehículos habituales y viajes programados.
- **Criterios de Aceptación**:
  1. **Dado** nombre y teléfono válidos, **cuando** se invoca `POST /api/choferes`, **entonces** se crea el registro con `activo = true` y `saldo_a_favor = 0.0` (`201 Created`).
  2. **Dado** que pueden existir homónimos, **entonces** el sistema permite dos choferes con igual nombre distinguiéndolos por su `id`.

### US-004.2 — Consultar y buscar choferes activos (Prioridad: P1)
- **Como** administrador o chofer,
- **quiero** listar únicamente a los choferes activos paginados y buscarlos por nombre (`GET /api/choferes?q=...`),
- **para** contactar rápido al personal disponible sin ver ex-empleados dados de baja.

### US-004.3 — Modificar los datos de un chofer (Prioridad: P2)
- **Como** administrador,
- **quiero** actualizar el nombre completo o el teléfono de un chofer activo (`PUT /api/choferes/{id}`),
- **para** corregir datos de contacto sin alterar su `saldo_a_favor` ni su `creado_en`.

### US-004.4 — Dar de baja lógicamente a un chofer (Prioridad: P3)
- **Como** administrador,
- **quiero** dar de baja a un chofer (`DELETE /api/choferes/{id}`),
- **para** que deje de aparecer como activo conservando su registro en la base (`activo = false`) y sin borrar su nombre en el historial de vehículos o servicios.

---

## Módulos 005, 006 y 007 — Frontend Base, Catálogos y Enriquecimiento de Flota

> **Objetivo de los módulos**: Construir la aplicación web en Next.js 16 + React 19 + TypeScript sincronizada por contrato OpenAPI (`npm run gen:api`), mobile-first y accesible (WCAG 2.1 AA).

### US-005.1 — Scaffolding del proyecto frontend y contrato OpenAPI tipado (Prioridad: P1)
- **Como** equipo de desarrollo,
- **quiero** contar con el frontend Next.js 16 estructurado por *vertical slices* (`src/features/`), con validación automática de lint, formato, typecheck, tests y generación de tipos OpenAPI,
- **para** detectar cualquier desalineación entre backend y frontend en CI antes de mergear.

### US-005.2 — Listado y búsqueda de clientes en interfaz web (Prioridad: P2)
- **Como** administrador,
- **quiero** visualizar los clientes activos en `/clientes` con buscador con *debounce* (350 ms o Enter), paginación en la URL (`?q=&page=`) y estados claros de carga, vacío y error con reintento,
- **para** consultar el padrón desde escritorio o teléfono móvil sin scroll horizontal.

### US-006.1 — Listado y búsqueda de choferes en interfaz web (Prioridad: P1)
- **Como** administrador,
- **quiero** consultar en `/choferes` el plantel activo con su teléfono, saldo a favor formateado en ARS y fecha de alta, con filtro por nombre en la URL y paginación,
- **para** gestionar el equipo de conductores desde el navegador.

### US-007.1 — Consultar la flota en `/vehiculos` con nombres legibles mediante JOIN (Prioridad: P1)
- **Como** administrador,
- **quiero** ver en `/vehiculos` cada unidad activa con su patente, la descripción del tipo, la capacidad de carga en kg y el nombre del chofer habitual (o `"Sin chofer habitual"`),
- **para** identificar cada móvil sin tener que descifrar IDs numéricos ni hacer llamadas N+1 desde el navegador.
- **Criterios de Aceptación**:
  1. **Dado** un vehículo cuyo chofer habitual fue dado de baja lógicamente, **cuando** se lista la flota en `GET /api/vehiculos`, **entonces** el `LEFT JOIN` conserva el nombre histórico del chofer sin ocultar el vehículo.

---

## Módulo 008 (H8) — Servicios, Cotizador Oficial, Disponibilidad, Ciclo de Vida, ABM UI, Agenda, Dashboard y Modo Oscuro

> **Objetivo del módulo**: Centralizar la operación diaria de Fletes y Mudanzas Express: cotización oficial en dos pasos en el servidor, consulta de disponibilidad por ventana horaria, alta con cliente existente o nuevo, máquina de estados, cancelación con motivo y hora del servidor, paneles interactivos (Dashboard, Agenda, Rendiciones), ABM completo con modales en catálogos y tema claro/oscuro sin parpadeo (FOUC).

### US-008.1 — Cotizar un viaje oficialmente desde el servidor (Prioridad: P1)
- **Como** administrador,
- **quiero** cotizar un viaje enviando tipo de vehículo, horas estimadas ($\ge 1$) y distancia de ida ($\ge 0$ km) a `POST /api/servicios/cotizar`,
- **para** obtener el importe exacto en ARS y el desglose oficial sin que el navegador invente tarifas ni fórmulas.
- **Criterios de Aceptación**:
  1. **Dado** un tipo activo con `tarifa_hora_base = $3.000` y `tarifa_km_excedente = $150`, `2` horas y `15` km de ida, **cuando** se cotiza, **entonces** el backend calcula `distancia_total_km = 30`, `km_franquicia = 10`, `km_excedente = 20` y devuelve `precio_final = $9.000,00 ARS` redondeado con `ROUND_HALF_UP`.
  2. **Dado** una distancia de ida de `4` km (`8` km totales $\le 10$ km de franquicia), **cuando** se cotiza, **entonces** `km_excedente = 0` y solo se cobra el tiempo base.

### US-008.2 — Consultar disponibilidad informativa de choferes y vehículos (Prioridad: P1)
- **Como** administrador,
- **quiero** que al elegir fecha, hora de inicio, horas estimadas y tipo de vehículo en el formulario de servicio se consulten los recursos libres (`GET /api/servicios/disponibilidad`),
- **para** asignar únicamente choferes y vehículos del tipo elegido que no estén ocupados en otro viaje no cancelado en esa franja horaria.

### US-008.3 — Registrar un servicio cotizado con cliente existente o nuevo (Prioridad: P1)
- **Como** administrador,
- **quiero** registrar un servicio en `/servicios` tras revisar y confirmar su cotización, pudiendo seleccionar un cliente del padrón (`id_cliente`) o dar de alta un `nuevo_cliente` en el mismo paso,
- **para** agendar el viaje con un snapshot inmutable de tarifas y estado inicial `pendiente`.
- **Criterios de Aceptación**:
  1. **Dado** que el usuario modifica el tipo de vehículo, las horas o los kilómetros después de cotizar, **entonces** la cotización previa se invalida automáticamente y el botón de alta se bloquea hasta volver a cotizar.
  2. **Dado** un request a `POST /api/servicios` que intente inyectar `precio_total` o tarifas en el JSON, **entonces** Pydantic lo rechaza con `422` (`extra="forbid"`).
  3. **Dado** el modo `"Cliente nuevo"` con una razón social que ya existe activa en la base, **cuando** se crea el servicio, **entonces** el backend reutiliza el cliente activo existente; si no existe, lo crea y lo vincula en la misma transacción; si existe inactivo, responde `409 Conflict`.

### US-008.4 — Avanzar el estado de un servicio según la máquina de estados (Prioridad: P1)
- **Como** administrador,
- **quiero** actualizar el estado de un servicio desde la fila del listado (`PATCH /api/servicios/{id}/estado`) con un diálogo de confirmación,
- **para** reflejar el progreso real del viaje respetando estrictamente la secuencia `pendiente → confirmado → en curso → finalizado → cobrado`.
- **Criterios de Aceptación**:
  1. **Dado** un servicio en `pendiente`, **cuando** se avanza a `confirmado`, **entonces** responde `200 OK` y actualiza la tabla.
  2. **Dado** un intento de saltar estados (ej. de `pendiente` a `finalizado`) o de cancelar por este endpoint, **entonces** el dominio rechaza la transición con `422 Unprocessable Entity`.

### US-008.5 — Cancelar un servicio registrando motivo y hora de finalización (Prioridad: P1)
- **Como** administrador,
- **quiero** cancelar un servicio (`PATCH /api/servicios/{id}/cancelar`) exigiendo un motivo obligatorio (1 a 255 caracteres),
- **para** dejar trazabilidad del motivo y de la `hora_fin` exacta del servidor sin borrar el registro histórico.
- **Criterios de Aceptación**:
  1. **Dado** un servicio en `pendiente`, `confirmado` o `en curso` y un motivo válido, **cuando** se cancela, **entonces** pasa a `estado = "cancelado"`, guarda `motivo_cancelacion` recortado e inyecta `hora_fin` del servidor (`200 OK`).
  2. **Dado** un servicio ya `finalizado`, `cobrado` o `cancelado`, **cuando** se intenta cancelar, **entonces** responde `409 Conflict` y no altera el registro.

### US-008.6 — Eliminar un servicio con confirmación (Prioridad: P2)
- **Como** administrador,
- **quiero** poder eliminar un servicio cargado por error (`DELETE /api/servicios/{id}`) previa confirmación en un modal,
- **para** limpiar registros erróneos que no tengan dependencias referenciales (`204 No Content`, o `409` si tiene referencias).

### US-008.7 — Administrar altas, ediciones, bajas y tarifas desde la UI (Prioridad: P1)
- **Como** administrador,
- **quiero** crear, editar y dar de baja clientes, choferes y vehículos mediante modales (`DialogoCliente`, `DialogoChofer`, `DialogoVehiculo`, `DialogoConfirmacion`) y editar tarifas por tipo en `PanelTarifas` (`/vehiculos`),
- **para** operar todos los catálogos desde la interfaz web con validación React Hook Form + Zod y revalidación automática de vistas.

### US-008.8 — Operar Dashboard, Agenda mensual, Cotizador comercial, Rendiciones y Modo Oscuro (Prioridad: P2)
- **Como** operador administrativo,
- **quiero** contar con un Dashboard con KPIs en vivo (`/`), una Agenda mensual conectada a los servicios reales (`/agenda`), un Cotizador comercial conectado al backend (`/cotizaciones`), una vista de arqueo de Rendiciones (`/rendiciones`) y un selector de Modo Claro/Oscuro persistente y sin parpadeo (anti-FOUC),
- **para** supervisar toda la logística diaria con comodidad visual tanto de día como en turnos nocturnos.

---

## Módulo 009 — Autenticación y Autorización por Rol (Especificado para siguiente fase)

> **Objetivo del módulo**: Reemplazar el modo demo local (`DEV_ASSUME_ADMIN`) por autenticación real de cuentas `admin` con hash Argon2, JWT firmado en cookie `httpOnly` y guardas en servidor Next.js y FastAPI.

### US-009.1 — Iniciar sesión como administrador (Prioridad: P1)
- **Como** administrador con cuenta activa,
- **quiero** iniciar sesión con mi `username` y contraseña,
- **para** obtener un JWT de acceso válido por 30 minutos sin exponer credenciales.

### US-009.2 — Validar JWT y aplicar permisos en FastAPI (Prioridad: P1)
- **Como** responsable de seguridad del sistema,
- **quiero** que `get_rol_actual` verifique la firma y vigencia del Bearer JWT y consulte en la base si la cuenta sigue activa,
- **para** impedir cualquier acceso mediante headers `X-Rol` falsificados y responder `401`/`403` según corresponda.

### US-009.3 — Mantener y cerrar sesión segura en Next.js (Prioridad: P1)
- **Como** administrador autenticado,
- **quiero** que mi sesión se almacene en una cookie `httpOnly` (`sameSite=lax`), que las rutas protegidas redirijan a `/login` si expira y poder cerrar sesión desde el layout,
- **para** operar de forma segura desde cualquier navegador.
