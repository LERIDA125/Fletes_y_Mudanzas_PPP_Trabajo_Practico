# Implementation Plan: 005 — Frontend Scaffolding y Listado de Clientes

**Branch**: `005-frontend-scaffolding-clientes` | **Date**: 2026-10-21 | **Spec**: [`specs/005-frontend-scaffolding-clientes/spec.md`](./spec.md)

**Input**: Feature specification from `/specs/005-frontend-scaffolding-clientes/spec.md`

**Note**: Este plan se emitió en una única iteración `speckit.specify` + `speckit.plan` por
instrucción explícita del Tech Lead. Los artefactos posteriores del ciclo (`research.md`,
`data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`) **no** se generan todavía: quedan
condicionados a la aprobación de este documento y del spec.

## Summary

Se crea el proyecto frontend (greenfield) y se construye sobre él la primera vista con datos
reales: el listado de clientes que consume el endpoint de lectura ya existente.

El enfoque es **lectura pura, servidor primero**: la página es un Server Component que hace el
`fetch` inicial contra FastAPI, el estado de la vista (búsqueda y página) vive en la URL, y el
único componente cliente necesario es el campo de búsqueda. No hay mutaciones, no hay sesión, no
hay caché de cliente. Se entrega además el pipeline de tipos generados desde el OpenAPI, que es lo
que convierte a backend y frontend en un solo contrato verificable en CI.

Dos hallazgos de esta planificación condicionan el arranque y están detallados en
*Constitution Check* y *Complexity Tracking*: la rama estable de Next.js **ya no es la que fija la
constitución**, y todavía no existe sesión que propagar.

## Technical Context

**Language/Version**: TypeScript en modo `strict`; `any` solo con justificación escrita (FR-006).

**Primary Dependencies**:

| Dependencia | Versión a usar | Estado de verificación |
|---|---|---|
| Next.js (App Router) | `16.x` (fijado en la constitución v2.0.0) | **Verificada 2026-10-21 contra npm**: `next` **16.4.2** es lo que instala npm hoy (16.4 salió 2026-10-06). Resuelto por enmienda MAJOR `v1.0.0 → v2.0.0`. |
| React | `19.x` | Verificada: `react` **19.3.1** en npm. Coincide con la constitución. |
| Tailwind CSS | `4.x` | Verificada: `tailwindcss` **4.3.3** en npm. Coincide con la constitución. |
| ESLint + `next/core-web-vitals` | la que trae el template de Next seleccionado | Verificada: `eslint-config-next` **16.4.2** (se alinea con `next`). El template define la versión de ESLint soportada; queda instalarla sin forzar número. |
| Vitest + Testing Library + `@testing-library/user-event` | última compatible con React 19 | Verificada 2026-10-21 en npm: `vitest` **5.0.5**, `@testing-library/react` **16.3.3**, `@testing-library/user-event` **14.6.8**. |
| `openapi-typescript` | última estable | Verificada: **7.13.0** en npm. |
| Prettier | última estable | Verificada: **3.9.10** en npm. |
| `clsx` (concatenación de clases) | última estable | Verificada: **2.1.1** en npm. Única utilidad adicional: la alternativa `tailwind-merge` se rechaza por YAGNI (no hay variantes de clase que colisionen todavía). |
| TanStack Query v5 | no se instala en esta historia | **Sin verificar** (YAGNI: ningún uso concreto). Se verifica al incorporarlo. |
| Playwright | no se instala en esta historia | Fuera de alcance del spec. |

**Storage**: N/A — el frontend no persiste nada; PostgreSQL y Alembic viven solo en `backend/`.

**Testing**: Vitest + React Testing Library (comportamiento observable). Sin Playwright en esta
historia: el spec lo declara fuera de alcance y no existe todavía un entorno con datos sembrables.

**Target Platform**: web; mobile-first desde 360 px de ancho; navegadores modernos de escritorio
y celular.

**Project Type**: frontend de un monolito modular (no es una aplicación independiente ni un BFF).

**Performance Goals**: pintado inicial de la lista con LCP ≤ 2,5 s en un teléfono de gama media
sobre 4G simulada (umbral "bueno" de Core Web Vitals), verificable con Lighthouse.

