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
   validan el rol (Administrador/Chofer) vía JWT, y llaman a un único método de un servicio
   de Aplicación. **No contienen reglas de negocio.**
2. **Aplicación** (`app/application/`) — Toda la lógica de negocio real vive acá: el
   validador de agenda, la calculadora de cotización, el gestor de pagos/cuenta corriente y
   el gestor de rendición. Es la capa más sensible a cambios del cliente, por eso:
   - Las reglas que pueden cambiar (sobre todo cotización) se implementan como una
     **estrategia intercambiable** (patrón Strategy), nunca como un `if/else` gigante.
   - Las tarifas (por hora, por km, por tipo de vehículo) se leen de una tabla de
     configuración en la base de datos — **nunca como constante en el código.**
   - El estado de un `Servicio` se maneja como una máquina de estados explícita:
     `pendiente → confirmado → en curso → finalizado → cobrado`.
3. **Dominio** (`app/domain/`) — Entidades y reglas invariantes: `Cliente`, `Chofer`,
   `Vehiculo`/`TipoVehiculo`, `Servicio`, `Pago`, `Rendicion`. Se actualizan siempre a través
   de un servicio de Aplicación, nunca directo desde un controlador.
4. **Infraestructura** (`app/infrastructure/`) — Repositorios: único punto de acceso a
   PostgreSQL para cada entidad. Un cambio de motor de base de datos no debería tocar
   ninguna capa superior.

**Regla de oro:** un cambio en la fórmula de cotización, en el flujo de pagos o en la
política de rendición solo debería tocar archivos dentro de `app/application/`. Si una tarea
te obliga a tocar `app/api/` o `app/domain/` para resolver algo que "debería" ser una regla
de negocio, primero preguntate si no se está mezclando lógica entre capas.

## 3. Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | Next.js 16 (App Router) + React 19 + TypeScript |
| Base de datos | PostgreSQL |
| Migraciones | Alembic |
| Autenticación | JWT, roles `admin` / `chofer` |
| Testing backend | Pytest |
| Testing frontend | Vitest + React Testing Library + Playwright (E2E) |
| Gestión de tareas | Trello (plantilla Scrum) |
| Agente de desarrollo | OpenCode |

## 4. Estructura de carpetas

```
fletes-mudanzas-express/
├── AGENTS.md                     # este archivo
├── .specify/                     # Spec Kit: constitución, templates, scripts y workflow
│   ├── memory/constitution.md    # constitución vigente (fuente de verdad de gobernanza)
│   ├── templates/                # templates de spec / plan / tasks / checklist
│   ├── scripts/powershell/       # scripts del CLI de Spec Kit
│   └── workflows/speckit/         # workflow con los gates de revisión del ciclo
├── specs/                        # Spec Kit: un directorio por historia (layout nativo)
│   ├── 001-gestion-clientes/
│   │   ├── spec.md               # requisitos y criterios de aceptación
│   │   ├── plan.md               # decisión técnica: capas, endpoints, migraciones, tests
│   │   ├── tasks.md              # tareas de implementación
│   │   ├── quickstart.md         # cómo levantar y ejercitar la historia
│   │   ├── checklists/
│   │   │   └── requirements.md   # checklist de calidad de requisitos
│   │   └── feature.json          # mapeo historia ↔ directorio ↔ rama
│   ├── 005-agenda-disponibilidad/
│   └── ...
├── .opencode/                     # config del agente (skills propias del proyecto, si se agregan más adelante)
├── backend/
│   ├── app/
│   │   ├── api/                  # 1. Presentación — routers de FastAPI
│   │   │   ├── clientes.py
│   │   │   ├── servicios.py
│   │   │   ├── agenda.py
│   │   │   ├── cotizaciones.py
│   │   │   ├── pagos.py
│   │   │   └── rendiciones.py
│   │   ├── application/          # 2. Aplicación — reglas de negocio
│   │   │   ├── agenda/
│   │   │   │   └── validador_agenda.py
│   │   │   ├── cotizacion/
│   │   │   │   ├── calculadora.py        # interfaz + selector de estrategia
│   │   │   │   └── estrategias/          # una estrategia por regla de tarifa
│   │   │   ├── pagos/
│   │   │   │   └── gestor_pagos.py
│   │   │   └── rendicion/
│   │   │       └── gestor_rendicion.py
│   │   ├── domain/               # 3. Dominio — entidades
│   │   │   ├── cliente.py
│   │   │   ├── chofer.py
│   │   │   ├── vehiculo.py
│   │   │   ├── servicio.py       # incluye la máquina de estados
│   │   │   ├── pago.py
│   │   │   └── rendicion.py
│   │   ├── infrastructure/       # 4. Infraestructura — repositorios
│   │   │   ├── db/
│   │   │   │   └── session.py
│   │   │   └── repositories/
│   │   │       ├── cliente_repo.py
│   │   │       ├── servicio_repo.py
│   │   │       └── ...
│   │   ├── core/                 # config, seguridad/JWT, dependencias compartidas
│   │   └── main.py
│   ├── alembic/                  # migraciones versionadas
│   ├── tests/
│   │   ├── unit/                 # tests de app/application/ (prioridad de cobertura)
│   │   └── integration/          # tests contra PostgreSQL real
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                  # App Router: rutas, layouts y route groups (admin) y (chofer)
│   │   ├── features/             # vertical slices: una carpeta por historia
│   │   │   └── <feature>/
│   │   │       ├── components/    # componentes de la feature
│   │   │       ├── hooks/        # useServicios, useAgenda, useCotizacion... (fetch acá, nunca en el componente)
│   │   │       ├── schemas/      # Zod schemas de validación de formulario
│   │   │       └── types.ts      # re-export de los tipos generados
│   │   ├── lib/
│   │   │   ├── api/              # cliente HTTP + tipos generados desde el OpenAPI de FastAPI
│   │   │   ├── auth/             # sesión y guards de rol
│   │   │   └── utils/            # helpers puros
│   │   ├── components/ui/        # primitivas de UI reutilizables
│   │   ├── styles/               # tokens de diseño (Tailwind) y estilos globales
│   │   └── types/                # tipos generados desde el OpenAPI de FastAPI
│   ├── tests/
│   └── package.json
├── .github/
│   └── workflows/                # CI: lint + tests en cada PR
└── docker-compose.yml            # backend + frontend + PostgreSQL para desarrollo local
```

