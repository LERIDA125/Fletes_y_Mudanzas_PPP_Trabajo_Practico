# Fletes y Mudanzas Express — Constitution

> Constitución del proyecto. Es la fuente de verdad de gobernanza: define los principios no
> negociables, los contratos técnicos de backend y frontend, y el proceso de desarrollo.
> Los comandos de Spec Kit (`speckit.specify`, `speckit.plan`, `speckit.tasks`, `speckit.implement`,
> `speckit.analyze`, `speckit.converge`) la cargan y la tratan como **no negociable**.
> `AGENTS.md` es la guía de uso en runtime (comandos, estructura, atajos) y NO sustituye a esta
> constitución: ante un conflicto, manda esta constitución.
>
> Versión del documento: ver *Governance*.

## Core Principles (Principios Transversales)

### I. Spec Before Code (NON-NEGOTIABLE)

Ninguna funcionalidad se escribe en código sin un `spec.md` y un `plan.md` aprobados por el
Tech Lead en la rama de la historia.

- **Debe**: cada historia vive en `specs/<NNN>-<slug>/` con `spec.md` (criterios Dado/Cuando/
  Entonces, *Out of Scope*, escenarios de usuario numerados con prioridad) y `plan.md` (capas,
  archivos, endpoints, migraciones, tests y decisiones de diseño).
- **Debe**: `spec.md` y `plan.md` se redactan **antes** de abrir la implementación. El agente
  DEBE frenar y pedir la redacción de ambos documentos ante cualquier pedido de funcionalidad
  nueva; NO DEBE anticipar el código.
- **Debe**: el `plan.md` declara el **Constitution Check** (§ Contrato Backend / § Contrato
  Frontend) y toda violación se justifica en la tabla *Complexity Tracking*.
- **No debe**: una historia se considera cerrada con criterios de aceptación sin cubrir, sin
  tests que los exertsen, o con el `plan.md` ausente.
- **Excepción**: solo la gobernanza (constitución, plantillas, scripts de Spec Kit, documentación
  de arquitectura) y la corrección de bugs que no cambian comportamiento de negocio pueden
  saltear el gate de spec. Todo cambio de comportamiento de negocio exige spec.

**Rationale**: el cliente puede cambiar reglas de negocio durante el desarrollo. El spec es el
único registro durable de *por qué* el sistema se comporta como se comporta; sin spec, un cambio
de reglas se convierte en arqueología de commits.

### II. Capas y Puertos: la Regla de Oro arquitectónica

El sistema es un **monolito modular en 4 capas** (no microservicios, no eventos). La dirección de
dependencia es estrictamente `api → application → domain`, e `infrastructure` implementa los
puertos que declara `application`.

- **Debe**: toda regla de negocio vive en `app/application/` o `app/domain/`.
- **Debe**: un router de `app/api/` valida rol y payload, y delega en **un único** método de un
  gestor de Aplicación. Un router no contiene reglas de negocio.
- **Debe**: la capa de Aplicación no importa SQLAlchemy, FastAPI ni `requests`; habla con la
  persistencia únicamente a través de `Protocol` (puertos) definidos en `app/application/*/puertos.py`.
- **Debe**: las entidades de Dominio son Python puro — sin SQLAlchemy, sin FastAPI, sin Pydantic.
- **No debe**: un cambio en la fórmula de cotización, en el flujo de pagos o en la política de
  rendición modifique `app/api/` o `app/infrastructure/`. Si lo requiere, la regla está mal
  ubicada: se corrige la ubicación, no se maquilla el archivo.
- **No debe**: el acceso a la base de datos se hace **solo** desde `app/infrastructure/repositories/`.

**Rationale**: el cliente puede cambiar reglas de negocio durante el desarrollo. La arquitectura
existe para que ese cambio impacte lo menos posible (AGENTS.md §2).

### III. Contrato de API como Fuente de Verdad

El contrato entre backend y frontend es el **OpenAPI de FastAPI**. Ninguna de las dos puntas
define el contrato por su cuenta.

- **Debe**: el frontend consume la API de FastAPI directamente. **No** existe un BFF ni un
  proxy de Next.js que duplique la superficie de endpoints.
- **Debe**: los tipos del cliente se **generan** desde el OpenAPI del backend (`openapi-typescript`
  sobre el JSON de `/openapi.json`); no se escriben a mano ni se copian del schema de Python.
- **Debe**: un job de CI regenera los tipos y falla si hay diff. La deriva entre backend y
  frontend se detecta en CI, no en producción.
