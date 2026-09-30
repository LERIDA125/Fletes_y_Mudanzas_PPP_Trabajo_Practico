# Tasks: H13 — Migración de datos históricos

**Feature Branch**: `feature/H13-migracion-datos-historicos`

**Spec**: `specs/H13-migracion-datos-historicos.md`

**Input**: Spec desde `/plan` (sección "Plan de implementación" de la spec).

## Format: `[ID] [P?] [Story] Description`

- `[P]` = corre en paralelo con otra task del mismo grupo.
- Las tasks **T001-T006** son el trabajo que ya estaba hecho en la rama al abrirla: se verifican y
  se ajustan, no se re-escriben desde cero.

## Phase 1: Setup

- [x] **T001** [P] Agregar `openpyxl>=3.1` a las dependencias de `backend/pyproject.toml` para poder
  leer el archivo de Excel sin pandas (el script no necesita un dataframe para 30 filas).
- [x] **T002** [P] Crear `backend/scripts/__init__.py` y `backend/scripts/migracion/__init__.py` para
  que `scripts.migracion` sea un paquete importable y se pueda correr con `python -m`.
- [x] **T003** Verificar que `openpyxl` entre en el `[tool.setuptools.packages.find]` o decidir
  explícitamente que `scripts` no se empaqueta (es código de una sola ejecución, no del desplegable).
  Dejar la decisión escrita en el archivo.

## Phase 2: Foundational — catálogos y extracción

- [x] **T004** [P] Escribir `catalogos.py` con los catálogos provisionales de tipo de vehículo,
  estado de móvil, condición de IVA y medios de pago, cada uno anotado como decisión pendiente
  (DP-01) y con el motivo de por qué es provisional. Marcar aparte los estados ambiguos y los cobros
  que no se pueden mapear, con la explicación de por qué.

  **Objetivo**: que ningún catálogo quede invisible como si estuviera confirmado.
  **Checks**: `python -c "from scripts.migracion import catalogos"`; cada constante tiene el
  comentario que la marca como provisional.

- [x] **T005** [P] Escribir `extraccion.py`: `leer_filas` con openpyxl en modo `read_only` +
  `data_only`, `Fila` con `hoja`, `numero` y `datos`, lectura de las tres hojas por nombre, ignorado
  de renglones vacíos, `verificar_hojas` que falla temprano si falta alguna, y `ruta_por_defecto`.

  **Objetivo**: que la extracción no normalice ni decida nada (FR-001, FR-002).
  **Checks**: leer el archivo real y devolver 10 filas por hoja.

- [x] **T006** [P] Escribir `revision.py` con `Motivo`, `Gravedad`, `RevisionHumana` y
  `ColaDeRevision` (agregar, agrupar por hoja, agrupar por motivo, extender, `hay_bloqueantes`).

  **Objetivo**: que exista un lugar único donde vive todo lo que no se pudo decidir (FR-034).
  **Checks**: `RevisionHumana.como_fila_markdown()` arma una fila de tabla.

## Phase 3: User Story 4 — No perder el texto original (Priority: P1)

*Ninguna task de este grupo escribe en la base: es el núcleo de la historia y va primero.*

- [x] **T007** [P] En `normalizacion.py`: `normalizar_texto` reusando `normalizar_razon_social` de
  H1, y `normalizar_codigo` + `codigo_de_movil` / `codigo_de_viaje` / `codigo_de_cliente`.

  **Objetivo**: una sola clave de comparación de textos en todo el proyecto (FR-008, FR-037).
  **Checks**: `"MOV-01"`, `"MOV01"`, `"03"` → `MOV-01`.

- [x] **T008** [P] En `normalizacion.py`: `normalizar_telefono` con el conteo de dígitos de H1 y las
  frases que no son un teléfono.

  **Objetivo**: que `"No tiene whatsapp"` termine en `NULL` y no en un teléfono inventado (FR-010).
  **Checks**: `"+54 9 11 4455-6677"` → `5491144556677`; `"No tiene whatsapp"` → `(None, motivo)`.