## 5. Cómo trabajamos siendo 4 personas en el mismo repo

- **Una rama corta por historia de usuario**, nunca se codea directo sobre `main`. El nombre de la
  rama es **exactamente** el nombre del directorio de su spec: `005-agenda-disponibilidad` ↔
  `specs/005-agenda-disponibilidad/`. Esa correspondencia hace auditable el rastro
  spec → rama → código. (Las ramas históricas `feature/H#-nombre` de H1, H4 y H13 preexisten a
  esta regla y quedan registradas en el `feature.json` de su historia.)
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`.
- **Pull Request obligatorio hacia `main`**, con:
  - Al menos 1 revisión cruzada de otro integrante (nunca autoaprobarse).
  - CI (lint + tests) en verde.
- **`main` siempre desplegable.** Un tag de versión (`v0.1`, `v0.2`, `v1.0-mvp1`) en cada hito
  del Gantt.
- **Antes de tocar una historia**, leer su `spec.md` y su `plan.md` en `/specs/<NNN>-<slug>/`. Si no
  existen todavía, escribirlos primero (ver sección 7) — no arrancar a codear sin especificación.
- **Si el cliente cambia una regla de negocio**, el cambio se hace primero en la spec
  afectada, después en el plan, y recién después en el código. Nunca se parchea el código
  directo sin dejar rastro de por qué cambió.

## 6. Decisiones de negocio todavía no confirmadas por el cliente

Estos puntos están abiertos — no automatizar una regla propia sobre ellos sin dejarlo
registrado en la spec correspondiente como supuesto temporal:

- Fórmula exacta de cotización (se sabe que depende de tiempo, distancia y tipo de vehículo).
- Rol de los ayudantes/peones en el servicio.
- Margen de tiempo entre servicios asignados a un mismo chofer.
- Política de cancelaciones (son frecuentes, pero no hay regla formal).
- Modo exacto de rendición (se controla recaudado/rendido/diferencia, pero el detalle final
  de proceso se está terminando de acordar).

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
`checklists/requirements.md` y `feature.json`. El código es un resultado derivado de la spec, no
al revés.

### Regla de Oro

> Ante **cualquier funcionalidad nueva**, el agente frena y responde:
> **"Primero redactemos el spec.md y el plan.md."**
> No escribe código hasta que el Tech Lead apruebe ambos documentos.

**La constitución vive en `.specify/memory/constitution.md`** y es la fuente de verdad de
gobernanza: los principios transversales y los contratos de backend y frontend. Este AGENTS.md es
la guía de uso en runtime y **no** la sustituye.

## 8. Testing: prioridad

La cobertura de tests no es pareja en todo el proyecto. Prioridad, de mayor a menor:

1. `app/application/` completo (validador de agenda, calculadora de cotización, gestor de
   pagos, gestor de rendición) — tests unitarios, con el repositorio mockeado, sin levantar
   PostgreSQL. Un test por criterio de aceptación de la spec correspondiente.
2. Integración de los endpoints críticos (`/servicios`, `/cotizaciones`) contra PostgreSQL
   real, en `tests/integration/`.
3. Componentes de frontend que muestran datos económicos (cotización, saldos, rendición).

Un caso límite marcado en una spec como "decisión pendiente" se testea con
`pytest.mark.skip(reason="regla no confirmada por el cliente, ver spec")`, nunca inventando
un comportamiento.

## 9. Definition of Done (por historia)

Antes de dar una historia por terminada:

- [ ] Los criterios de aceptación de la spec están cumplidos.
- [ ] Hay tests unitarios de la lógica de negocio afectada, pasando.
- [ ] El PR tiene 1 aprobación de otro integrante + CI en verde.
- [ ] Si algo cambió respecto a lo que decía la spec original, la spec quedó actualizada.
- [ ] El endpoint nuevo (si aplica) aparece documentado en Swagger/OpenAPI.

## 10. Comandos frecuentes

```bash
# Backend
cd backend
uvicorn app.main:app --reload          # levantar el servidor de desarrollo
pytest tests/unit                       # tests de la Capa de Aplicación (correr siempre antes de un PR)
pytest tests/integration                # tests contra PostgreSQL
alembic revision --autogenerate -m ""   # nueva migración
alembic upgrade head                    # aplicar migraciones