**Constraints**: WCAG 2.1 AA (foco visible, contraste ≥ 4,5:1 en texto, teclado completo,
`prefers-reduced-motion`); mobile-first; `es-AR` con fechas `dd/mm/aaaa`; ningún `any` sin
justificar; sin `useEffect` que dispare datos.

**Scale/Scope**: 1 vista y 1 endpoint consumido en esta historia. El sistema completo se proyecta
a ~10 módulos de negocio (AGENTS.md §2). Volumen esperado: cientos de clientes, no millones
(misma estimación que asume la paginación de H1).

## Constitution Check

*GATE: debe pasar antes de la fase de investigación. Se re-evalúa al cierre del diseño.*

| Principio / contrato | Resultado | Evidencia y acción |
|---|---|---|
| **I. Spec Before Code** | **PASS** | `spec.md` y `plan.md` existen y quedan a revisión antes de cualquier línea de código. Ningún archivo fuente fue creado (gate respetado). |
| **II. Capas y Puertos** | **PASS / N/A** | La historia no toca reglas de negocio del backend. El único cambio de `backend/` es el origen CORS, que la constitución exige expresamente y que se declara más abajo. |
| **III. Contrato de API como Fuente de Verdad** | **PASS** | Consumo directo de FastAPI, **sin BFF** y sin Route Handlers de proxy. Tipos generados con `openapi-typescript` desde `/openapi.json` (FR-004). Job de CI que regenera y falla ante diff (FR-005). Sin escrituras, por lo que la regla PUT/PATCH no aplica. |
| **IV. Testing Orientado al Comportamiento** | **PASS** | La prioridad 3 (componentes con datos económicos y flujos de rol) **no aplica**: esta vista no muestra importes y todavía no existe rol autenticado. Se cubre con unitarios de componentes por criterio de aceptación. El CI corre `vitest run` y `eslint` en cada PR. |
| **V. Simplicidad y Trazabilidad** | **PASS** | Rama `005-frontend-scaffolding-clientes` = nombre exacto del directorio del spec. Commits Conventional con prefijo `feat(005)`. Sin TanStack Query ni Playwright porque **no tienen uso concreto** en esta historia: instalarlos sería exactamente el "dejemos esto preparado para cuando haga falta" que prohíbe el Principio V. |
| **Contrato Backend — CORS** | **PASS** | `app/main.py` apunta hoy a `http://localhost:5173` (puerto de Vite, no existe en este proyecto). Se alinea a `http://localhost:3000` + origen de producción. La constitución califica esto de "cambio de contrato, no un detalle de config", por eso se declara acá. |
| **Contrato Frontend — Stack** | **PASS** | Resultado de la re-evaluación tras la aprobación del Tech Lead: la violación detectada en la planificación (Next.js 15 en la constitución vs rama estable 16.x) **queda resuelta por la enmienda MAJOR `v1.0.0 → v2.0.0`** del 2026-10-21, aplicada en `.specify/memory/constitution.md` antes de escribir código. El contrato ahora fija Next.js 16 y npm. React 19 y Tailwind v4 coincidían y no cambiaron. Ver *Complexity Tracking* para el detalle y *Registro de enmiendas* en la constitución. |
| **Contrato Frontend — datos y renderizado** | **PASS** | Lectura inicial en Server Component con `fetch` a FastAPI. Sin mutaciones → sin Server Actions. Sin `fetch` en componentes cliente. Sin `useEffect` que dispare datos (el debounce vive en `onChange`, ver *Manejo de estado*). Sin validaciones de negocio duplicadas: Zod no se usa porque no hay formulario. |
| **Contrato Frontend — rol y sesión** | **FAIL** | Exige propagar el token de sesión en todo fetch y resolver la sesión en el middleware. **No existe sesión**: DD-3 resuelve el rol por un stub de cabecera y el endpoint de lectura no exige rol. Fabricar un token placeholder sería código muerto (Prohibido por el Principio V). **Acción requerida**: justificación en *Complexity Tracking* + deficiencia conocida hasta la historia de autenticación. |
| **Contrato Frontend — calidad visual** | **PASS** | Brief de diseño en el spec (sección *Brief de diseño*) y plan de tokens en este documento, ambos **antes** del primer componente. Skill `frontend-design` aplicada. WCAG 2.1 AA, mobile-first, `es-AR`, `dd/mm/aaaa`, `Intl.NumberFormat`. |
| **Governance — re-evaluación** | **PENDIENTE** | Se re-evalúa al cierre de la implementación, como exige la constitución. |