- [x] **T009** [P] En `normalizacion.py`: `normalizar_fecha` con los cuatro formatos probados uno por
  uno contra cada celda, `MESES_EN_TEXTO` y la proyección del año de dos dígitos.

  **Objetivo**: que el formato se detecte por contenido y no por posición de columna (FR-022,
  FR-023).
  **Checks**: los cuatro formatos dan la misma fecha; `"31/02/2026"` se rechaza.

- [x] **T010** [P] En `normalizacion.py`: `normalizar_hora` con 24h y 12h con AM/PM.

  **Objetivo**: `"2:30 PM"` → `14:30` (FR-025).
  **Checks**: `"08:00 AM"` → `08:00`; `"13:00 PM"` se rechaza.

- [x] **T011** [P] En `normalizacion.py`: `normalizar_monto` con el separador argentino y la
  detección de dólares, más `normalizar_decimal_argentino` para los números que no son moneda.

  **Objetivo**: que los dólares conserven su moneda y no se conviertan (FR-015, FR-016).
  **Checks**: `"$ 11.000,00"` → `11000.00`; `"U$S 15"` → `(15, "USD")`; `"35,5"` → `35.5`.

- [x] **T012** [P] En `normalizacion.py`: `normalizar_capacidad` a kilogramos, con el factor por
  unidad y el flag de unidad supuesta.

  **Objetivo**: `"3,5 toneladas"` → `3500` kg y `"1000"` → `1000` kg marcado como supuesto
  (FR-013, FR-014).
  **Checks**: `"1,5 tn"` → `1500`; `"800kg"` → `800`.

- [x] **T013** [P] En `normalizacion.py`: `normalizar_tipo_vehiculo`, `normalizar_estado_movil`,
  `normalizar_condicion_iva`, `es_direccion_no_estructurada` y `normalizar_bultos`.

  **Objetivo**: que los cuatro casos pedidos queden explícitos (FR-012, FR-017, FR-018, FR-019,
  FR-027).
  **Checks**: `"Archivadores pesados"` → `Bultos(None, True)`; `"6 muebles embalados"` → `6`.

- [x] **T014** [P] En `normalizacion.py`: `descomponer_estado_cobro` con los tres conceptos
  separados y `saldo` calculado solo en los dos casos permitidos.

  **Objetivo**: que `"Pagó mitad resta factura"` no cuente como cobrado y que el saldo no se invente
  (FR-028, FR-029, FR-030).
  **Checks**: `"Transferido completo"` → `("Transferencia bancaria", "cobrado", 0)`;
  `"Anotado en la libreta"` → medio y estado en `None` con motivo.

- [x] **T015** Escribir `transformacion.py`: `transformar_moviles` con la detección de códigos
  repetidos y el reporte del choque campo por campo.

  **Objetivo**: que `"MOV-01"`/`"MOV01"` y `"MOV-05"` con dos nombres se traten como un móvil con dos
  versiones sin elegir la buena (FR-009).
  **Checks**: 10 filas → 8 móviles, con 2 casos de duplicado en la cola.

- [x] **T016** Escribir `transformacion.py`: `transformar_clientes` con `tiene_cuenta_corriente`
  siempre en `false`, las columnas sin mapeo y el marcado de las direcciones no estructuradas.

  **Objetivo**: que ningún texto en palabras se convierta en un booleano (FR-020, FR-021, DP-06).
  **Checks**: `"Cuenta corriente"` en `Historial_Pagos` no produce `true`; 4 gaps de mapeo.

- [x] **T017** Escribir `transformacion.py`: `transformar_viajes` y `cruzar_viajes_con_choferes` /
  `aplicar_cruce`.

  **Objetivo**: que los viajes queden completos y cruzados por nombre normalizado (FR-032).
  **Checks**: `"MARCELO RODRIGUEZ"` y `"Marcelo Rodriguez"` caen en el mismo móvil.

## Phase 4: User Stories 1 y 2 — Cargar clientes e idempotencia (Priority: P1)

