# Implementation Plan: 011 — Motor de Cotizaciones: Precio Sugerido vs Precio Acordado

**Feature Branch**: `011-cotizacion-precio-sugerido-vs-acordado`

**Spec**: [spec.md](./spec.md)

**Status**: Draft — pendiente de aprobación del Tech Lead. No se implementa hasta el OK sobre
`spec.md` + `plan.md` (Constitución, Principio I).

**Última actualización**: 2026-10-30

---

## 1. Resumen técnico

Se reemplaza la estrategia `PorHoraYKm` (distancia duplicada + franquicia de 10 km) por una
estrategia con modificadores y se formaliza el par `precio_sugerido` / `precio_acordado`.

- **Cálculo**: nuevo caso de uso de Aplicación que cotiza directamente por `id_tipo_vehiculo`
  activo, obtiene la configuración de modificadores y ejecuta una estrategia intercambiable. La fórmula
  vive **solo** en `app/application/`; el router solo valida y delega.
- **Persistencia**: `configuracion_cotizacion` (singleton) guarda importes fijos y porcentajes;
  `servicios` guarda el snapshot del sugerido y el acordado ingresado por el operador.
- **Contrato**: se agrega `POST /api/cotizaciones/calcular` y se retira
  `POST /api/servicios/cotizar`; `POST /api/servicios` pasa a exigir `precio_acordado`.
- **Frontend**: panel de cotización reutilizable, reactivo por eventos con debounce, con
  autocompletado del acordado que respeta la edición manual.

---

## 2. Constitution Check

> Constitución vigente: v2.0.0 (`.specify/memory/constitution.md`). Toda violación debe justificarse
> en *Complexity Tracking*. Este plan **no** implementa antes de la aprobación.

| Principio / regla | Estado | Evidencia / decisión |
|---|---|---|
| **I. Spec Before Code** (NON-NEGOTIABLE) | ✅ Cumple | `spec.md` y `plan.md` redactados antes de tocar código; el plan queda en Draft hasta el OK del Tech Lead. |
| **II. Capas y Puertos** — reglas de negocio solo en Aplicación/Dominio | ✅ Cumple | La fórmula y los modificadores viven en `app/application/cotizacion/` y `app/domain/cotizacion.py`. El router no calcula. |
| **II** — Aplicación no importa SQLAlchemy/FastAPI | ✅ Cumple | Tarifas y configuración se leen por `Protocol` en `app/application/cotizacion/puertos.py`. |
| **II** — Dominio en Python puro | ✅ Cumple | `ConfiguracionCotizacion` y `CotizacionCalculada` son dataclasses sin ORM/Pydantic. |
| **II** — Un cambio de fórmula no debe tocar `api/` ni `infrastructure/` | ⚠️ Justificado | La **fórmula** no sale de Aplicación. `api/` e `infrastructure/` cambian por **forma del contrato y del dato** (nuevos flags, nueva tabla, renombres), no porque la regla esté mal ubicada. El cálculo sigue siendo reemplazable sin tocar router/repo. Se registra en *Complexity Tracking*. |
| **III. Contrato de API como Fuente de Verdad** | ✅ Cumple | OpenAPI se regenera; el frontend consume los tipos generados. Se elimina la ruta vieja para no tener dos autoridades. |
| **III** — El frontend no recalcula cifras de negocio | ✅ Cumple | La UI solo muestra el desglose que devuelve la API. El `precio_acordado` es un **dato de entrada comercial** del operador, no un cálculo derivado; el backend lo persiste tal cual. |
| **IV. Testing por comportamiento** | ✅ Cumple | Un test unitario por escenario de aceptación en Aplicación; integración del endpoint contra PostgreSQL; RTL para el autocompletado y la edición manual. |
| **IV** — Regla no confirmada no se automatiza | ✅ Cumple | La directiva del Tech Lead confirma la fórmula y el rol de ayudantes. La constitución fue enmendada a v3.0.0 (MAJOR) y `AGENTS.md` actualizado antes de implementar. Ver §11. |
| **V. Simplicidad y Trazabilidad** | ✅ Cumple | No se agregan entidades ni endpoints no pedidos. Se reutiliza el patrón Strategy existente. |
| **V** — Rama `<NNN>-<slug>` | ⚠️ Acción previa | La rama actual es `feature/H7-motor-cotizaciones`. Antes de implementar se crea/renombra a `011-cotizacion-precio-sugerido-vs-acordado`. |
| **Contrato Backend** — tarifas en tabla de configuración | ✅ Cumple | Tarifas en `tipos_vehiculo`; nuevos importes/porcentajes en `configuracion_cotizacion`. Cero constantes de negocio en Python. |
| **Contrato Backend** — Strategy intercambiable | ✅ Cumple | `EstrategiaCotizacion` se mantiene; nueva implementación `EstrategiaPorHoraKmModificadores`. |
| **Contrato Backend** — sin `os.environ` fuera de `config.py` | ✅ Cumple | No se agrega configuración de entorno; la configuración de negocio va a base de datos. |
| **Contrato Backend** — DI en `core/dependencias.py` | ✅ Cumple | Se agregan `get_consulta_configuracion_cotizacion` y `get_cotizador_servicios`; se actualiza `get_gestor_servicios`. |
| **Contrato Frontend** — tipos generados + `npm run gen:api` | ✅ Cumple | Se regenera `src/types/openapi.d.ts`. |
| **Contrato Frontend** — sin endpoints inventados | ✅ Cumple | El endpoint nuevo se agrega al backend en esta historia. |