### Sobre dos puntos que parecen violaciones y no lo son

- **FR-013 (calcular el total de páginas en el cliente)** no viola el Principio III. El endpoint
  `Pagina[T]` envía `total` y `size`; derivar `ceil(total / size)` es aritmética de presentación
  sobre datos que entrega el backend, no el recálculo de una cifra de negocio (cotización, saldo,
  rendición o total monetario). Se verifica además que `Pagina.pages` **no se serializa**: es un
  `@property` de Pydantic y no aparece ni en `model_dump(mode="json")` ni en el cuerpo de la
  respuesta, medido sobre Pydantic 2.13.5. Es decir, el backend **no** puede entregar ese número
  hoy sin una migración de contrato, que tampoco correspondería a esta historia.
- **Cambiar `app/main.py` para el CORS** no toca la capa de Aplicación ni una regla de negocio:
  es la composición del middleware en la raíz, y la constitución lo exige literalmente.

## Project Structure

### Documentation (this feature)

```text
specs/005-frontend-scaffolding-clientes/
├── spec.md               # requisitos y criterios de aceptación (aprobación pendiente)
├── plan.md               # este documento (aprobación pendiente)
└── feature.json          # mapeo historia ↔ directorio ↔ rama (creado por Spec Kit)

# Generados por fases posteriores, DESPUÉS de la aprobación:
# research.md, data-model.md, contracts/, quickstart.md, tasks.md
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── (admin)/
│   │   │   ├── layout.tsx        # shell del administrador: banda de identidad + navegación
│   │   │   └── page.tsx          # Server Component: resuelve ?q=&page= y trae los datos
│   │   ├── layout.tsx            # raíz: <html lang="es-AR">, importa tokens y tipografía
│   │   └── globals.css           # @import de styles/tokens.css + base Tailwind
│   ├── features/
│   │   └── clientes/
│   │       ├── components/
│   │       │   ├── listado-clientes.tsx      # presentación pura, recibe datos por props
│   │       │   ├── fila-cliente.tsx          # una fila (tabla) o un bloque apilado (móvil)
│   │       │   ├── cabecera-listado.tsx      # título + total de clientes + total de páginas
│   │       │   ├── paginacion.tsx            # recibe page/pages y navega
│   │       │   ├── buscador-clientes.tsx     # único componente cliente con estado propio
│   │       │   └── estados/
│   │       │       ├── cargando.tsx
│   │       │       ├── vacio.tsx             # distingue "sin datos" de "sin coincidencias"
│   │       │       └── error.tsx             # incluye acción de reintento
│   │       ├── hooks/
│   │       └── types.ts                      # re-export de los tipos generados
│   ├── lib/
│   │   ├── api/
│   │   │   ├── http.ts                       # cliente HTTP base + manejo tipado de errores
│   │   │   └── clientes.ts                   # listarClientes({ q, page, size })
│   │   ├── auth/                             # no se crea todavía (sin sesión)
│   │   └── utils/
│   │       ├── formato.ts                    # fecha dd/mm/aaaa, paginación
│   │   └── cn.ts                             # concatenación condicional de clases
│   ├── components/
│   │   └── ui/
│   │       ├── boton.tsx
│   │       └── campo-busqueda.tsx
│   ├── styles/
│   │   └── tokens.css                        # variables de color, tipografía y espaciado
│   └── types/
│       └── openapi.d.ts                      # SALIDA de openapi-typescript (versionada)
├── tests/
│   ├── setup.ts
│   └── features/clientes/                    # Vitest + RTL
├── scripts/
│   └── generar-tipos-api.mjs                 # vuelca app.openapi() y corre openapi-typescript
├── package.json
├── tsconfig.json                             # "strict": true
├── next.config.ts
├── eslint.config.mjs                         # next/core-web-vitals + Prettier
├── vitest.config.ts
└── .env.local.example                        # API_URL, NEXT_PUBLIC_API_URL
```

> `src/app/api/` **no se crea**: no hace falta ningún Route Handler porque no hay BFF (Principio III).

**Structure Decision**: opción 2 (*Web application*: `backend/` + `frontend/`), que es la que la
constitución fija en su *Estructura de carpetas*. Los directorios de arriba son los de la
constitución, ampliados con los archivos concretos de esta historia. `backend/` queda intacto salvo
el origen CORS, declarado en *Constitution Check*.