- [x] **T018** Escribir `carga.py`: `ResultadoCarga` con los contadores de agregados, ya existentes y
  omitidos, y `cargar_clientes` que arma el `Cliente` con la API de H1 y lo inserta con
  `ClienteRepo.crear`.

  **Objetivo**: que la escritura pase por el repositorio y no por un `INSERT` a mano (FR-004).
  **Checks**: un doble de repo registra las inserciones; el `Cliente` se construye con
  `Cliente.crear`.

- [x] **T019** [P] En `carga.py`: la idempotencia por `razon_social_key` con
  `ClienteRepo.existe_razon_social`, y el manejo de `RazonSocialDuplicada` por si dos filas del
  archivo traen la misma razón social.

  **Objetivo**: que correr dos veces no duplique clientes (FR-005).
  **Checks**: dos corridas seguidas → 0 inserts en la segunda.

- [x] **T020** [P] En `carga.py`: omisión de las filas sin teléfono válido, con el motivo en la cola
  de revisión, sin abortar el resto.

  **Objetivo**: que una fila ilegible no tumbe la migración entera (FR-007).
  **Checks**: una fila inválida entre dos válidas → las dos válidas se cargan.

## Phase 5: User Story 3 — El reporte (Priority: P1)

- [x] **T021** Escribir `reporte.py`: el encabezado, la sección de transformaciones aplicadas, la de
  revisión humana con su tabla, la de gaps de mapeo y el resumen de lo cargado y lo pendiente.

  **Objetivo**: que el reporte sea el entregable que le dice a una persona qué mirar (FR-034,
  FR-035, FR-036).
  **Checks**: el Markdown tiene las cuatro secciones y ninguna tabla queda con filas partidas.

- [x] **T022** [P] En `reporte.py`: la sección de casos bloqueantes separada de los que solo
  necesitan confirmación, y el listado de los catálogos provisionales.

  **Objetivo**: que se sepa qué frena la migración y qué es solo informativo (FR-036).
  **Checks**: cada caso cae en exactamente una de las dos secciones.

## Phase 6: User Story 5 — Dejar listo para los modelos que faltan (Priority: P2)

- [x] **T023** Escribir `__main__.py`: la CLI con `--archivo`, `--reporte`, `--solo-transformacion` y
  `--simular`, orquestando lectura → transformación → carga → reporte.

  **Objetivo**: que la migración se pueda correr sin argumentos y sin tocar la base cuando se quiere
  solo ver el reporte (FR-038).
  **Checks**: `python -m scripts.migracion --solo-transformacion` corre sin conexión.

- [x] **T024** [P] En `__main__.py`: la verificación de hojas antes de escribir y el mensaje de error
  claro cuando falta alguna.

  **Objetivo**: que no se migre la mitad del archivo (FR-001).
  **Checks**: un archivo sin `Registro_Viajes` falla sin escribir nada.

## Phase 7: Tests

- [x] **T025** [P] `tests/unit/scripts/migracion/test_normalizacion_fechas.py`: los cuatro formatos de
  fecha, el año supuesto, el calendario inválido, la celda vacía y las horas 24h/12h.

  **Objetivo**: cubrir FR-022 a FR-025.
  **Checks**: pasa con `pytest tests/unit`.

- [x] **T026** [P] `tests/unit/scripts/migracion/test_normalizacion_montos.py`: separador argentino,
  símbolo, dólares, capacidad de carga y números no monetarios.

  **Objetivo**: cubrir FR-013 a FR-016.
  **Checks**: pasa con `pytest tests/unit`.

- [x] **T027** [P] `tests/unit/scripts/migracion/test_normalizacion_telefonos.py`: formatos con y sin
  código de país, las frases que no son teléfono y el rango de dígitos de H1.

  **Objetivo**: cubrir FR-010, FR-011.
  **Checks**: pasa con `pytest tests/unit`.

