# AGENTS.md — Fletes y Mudanzas Express (MVP 1)

Este archivo es la fuente de verdad **operativa** para cualquier agente de IA (OpenCode, Claude
Code, etc.) y para cualquier integrante del equipo que empiece a codear en este repositorio.
Léelo entero antes de tocar código.

> **Precedencia documental** (ver *Governance* de la constitución):
> 1. **`.specify/memory/constitution.md`** — la constitución: principios no negociables y
>    contratos técnicos de backend y frontend. **Manda sobre todo lo demás.**
> 2. `specs/<NNN>-<slug>/spec.md` — requisitos de esa historia.
> 3. `specs/<NNN>-<slug>/plan.md` — decisión técnica de esa historia.
> 4. **Este AGENTS.md** — guía de uso en runtime, atajos y convenciones de equipo.
>
> Si algo acá contradice lo que pide una historia puntual, gana la spec de esa historia. Si algo
> acá contradice la constitución, gana la constitución y hay que corregir este archivo.

## 1. Qué es este proyecto

Sistema de gestión para **Fletes y Mudanzas Express**, una empresa de transporte urbano y
logística liviana (caso de cátedra). Reemplaza una planilla de Excel por un sistema web
responsive que centraliza clientes, choferes, vehículos, servicios, agenda, cotizaciones,
pagos, cuentas corrientes y rendiciones.

Trabajo Integrador de Prácticas Pre-Profesionales 1 (2026) — Licenciatura en Sistemas, UNLa.
Equipo de **4 personas**, plazo de **8 semanas**, 4 sprints de 2 semanas (ver Gantt del
proyecto). El cliente puede cambiar reglas de negocio durante el desarrollo: la arquitectura
existe para que ese cambio impacte lo menos posible.

## 2. Arquitectura: monolito modular en capas

**No usamos microservicios ni arquitectura orientada a eventos.** Es un único desplegable
dividido en 4 capas, de la más externa a la más interna:

1. **Presentación** (`app/api/`) — Controladores/routers de FastAPI. Reciben el request,
   validan el rol (Administrador/Chofer) vía puerto de autorización, y llaman a un único método
   de un servicio de Aplicación. **No contienen reglas de negocio.**
2. **Aplicación** (`app/application/`) — Toda la lógica de negocio real vive acá: los gestores
   de clientes, choferes, vehículos y servicios (incluyendo disponibilidad informativa y ciclo de
   vida), la calculadora de cotización, el gestor de pagos/cuenta corriente y el gestor de
   rendición. Es la capa más sensible a cambios del cliente, por eso:
   - Las reglas que pueden cambiar (sobre todo cotización) se implementan como una
     **estrategia intercambiable** (patrón Strategy), nunca como un `if/else` gigante.
   - Las tarifas (por hora base, por km excedente, por tipo de vehículo) se leen de la tabla
     `tipos_vehiculo` en la base de datos — **nunca como constante en el código.**
   - El estado de un `Servicio` se maneja como una máquina de estados explícita:
     `pendiente → confirmado → en curso → finalizado → cobrado`, más la operación dedicada de
     cancelación (`cancelado` con motivo obligatorio y `hora_fin` del servidor).
3. **Dominio** (`app/domain/`) — Entidades y reglas invariantes: `Cliente`, `Chofer`,
   `Vehiculo`/`TipoVehiculo`, `Servicio`, `Pago`, `Rendicion`. Se actualizan siempre a través
   de un servicio de Aplicación, nunca directo desde un controlador.
4. **Infraestructura** (`app/infrastructure/`) — Modelos ORM y Repositorios: único punto de
   acceso a PostgreSQL para cada entidad. Un cambio de motor de base de datos no debería tocar
   ninguna capa superior.

**Regla de oro:** un cambio en la fórmula de cotización, en el flujo de pagos o en la
política de rendición solo debería tocar archivos dentro de `app/application/`. Si una tarea
te obliga a tocar `app/api/` o `app/domain/` para resolver algo que "debería" ser una regla
de negocio, primero preguntate si no se está mezclando lógica entre capas.