## Arquitectura de componentes

### Regla que gobierna todo el árbol

**El Server Component es el que pide datos; el componente cliente solo maneja lo que el usuario
toca.** Eso deja una frontera nítida y evita el error clásico de arrastrar datos de servidor al
bundle del navegador.

```text
app/(admin)/page.tsx                [Servidor] lee searchParams, hace fetch, resuelve Suspense
   └── <ListadoClientes …/>         [Presentación] props puras: items, total, page, size
         ├── <CabeceraListado/>     [Presentación] título + "45 en total · 3 páginas"
         ├── <FilaCliente/> × N     [Presentación] repite por item
         └── <Paginacion/>          [Presentación] renderiza controles con page/pages
                                    [Cliente] solo navega (router.push), no pide datos

app/(admin)/page.tsx (rama vacía)
   └── <EstadoVacio motivo=…/>      [Presentación] "todavía no hay clientes" vs "sin coincidencias"

app/(admin)/page.tsx (rama de error)
   └── <EstadoError/>               [Cliente] ofrece reintento, no lee datos por su cuenta

<BuscadorClientes/>                 [Cliente] controla el input y escribe en la URL
```

### Responsabilidades

| Archivo | Capa | Recibe | No hace |
|---|---|---|---|
| `app/(admin)/page.tsx` | servidor | `searchParams` (`q`, `page`) | no estiliza, no tiene lógica de presentación |
| `lib/api/clientes.ts` | servicio | criterio de búsqueda y paginación | no recalcula nada; devuelve la respuesta tal cual |
| `features/clientes/components/listado-clientes.tsx` | presentación | `items`, `total`, `page`, `size` | no hace `fetch`, no conoce la URL |
| `features/clientes/components/paginacion.tsx` | presentación + navegación | `page`, `pages` | no pide datos |
| `lib/utils/formato.ts` → `totalPaginas(total, size)` | utilidad pura | `total`, `size` de la respuesta | no accede a `Pagina.pages` (es un `@property` y no se serializa); cumple FR-013 |
| `features/clientes/components/buscador-clientes.tsx` | cliente | valor de `q` actual | no pide datos; solo escribe en la URL |

### Manejo de estado

| Tipo de estado | Dónde vive | Por qué |
|---|---|---|
| Lista de clientes | Server Component + `fetch` | lectura inicial, ya resuelta en el servidor (contrato frontend) |
| `q` y `page` | **URL** (`?q=…&page=…`) | fuente de verdad única: se comparta, se recargue y se navegue con atrás/adelante conservando resultados (FR-022) |
| Texto mientras se teclea | estado local del `BuscadorClientes` | es efímero y no debe disparar renderizados del servidor por tecla |
| Caché de cliente (TanStack Query) | **no se instala** | sin actualización optimista ni polling en esta historia; YAGNI (Principio V) |
| Estado global | **no existe** | no hay ningún dato compartido entre vistas todavía |

**Sobre el debounce sin `useEffect`**: la constitución prohíbe usar `useEffect` para disparar
fetches. El criterio de búsqueda no dispara un `fetch` sino una **navegación del App Router**, pero
para no dejar la zona gris abierta el temporizador vive íntegramente en el manejador `onChange`
referenciado con `useRef`, limpiando y reiniciando en cada pulsación. El único `useEffect` del
árbol es la limpieza al desmontar, que no solicita datos. Enter navega de inmediato, sin esperar
la pausa (FR-023).

### Servicios HTTP

**`src/lib/api/http.ts` — cliente base**

```text
resolverBaseUrl()      → process.env.API_URL en servidor; NEXT_PUBLIC_API_URL en navegador
request<T>(ruta, init) → fetch, lee el cuerpo, y lanza ErrorApi { status, detalle, clase }
```

`clase` es una unión cerrada que traduce el status a algo que la interfaz sabe mostrar:

| Status | `clase` | Mensaje de interfaz |
|---|---|---|
| 401 | `sesion-expirada` | "Tu sesión expiró. Vuelve a iniciar sesión." |
| 403 | `sin-permisos` | "No tenés permisos para ver este listado." |
| 404 / 409 / 422 | `error-de-servicio` | "No pudimos leer los clientes. Reintentar." |
| resto / red caída | `sin-respuesta` | "No pudimos conectar con el sistema. Reintentar." |