### Complexity Tracking

| Violación aparente | Por qué no es una regla mal ubicada | Mitigación |
|---|---|---|
| Cambios en `app/api/servicios.py` y `app/api/schemas/servicio.py` | La fórmula no se toca ahí. Cambian los **campos del contrato** (flags, `km_estimados`, `precio_acordado`) y se retira una ruta duplicada. | El router delega en un único método; los tests verifican que no hay aritmética en `api/`. |
| Nueva tabla `configuracion_cotizacion` + repositorio | La configuración de negocio **debe** persistirse, no hardcodearse. El acceso SQL sigue confinado a `infrastructure/`. | La Aplicación solo ve un `Protocol`; los tests unitarios usan un fake. |
| El frontend mantiene un importe editable | El `precio_acordado` es una decisión comercial humana, no un total calculado. Permitir editarlo no viola «no recalcular». | La UI nunca deriva importes: solo formatea y envía el valor tipeado. |

---

## 3. Fórmula canónica

Sea:

- `h` = `horas_estimadas` (≥ 1)
- `k` = `km_estimados` (≥ 0; kilómetros directos, sin duplicación ni franquicia)
- `th` = `tarifa_hora_base` del tipo del vehículo
- `tk` = `tarifa_km_excedente` del tipo del vehículo
- `fa` = `recargo_ayudante` (config)
- `fe` = `recargo_escalera` (config)
- `pz` = `porcentaje_zona_concurrida` (config, 0–100)
- `pu` = `porcentaje_urgencia_mismo_dia` (config, 0–100)

Componentes (todos `Decimal`, ARS, cuantizados a 2 decimales con `ROUND_HALF_UP`):

```
base_horas            = q(th * h)
base_km               = q(tk * k)
subtotal_base         = q(base_horas + base_km)
recargo_ayudante      = q(fa)  si requiere_ayudante, si no 0
recargo_escalera      = q(fe)  si acceso_escalera, si no 0
subtotal_con_fijos    = q(subtotal_base + recargo_ayudante + recargo_escalera)
importe_zona          = q(subtotal_con_fijos * pz / 100)  si zona_concurrida, si no 0
importe_urgencia      = q(subtotal_con_fijos * pu / 100)  si urgencia_mismo_dia, si no 0
total_recargos_pct    = q(importe_zona + importe_urgencia)
precio_sugerido       = q(subtotal_con_fijos + total_recargos_pct)
```

Reglas:

- `q(x)` = `x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- Los porcentajes son **aditivos**: ambos se calculan sobre el mismo `subtotal_con_fijos`; no se
  aplican en cascada.
- `precio_sugerido` es la suma de componentes ya cuantizados, para que el desglose mostrado y el
  total persistido coincidan al centavo.
- Caso de referencia aprobado: `th=3000`, `tk=150`, `h=2`, `k=10`, `fa=500`, `fe=300`,
  `pz=15`, `pu=20` → `7500 + 800 = 8300`; `1245 + 1660 = 2905`; total **11205.00**.

### Estrategia

- `app/application/cotizacion/estrategias/por_hora_km_modificadores.py` implementa la fórmula y
  devuelve un `CotizacionCalculada`.
- El selector en `calculadora.py` elige la estrategia por defecto. No se agregan `if/else` de
  negocio en el router.
- La estrategia anterior `por_hora_y_km.py` se elimina: mantenerla sería una segunda fuente de
  verdad.

---

## 4. Configuración de negocio

### `configuracion_cotizacion` (singleton)

| Columna | Tipo | Default en migración | Notas |
|---|---|---|---|
| `id` | `INTEGER` identity PK | — | Fila única (`id = 1`). |
| `recargo_ayudante` | `NUMERIC(12,2) NOT NULL` | valor aprobado por el Tech Lead | `[Supuesto temporal]` hasta confirmación del cliente. No hardcodear. |
| `recargo_escalera` | `NUMERIC(12,2) NOT NULL` | valor aprobado por el Tech Lead | idem |
| `porcentaje_zona_concurrida` | `NUMERIC(5,2) NOT NULL` | `15.00` | aprobado por la directiva |
| `porcentaje_urgencia_mismo_dia` | `NUMERIC(5,2) NOT NULL` | `20.00` | aprobado por la directiva |
| `creado_en` / `actualizado_en` | `TIMESTAMPTZ NOT NULL DEFAULT now()` | — | patrón de auditoría vigente |

- `CHECK` de no negatividad en importes y de rango `0..100` en porcentajes.
- La migración inserta la fila singleton si no existe; `configuracion_cotizacion_repo` la lee y
  falla con `ConfiguracionCotizacionInvalida` (422) si falta.
- `scripts/seed.py` no duplica la fila; si se agrega, usa `ON CONFLICT DO NOTHING`.

---

## 5. Cambios por capa

### 5.1 Dominio — `app/domain/`

| Archivo | Acción | Detalle |
|---|---|---|
| `domain/configuracion_cotizacion.py` | Crear | `@dataclass(frozen=True) ConfiguracionCotizacion` con validación de no negatividad, porcentajes `0..100` y `Decimal` finitos. |
| `domain/cotizacion.py` | Crear | `@dataclass(frozen=True) CotizacionCalculada`: entradas normalizadas + componentes + flags + recargos + `precio_sugerido`. Valida finitud, no negatividad, horas ≥ 1, km ≥ 0 y coherencia de la suma. |
| `domain/servicio.py` | Modificar | Reemplazar `distancia_ida_km` → `km_estimados` y `precio_total` → `precio_acordado`; agregar `precio_sugerido`, flags y 6 campos de snapshot; `crear(..., cotizacion: CotizacionCalculada, precio_acordado: Decimal)` para evitar una fábrica de 20 parámetros; `_validar` valida importes y consistencia. |
| `domain/errores.py` | Modificar | Agregar `ConfiguracionCotizacionInvalida` colgada de la jerarquía existente (`DatoInvalido`), mapeada a 422. |

Notas de dominio:

- Las columnas heredadas `distancia_total_km`, `km_franquicia`, `km_excedente` se mantienen en la
  entidad y se completan con `km_estimados`, `0`, `0` en altas nuevas.
- `precio_acordado` se valida pero **no** se compara con `precio_sugerido`.
- `Servicio` sigue siendo Python puro.

### 5.2 Aplicación — `app/application/`

| Archivo | Acción | Detalle |
|---|---|---|
| `application/cotizacion/puertos.py` | Modificar | Mantener `ConsultaTipoVehiculoTarifas`; agregar `ConsultaConfiguracionCotizacion` (`obtener() -> ConfiguracionCotizacion | None`). |
| `application/cotizacion/estrategias/por_hora_km_modificadores.py` | Crear | `EstrategiaPorHoraKmModificadores.calcular(...) -> CotizacionCalculada` con la fórmula de §3 y `ROUND_HALF_UP`. |
| `application/cotizacion/estrategias/por_hora_y_km.py` | Eliminar | Reemplazado; no se deja código muerto. |
| `application/cotizacion/calculadora.py` | Modificar | `CalculadoraCotizacion(consulta_tipos, consulta_configuracion, estrategia=None)`; `cotizar(id_tipo_vehiculo, horas_estimadas, km_estimados, flags...)` valida tipo activo y configuración, y devuelve `Cotizacion` (tipo + descripción + `resultado: CotizacionCalculada`). |
| `application/cotizacion/cotizador_servicios.py` | Crear | Caso de uso `CotizadorServicios.cotizar_por_tipo(id_tipo_vehiculo, ...)`: delega en la calculadora; no requiere una unidad de flota. Devuelve `Cotizacion`. |
| `application/servicios/gestor_servicios.py` | Modificar | `crear()` recibe `km_estimados`, flags y `precio_acordado`; calcula el sugerido con la configuración vigente y llama `Servicio.crear(..., cotizacion=resultado, precio_acordado=...)`. Se elimina `cotizar()` de este gestor (lo asume `CotizadorServicios`). |
| `application/servicios/puertos.py` | Sin cambio | `ConsultaVehiculoServicio` y `ConsultaTipoServicio` ya cubren las consultas necesarias. |

Decisión de diseño: `CotizadorServicios` reutiliza los puertos de `servicios` (`obtener_por_id` de
vehículo y tipo) en lugar de crear puertos casi idénticos. Son puertos de Aplicación; no hay
acoplamiento a infraestructura.

### 5.3 Infraestructura — `app/infrastructure/`

| Archivo | Acción | Detalle |
|---|---|---|
| `infrastructure/models/configuracion_cotizacion.py` | Crear | `ConfiguracionCotizacionORM` + constraints. |
| `infrastructure/models/__init__.py` | Modificar | Registrar el modelo para que Alembic lo vea. |
| `infrastructure/models/servicio.py` | Modificar | Renombrar `distancia_ida_km` → `km_estimados`, `precio_total` → `precio_acordado`; agregar `precio_sugerido`, flags y snapshots; actualizar `CHECK` (no negatividad de importes nuevos y rangos de porcentajes). Conservar columnas heredadas. |
| `infrastructure/repositories/configuracion_cotizacion_repo.py` | Crear | `obtener()` con `SELECT` de la fila singleton; devuelve `ConfiguracionCotizacion` o `None`. |
| `infrastructure/repositories/servicio_repo.py` | Modificar | `a_dominio`, `a_orm`, `actualizar` mapean los campos nuevos/renombrados. |
| `infrastructure/repositories/vehiculo_repo.py` / `tipo_vehiculo_repo.py` | Sin cambio | Ya implementan los puertos usados por `CotizadorServicios` y `GestorServicios`. |

### 5.4 Presentación — `app/api/` y `core/`

| Archivo | Acción | Detalle |
|---|---|---|
| `api/cotizaciones.py` | Crear | Router `prefix="/api/cotizaciones"`, `tag="cotizaciones"`, `POST /calcular` con `require_rol(ROL_ADMIN)`. Delega a `CotizadorServicios.cotizar_por_tipo` y mapea a `CotizacionRead`. Sin aritmética. |
| `api/schemas/cotizacion.py` | Crear | `CotizacionRequest` y `CotizacionRead` (ver §6). `extra="forbid"`. |
| `api/schemas/servicio.py` | Modificar | `ServicioCreate` deja de heredar de `CotizacionRequest`; agrega `km_estimados`, flags y `precio_acordado`. `ServicioRead` expone `km_estimados`, `precio_sugerido`, `precio_acordado`, flags y snapshots; conserva `distancia_total_km`, `km_franquicia`, `km_excedente`. |
| `api/servicios.py` | Modificar | Retirar `POST /cotizar` y sus imports; `crear_servicio` pasa los campos nuevos al gestor. |
| `api/schemas/__init__.py` | Modificar (si aplica) | Re-exportar los schemas nuevos. |
| `core/dependencias.py` | Modificar | `get_consulta_configuracion_cotizacion`, `get_cotizador_servicios`; `get_gestor_servicios` recibe configuración y usa la calculadora nueva. |
| `main.py` | Modificar | `include_router(router_cotizaciones)`; registrar el handler de `ConfiguracionCotizacionInvalida` si no cae en el handler genérico de `DatoInvalido`. |

### 5.5 Migración — `backend/alembic/versions/`

`0007_cotizacion_sugerido_vs_acordado.py` (down_revision = revisión de
`0006_crear_usuarios_rbac.py`):

1. Crear `configuracion_cotizacion` con constraints e insertar la fila singleton con los valores
   aprobados.
2. `ALTER TABLE servicios RENAME COLUMN distancia_ida_km TO km_estimados`.
3. `ALTER TABLE servicios RENAME COLUMN precio_total TO precio_acordado`.
4. Agregar `precio_sugerido`, los 4 flags y los 6 campos de snapshot.
5. Backfill:
   - `precio_sugerido = precio_acordado`
   - flags = `false`
   - recargos/porcentajes = `0`
   - `distancia_total_km`, `km_franquicia` y `km_excedente` conservan el valor histórico; solo
     las altas nuevas usan `km_estimados`, `0` y `0`.
6. `SET NOT NULL` en las columnas nuevas que correspondan y recrear los `CHECK` afectados
   (`ck_servicios_importes_no_negativos` incluye `precio_sugerido`).
7. `downgrade()` revierte renombres, columnas nuevas y la tabla.

---

## 6. Contrato exacto (Pydantic)

### `CotizacionRequest` (`api/schemas/cotizacion.py`)

| Campo | Tipo | Reglas |
|---|---|---|
| `id_tipo_vehiculo` | `int` | `gt=0`, obligatorio; la categoría debe estar activa |
| `horas_estimadas` | `Decimal` | `ge=1`, `max_digits=10`, `decimal_places=2`, `allow_inf_nan=False` |
| `km_estimados` | `Decimal` | `ge=0`, `max_digits=10`, `decimal_places=2`, `allow_inf_nan=False` |
| `requiere_ayudante` | `bool` | default `false` |
| `acceso_escalera` | `bool` | default `false` |
| `zona_concurrida` | `bool` | default `false` |
| `urgencia_mismo_dia` | `bool` | default `false` |

`model_config = ConfigDict(extra="forbid")`.

### `CotizacionRead`

Todos los importes como `Decimal`, `moneda: Literal["ARS"] = "ARS"`:

`id_tipo_vehiculo`, `descripcion_tipo_vehiculo`, `horas_estimadas`,
`km_estimados`, `tarifa_hora_base`, `tarifa_km_excedente`, `base_horas`, `base_km`,
`subtotal_base`, `requiere_ayudante`, `recargo_ayudante`, `acceso_escalera`,
`recargo_escalera`, `subtotal_con_fijos`, `zona_concurrida`,
`porcentaje_zona_concurrida`, `importe_recargo_zona_concurrida`, `urgencia_mismo_dia`,
`porcentaje_urgencia_mismo_dia`, `importe_recargo_urgencia_mismo_dia`,
`total_recargos_porcentuales`, `precio_sugerido`.

`de_cotizacion(cotizacion: Cotizacion)` mapea 1:1; sin cálculos.

### `ServicioCreate`

| Campo | Regla |
|---|---|
| `id_cliente` / `nuevo_cliente` | igual que 008 (excluyentes) |
| `id_tipo_vehiculo` | `gt=0` |
| `id_chofer` | opcional, `gt=0` |
| `id_vehiculo` | opcional, `gt=0`; si viene, debe pertenecer al tipo |
| `fecha`, `hora_inicio` | igual que 008 |
| `horas_estimadas` | `ge=1`, `max_digits=10`, `decimal_places=2` |
| `km_estimados` | `ge=0`, `max_digits=10`, `decimal_places=2` |
| `requiere_ayudante`, `acceso_escalera`, `zona_concurrida`, `urgencia_mismo_dia` | `bool = false` |
| `precio_acordado` | `Decimal`, `ge=0`, `max_digits=12`, `decimal_places=2`, `allow_inf_nan=False`, **obligatorio** |

`extra="forbid"`; ningún campo derivado es aceptado.

---

## 7. Frontend

### Archivos

| Archivo | Acción | Detalle |
|---|---|---|
| `features/cotizaciones/schemas/cotizacion.ts` | Crear | Zod: `id_tipo_vehiculo` requerido, horas ≥ 1, km ≥ 0, flags booleanos. Solo forma/UX, sin fórmula. |
| `features/cotizaciones/components/formulario-cotizacion.tsx` | Crear | Panel reutilizable: tipo de vehículo (sin patentes), horas, km, 4 switches, desglose y campo acordado. Es el único lugar con la lógica de autocompletado. |
| `features/cotizaciones/actions.ts` | Crear | Server Action `calcularCotizacion` que llama a `lib/api/cotizaciones.ts`. |
| `lib/api/cotizaciones.ts` | Crear | `POST /api/cotizaciones/calcular` tipado desde OpenAPI. |
| `features/cotizaciones/components/cotizador.tsx` | Modificar | Usar el panel compartido; eliminar el cálculo local y `precio_final`. |
| `features/servicios/components/formulario-servicio.tsx` | Modificar | El selector comercial usa categorías; la unidad opcional se asigna abajo, desde disponibilidad y filtrada por tipo, fecha y hora. Mantener cliente/chofer/fecha y agregar `precio_acordado` al submit. |
| `features/servicios/components/resumen-cotizacion.tsx` | Modificar | Mostrar desglose nuevo (`precio_sugerido`, recargos) en lugar de `precio_final`. |
| `features/servicios/schemas/servicio.ts` | Modificar | `distancia_ida_km` → `km_estimados`; agregar flags y `precio_acordado`. |
| `features/servicios/actions.ts` | Modificar | Quitar `solicitarCotizacion` (migra a `cotizaciones/actions.ts`); el alta envía `precio_acordado`. |
| `lib/api/servicios.ts` | Modificar | Quitar `cotizarServicio`; el alta usa el payload nuevo. |
| `features/servicios/components/fila-servicio.tsx`, `tarjeta-viaje-chofer.tsx` | Modificar | `precio_total` → `precio_acordado`; `distancia_ida_km` → `km_estimados`; mostrar acordado (no sugerido) en listados/portal. |
| `types/openapi.d.ts` | Regenerar | `npm run gen:api`. |

### Flujo reactivo

- Eventos que disparan recálculo: cambio de tipo de vehículo, horas, km o flags.
- Implementación: temporizador en un `ref` compartido del panel; se limpia al cambiar y se
  programa a ~350 ms.
- **Prohibido** `useEffect` para fetch y `fetch` directo en componentes (constitución + patrón del
  repo). El panel usa un handler de evento → Server Action.
- Si faltan datos obligatorios, se cancela el temporizador y se limpia el resultado anterior.
- Mientras calcula: estado `calculando` (deshabilitar el submit no es obligatorio; el alta no
  depende del cálculo).

### Autocompletado del acordado

Estado local del panel:

```
precio_acordado: string
editado_manualmente: boolean  // false al abrir/limpiar
sugerido_actual: Cotizacion | null
```

1. Llega un sugerido:
   - si `editado_manualmente === false` → `precio_acordado = resultado.precio_sugerido`.
   - si `true` → no tocar.
2. `onChange` del input → `editado_manualmente = true` (incluye borrar).
3. Al reiniciar el formulario (nuevo servicio) → `editado_manualmente = false` y limpiar.
4. El submit envía `precio_acordado` actual y `km_estimados`, flags; nunca campos derivados.

### Validación

- `precio_acordado` requerido, ≥ 0, hasta 2 decimales; el input es `type="number"`,
  `step="0.01"`, `min="0"`.
- Los mensajes de error siguen el patrón accesible existente (`aria-invalid`,
  `aria-describedby`).
- Formato ARS con `Intl.NumberFormat("es-AR")`; la UI muestra el desglose con las etiquetas
  acordadas.

---

## 8. Tests

### Unitarios (Aplicación/Dominio) — `backend/tests/unit/`

| Archivo | Cubre |
|---|---|
| `test_h7_cotizacion_dominio.py` | Validación de `ConfiguracionCotizacion` y `CotizacionCalculada` (finitos, rangos, suma coherente). |
| `test_h7_estrategia_cotizacion.py` | Escenarios 1–4 de US1: fórmula, flags, porcentajes aditivos, redondeo `ROUND_HALF_UP`, caso 11205.00, tarifas en cero, km = 0. |
| `test_h7_calculadora.py` | Tipo activo/inactivo, configuración faltante/inválida, selector de estrategia. |
| `test_h7_cotizador_servicios.py` | Tipo inexistente/inactivo, cotización por tipo sin unidad asignada. |
| `test_h7_gestor_crear.py` | Acordado igual/distinto del sugerido, sin acordado/negativo rechazado en dominio, snapshot persistido, `precio_sugerido` recalculado al crear. |
| `test_h7_migracion_contrato.py` (si aplica) | El schema viejo ya no existe; los nombres nuevos están expuestos. |

Los repositorios se reemplazan por fakes; sin PostgreSQL.

### Integración — `backend/tests/integration/api/`

| Archivo | Cubre |
|---|---|
| `test_cotizaciones_api.py` | `POST /api/cotizaciones/calcular`: 200 con desglose por categoría sin unidad asignada, 422 (tipo inactivo, horas/km, campos extra), 403 sin admin, 401 sin credenciales cuando aplica. |
| `test_servicios_api.py` (modificar) | Alta con `precio_acordado` distinto/igual al sugerido; persistencia de ambos vía `SELECT`; 422 sin acordado, negativo, con `precio_sugerido`; renombres en `ServicioRead`; compatibilidad con históricos. |

### Frontend — `frontend/tests/`

| Archivo | Cubre |
|---|---|
| `cotizaciones.test.tsx` (nuevo) | Debounce, desglose, autocompletado, no-sobrescritura tras edición, borrar y reescribir, error de cálculo no bloquea. |
| `servicios.test.tsx` (modificar) | Payload nuevo (`km_estimados`, flags, `precio_acordado`), quita `distancia_ida_km`; sigue probando alta con cliente existente/nuevo y cambio de estado. |
| `portal-chofer.test.tsx` (modificar) | Fixtures con `km_estimados` y `precio_acordado`. |

### Comandos de cierre

```
cd backend
ruff check .
pytest tests/unit
pytest tests/integration
alembic upgrade head
alembic downgrade -1 && alembic upgrade head
cd ../frontend
npm run gen:api
npm run verificar
npm run build
```

---

## 9. Orden de implementación

| Fase | Contenido | Gate |
|---|---|---|
| **0. Gobernanza y rama** | Enmienda de constitución + `AGENTS.md`; crear rama `011-cotizacion-precio-sugerido-vs-acordado`; `feature.json`. | Aprobación del Tech Lead. |
| **1. Datos** | Modelo `configuracion_cotizacion`, cambios en `ServicioORM`, migración `0007`, repo de configuración. | `alembic upgrade/downgrade` OK. |
| **2. Dominio** | `ConfiguracionCotizacion`, `CotizacionCalculada`, refactor de `Servicio`, error nuevo. | Tests de dominio. |
| **3. Aplicación** | Puertos, estrategia nueva, calculadora, `CotizadorServicios`, `GestorServicios.crear`. | Tests unitarios de Aplicación en verde. |
| **4. API** | `schemas/cotizacion.py`, `api/cotizaciones.py`, cambios en `servicio.py`/`servicios.py`, DI, `main.py`. | OpenAPI exportable; integración verde. |
| **5. Frontend** | Schemas, cliente API, Server Action, panel, integración en servicio y cotizador, textos. | `npm run verificar`. |
| **6. Sincronización y cierre** | `npm run gen:api`, `npm run build`, checklist, actualización de `ssd.md`/`quickstart.md` si el equipo los usa. | CI completo + revisión cruzada. |

Cada fase es un commit convencional con prefijo `feat(H7)` / `test(H7)` / `docs(H7)`.

---

## 10. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Doble autoridad de cálculo si `/api/servicios/cotizar` queda vivo | Divergencia de precios | Se elimina en el mismo PR; test de contrato verifica 404. |
| Cambio breaking de `precio_total`/`distancia_ida_km` | Rompe frontend/fixtures | `npm run gen:api` + grep global + tests actualizados en el mismo PR. |
| Importes fijos no confirmados | Demo con valores incorrectos | Configuración editable en DB + `[Supuesto temporal]` + un solo punto de cambio. |
| Redondeo inconsistente entre UI y backend | Diferencias de 1 centavo | La UI no calcula; muestra el desglose de la API. El backend cuantiza cada componente. |
| `precio_acordado` muy grande rompe la columna | 500 en producción | Validación Pydantic `max_digits=12` → 422; test de integración. |
| Autocompletado pisa la edición manual | Pérdida de trabajo del operador | `editado_manualmente` en estado local + tests RTL de regresión. |
| Históricos inconsistentes tras el backfill | Reportes erróneos | Backfill `precio_sugerido = precio_acordado`; conservar columnas heredadas; `downgrade()` probado. |
| Governance: automatizar una regla antes abierta | Violación de Constitución IV/§Estado | Enmienda explícita y migración documentada (§11) antes de codear. |

---

## 11. Gobernanza aplicada

**Estado: resuelto el 2026-10-30 antes de escribir código.**

La directiva del Tech Lead **confirmó** una regla que la constitución v2.0.0 y `AGENTS.md §6`
listaban como no confirmada (fórmula y rol de ayudantes). Además, la historia **rompe el contrato
de API** vigente (retira un endpoint y renombra campos). Se aplicó:

1. **Enmienda de constitución** con `speckit.constitution`, propuesta **v3.0.0 (MAJOR)**:
   - *Qué*: reemplazar la fórmula de cotización vigente por la de §3; incorporar modificadores;
     formalizar `precio_sugerido` vs `precio_acordado`; declarar confirmada la participación de
     ayudantes en el cálculo (los montos siguen como supuesto configurable).
   - *Por qué*: directiva del Tech Lead del 2026-10-30.
   - *Migración*: `0007`, retiro de `POST /api/servicios/cotizar`, actualización del frontend y
     de los tipos OpenAPI en el mismo PR.
2. **`AGENTS.md`**:
   - §2 y §4: actualizar la referencia a `por_hora_y_km.py` → `por_hora_km_modificadores.py`.
   - §6: reemplazar la fórmula y la nota de ayudantes; apuntar a `specs/011-.../spec.md`.
   - §11: reescribir **DD-6** (el alta ya no ignora importes del cliente: acepta
     `precio_acordado` y guarda el sugerido como snapshot) y agregar una DD nueva para
     «Precio sugerido vs acordado» si el equipo prefiere no sobrecargar DD-6.
3. **`feature.json`** de la historia con `status: "tasks"` y la rama corregida.
4. **Rama**: `011-cotizacion-precio-sugerido-vs-acordado` (la anterior
   `feature/H7-motor-cotizaciones` no cumplía la regla `<NNN>-<slug>`).

Los puntos 1–4 quedaron aplicados. Los cambios de código de las fases 2–6 siguen bajo el gate
normal de revisión y CI.

---

## 12. Fuera de este plan

- Persistencia de cotizaciones, versiones, validez o aceptación.
- Aprobaciones o topes de descuento.
- Liquidación/pagos/rendición (H10).
- Autenticación real (se mantiene `require_rol` + modo demo).
- Recalcular servicios históricos con la fórmula nueva.

## 13. Definición de terminado (resumen)

- Criterios de `spec.md` cubiertos con tests unitarios de Aplicación e integración de API.
- `ruff`, `pytest tests/unit`, `pytest tests/integration`, `npm run verificar` y
  `npm run build` en verde.
- `npm run gen:api` sin diff.
- Migración `0007` aplicable y reversible.
- Enmienda de constitución y `AGENTS.md` actualizados en el mismo PR.
- Revisión cruzada de otro integrante y CI completo en verde.