- **Debe**: los endpoints de escritura usan `PUT` completo cuando el dominio valida una entidad
  entera (DD-5), y `PATCH` solo si el dominio modela explícitamente la actualización parcial.
- **No debe**: el frontend recalcula cifras de negocio (cotizaciones, saldos, rendiciones,
  totales). El backend es la única autoridad; el frontend formatea y muestra.

**Rationale**: con 4 personas y 8 semanas, un contrato duplicado deriva en silencio hasta que un
chofer ve un saldo distinto al real.

### IV. Testing Orientado al Comportamiento

Cada criterio de aceptación de un spec tiene un test que lo ejerce. La prioridad de inversión
de testing es explícita y no uniforme.

1. `app/application/` completo — unitarios, con el repositorio mockeado, sin PostgreSQL. **Máxima
   prioridad**: un test por criterio de aceptación del spec.
2. Endpoints críticos (`/clientes`, `/choferes`, `/vehiculos`, `/cotizaciones`) — integración
   contra PostgreSQL real.
3. Frontend — componentes que muestran datos económicos (cotización, saldos, rendición) y flujos
   críticos de rol.
4. E2E — Playwright sobre los flujos completos de admin y chofer.

- **Debe**: un caso marcado como *"decisión pendiente"* en el spec se testea con
  `pytest.mark.skip(reason="regla no confirmada por el cliente, ver spec")`. **Nunca** se inventa
  un comportamiento para hacer pasar un test.
- **Debe**: el CI corre lint + unitarios en cada PR, e integración contra PostgreSQL en cada PR.
- **No debe**: se comercia cobertura de tests de una capa por cobertura de otra sin autorización
  explícita del Tech Lead.

**Rationale**: la cobertura no es pareja en todo el proyecto y no se pretende que lo sea. Lo que
no se negocia es que **la lógica de negocio esté cubierta**.

### V. Simplicidad y Trazabilidad

- **Debe**: se elige la solución más simple que satisface el spec. YAGNI. Una abstracción se
  justifica por dos o más usos concretos, nunca por anticipación.
- **Debe**: toda decisión de fondo (no un detalle de una sola historia) queda registrada en el
  registro de decisiones de diseño de `AGENTS.md` §11 con su razón.
- **Debe**: el estándar de commits es **Conventional Commits** con el prefijo de historia en el
  cuerpo, p. ej. `feat(H3): agrega endpoint de alta de choferes`.
- **Debe**: una rama corta por historia, un PR a `main` con 1 aprobación cruzada de otro
  integrante y CI en verde. `main` siempre desplegable.
- **Debe**: **el nombre de la rama es exactamente el nombre del directorio del spec**, es decir
  `<NNN>-<slug>` (por ejemplo `007-gestion-cuentas-corrientes` ↔ `specs/007-gestion-cuentas-corrientes/`).
  Esa correspondencia es la que hace auditable el rastro spec → rama → código sin ambigüedad.
  Las ramas históricas `feature/H#-nombre` de H1, H4 y H13 preexisten a esta regla y quedan
  registradas en el `feature.json` de su historia; no se renombran (ya están mergeadas).
- **No debe**: código muerto, abstracciones de un solo uso, ni "dejemos esto preparado para
  cuando haga falta" sin una historia que lo exija.

**Rationale**: el plazo es de 8 semanas y el equipo es de 4 personas. La complejidad no solicitada
es deuda que se paga con tiempo de entrega.

---

## Contrato Backend (Additional Constraints)

### Stack (fijado; cambiarlo es una enmienda de constitución)

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12+ (sintaxis de genéricos PEP 695, p. ej. `class Pagina[T]`) |
| Framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 (declarativo con `Mapped` / `mapped_column`) |
| Base de datos | PostgreSQL 16, driver `psycopg3` |
| Migraciones | Alembic |
| Validación / config | Pydantic v2 + `pydantic-settings` |
| Lint / formato | Ruff (`ruff check`, `ruff format --check`) |
| Testing | Pytest + HTTPX (`TestClient`) |
| Contenedores | Docker + Docker Compose |

### Estructura de capas

```text
app/
├── api/              # 1. Presentación — routers + schemas Pydantic
├── application/      # 2. Aplicación — reglas de negocio, gestores, puertos (Protocol)
├── domain/           # 3. Dominio — entidades e invariantes, Python puro
├── infrastructure/   # 4. Infraestructura — modelos ORM + repositorios + sesión
├── core/             # config, seguridad, dependencias compartidas
└── main.py
```

### Convenciones de dominio y persistencia