## 3. Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python 3.12+) + SQLAlchemy 2.0 + Pydantic v2 |
| Frontend | Next.js 16 (App Router, Turbopack) + React 19 + TypeScript + Tailwind CSS v4 |
| Formularios y Validación | React Hook Form + Zod v4 + Server Actions |
| Base de datos | PostgreSQL 16 |
| Migraciones | Alembic (`0001` a `0005`) |
| Autenticación | Puerto `require_rol` (`admin` / `chofer`); JWT previsto en historia `009` |
| Testing backend | Pytest (44 tests unitarios en `tests/unit` + suite de integración en `tests/integration`) |
| Testing frontend | Vitest + React Testing Library (80 tests en 12 suites) |
| Gestión de tareas | Trello (plantilla Scrum) |
| Agente de desarrollo | OpenCode |

## 4. Estructura de carpetas

```
fletes-mudanzas-express/
├── AGENTS.md                     # este archivo (guía operativa de agentes y equipo)
├── .specify/                     # Spec Kit: constitución, templates, scripts y workflow
│   ├── memory/constitution.md    # constitución vigente v2.0.0 (fuente de verdad de gobernanza)
│   ├── templates/                # templates de spec / plan / tasks / checklist
│   ├── scripts/powershell/       # scripts del CLI de Spec Kit
│   └── workflows/speckit/        # workflow con los gates de revisión del ciclo
├── specs/                        # Spec Kit: un directorio por historia (layout nativo)
│   ├── 001-gestion-clientes/             # H1: ABM de clientes y normalización
│   ├── 002-migracion-datos-historicos/   # H13: Script ETL desde planilla histórica
│   ├── 003-gestion-vehiculos/            # H4: ABM de flota y tipos de vehículo con tarifas
│   ├── 004-gestion-choferes/             # H3: ABM de choferes y saldo cuenta corriente
│   ├── 005-frontend-scaffolding-clientes/# Base Next.js 16 y vertical slice de clientes
│   ├── 006-frontend-listado-choferes/    # Vertical slice de choferes
│   ├── 007-frontend-listado-vehiculos/   # Vertical slice de vehículos y enriquecimiento API
│   ├── 008-frontend-gestion-servicios/   # Servicios, cotizador, agenda, dashboard, modo oscuro y SSD
│   │   ├── spec.md               # requisitos, enmiendas y criterios de aceptación
│   │   ├── plan.md               # decisión técnica por capas y contratos
│   │   ├── tasks.md              # desglose de tareas completadas (Fases 1 a 7)
│   │   ├── ssd.md                # Diagramas de Secuencia del Sistema (Mermaid) y trazabilidad
│   │   ├── quickstart.md         # cómo levantar y ejercitar todo el sistema
│   │   └── feature.json          # mapeo historia ↔ directorio ↔ rama
│   └── 009-autenticacion-roles/          # Especificación de login y JWT por rol
├── backend/
│   ├── app/
│   │   ├── api/                  # 1. Presentación — routers y schemas Pydantic de FastAPI
│   │   │   ├── clientes.py
│   │   │   ├── choferes.py
│   │   │   ├── vehiculos.py      # incluye /api/vehiculos y /api/tipos-vehiculo
│   │   │   ├── servicios.py      # incluye /cotizar, /disponibilidad, /{id}/estado, /{id}/cancelar
│   │   │   └── schemas/          # contratos de entrada/salida (extra="forbid" en mutaciones)
│   │   ├── application/          # 2. Aplicación — reglas de negocio y puertos (Protocols)
│   │   │   ├── clientes/
│   │   │   ├── choferes/
│   │   │   ├── vehiculos/
│   │   │   ├── cotizacion/
│   │   │   │   ├── calculadora.py             # interfaz + selector de estrategia
│   │   │   │   └── estrategias/
│   │   │   │       └── por_hora_y_km.py       # tarifa_hora * horas + tarifa_km * max(0, km*2 - 10)
│   │   │   └── servicios/
│   │   │       ├── gestor_servicios.py        # cotizar, crear, listar, disponibilidad, estados, cancelar, eliminar
│   │   │       └── puertos.py
│   │   ├── domain/               # 3. Dominio — entidades e invariantes puras
│   │   │   ├── cliente.py
│   │   │   ├── chofer.py
│   │   │   ├── vehiculo.py
│   │   │   ├── servicio.py       # incluye la máquina de estados y reglas de cancelación
│   │   │   └── errores.py        # jerarquía de excepciones de dominio
│   │   ├── infrastructure/       # 4. Infraestructura — modelos SQLAlchemy y repositorios
│   │   │   ├── db/
│   │   │   │   └── session.py
│   │   │   ├── models/           # ClienteORM, ChoferORM, VehiculoORM, TipoVehiculoORM, ServicioORM
│   │   │   └── repositories/     # cliente_repo, chofer_repo, vehiculo_repo, servicio_repo
│   │   ├── core/                 # config, seguridad/roles, dependencias inyectadas
│   │   └── main.py
│   ├── scripts/
│   │   ├── exportar_openapi.py   # exporta el contrato OpenAPI sin levantar servidor
│   │   ├── seed.py               # carga inicial de clientes, choferes, tipos, flota y servicios
│   │   └── migracion/            # importador de datos históricos (H13)
│   ├── alembic/                  # migraciones versionadas (0001 a 0005)
│   ├── tests/
│   │   ├── unit/                 # tests de aplicación, dominio e infraestructura con fakes
│   │   └── integration/          # tests de API contra PostgreSQL real
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                  # App Router: layout con anti-FOUC y grupo (admin)
│   │   │   └── (admin)/          # Dashboard (/), /agenda, /servicios, /cotizaciones, /clientes, /choferes, /vehiculos, /rendiciones
│   │   ├── features/             # vertical slices por dominio
│   │   │   └── <feature>/
│   │   │       ├── actions.ts    # Server Actions (mutaciones y revalidatePath)
│   │   │       ├── components/   # tablas, filas con menús de acción, diálogos RHF+Zod, buscadores
│   │   │       ├── schemas/      # Zod schemas de validación de formulario
│   │   │       └── types.ts      # re-export de los tipos generados desde OpenAPI
│   │   ├── lib/
│   │   │   ├── api/              # cliente HTTP con fallback de red + módulos clientes, choferes, vehiculos, servicios
│   │   │   ├── hooks/            # hooks de UI (ej. use-menu-desplegable)
│   │   │   └── utils/            # helpers puros (formato ARS, fechas, cn)
│   │   ├── components/ui/        # primitivas reutilizables (dialogo-confirmacion, card, badge, button, table, avatar)
│   │   ├── styles/               # tokens de diseño (modo claro y oscuro)
│   │   └── types/                # openapi.d.ts generado automáticamente con npm run gen:api
│   ├── tests/                    # 12 suites de Vitest + React Testing Library
│   └── package.json
├── .github/
│   └── workflows/ci.yml          # CI: lint-and-unit-tests, integration-tests, frontend y docker-compose
└── docker-compose.yml            # PostgreSQL 16 + Backend (con migración automática) + Frontend
```