Los `401`/`403` se modelan **desde esta historia** aunque el endpoint de lectura no los produzca:
el contrato de integración de la constitución es normativo desde ya y el mapeo es un único
`switch`. Lo que **no** se hace es propagar un token, porque no existe; queda como deficiencia
conocida en *Complexity Tracking*.

**`src/lib/api/clientes.ts` — servicio de la feature**

```text
listarClientes({ q, page, size }): Promise<Pagina<Cliente>>
```

Devuelve exactamente lo que emite el backend (`items`, `total`, `page`, `size`) sin derivar nada.
Las firmas se importan de `src/types/openapi.d.ts`, no se escriben a mano.

**Uso**: `page.tsx` llama a `listarClientes` dentro del Server Component y lo envuelve en
`<Suspense>` con el estado de carga. Ningún componente cliente importa este módulo.

### Cambios fuera de `frontend/` que exige esta historia

1. **`backend/app/main.py`** — `allow_origins` pasa de `["http://localhost:5173"]` a
   `["http://localhost:3000"]`, más el origen de producción cuando se defina. Obligación expresa
   del Contrato Backend.
2. **`docker-compose.yml`** — se agrega el servicio `frontend` (Node 24, puerto 3000) para que el
   `docker compose up` documentado en AGENTS.md §10 deje de prometer un servicio que no existe.
3. **`.github/workflows/ci.yml`** — se agregan dos jobs: `frontend` (install, lint, `vitest run`)
   y `api-types-drift` (instala backend, vuelca `app.openapi()`, genera tipos, `git diff
   --exit-code`).

## Plan de tokens de diseño

> Obligación de la constitución: el plan de tokens se revisa **antes** de escribir la primera
> línea de componente. Este bloque, junto al *Brief de diseño* del spec, es lo que se somete a
> aprobación. Los valores concretos se asientan en `src/styles/tokens.css` y en el bloque `@theme`
> de Tailwind v4 (configuración en CSS, no en JS).

### Color

Seis valores, sin degradados ni tintas de fondo decorativas.

| Token | Valor | Uso |
|---|---|---|
| `--papel` | `#F7F8FA` | fondo general. Papel **frío**, no crema cálido |
| `--tinta` | `#15181D` | texto principal y fondo de la banda de identidad |
| `--tinta-media` | `#5C6575` | texto secundario y encabezados de columna (verificar ≥ 4,5:1 sobre `--papel`) |
| `--linea` | `#E1E5EA` | reglas horizontales entre registros |
| `--senal` | `#1E4AA8` | foco, enlace y página activa. **Solo** eso: nunca como relleno |
| `--alerta` | `#B42318` | exclusivamente estados de error, para no ambiguar con `--senal` |

**La banda de identidad (`--tinta`) es el único gesto audaz** de la pantalla: ocupa el ancho
completo en la parte superior y contiene el título y el campo de búsqueda. Todo lo demás es papel
y reglas.

### Tipografía

- **Familia única: Archivo**, de Omnibus-Type (fundición de Buenos Aires). Grotesca diseñada para
  texto y titular, con eje de ancho. Se elige por raíz local —la compañía, los documentos y la
  interfaz son argentinos— y porque es una decisión sobre el sujeto, no el default de plantilla.
- **Roles y escala** (base 16 px, razón ≈ 1,25):

  | Rol | Tamaño | Peso | Uso |
  |---|---|---|---|
  | Identidad | 32 / 24 px | 700 | banda superior |
  | Título de vista | 24 px | 600 | "Clientes" |
  | Razón social | 16 px | 600 | el dato que se busca |
  | Cuerpo | 16 px | 400 | teléfono, dirección |
  | Auxiliar | 14 px | 400 | fechas, totales |
  | Micro | 12 px | 500 | paginación |

- Fechas con `font-variant-numeric: tabular-nums` para que la columna se alinee sin usar una
  tipografía monoespaciada (que sería un default a evitar).
- Encabezados de columna en caja baja (`Razón social`, no `RAZÓN SOCIAL`).
- Nada de cursivas ni colores aislados dentro de un titular.

### Layout