- **Debe**: las claves primarias son `integer` con identity, expuestas como `id` en la API. No UUID.
- **Debe**: toda entidad con baja usa el flag `activo` (baja lógica, DD-1). La fila **nunca** se
  borra físicamente: su historial de servicios, cotizaciones y rendiciones queda intacto.
- **Debe**: la razón social y toda clave de unicidad o de búsqueda se persisten **doble**: el
  valor visible tal como lo escribe el usuario y una clave normalizada (`*_key`: minúsculas, sin
  acentos, sin espacios sobrantes) que alimenta el `UNIQUE` y el filtro `q` (DD-2).
- **Debe**: toda migración Alembic es versionada, declara `downgrade()` y se aplica con
  `alembic upgrade head`. En tablas con filas preexistentes, el patrón es
  **agregar nullable → backfill → `NOT NULL`**.
- **Debe**: `actualizado_en` se fuerza explícitamente en el repositorio (`func.now()`). El
  `onupdate` de SQLAlchemy no dispara si el `UPDATE` no altera ningún valor.
- **Debe**: las fechas de auditoría usan `TIMESTAMPTZ` con `server_default now()`.

### Convenciones de API

- **Debe**: el CORS del backend habilita explícitamente el origen del frontend. Hoy apunta a
  `http://localhost:5173`; al integrar el frontend hay que alinearlo con el puerto real de
  desarrollo y con el origen de producción. Es un cambio de contrato, no un detalle de config.
- **Debe**: los listados devuelven el esquema genérico `Pagina[T]` (`items`, `total`, `page`,
  `size`) definido en `app/api/schemas/comun.py`.
- **Debe**: los schemas de escritura usan `extra="forbid"` para que el usuario no pueda mandar
  campos de sistema (`id`, `activo`, `saldo_a_favor`, `creado_en`).
- **Debe**: la traducción de errores a HTTP es **polimórfica y centralizada** en `app/main.py`,
  agrupada por clase base de `app/domain/errores.py`:

  | Error base | HTTP |
  |---|---|
  | `RecursoNoEncontrado` | 404 |
  | `ConflictoOperacion` | 409 |
  | `DatoInvalido` | 422 |
  | `ReglaNegocioError` (base) | 422 |

  Los errores concretos de entidad (`ClienteNoEncontrado`, `PatenteDuplicada`, `ChoferInvalido`,
  …) heredan de una de esas bases y **no** requieren handler propio.
- **Debe**: la autorización se consume por puerto, no leyendo el JWT en los handlers. Hoy
  `require_rol(rol)` lee el header `X-Rol` como stub (DD-3); cuando llegue la autenticación real
  se cambia **solo** el cuerpo de `get_rol_actual` y ninguna ruta se modifica.
- **Debe**: los routers declaran `dependencies=[Depends(require_rol(ROL_ADMIN))]` y el handler no
  inspecciona el rol.

### Reglas de negocio de fondo

- **Debe**: las tarifas (por hora, por km, por tipo de vehículo) se leen de una **tabla de
  configuración en la base de datos**. Nunca como constante en el código.
- **Debe**: las reglas de cotización que el cliente puede cambiar se implementan como
  **estrategia intercambiable** (patrón Strategy) con un selector, nunca como un `if/else` gigante.
- **Debe**: el estado de un `Servicio` es una **máquina de estados explícita**:
  `pendiente → confirmado → en curso → finalizado → cobrado`.
- **Debe**: las reglas de negocio **no confirmadas por el cliente** (fórmula de cotización, rol de
  los ayudantes, margen entre servicios, política de cancelaciones, modo exacto de rendición)
  se dejan registradas como supuesto en el spec y **no se automatizan**. Ver §6 de `AGENTS.md`.

### Dependencias y proyecto

- **Debe**: `backend/app/core/config.py` centraliza la configuración por `pydantic-settings`
  (`Settings`, `get_settings()` cacheado). Ningún módulo lee `os.environ` directamente.
- **Debe**: la inyección de dependencias vive en `backend/app/core/dependencias.py` con providers
  `get_repo_*` / `get_gestor_*`. Los tests de integración los sobreescriben con
  `app.dependency_overrides`.

---

## Contrato Frontend (Development Workflow & Constraints)

> Esta sección es **normativa** desde ya. El frontend todavía **no existe** (greenfield): el
> contrato de abajo es el que va a regir la primera historia de frontend, que DEBE arrancar por
> `spec.md` + `plan.md` de la historia correspondiente, y no por scaffolding directo.

### Stack (fijado; cambiarlo es una enmienda de constitución)