- [x] **T028** [P] `tests/unit/scripts/migracion/test_normalizacion_catalogos.py`: códigos, tipo de
  vehículo, estado de móvil, condición de IVA, direcciones no estructuradas y bultos.

  **Objetivo**: cubrir FR-008, FR-012, FR-017 a FR-019, FR-027.
  **Checks**: pasa con `pytest tests/unit`.

- [x] **T029** [P] `tests/unit/scripts/migracion/test_normalizacion_cobro.py`: los tres conceptos de
  `Estado_Cobro` y los casos que no se pueden mapear.

  **Objetivo**: cubrir FR-028 a FR-031.
  **Checks**: pasa con `pytest tests/unit`.

- [x] **T030** `tests/unit/scripts/migracion/test_transformacion.py`: los duplicados de móvil, el
  cruce de viajes con choferes y la garantía de que `tiene_cuenta_corriente` nunca queda en `true`.

  **Objetivo**: cubrir FR-009, FR-020, FR-021, FR-032.
  **Checks**: pasa con `pytest tests/unit`.

- [x] **T031** `tests/unit/scripts/migracion/test_carga.py`: la idempotencia con un doble de
  `ClienteRepo` y la omisión de filas inválidas.

  **Objetivo**: cubrir FR-004 a FR-007.
  **Checks**: dos corridas → 0 inserts en la segunda; una fila inválida no corta el resto.

- [x] **T032** `tests/unit/scripts/migracion/test_reporte.py`: que el Markdown tenga las secciones
  que la spec exige y que los casos aparezcan con hoja, fila y valor original.

  **Objetivo**: cubrir FR-034 a FR-036.
  **Checks**: pasa con `pytest tests/unit`.

- [x] **T033** `tests/unit/scripts/migracion/test_extraccion.py`: las tres hojas del archivo real, el
  conteo de filas, los renglones vacíos ignorados y el error por hoja faltante.

  **Objetivo**: cubrir FR-001, FR-002.
  **Checks**: pasa con `pytest tests/unit`.

## Phase 8: Polish y Definition of Done

- [x] **T034** [P] Generar `backend/data/reporte_migracion.md` corriendo el script contra el archivo
  real, y revisar que no haya secciones vacías ni casos sin explicar.

  **Checks**: el reporte nombra los 2 duplicados de móvil, los montos en dólares, el historial de
  pagos ambiguo, las direcciones no estructuradas y los bultos sin cantidad.

- [x] **T035** [P] Agregar `backend/data/` y `raw-data/` al `.gitignore` si corresponde, y borrar los
  `__pycache__` que la corrida dejó en `backend/scripts/`.

  **Objetivo**: no commitear datos crudos ni artefactos de Python.
  **Checks**: `git status` limpio de artefactos.

- [x] **T036** [P] Documentar en `specs/H13-migracion-datos-historicos-quickstart.md` cómo correr la
  migración, igual que hizo H1.

  **Checks**: los comandos del quickstart son los que funcionan.

- [x] **T037** [P] Revisar si la historia deja alguna decisión de diseño nueva para AGENTS.md §11 (DD).
  Hoy no debería agregar ninguna: la migración no cambia entidades.

  **Checks**: o se agrega la DD, o queda escrito por qué no haga falta.

  **Resultado**: no hace falta ninguna DD nueva. H13 no cambia entidades ni columnas: usa
  Cliente, ClienteRepo y la normalización de 
azon_social_key que ya definió DD-2. La
  única decisión de implementación nueva es que scripts no se empaqueta (T003), que es
  packaging y no arquitectura, así que no va a AGENTS.md §11.

- [x] **T038** Trazabilidad FR ↔ test: cada FR de la spec tiene al menos un test que lo cubre y pasa.

  **Checks**: una tabla FR → archivo de test → test, toda en verde.

- [x] **T039** Gate de AGENTS.md §2: confirmar que ningún archivo de `app/api/`, `app/application/` ni
  `app/domain/` fue tocado, y que la escritura de la base pasa por `ClienteRepo`.

  **Checks**: `git diff main --stat` solo muestra `backend/scripts/`, `backend/tests/` y `specs/`.