## 5. Cómo trabajamos siendo 4 personas en el mismo repo

- **Una rama corta por historia de usuario**, nunca se codea directo sobre `main`. El nombre de la
  rama es **exactamente** el nombre del directorio de su spec: `008-frontend-gestion-servicios` ↔
  `specs/008-frontend-gestion-servicios/`. Esa correspondencia hace auditable el rastro
  spec → rama → código. (Las ramas históricas `feature/H#-nombre` y `feature/frontend-integracion-ui`
  quedan registradas en el historial de PRs hacia `main`.)
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `ci:`, `chore:`.
- **Pull Request obligatorio hacia `main`**, con:
  - Al menos 1 revisión cruzada de otro integrante (nunca autoaprobarse).
  - CI (`lint-and-unit-tests`, `integration-tests`, `frontend`, `docker-compose`) en verde.
- **`main` siempre desplegable.** Un tag de versión (`v0.1`, `v0.2`, `v1.0-mvp1`) en cada hito
  del Gantt.
- **Antes de tocar una historia**, leer su `spec.md` y su `plan.md` en `/specs/<NNN>-<slug>/`. Si no
  existen todavía, escribirlos primero (ver sección 7) — no arrancar a codear sin especificación.
- **Si el cliente cambia una regla de negocio**, el cambio se hace primero en la spec
  afectada, después en el plan, y recién después en el código. Nunca se parchea el código
  directo sin dejar rastro de por qué cambió.