| Capa | Tecnología |
|---|---|
| Framework | **Next.js 15** con App Router (RSC, Server Actions, Route Handlers) |
| UI | React 19 |
| Lenguaje | TypeScript en modo `strict` (sin `any` sin justificación) |
| Estilos | Tailwind CSS v4 con tokens de diseño en `src/styles/tokens.css` |
| Estado servidor | TanStack Query v5 **solo** para interactividad cliente (optimistic updates, polling de agenda) |
| Formularios | React Hook Form + Zod |
| Tipos de API | `openapi-typescript` generado desde el OpenAPI de FastAPI |
| Tests | Vitest + React Testing Library + `@testing-library/user-event`; Playwright para E2E |
| Lint / formato | ESLint (`next/core-web-vitals`) + Prettier |
| Paquete | Gestor de paquetes a definir en el spec de la primera historia (npm o pnpm) |

**Nota de versionado**: Context7 no estuvo disponible al ratificar esta constitución, así que las
versiones mayores fijadas acá (Next.js 15, React 19, Tailwind v4, TanStack Query v5) **deben
verificarse contra la documentación oficial vigente en el momento de implementar**. Si la
verificación revela una versión mayor incompatible con esta sección, la corrección se hace
actualizando esta constitución, no desviándose en la implementación.

### Estructura de carpetas

```text
frontend/src/
├── app/                    # App Router: rutas, layouts, route groups
│   ├── (admin)/            # Rutas de administrador
│   ├── (chofer)/           # Rutas de chofer
│   └── api/                # Route Handlers, SOLO si hacen falta (no es un BFF)
├── features/               # Vertical slices: un módulo de negocio por historia
│   └── <feature>/
│       ├── components/      # Componentes de la feature
│       ├── hooks/          # Hooks de datos (TanStack Query) y de estado local
│       ├── schemas/        # Zod schemas de validación de formulario
│       └── types.ts        # Re-export de los tipos generados
├── lib/
│   ├── api/                # Cliente HTTP + tipos generados desde OpenAPI
│   ├── auth/               # Lectura de sesión, guards de rol
│   └── utils/              # Helpers puros
├── components/ui/          # Primitivas de UI reutilizables
├── styles/                 # Tokens de diseño y estilos globales
└── types/                  # Tipos generados desde el OpenAPI (salida de openapi-typescript)
```

### Reglas de datos y renderizado

- **Debe**: la lectura inicial de datos se hace en **Server Components** con `fetch` a la API de
  FastAPI; las **Server Actions** ejecutan las mutaciones y revalidan la ruta afectada.
- **Debe**: TanStack Query se usa **solo** donde hace falta interactividad en el cliente
  (actualización optimista, polling de disponibilidad, filtros en vivo). No se usa como caché
  global de datos que ya se resolvieron en el servidor.
- **No debe**: un componente cliente hace `fetch` directo a la API. Todo acceso a datos pasa por
  `src/lib/api/` o por un hook de `src/features/*/hooks/`.
- **No debe**: se usa `useEffect` para disparar fetches.
- **No debe**: el frontend duplica validaciones de negocio que el backend ya garantiza. La
  validación con Zod es de **forma y de UX** (feedback inmediato, campos requeridos); la
  **verificación de reglas** (razón social única, chofer activo, saldo) es del backend y se
  traduce a un mensaje de error comprehensible.
- **Debe**: todo fetch de la API propaga el token de sesión y trata `401`/`403` como
  navegación a login o a "sin permisos", nunca como un error genérico.

### Reglas de rol y navegación

- **Debe**: el rol vive en los route groups `(admin)` y `(chofer)`. El **middleware** de Next.js
  resuelve la sesión y redirige; cada layout de grupo revalida el rol en servidor.
- **Debe**: la autorización real la aplica **el backend** (DD-3). El guard del frontend es
  experiencia de usuario, **no** una frontera de seguridad. Nunca se confía en un rol que llegue
  desde el cliente.
- **Debe**: la sesión se guarda en cookie `httpOnly` + `sameSite=lax` + `secure` en producción.

### Reglas de calidad visual y accesibilidad

- **Debe**: el diseño parte de un **brief** y de un plan de tokens (color, tipografía, layout)
  revisado antes de escribir la primera línea de componente. No se arranca por el wireframe.
- **Debe**: se sigue la skill `frontend-design` del registro del proyecto para la dirección
  visual, y se evitan los defaults de plantilla (tarjetas iguales, eyebrows en mayúsculas,
  acentos decorativos, gradientes de relleno).