- [ ] **T040** Definition of Done (AGENTS.md §9).

  **Checks**: los 5 puntos de §9 verificados uno por uno.

## Trazabilidad FR ↔ test (T038)

Las 38 FR de la spec tienen al menos un test que las cita en el docstring. Verificado con
python -m pytest tests/unit -q (386 tests) y un chequeo de que ningún FR queda sin
archivo asociado.

| FR | Archivo(s) de test |
|---|---|
| FR-001 | cli, extraccion |
| FR-002 | extraccion |
| FR-003 | cli |
| FR-004 | carga |
| FR-005 | carga, normalizacion_telefonos |
| FR-006 | carga |
| FR-007 | carga |
| FR-008 | normalizacion_catalogos, transformacion |
| FR-009 | transformacion |
| FR-010 | normalizacion_telefonos |
| FR-011 | normalizacion_telefonos |
| FR-012 | normalizacion_catalogos |
| FR-013 | normalizacion_montos |
| FR-014 | normalizacion_montos |
| FR-015 | normalizacion_montos |
| FR-016 | normalizacion_montos |
| FR-017 | normalizacion_catalogos |
| FR-018 | normalizacion_catalogos |
| FR-019 | normalizacion_catalogos |
| FR-020 | reporte, transformacion |
| FR-021 | carga, transformacion |
| FR-022 | normalizacion_fechas |
| FR-023 | normalizacion_fechas |
| FR-024 | normalizacion_fechas |
| FR-025 | normalizacion_fechas |
| FR-026 | normalizacion_montos |
| FR-027 | normalizacion_catalogos |
| FR-028 | normalizacion_cobro |
| FR-029 | normalizacion_cobro |
| FR-030 | normalizacion_cobro |
| FR-031 | normalizacion_cobro |
| FR-032 | cli, normalizacion_catalogos, transformacion |
| FR-033 | cli, reporte |
| FR-034 | reporte |
| FR-035 | extraccion, reporte |
| FR-036 | reporte |
| FR-037 | normalizacion_fechas |
| FR-038 | cli |

## Dependencias y orden de ejecución

```
T001, T002 ──> T003
                 |
      T004 ──────┼──> T005 ──> T033
                 |      |
                 |      v
                 |    T015, T016, T017 ──> T030
                 |
                 └──> T007..T014 ──> T025..T029
                                          |
                                          v
                              T018, T019, T020 ──> T031
                                          |
                                          v
                              T021, T022, T023, T024
                                          |
                                          v
                              T034, T035, T036, T037, T038, T039, T040
```

## Estrategia de entrega

Un solo PR. La historia no se puede partir en varios: sin la transformación no hay nada que cargar,
y sin el reporte la carga es a ciegas. Lo que sí se puede hacer es revisar por grupo de phases —
fundacional (catálogos y normalización), después transformación, después carga y reporte.

## Notas

- **El archivo crudo no se versiona.** `raw-data/Caso 2 Fletes_Mudanzas_Express_Datos.xlsx` es el
  insumo del cliente. El script lo toma de `raw-data/` por configuración y falla claro si no está.
- **`--simular` y `--solo-transformacion` son distintos.** El primero dice qué se cargaría si la base
  aceptara todo; el segundo ni siquiera intenta conectarse. El segundo es el que corre en CI, donde
  no hay PostgreSQL.
- **Los tests de normalización no usan fixtures.** Son funciones puras (FR-037), así que se prueban
  con literales. Si algún test necesita un archivo, es que se coló una regla de negocio adentro de
  una función que debía ser pura.
- **Lo que la migración NO hace, y hay que decir de nuevo en la revisión del PR:** no crea tablas,
  no define `Servicio` ni `Pago`, no convierte dólares, no inventa la política de cuenta corriente
  y no agrega columnas a `Cliente`. Todo eso está en "Gaps de mapeo" y en "Decisiones pendientes" de
  la spec, y sale de ahí, no del código.