## 6. Decisiones de negocio pendientes o con supuesto temporal activo

Estos puntos dependen de confirmación final del cliente — donde se implementó comportamiento para
el MVP, quedó documentado como `[Supuesto temporal]` en la spec respectiva:

- **Fórmula de cotización (implementada en `PorHoraYKm` como supuesto aprobado para MVP)**:
  `distancia_total_km = distancia_ida_km * 2`, franquicia fija de `10 km`,
  `km_excedente = max(0, distancia_total_km - 10)` y
  `precio_final = tarifa_hora_base * horas_estimadas + tarifa_km_excedente * km_excedente`
  redondeado a 2 decimales (`ROUND_HALF_UP`).
- **Rol de los ayudantes/peones en el servicio**: todavía fuera del cálculo automático de tarifa.
- **Disponibilidad y margen entre servicios (`[Supuesto temporal]` en H8)**: `GET /api/servicios/disponibilidad`
  compara ventanas `[hora_inicio, hora_inicio + horas_estimadas)` contra servicios no cancelados
  del mismo día (sin margen extra entre viajes; si un servicio del día no tiene `hora_inicio`,
  ocupa la jornada completa). La disponibilidad es **informativa** en la UI y el alta no bloquea
  solapamientos hasta que el cliente confirme la política definitiva de agenda.
- **Política de cancelaciones (implementada en migración `0005`)**: se permite cancelar desde
  `pendiente`, `confirmado` o `en curso` exigiendo `motivo` obligatorio (1–255 caracteres) y
  registrando automáticamente `hora_fin` del servidor. No se permite cancelar servicios `finalizado`,
  `cobrado` ni ya `cancelado` (`409 Conflict`).
- **Modo exacto de rendición y pagos**: la vista `/rendiciones` está maquetada en el frontend como
  prototipo interactivo; la persistencia y reglas finales de liquidación/pagos se implementarán
  en su historia de backend correspondiente.

## 7. Spec-Driven Development (Spec Kit)

Antes de escribir código para una historia:

```
speckit.constitution   # amendá la constitución si la historia la pone en riesgo (raro)
speckit.specify        # especificar la historia puntual (criterios "dado/cuando/entonces")
speckit.plan           # qué capas, entidades y endpoints toca
speckit.tasks          # descomponer en tareas chicas
speckit.implement      # recién acá se escribe código y tests
```

Los comandos de Spec Kit viven en `.opencode/commands/speckit.*.md` y se invocan con el separador
`.` (no `/`). El ciclo completo, con sus gates de revisión, está declarado en
`.specify/workflows/speckit/workflow.yml`.

Cada historia vive en `/specs/<NNN>-<slug>/` con `spec.md`, `plan.md`, `tasks.md`, `quickstart.md`,
`ssd.md` (cuando incluye diagramas de secuencia del sistema), `checklists/requirements.md` y
`feature.json`. El código es un resultado derivado de la spec, no al revés.

### Regla de Oro

> Ante **cualquier funcionalidad nueva**, el agente frena y responde:
> **"Primero redactemos el spec.md y el plan.md."**
> No escribe código hasta que el Tech Lead apruebe ambos documentos.

**La constitución vive en `.specify/memory/constitution.md`** y es la fuente de verdad de
gobernanza: los principios transversales y los contratos de backend y frontend. Este AGENTS.md es
la guía de uso en runtime y **no** la sustituye.

## 8. Testing: prioridad

La cobertura de tests no es pareja en todo el proyecto. Prioridad, de mayor a menor:

1. `app/application/` completo (gestores de clientes, choferes, vehículos y servicios, calculadora
   de cotización) — tests unitarios en `backend/tests/unit/`, con los repositorios mockeados/fakes,
   sin levantar PostgreSQL. Un test por criterio de aceptación de la spec correspondiente.