Escritorio / tablet ancha (≥ 640 px):

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Fletes y Mudanzas Express          [ Buscar por razón social     ]   │  ← banda --tinta
├──────────────────────────────────────────────────────────────────────┤
│ Clientes                          45 en total · 3 páginas           │
├──────────────────────────────────────────────────────────────────────┤
│ Razón social / dirección habitual   Teléfono    Cta. cte.  Alta     │  ← enc. caja baja
├──────────────────────────────────────────────────────────────────────┤
│ Distribuidora del Sur S.A.                                             │
│ Av. Colón 1250, Córdoba          351 555 0100   Sí    12/03/26  │  ← reglas entre registros
│ ──────────────────────────────────────────────────────────────────────│
│ Mudanzas López Hnos.                                                  │
│ San Martín 45                    351 555 0177   No    02/04/26  │
├──────────────────────────────────────────────────────────────────────┤
│ Anterior  1  2  3  Siguiente        Mostrando 1–20 de 45            │
└──────────────────────────────────────────────────────────────────────┘
```

Celular (< 640 px): cada cliente es un bloque apilado, sin desplazamiento horizontal.

```text
┌────────────────────────────────┐
│ Fletes y Mudanzas Express      │
│ [ Buscar por razón social   ]  │
├────────────────────────────────┤
│ Clientes    45 en total · 3 pá│
├────────────────────────────────┤
│ Distribuidora del Sur S.A.     │
│ Av. Colón 1250, Córdoba        │
│ 351 555 0100                   │
│ Cuenta corriente: Sí           │
│ Alta: 12/03/26                 │
├────────────────────────────────┤
│ Mudanzas López Hnos.           │
│ …                              │
├────────────────────────────────┤
│ Anterior   1  2  3   Siguiente │
└────────────────────────────────┘
```

- **Dirección habitual vive debajo de la razón social**, como línea secundaria de la misma celda.
  Es la solución para que 5 datos entren en 640 px sin columnas aplastadas ni scrolls
  horizontales, y porque la dirección es un atributo del domicilio del cliente, no una columna
  independiente que el administrador escanee.
- **Alineación**: todo el texto a la izquierda; la columna `Alta` se alinea a la derecha con
  cifras tabulares.
- **Radio de borde**: 4 px, solo en controles interactivos (campo y botones). Las filas no tienen
  radio ni sombra: se delimitan con reglas de 1 px, porque **la regla codifica el límite entre dos
  registros**, información y no adorno.
- Sin tarjetas, sin sombras difusas, sin etiquetas decorativas, sin degradados.

### Principios

1. La lista **es** la interfaz: no hay panel de indicadores ni tarjetas de resumen.
2. La estructura informa, no decora: si un elemento no separa, agrupa o jerarquiza, se quita.
3. Un solo acento, gastado en foco y estado activo; jamás como relleno.
4. Densidad sobre adorno: el administrador escanea, el chofer toca.
5. El movimiento solo responde a una acción del usuario (buscar, paginar). Sin animaciones de
   entrada, y `prefers-reduced-motion` lo desactiva por completo.

## Decisiones de esta historia

1. **Gestor de paquetes: npm.** La constitución delega expresamente esta elección en el spec de la
   primera historia de frontend; queda registrada en FR-007. npm ya viene con Node.js, así el
   equipo de cuatro integrantes no depende de instalar ni sincronizar un gestor adicional.
2. **Estado en la URL, no en caché de cliente.** `q` y `page` viven en el query string. Es lo que
   hace compartible y navegable la vista sin una capa de estado extra.
3. **Sin TanStack Query ni Playwright en esta historia.** Ambos figuran en el stack de la
   constitución como herramientas **permitidas y acotadas**, no como dependencias obligatorias de
   instalar de antemano. El Principio V prohíbe preparar código sin historia que lo exija. TanStack
   Query entra con actualización optimista o polling (agenda, formularios); Playwright entra con el
   primer flujo end-to-end con datos sembrables, como declara el *Out of Scope* del spec.
4. **Sin Zod en esta historia.** Zod valida formularios; aquí no hay ninguno. Entra con el alta de
   clientes.
5. **La página vive en `/`** bajo el route group `(admin)`. Si un futuro spec pide un dashboard,
   ese spec decide el traslado del listado.
6. **Sin columna de estado.** El repositorio del backend filtra `activo.is_(True)`, así que el
   listado solo devuelve clientes activos y una columna de estado sería un valor constante
   (FR-019). El campo `activo` existe en el schema de respuesta pero se ignora aquí.

## Pendientes de verificación antes de escribir código

1. Fijar el patch exacto de Next.js 16 y de React 19 al momento de instalar.
2. Confirmar el soporte de `next/core-web-vitals` sobre la versión de ESLint que instale Next 16.
3. Revisar la semántica de caché del App Router en Next 16 (introduce *Cache Components*): el
   listado **debe** declarar su política de caché de forma explícita para que una búsqueda siempre
   refleje el estado actual de la base, en lugar de heredar un default que podría servir una
   página vieja.
4. Contrastar el contraste real de `--tinta-media` sobre `--papel` y de `--senal` sobre `--tinta`
   con un verificador de contraste antes de aprobar los tokens.
5. Verificar la versión de TanStack Query **al momento de incorporarlo**, no antes.

## Complexity Tracking

> Se completa **solo** si el Constitution Check tiene violaciones que deban justificarse. Las dos
> detectadas en la planificación quedaron **ambas resueltas**; se conservan con su estado porque
> son la memoria de por qué el stack es ése y de qué falta todavía.

| Violación | Estado | Por qué era necesaria | Alternativa más simple rechazada porque |
|---|---|---|---|
| **Stack: Next.js 15 (constitución v1.0.0) → 16.x (rama estable)** | ✅ **Resuelta por enmienda MAJOR `v1.0.0 → v2.0.0`** (2026-10-21) | La constitución fijaba una versión mayor que ya no era la estable. Elegir 15 significaba arrancar un frontend nuevo sobre una rama anterior, con los avisos de seguridad de React Server Components (CVE-2025-66478) y las actualizaciones out-of-band de octubre 2026 por delante, y con soporte de herramientería cada vez menor. | *"Mantener Next.js 15 y no tocar la constitución"* se rechazó porque la constitución misma obliga: dice que si la verificación revela una versión mayor incompatible, **la corrección se hace actualizando esta constitución, no desviándose en la implementación**. La vía reglada es una enmienda **MAJOR** (`v1.0.0 → v2.0.0`, porque su regla de versionado califica como MAJOR "romper un contrato — stack…"). No había nada frontend implementado, por lo que no correspondió plan de migración. La enmienda quedó registrada en el *Registro de enmiendas* de la constitución y se alinearon `AGENTS.md` y `README.md`, que también fijaban 15. |
| **Token de sesión y middleware no implementados** | ⏳ **Abierta hasta la historia de autenticación** | El contrato exige que todo fetch propague el token y que el middleware resuelva la sesión y redirija. No hay autenticación: DD-3 resuelve el rol por un stub de cabecera y el endpoint de lectura no exige rol. | *"Inventar un placeholder de token y un middleware que redirige a un login inexistente"* se rechaza porque sería código muerto y una falsa sensación de seguridad, prohibidos por el Principio V, además de exponer una pantalla de login que el backend no puede validar. **La autorización real la aplica el backend** (ya la aplica: los endpoints de escritura exigen rol); el guard del frontend llega con la historia de autenticación. |

**Deficiencia conocida y aceptada**: hasta esa historia futura, el frontend no envía credenciales.
No es una brecha de seguridad —no existe sesión que robar ni endpoint de lectura que proteger—,
pero sí queda registrada acá para que ninguna revisión la lea como un olvido.

## Orden de implementación propuesto

1. Ratificar la enmienda de constitución (Next.js 15 → 16). ✅ **Hecho**: enmienda MAJOR
   `v1.0.0 → v2.0.0` aplicada el 2026-10-21, con `AGENTS.md` y `README.md` alineados.
2. Scaffolding: `create-next-app`, estructura de carpetas, tokens, ESLint/Prettier, Vitest.
3. Pipeline de tipos: vuelca de `app.openapi()`, `openapi-typescript`, script `gen:api`.
4. Cliente HTTP `lib/api/http.ts` + `listarClientes`, con sus tests.
5. Vista de lectura: `page.tsx` + componentes de presentación + estados.
6. Paginación y, por último, búsqueda con debounce en la URL.
7. Cambios de soporte: CORS en `app/main.py`, servicio `frontend` en Compose, jobs de CI.
8. Re-evaluar el *Constitution Check* al cierre, como exige Governance.