- **Debe**: **WCAG 2.1 AA** como mínimo — foco visible, contraste suficiente, navegación por
  teclado, `prefers-reduced-motion` respetado.
- **Debe**: **mobile-first**. El chofer opera el sistema desde el celular, en la calle, con una
  mano; el admin puede estar en escritorio.
- **Debe**: idioma `es-AR`, formatos de fecha `dd/mm/aaaa` y moneda **ARS**. Los importes se
  formatean con `Intl.NumberFormat`, nunca con concatenación manual.
- **Debe**: los textos de interfaz usan el vocabulario del dominio y son consistentes de punta a
  punta (el botón dice "Guardar cambios", el toast dice "Cambios guardados").

### Reglas de testing

- **Debe**: los tests de componentes se escriben con **Testing Library** guidándose por el
  comportamiento observable, nunca por la implementación interna.
- **Debe**: hay test para todo componente que muestre **datos económicos** (cotización, saldos,
  rendición) y para todo flujo sensible al **rol**.
- **Debe**: los tests de red se hacen con MSW o un mock del cliente de `src/lib/api/`, nunca
  contra un backend real en unitarios.
- **Debe**: el CI corre `vitest run` y `eslint` en el frontend, en cada PR.
- **No debe**: se testea la appearance de un componente con snapshots gigantes. Se testean
  interacciones y contenido.

### Reglas de integración con el backend

- **Debe**: el frontend **no** recalcula nada de negocio (Principio III). Los totales, saldos y
  cotizaciones llegan calculados desde la API.
- **Debe**: los tipos generados se regeneran con un comando documentado (p. ej.
  `npm run gen:api`) y el resultado se versiona en `src/types/`.
- **Debe**: el CORS del backend se alinea con el origen real del frontend antes de la primera
  historia de frontend.
- **No debe**: el frontend inventa endpoints. Si falta un endpoint, se **agrega al backend con su
  propio spec**, no se emula en el cliente.

---

## Governance

### Precedencia

1. **Esta constitución** — principios no negociables y contratos técnicos.
2. El **spec** de la historia — requisitos y criterios de aceptación de *esa* historia.
3. El **plan** de la historia — decisión técnica de implementación de *esa* historia.
4. **`AGENTS.md`** — guía de uso en runtime, convenciones de equipo, decisiones de diseño (DD).

Ante conflicto entre 1 y 2–4, **manda la constitución** y el conflicto se corrige en el documento
de menor rango. La constitución nunca se "interpreta" para admitir una violación: o se corrige
el código, o se enmienda la constitución de forma explícita.

### Enmiendas

- Una enmienda se propone con el comando `speckit.constitution` (o por escrito), se documenta el
  *qué*, el *por qué* y la *migración* de lo ya implementado.
- **Versionado semver**:
  - **MAJOR** — se elimina o redefine un principio, o se rompe un contrato (stack, estructura,
    contrato de API).
  - **MINOR** — se agrega un principio, o se expande materialmente una sección.
  - **PATCH** — corrección editorial, aclaración o ejemplo sin cambio de obligación.
- Cada enmienda actualiza `Last Amended` y deja la razón en el cuerpo del commit
  (`docs: enmenda constitución a vX.Y.Z (...)`).
- Una enmienda **MAJOR** que rompa un contrato ya implementado **debe** incluir un plan de
  migración de lo existente en el mismo PR.

### Cumplimiento

- `speckit.analyze` y `speckit.converge` tratan los conflictos con esta constitución como
  **CRÍTICOS**. No se diluyen ni se reinterpretan.
- Toda historia nueva **debe** pasar el *Constitution Check* de su `plan.md` antes de la fase de
  implementación, y volver a pasarlo al cierre.
- Toda PR **debe** declarar en su descripción si la historia afecta o no cada principio. Si no
  afecta, se dice explícitamente.
- El Tech Lead es responsable de que el CI detecte violaciones. Un check deshabilitado en CI que
  cubría un principio de esta constitución es una violación de esta constitución.

### Estado de las decisiones abiertas del cliente

Las reglas de negocio **no confirmadas por el cliente** (ver `AGENTS.md` §6) no se codifican.
Cuando el cliente confirme una de ellas, el flujo obligatorio es:

1. Actualizar el spec afectado (dejando registro de por qué cambió).
2. Actualizar el `plan.md` de la historia.
3. Actualizar esta constitución **solo** si el cambio altera un principio o un contrato técnico.
4. Recién entonces, implementar.

**Version**: 1.0.0 | **Ratified**: 2026-10-21 | **Last Amended**: 2026-10-21