2. Integración de los endpoints (`/api/clientes`, `/api/choferes`, `/api/vehiculos`,
   `/api/tipos-vehiculo`, `/api/servicios`) contra PostgreSQL real, en `backend/tests/integration/`.
3. Componentes y flujos críticos de frontend en `frontend/tests/` (Vitest + RTL): cotización en dos
   pasos, alta con cliente existente y cliente nuevo, cambio de estado y cancelación con motivo,
   edición y baja con diálogo de confirmación en clientes, choferes y vehículos, buscadores con
   debounce y paginación.

Un caso límite marcado en una spec como "decisión pendiente" se testea con
`pytest.mark.skip(reason="regla no confirmada por el cliente, ver spec")`, nunca inventando
un comportamiento.

## 9. Definition of Done (por historia)

Antes de dar una historia por terminada:

- [ ] Los criterios de aceptación de la spec están cumplidos.
- [ ] Hay tests unitarios de la lógica de negocio afectada, pasando (`pytest tests/unit` y `npm run verificar`).
- [ ] El contrato OpenAPI está sincronizado (`npm run gen:api` sin diff).
- [ ] El PR tiene 1 aprobación de otro integrante + los 4 jobs de CI en verde.
- [ ] Si algo cambió respecto a lo que decía la spec original, la spec, el plan y el SSD quedaron actualizados.
- [ ] El endpoint nuevo (si aplica) aparece documentado en Swagger/OpenAPI.

## 10. Comandos frecuentes

```bash
# Todo el entorno con Docker (aplica migraciones automáticamente al iniciar el backend)
docker compose up --build               # PostgreSQL (5432) + Backend (8000) + Frontend (3000)

# Backend (desarrollo local)
cd backend
uvicorn app.main:app --reload          # levantar el servidor de desarrollo en :8000
pytest tests/unit                       # 44 tests unitarios (correr siempre antes de un PR)
pytest tests/integration                # tests de integración contra PostgreSQL
ruff check .                            # linter de Python
alembic upgrade head                    # aplicar todas las migraciones, incluida RBAC
python -m scripts.crear_admin           # aprovisionar el primer ADMIN de forma interactiva
python -m scripts.seed                  # poblar base local con clientes, flota, tarifas y servicios

# Frontend (desarrollo local)
cd frontend
npm run dev                             # servidor de desarrollo en :3000
npm run verificar                       # corre lint + format:check + typecheck + vitest (80 tests)
npm run format                          # formatea todo el código con Prettier
npm run gen:api                         # exporta OpenAPI del backend y regenera src/types/openapi.d.ts
npm run build                           # build de producción con Next.js 16 Turbopack
```

## 11. Decisiones de diseño adoptadas (DD)

Decisiones de fondo que se tomaron durante el desarrollo y que conviene conocer antes de tocar
el código. Son decisiones de **diseño e implementación**, distintas de las de negocio todavía
abiertas (ver sección 6). Si una historia nueva las contradice, revisarlas acá antes de parchear.

- **DD-1 — Baja lógica con flag `activo` y protección referencial (`409`).** Clientes, choferes,
  vehículos y tipos de vehículo dados de baja no se borran físicamente: la fila queda con
  `activo = False` y desaparece de los listados activos. Si la entidad ya tiene servicios o
  vehículos asociados, el backend rechaza la baja con `409 Conflict` y el frontend lo explica en
  el diálogo de confirmación sin cerrar el modal silenciosamente.
- **DD-2 — Dato visual + clave normalizada (`*_key`).** Tanto `razon_social` en clientes como
  `descripcion` en tipos de vehículo se guardan tal como los escribe el usuario *y* en una columna
  normalizada (`razon_social_key`, `descripcion_key`: minúsculas, sin acentos, sin espacios
  sobrantes) que alimenta el `UNIQUE` de unicidad y los filtros de búsqueda. En vehículos, la
  patente se normaliza en `patente_norm` (alfanumérica en mayúsculas sin espacios ni guiones).
