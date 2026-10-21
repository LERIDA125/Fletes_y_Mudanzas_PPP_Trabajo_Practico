# Implementation Plan: H13 — Migración de Datos Históricos

**Spec**: `specs/002-migracion-datos-historicos/spec.md`

**Branch**: `feature/H13-migracion-datos-historicos`

**Estado**: plan de implementación **retrospectivo**. Documentado el 2026-10-21 por ingeniería
inversa sobre el código ya mergeado (PR #2, merge `9ce322f`). No describe trabajo pendiente: describe
lo que la historia decidió hacer, cómo quedó implementado, y qué desviaciones del plan original
quedaron registradas en el código.

## 1. Qué construye esta historia

Una herramienta de línea de comandos que lee el archivo Excel histórico del cliente
(`raw-data/Caso 2 Fletes_Mudanzas_Express_Datos.xlsx`, 30 filas de datos en 3 hojas), lo normaliza a
las reglas del modelo relacional y **carga los clientes** en la base. Móviles (choferes) y viajes
(servicios) se transforman y quedan listos, pero **no se cargan**: sus tablas todavía no existen.

El principio rector es explícito y es lo más importante de esta historia:

> Si la migración no puede decidir con confianza, **no decide**. Deja el caso señalado para que una
> persona lo resuelva.

Por eso el script no "limpia" los datos: los convierte y, cuando no sabe, produce un caso de revisión
humana con su valor original intacto.

## 2. Punto de partida: qué ya existe

H13 es la **primera historia** que toca el backend, y arranca sobre un repo sin `backend/` (la tarea
T001 de H1 creó el proyecto). En concreto:

- **H1 ya estaba mergeada** cuando H13 se brancheó: existe `Cliente` en `app/domain/cliente.py`,
  `ClienteRepo` en `app/infrastructure/repositories/cliente_repo.py` y `normalizar_razon_social`.
  H13 **reutiliza** esa lógica en vez de duplicarla.
- **No existe el directorio `raw-data/`**: es un insumo de la cátedra, deliberadamente no versionado
  (`.gitignore` raíz). El script lo busca por ruta y falla con un mensaje claro si no está.
- **No existen las tablas** `choferes`, `vehiculos`, `servicios` ni `pagos`. H13 no las crea.

## 3. Pipeline y archivos que toca

La historia **no** es un CRUD: es un pipeline de seis etapas con una frontera estricta — la decisión
de "no saber" se materializa en una estructura de datos (`ColaDeRevision`) que viaja de etapa en
etapa.

```
   raw-data/*.xlsx
        │
        ▼
 ┌─────────────────┐
 │  extraccion.py  │  Lee el Excel con openpyxl. NO normaliza, NO decide.
 └────────┬────────┘  Devuelve filas con su número original.
          │
          ▼
 ┌─────────────────────┐
 │  normalizacion.py   │  Funciones PURAS: sin BD, sin archivos, sin datetime.now().
 └────────┬────────────┘  Devuelve (valor_normalizado | None, motivo | None).
          │                 El motivo es la razón textual de por qué no pudo decidir.
          ▼
 ┌──────────────────────┐
 │  transformacion.py   │  Resuelve cada anomalía conocida sobre las 3 hojas.
 └────────┬─────────────┘  Emite registros normalizados + ColaDeRevision.
          │
          ├──────────────────────────────┐
          ▼                              ▼
 ┌────────────────┐            ┌──────────────────┐
 │   revision.py  │           │    carga.py       │  ← ÚNICO módulo que escribe en la BD
 │ ColaDeRevision │           │ (solo clientes)   │
 │  9 motivos ×   │           └────────┬─────────┘
 │  2 gravedades  │                    │  vía ClienteRepo + Cliente.crear
 └───────┬────────┘                    │
         │                             ▼
         │                    ┌──────────────────┐
         │                    │   reporte.py      │  Markdown con 8 secciones
         │                    └──────────────────┘
         ▼
 ┌──────────────────┐
 │   __main__.py    │  CLI: orquesta todo y decide códigos de salida.
 └──────────────────┘
```

### 3.1 Extracción — `scripts/migracion/extraccion.py` (115 líneas)

Lee el `.xlsx` con `openpyxl` en modo `read_only` y devuelve filas **con su número original**, para
que cada caso de revisión pueda citar "fila 8, columna Tarifa_Hora_Base".

- `Fila` es un dataclass frozen con `hoja`, `numero` y `datos: dict[str, object]`.
- `FILA_ENCABEZADO = 1`; los encabezados se normalizan con `str(valor).strip()`.
- Renglones totalmente vacíos se ignoran (no generan ruido en el reporte).
- `verificar_hojas(ruta)` falla temprano y con mensaje claro si falta `Choferes_y_Moviles`,
  `Clientes_Cotizaciones` o `Registro_Viajes` (FR-001).
- `ruta_por_defecto()` resuelve `<raíz del repo>/raw-data/Caso 2 Fletes_Mudanzas_Express_Datos.xlsx`.
  Es **hardcodeada** a propósito: es la ruta del insumo de la cátedra, no una configuración de
  despliegue. El override es el flag `--archivo`.

### 3.2 Normalización — `scripts/migracion/normalizacion.py` (772 líneas)

El módulo más grande y el más delicado. Todas las funciones son **puras**: reciben `object` (el valor
crudo de la celda) y devuelven `(valor_normalizado | None, motivo | None)`. El `motivo` es la razón
textual de por qué no se pudo decidir — es lo que después se muestra al humano en el reporte.

**Reutiliza H1 en vez de duplicar**: importa `TELEFONO_DIGITOS_MIN/MAX` y `normalizar_razon_social`
de `app.domain.cliente`. No reimplementa la comparación de textos.

Dataclasses de resultado: `Codigo`, `Telefono`, `FechaNormalizada`, `Monto`, `Capacidad`, `Bultos`,
`Cobro`. Cada una lleva la marca de si hubo un supuesto (`anio_supuesto`, `unidad_supuesta`,
`digitos_con_pais`).

Reglas implementadas (todas con patrón literal en el código):

| Dato | Regla | Ejemplo literal |
|---|---|---|
| Texto libre | NFD + filtro de diacríticos, minúsculas, espacios colapsados | `"Distribuidora  del Sur"` → clave comparable |
| Códigos | `RE_CODIGO` separa prefijo y número, se re-canonicaliza con `zfill` | `"MOV-01"`, `"MOV01"`, `"03"` → `MOV-01` |
| Teléfono | Solo dígitos; se detecta prefijo de país pero **no se toca** | `"+54 9 11 4455-6677"` → `5491144556677` |
| Fechas | 4 formatos probados **uno por uno contra cada celda**, nunca por posición de columna | `dd/mm/aaaa`, `aaaa-mm-dd`, `"16 de Mayo 2026"`, `dd/mm/aa` |
| Años de 2 dígitos | Umbral `ANIO_PIVOTE = 50`; `< 50` → siglo XXI, `>= 50` → siglo XX. Se marca `anio_supuesto=True` | `"16/05/26"` → `2026-05-16` |
| Horas | `RE_HORA` con meridiano opcional; sin meridiano se lee 24h | `"2:30 PM"` → `14:30` |
| Montos | Separador argentino: el separador derecho es el decimal | `"$ 11.000,00"` → `11000.00` |
| Moneda extranjera | `RE_MONEDA` detecta `u$`/`us$`/`usd`/`dolar` → moneda `USD`. **No se convierte** | `"U$S 15"` → `Decimal("15")`, `USD` |
| Capacidad | `FACTORES_UNIDAD_CARGA` convierte a kilogramos | `"3,5 toneladas"` → `3500` kg |
| Bultos | Solo se extrae el número si hay **exactamente uno** | `"10 cajas y 1 heladera"` → texto libre |
| Estado de cobro | Separado en 3 conceptos: **medio**, **estado**, **saldo** | `"Seña $5000 debe el resto"` → saldo `14000` |

**El detalle que más importa**: la detección de estado de cobro prueba los patrones en el orden
**parcial → pendiente → cobrado**, a propósito. Si "cobrado" se probara primero, `"Pagó mitad resta
factura"` se contaría como cobrado. Por eso la raíz `pago`/`pagó` suelta **no** está en
`PATRONES_ESTADO_COBRADO`.

### 3.3 Transformación — `scripts/migracion/transformacion.py` (719 líneas)

Resuelve las anomalías conocidas de cada hoja y emite, por cada fila, un registro normalizado y/o
casos de revisión.

- `transformar_moviles` / `transformar_clientes` / `transformar_viajes` devuelven
  `(registros, ColaDeRevision)`.
- **Duplicados**: si un código aparece en más de una fila, se conserva la **primera** como provisional
  y se reporta un caso `BLOQUEANTE` con la diferencia campo por campo. **Todas** las filas
  duplicadas se normalizan (no solo la primera), para que sus anomalías no desaparezcan del reporte.
- **Clientes**: la clave de deduplicación es `codigo.valor` si se pudo leer `ID_Cliente`; si no, la
  clave de texto normalizada. `tiene_cuenta_corriente` se fuerza a `False` (DP-06) porque
  `Historial_Pagos` es una nota en palabras, no un dato estructurado.
- **Direcciones no estructuradas**: 8 indicadores (`"retira en"`, `"a retirar"`, `"consultar"`, …)
  marcan la dirección como no estructurada → caso `BLOQUEANTE`, y el texto se conserva tal cual.
- **Cruce viajes ↔ choferes**: por **nombre normalizado** (no por código, porque la planilla no
  comparte clave). 0 candidatos → `SIN_MAPEO_EN_MODELO` / `A_CONFIRMAR`; más de 1 → `DUPLICADO` /
  `BLOQUEANTE`; exactamente 1 → se aplica el cruce.
- **Columnas sin mapeo** (`COLUMNAS_SIN_MAPEO_CLIENTE`): 4 columnas de la planilla no tienen destino
  en el modelo y se documentan con el motivo exacto — entre ellas `ID_Cliente` ("el `Cliente` de H1
  genera su propio `id` con identity") y `Localidad_Barrio` ("no existe un campo de localidad").

### 3.4 Revisión — `scripts/migracion/revision.py` (90 líneas)

La estructura que materializa el principio de la historia.

- `Motivo` (StrEnum, **9 miembros**): `duplicado`, `moneda_extranjera`, `direccion_no_estructurada`,
  `sin_mapeo_en_modelo`, `texto_ambiguo`, `dato_incompleto`, `supuesto_de_anio`, `unidad_implicita`,
  `duplicado_en_archivo`.
- `Gravedad` (StrEnum, 2 miembros): `BLOQUEANTE`, `A_CONFIRMAR`.
- `RevisionHumana` (frozen) con `hoja`, `fila`, `clave`, `motivo`, `gravedad`, `valor_original`,
  `detalle`, y `como_fila_markdown()`.
- `ColaDeRevision` con `agregar`, `agregar_varios`, `extender`, `hay_bloqueantes`, `por_hoja`,
  `por_motivo`.

### 3.5 Carga — `scripts/migracion/carga.py` (147 líneas)

**Único módulo que escribe en la base**, y escribe **solo clientes**.

- `cliente_creable(migrable)` arma la entidad con la API de H1:
  `Cliente.crear(razon_social=..., telefono=..., direccion_habitual=..., tiene_cuenta_corriente=False)`.
  **No** se redefine ni se modifica la entidad `Cliente`.
- `cargar_clientes(clientes, repo, simular=False)` devuelve `ResultadoCarga` con cuatro grupos:
  `agregados`, `ya_existentes`, `omitidos`, `casos`.
- **Idempotencia** (FR-005): antes de insertar, `repo.existe_razon_social(cliente.razon_social_key)`.
  Si el `INSERT` igual dispara `RazonSocialDuplicada` (carrera entre corridas), se trata como
  "ya existente" + caso `A_CONFIRMAR` en vez de abortar.
- Un `ReglaNegocioError` del dominio → el cliente se **omite** y se reporta `BLOQUEANTE`.
- Un teléfono ausente → se omite **antes** de tocar la base.

### 3.6 Reporte — `scripts/migracion/reporte.py` (386 líneas)

`generar_markdown(datos)` produce un documento de **8 secciones**:

1. Metadatos (archivo de origen, generado, filas leídas, casos de revisión con conteo por gravedad).
2. `## Resumen` — tabla Conjunto / Registros / Destino / Estado.
3. `## Clientes que no se pudieron cargar` (solo si hay omitidos).
4. `## Textos que se conservaron como observación` (solo si hay observaciones).
5. `## Transformaciones aplicadas` — tabla de **20 filas** (hoja → columna → normalización → criterio).
6. Catálogos provisionales (los 5 de `resumen_de_catalogos()`).
7. `## Casos para revisión humana` → `## Bloqueantes (N)` + `## Para confirmar (N)`.
8. `## Gaps de mapeo` — tabla Columna / Por qué no tiene destino / Qué se hizo.

### 3.7 Orquestación — `scripts/migracion/__main__.py` (196 líneas)

CLI: `python -m scripts.migracion`, con `--archivo`, `--reporte`, `--solo-transformacion`, `--simular`.

- `--solo-transformacion` normaliza y escribe el reporte **sin conectarse a la base**. Para que eso
  sea cierto, el import de `SessionLocal` y `ClienteRepo` está **dentro** del contextmanager `_repo()`,
  de modo que el modo sin base no carga `psycopg` ni necesita configuración.
- `--simular` se conecta y lee, pero no inserta: informa qué se cargaría.
- Códigos de salida: `0` éxito; `1` si el archivo no existe o si falla la lectura.
- Si quedan casos bloqueantes, escribe un aviso a `stderr` apuntando a la sección del reporte.

### 3.8 Catálogos — `scripts/migracion/catalogos.py` (246 líneas)

Tablas de texto **provisionales** (DP-01), agrupadas en un solo módulo versionable:

- `TIPOS_VEHICULO_CANONICOS` (8 valores) + `ALIAS_TIPO_VEHICULO` (9 alias).
- `ALIAS_ESTADO_MOVIL` + `ESTADOS_AMBIGUOS` (2 casos: `"en taller hasta el martes"` → `inactivo`,
  `"de franco"` → `disponible` — lecturas restrictiva y permisiva respectivamente).
- `ALIAS_CONDICION_IVA` (3 canónicos).
- `MEDIOS_PAGO_PROPUESTOS` (3) + `PATRONES_MEDIO_PAGO` (8, evaluados **en orden**).
- `PATRONES_ESTADO_COBRADO` / `_PARCIAL` / `_PENDIENTE` + `COBROS_AMBIGUOS` (6 casos que no se pueden
  resolver a un solo campo).

`catalogos.py` es el **único módulo que no importa nada de `app/`**: son tablas de texto, no reglas de
negocio.

### 3.9 Tests

- `backend/tests/unit/scripts/migracion/test_migracion.py` — **1 función de test**,
  `test_migracion_h13_completa`, que cubre normalización, transformación sintética, reporte, carga e
  idempotencia. Incluye un doble en memoria `ClienteRepoFalso`.

## 4. Decisiones de diseño aplicadas

| Decisión | Cómo se aplica en H13 |
|---|---|
| **DD-2** (clave normalizada) | Se reutiliza `normalizar_razon_social` de H1 en vez de reimplementar la comparación de textos. |
| **DD-4** (teléfono 7–20 dígitos) | `Telefono.es_valido_para_h1` valida contra `TELEFONO_DIGITOS_MIN/MAX` de H1. El prefijo de país **no** se toca: la política de normalización telefónica sigue abierta. |
| **Principio I** (spec antes que código) | La spec de H13 tiene 38 FR y 20 transformaciones documentadas, y el código tiene un módulo por etapa con el nombre de la etapa en el nombre del archivo. |
| **Principio II** (capas) | El script vive **fuera** de `app/` y **no se empaqueta** (`pyproject.toml` incluye solo `app*`), para que una imagen de producción no cargue `openpyxl` ni el módulo de migración. |
| **Escribir solo por repositorio** | `carga.py` no escribe SQL: escribe por `ClienteRepo`. No hay `INSERT` manual ni sesión propia. |
| **Decir "no sé" antes que inventar** | Todo caso dudoso termina en `ColaDeRevision` con su valor original, en vez de una corrección silenciosa. |

## 5. Puntos que el plan NO resuelve solo

- **Móviles y viajes no se cargan**: `Viaje.servicio_id` y `Viaje.pago_id` quedan en `None` porque las
  tablas `servicios` y `pagos` no existen. La carga de esas dos depende de H4 (choferes y
  vehículos), H6 (servicios) y H10 (pagos).
- **`tiene_cuenta_corriente` se fuerza a `False`** (DP-06): `Historial_Pagos` es texto libre, no un
  dato estructurado. La condición de cuenta corriente real llega con H2.
- **Los catálogos son provisionales** (DP-01): en cuanto cada entidad tenga su catálogo propio, el
  catálogo de la migración debe dejar de ser la fuente.
- **La normalización de teléfono no resuelve el prefijo de país** ni el `0` inicial: la regla de
  teléfono no está confirmada por el cliente.
- **Los montos en USD no se convierten**: no hay tipo de cambio confirmado.

## 6. Riesgos y cuidados — y desviaciones registradas

Verificados contra el código en la revisión retrospectiva del 2026-10-21:

1. **`raw-data/` no está en el repo** (es insumo de la cátedra, excluido por `.gitignore`). La rama
   `if archivo_excel.exists():` del test unitario **nunca se ejecuta en CI**, así que las aserciones
   `10 clientes / 8 móviles / 10 viajes / 37 casos` **no se validan automáticamente**. Es el gap de
   cobertura más relevante de la historia.
2. **La suite de tests se comprimió de 10 archivos a 1** (commits `14648e6` y `60f9e4f`). Esto dejó
   obsoleta la tabla de trazabilidad FR↔test del `tasks.md` y el path
   `tests/unit/scripts/migracion/test_carga.py` que el `quickstart.md` todavía cita.
3. **El CI nunca corre la migración**: ni siquiera `--solo-transformacion`, pese a lo que afirma la
   spec y el `tasks.md`. No hay ningún paso en `.github/workflows/ci.yml` que invoque
   `python -m scripts.migracion`.
4. **El PR de H13 sí tocó `app/api/schemas/`** (14 archivos de schemas alineados al ERD), lo que
   contradice la tabla de capas de la spec ("Presentación: No") y el check T039 del `tasks.md`. Los
   schemas quedaron ahí como borrador de historias futuras; la migración no los usa.
5. **El reporte versionado tiene una ruta absoluta de otra máquina** (`C:\Users\pikor\...`) en lugar de
   la ruta del repo. Es dato de ejecución, no de código, pero delata que se generó en otro equipo.
6. **`reporte.RUTA_REPORTE_POR_DEFECTO = "data/reporte_migracion.md"`** es un string relativo y no se
   usa: la constante efectiva es `__main__.RUTA_REPORTE_POR_DEFECTO`, que sí es un `Path` absoluto.
   Dead code.
7. **`Viaje.servicio_id` y `Viaje.pago_id`** son campos muertos hasta que existan las tablas.
8. **`ResultadoCarga(agregados=[c])`** en el test pasa un `ClienteMigrable` donde el tipo declara
   `Cliente`. Funciona porque el reporte solo usa `len()`, pero el tipo del test es incorrecto.
9. **T040 (Definition of Done)** queda sin checkear en el `tasks.md`.

## 7. Trazabilidad spec → plan → código

| Etapa | Módulo | Entradas | Salidas |
|---|---|---|---|
| Verificación de hojas | `extraccion.verificar_hojas` | ruta del `.xlsx` | `None` o excepción con mensaje |
| Extracción | `extraccion.leer_*` | ruta + nombre de hoja | `list[Fila]` con número de fila |
| Normalización | `normalizacion.normalizar_*` | valor crudo de celda | `(valor \| None, motivo \| None)` |
| Transformación | `transformacion.transformar_*` | `list[Fila]` | `(registros, ColaDeRevision)` |
| Cruce | `transformacion.cruzar_viajes_con_choferes` | viajes + móviles | `(mapa, casos)` |
| Revisión | `revision.ColaDeRevision` | casos de las 3 etapas | cola consolidada por hoja y motivo |
| Carga | `carga.cargar_clientes` | clientes + `ClienteRepo` | `ResultadoCarga` |
| Reporte | `reporte.generar_markdown` | `DatosReporte` | Markdown de 8 secciones |
| Orquestación | `__main__.correr` / `__main__.main` | CLI args | `Resultado` + reporte escrito + exit code |

## 8. Plan de entrega

- **MVP**: extracción + normalización + transformación + cola de revisión + reporte, sin tocar la
  base. Es lo que permite que una persona revise los 37 casos antes de que se escriba un solo
  registro. `--solo-transformacion` es exactamente ese modo.
- **Incremento**: carga de clientes por `ClienteRepo`, con idempotencia por `razon_social_key`.
- **Futuro (depende de otras historias)**: carga de choferes y vehículos (H4), de servicios (H6) y de
  pagos (H10), y catálogos definitivos en lugar de provisionales.

## 9. Mapeo a la arquitectura de monolito modular en capas

La historia **no** es un CRUD y por eso su mapeo a las 4 capas es particular: casi todo vive fuera de
la pirámide.

| Capa | Archivos | Responsabilidad | No debe contener |
|---|---|---|---|
| **1. Presentación** | — | No hay endpoints: la entrada es una CLI. | — |
| **2. Aplicación** | — | No hay casos de uso: la lógica es una transformación de datos por lotes. | — |
| **3. Dominio** | `app/domain/cliente.py` (**reutilizado** de H1) | Entidad `Cliente` y `normalizar_razon_social`. H13 no lo modifica. | — |
| **4. Infraestructura** | `backend/scripts/migracion/` (9 módulos) | Lectura del Excel, normalización, transformación, carga y reporte. | Reglas de negocio de la aplicación |
| **Puertos** | `app/infrastructure/repositories/cliente_repo.py` (**reutilizado** de H1) | Único punto de acceso a PostgreSQL. `carga.py` no escribe SQL. | — |

**Principio de dependencia**: `scripts/migracion/` → `app/domain/` y
`scripts/migracion/` → `app/infrastructure/repositories/`. La dependencia va **hacia adentro** del
monolito, nunca al revés: la aplicación no sabe que existe la migración. Un cambio en la entidad
`Cliente` rompe la migración en el momento — que es exactamente lo que se quiere, porque la
migración tiene que seguirle el ritmo al modelo.