# Frontend
cd frontend
npm run dev                             # servidor de desarrollo
npm run test                            # Vitest
npm run lint                            # ESLint + Prettier

# Todo el entorno
docker compose up                       # backend + frontend + PostgreSQL local
```

## 11. Decisiones de diseño adoptadas (DD)

Decisiones de fondo que se tomaron durante el desarrollo y que conviene conocer antes de tocar
el código. Son decisiones de **diseño e implementación**, distintas de las de negocio todavía
abiertas (ver sección 6). Si una historia nueva las contradice, revisarlas acá antes de parchear.

- **DD-1 — Baja lógica con flag `activo`.** Un cliente dado de baja no se borra de la base: la
  fila queda con `activo = False` y desaparece del listado y del detalle. La razón social sigue
  reservada por el `UNIQUE` de `razon_social_key` aunque el cliente esté inactivo (su historial de
  servicios, cotizaciones y rendiciones queda intacto — SC-007). Cuando el cliente confirme la
  política de baja real de esta decisión (#DP-01), se cambia apoyándose en este flag.
- **DD-2 — Dato visual + clave normalizada `razon_social_key`.** La razón social se guarda tal
  como la escribe el usuario (`razon_social`) *y* en una columna normalizada
  (`razon_social_key`: minúsculas, sin acentos, sin espacios sobrantes) que alimenta el `UNIQUE`
  de unicidad (FR-004) y el filtro de búsqueda `q` (FR-008). Así comparar "Distribuidora del Sur"
  con "distribuidora  del sur" da igual sin tocar el texto que se muestra.
- **DD-3 — Permisos consumidos por puerto, no por JWT todavía.** `require_rol` en
  `app/core/dependencias.py` lee el rol del header `X-Rol` como **stub** hasta la historia de
  autenticación. Las rutas declaran `dependencies=[Depends(require_rol("admin"))]` y no tocan el
  rol directamente; cuando llegue el JWT solo se cambia el cuerpo de `get_rol_actual` y ninguna
  ruta se modifica.
- **DD-4 — Un único teléfono, sin formato único.** Se guarda un solo teléfono como texto y solo
  se valida que tenga entre 7 y 20 dígitos (FR-005); el signo `+`, los espacios y los guiones son
  libres. Un teléfono puede repetirse entre clientes (los contactos múltiples quedan para H2).
- **DD-5 — Modificación por `PUT` completo, no `PATCH`.** El body de edición repite los mismos 4
  campos obligatorios que el alta, para que el dominio siempre valide un cliente entero y nunca
  quede un registro a medio modificar por un campo que el cliente olvidó mandar.

**Convenciones de modelo de datos**:

- Las PK son `integer` generadas por identidad (`identity`), expuestas como `id` en la API. No se
  usan UUID.
- Las fechas de auditoría usan `TIMESTAMPTZ` con `server_default now()`; `actualizado_en` suma
  `onupdate`. Ojo: `onupdate` no dispara si el `UPDATE` no ocurre (ver Notas de H1, T047).
- Las decisiones marcadas `[Supuesto temporal]` en la spec se implementan con tests que respetan
  la regla supuesta; si el cliente cambia la decisión, primero se actualiza la spec (§5).