- **DD-3 — Permisos por puerto + modo demo local explícito.** `require_rol` en
  `app/core/dependencias.py` desacopla las rutas del mecanismo de autenticación. Para la demo del
  MVP sin pantalla de login (hasta la historia `009`), el backend asume rol `admin` **únicamente**
  cuando `ENVIRONMENT=dev` y `DEV_ASSUME_ADMIN=true` están activos en el servidor; fuera de `dev`
  falla cerrado con `401`. El frontend nunca envía headers `X-Rol` hardcodeados.
- **DD-4 — Un único teléfono, validado por cantidad de dígitos.** En clientes y choferes se guarda
  un solo teléfono como texto validando que contenga entre 7 y 20 dígitos; el signo `+`, los
  espacios y los guiones son libres.
- **DD-5 — Modificación de catálogos por `PUT` completo.** Los endpoints `PUT /api/clientes/{id}`,
  `PUT /api/choferes/{id}`, `PUT /api/vehiculos/{id}` y `PUT /api/tipos-vehiculo/{id}` reciben la
  entidad completa para que el dominio valide todas sus invariantes en bloque.
- **DD-6 — Cotización no persistida y snapshot tarifario inmutable en `Servicio`.**
  `POST /api/servicios/cotizar` realiza un cálculo puro sin persistir en base. Al confirmar el
  alta (`POST /api/servicios`), el backend ignora cualquier precio del cliente (`extra="forbid"`),
  recalcula con las tarifas vigentes de `tipos_vehiculo` y persiste un snapshot inmutable
  (`tarifa_hora_aplicada`, `tarifa_km_aplicada`, `km_franquicia_aplicados`, `distancia_total_km`,
  `km_excedente`, `precio_total`). Así, cambios futuros de tarifas en `/vehiculos` no alteran
  servicios históricos.
- **DD-7 — Máquina de estados estricta + Cancelación como operación de negocio separada.**
  `PATCH /api/servicios/{id}/estado` solo permite avanzar al estado inmediato siguiente de la
  secuencia `pendiente → confirmado → en curso → finalizado → cobrado`. Cancelar no es un simple
  cambio de etiqueta: se invoca por `PATCH /api/servicios/{id}/cancelar` con `motivo` obligatorio,
  solo desde `pendiente`, `confirmado` o `en curso`, e inyecta `hora_fin` desde el reloj del
  servidor, respaldado por un constraint `CHECK` en PostgreSQL (migración `0005`).
- **DD-8 — Alta de servicio con cliente existente o nuevo en un solo paso.** `POST /api/servicios`
  acepta exactamente uno de `id_cliente` o `nuevo_cliente`. Cuando recibe `nuevo_cliente`, el
  gestor normaliza la razón social: si ya existe un cliente activo equivalente lo reutiliza, si
  está inactivo responde `409`, y si no existe lo crea y vincula en la misma transacción.
- **DD-9 — Cliente HTTP resiliente en SSR y modo oscuro sin FOUC.** En el frontend,
  `src/lib/api/http.ts` resuelve `API_URL` en el servidor con fallback automático entre
  `http://backend:8000` (red Docker) y `http://localhost:8000` (ejecución local) ante errores de
  conexión, usando `cache: "no-store"` y evitando reintentar `POST` tras timeout para no duplicar
  altas. El tema visual claro/oscuro se inicializa con un script inline en `<head>` y se sincroniza
  en React 19 mediante `useSyncExternalStore`.

**Convenciones de modelo de datos**:

- Las PK son `integer` generadas por identidad (`identity`), expuestas como `id` en la API. No se
  usan UUID.
- Los importes monetarios y tarifas se almacenan en `Numeric(12, 2)` y se operan en Python
  exclusivamente con `Decimal` y redondeo `ROUND_HALF_UP`.
- Las fechas de auditoría usan `TIMESTAMPTZ` con `server_default now()`; `actualizado_en` suma
  `onupdate`. Ojo: `onupdate` no dispara si el `UPDATE` no ocurre (ver Notas de H1, T047).
- Las decisiones marcadas `[Supuesto temporal]` en la spec se implementan con tests que respetan
  la regla supuesta; si el cliente cambia la decisión, primero se actualiza la spec (§5).
