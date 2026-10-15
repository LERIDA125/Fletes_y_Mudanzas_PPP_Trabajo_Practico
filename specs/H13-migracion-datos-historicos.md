# Feature Specification: H13 — Migración de datos históricos

**Feature Branch**: `feature/H13-migracion-datos-historicos`

**Created**: 2026-09-30

**Status**: Draft

**Input**: User description: "Migrar los datos históricos del archivo `raw-data/Caso 2 Fletes_Mudanzas_Express_Datos.xlsx` (hojas `Choferes_y_Moviles`, `Clientes_Cotizaciones` y `Registro_Viajes`) hacia el modelo relacional del sistema. La planilla tiene 30 filas de datos en total y está sucia: códigos con prefijos inconsistentes, teléfonos mezclados, unidades de carga mezcladas, montos con separador decimal argentino y un caso en dólares, fechas en cuatro formatos distintos, horas mezclando 24h y 12h, y varios campos de texto libre que no son un dato estructurado. Ningún campo ambiguo puede resolverse inventando una regla de negocio: cuando la migración no puede decidir con confianza, tiene que dejarlo señalado para que una persona lo resuelva."

## Contexto del repositorio al momento de esta historia

Este punto condiciona todo el alcance y conviene dejarlo escrito antes que cualquier código,
porque es la razón por la que la historia carga una sola de las cinco entidades.

- La historia H1 (Gestionar Clientes) está mergeada en `main`. La entidad `Cliente`
  (`app/domain/cliente.py`), su repositorio (`app/infrastructure/repositories/cliente_repo.py`) y la
  tabla `clientes` (migración Alembic `0001_crear_clientes.py`) ya existen.
- **No existen** las entidades `Chofer`, `Vehiculo`, `TipoVehiculo`, `Servicio` ni `Pago`: no hay
  dominio, ni modelos de persistencia, ni repositorios, ni migraciones Alembic para ellas. Sus
  tablas son de H4 (choferes y vehículos), H5/H6 (agenda y servicios) y H10 (pagos).
- Por lo tanto la **única carga posible hoy es `clientes`**. Las otras cuatro entidades se
  transforman, se prueban y se dejan listas, pero no se escriben: hacerlo exigiría inventar la
  máquina de estados de `Servicio` y el catálogo de medios de pago, que son justamente dos de las
  decisiones que AGENTS.md §6 deja abiertas con el cliente.

## Out of Scope

- Crear las tablas `choferes`, `tipo_vehiculo`, `vehiculos`, `servicios` y `pagos`, ni sus
  entidades de dominio y repositorios. Esas historias van por separado.
- Escribir en la base con SQL a mano o saltarse los repositorios de la Capa de Infraestructura.
- Agregar columnas nuevas a la entidad `Cliente` para acomodar columnas de la planilla que no
  tienen destino (ver **Gaps de mapeo** más abajo).
- Traducir `Historial_Pagos` a `tiene_cuenta_corriente`, o cualquier otra traducción de una nota en
  palabras a un datobooleano o numérico.
- Convertir montos en dólares a pesos.
- Normalizar los teléfonos a un formato único (agregar código de país, sacar el `0` inicial).
- Limpiar el archivo de Excel de origen: la planilla es la fuente y se lee tal como está.
- Exponer la migración por la API o por un endpoint: es una tarea de una sola vez, ejecutada desde
  la línea de comandos.
- Un tablero o pantalla para ver la cola de revisión humana. La salida es el reporte en Markdown.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Cargar los clientes históricos sin duplicar (Priority: P1)

Como administrador, quiero cargar los 10 clientes de `Clientes_Cotizaciones` para poder empezar a
usar el sistema sin volver a tipear la planilla.

**Why this priority**: Es el único flujo de esta historia que produce datos en la base, y es el
mínimo valor entregable por sí solo: clientes cargados ya se pueden listar, buscar y consultar con
los endpoints que H1 dejó funcionando.

**Independent Test**: Con la base vacía, correr el script y verificar que los 10 clientes quedan
disponibles en el listado de `GET /api/clientes` con sus datos normalizados.

**Acceptance Scenarios**:

1. **Dado** una base de datos vacía y el archivo de Excel con 10 filas en `Clientes_Cotizaciones`,
   **cuando** se corre la migración, **entonces** los 10 clientes quedan cargados y cada uno es
   consultable por su identificador.
2. **Dado** la hoja `Clientes_Cotizaciones` donde `ID_Cliente` viene como `"CLI-101"`, `"102"`,
   `"CLI-103"`, `"104"`, `"105"`… **cuando** se corre la migración, **entonces** cada fila se carga
   una vez, sin que el prefijo ausente/del prefijo genere clientes repetidos.
3. **Dado** un cliente de la planilla cuyo teléfono está escrito como `"+54 9 11 9876-5432"`,
   **cuando** se carga, **entonces** el teléfono queda guardado solo con dígitos (`5491198765432`),
   con el `+`, los espacios y los guiones eliminados.
4. **Dado** el cliente de la fila 6 de la planilla, cuyo `Direccion_Habitual` es
   `"Retira en depósito"`, **cuando** se carga, **entonces** el cliente queda cargado con ese texto
   tal cual, y el reporte lista el caso como dirección no estructurada para resolverlo con quien
   implementó H1.
5. **Dado** los 10 clientes de la planilla, **cuando** se corre la migración, **entonces** ninguno
   queda con `tiene_cuenta_corriente = true`, aunque su `Historial_Pagos` diga `"Cuenta corriente"`
   o `"Paga a 30 días"`, y esas notas quedan íntegras en el reporte.

---

### User Story 2 — Poder correr la migración otra vez sin romper nada (Priority: P1)

Como administrador, quiero poder volver a correr el script si algo sale mal, sin duplicar clientes
ni dejar la base a medias.

**Why this priority**: Es una migración de datos reales de un cliente. Un error de tipeo en el
archivo obliga a correrla de nuevo, y si duplica clientes hay que dar de baja a mano cada
duplicado. La idempotencia no es un lujo: es lo que hace recuperable el procedimiento.

**Independent Test**: Correr el script dos veces seguidas contra la misma base y verificar que el
total de clientes no cambia y que el reporte da el mismo resultado.

**Acceptance Scenarios**:

1. **Dado** una base con los 10 clientes ya cargados por una corrida anterior, **cuando** se corre
   la migración de nuevo, **entonces** no se crea ningún cliente nuevo y el total sigue siendo 10.
2. **Dado** una base donde un cliente ya existe cargado a mano con la misma razón social (ignorando
   mayúsculas, minúsculas, acentos y espacios sobrantes), **cuando** se corre la migración,
   **entonces** ese cliente no se duplica: se lo reconoce por su `razon_social_key` y se lo reporta
   como ya existente.
3. **Dado** una base con datos y un archivo con una fila inválida, **cuando** se corre la
   migración, **entonces** la fila inválida se omite y se reporta, y las filas válidas quedan
   cargadas: una fila ilegible no aborta la migración entera.
4. **Dado** una migración ya corrida, **cuando** se corre de nuevo y el archivo cambió, **entonces**
   el script informa cuántos clientes agrega, cuántos reconoce y cuántos omite.

---

### User Story 3 — Saber qué se transformó y qué falta decidir (Priority: P1)

Como administrador, quiero un reporte que liste cada transformación aplicada y, aparte, todos los
casos que una persona tiene que resolver, para no confiar ciegamente en datos que una máquina
decidió por conveniencia.

**Why this priority**: La migración deja de ser "datos migran bien" y pasa a ser "datos migran bien
y sé exactamente qué mirar". Sin el reporte, los casos ambiguos quedan escondidos en la base y se
descubren meses después, cuando ya no se puede saber de dónde vinieron.

**Independent Test**: Correr la migración y abrir `backend/data/reporte_migracion.md`: tiene que
estar el detalle de cada transformación, una sección propia con los casos a revisar, y una sección
propia con los gaps de mapeo.

**Acceptance Scenarios**:

1. **Dado** una migración corrida, **cuando** se abre el reporte, **entonces** lista cada
   transformación aplicada, con la hoja y la columna de la que sale y el criterio usado.
2. **Dado** una migración corrida, **cuando** se abre el reporte, **entonces** los casos que
   necesitan decisión humana están en una sección separada de las transformaciones normales, y cada
   uno cita la hoja, el número de fila original del Excel y el valor textual que había.
3. **Dado** una migración corrida, **when** se abre el reporte, **entonces** los casos
   bloqueantes y los que solo hay que confirmar están distinguidos entre sí.
4. **Dado** una migración corrida, **cuando** se abre el reporte, **entonces** hay una sección de
   gaps de mapeo que nombra cada columna de la planilla que no tiene destino en el modelo actual, y
   dice explícitamente que no se agregó la columna ni se descartó el valor.
5. **Dado** una migración corrida, **cuando** se abre el reporte, **entonces** dice cuántos
   registros se cargaron, cuántos se omitieron y cuántos de cada conjunto quedan pendientes de
   modelo.

---

### User Story 4 — No perder el texto original de los campos libres (Priority: P1)

Como administrador, quiero que cuando una celda de texto libre no se pueda convertir en un dato
estructurado, el texto original quede guardado, para poder leer después qué quiso decir el
administrador que llevaba la planilla.

**Why this priority**: El texto libre es la única evidencia de intención que hay. Si la migración lo
descarta y lo reemplaza por `NULL`, esa información se pierde para siempre y no hay forma de
recuperarla.

**Independent Test**: Correr la migración y verificar en el reporte que aparecen, con su texto
original, los casos de `Estado_Actual` ("En taller hasta el martes", "De franco"), los de
`Bultos_Estimados` sin cantidad ("Archivadores pesados", "Sonido y luces") y los de `Estado_Cobro`
ambiguos ("Anotado en la libreta", "Cta Cte").

**Acceptance Scenarios**:

1. **Dado** un móvil con `Estado_Actual = "En taller hasta el martes"`, **cuando** se transforma,
   **entonces** el estado queda en un valor del catálogo reducido y el texto `"En taller hasta el
   martes"` queda como observación, además de aparecer en la cola de revisión.
2. **Dado** un viaje con `Bultos_Estimados = "Archivadores pesados"`, **cuando** se transforma,
   **entonces** la cantidad de bultos queda en `NULL` y el texto original queda conservado.
3. **Dado** un viaje con `Bultos_Estimados = "Sonido y luces"`, **cuando** se transforma, **entonces**
   la cantidad queda en `NULL` y el caso se marca como celda que describe un servicio y no una
   cantidad.
4. **Dado** un viaje con `Estado_Cobro = "Anotado en la libreta"`, **cuando** se transforma, **entonces**
   ni el medio de pago ni el estado del cobro se fuerzan a ninguna categoría y el caso queda
   reportado con el motivo.

---

### User Story 5 — Tener los datos de las otras entidades listos para cuando existan (Priority: P2)

Como administrador, quiero que los datos de choferes, móviles, servicios y pagos ya estén
normalizados aunque todavía no se puedan cargar, para que el día que se implementen esas historias
no haya que volver a leer el Excel ni volver a decidir los criterios.

**Why this priority**: No aporta nada por sí solo en la base, pero evita repetir todo el trabajo de
limpieza y, sobre todo, evita que cada persona normalice el mismo dato de forma distinta en su
historia. Es la razón de que la transformación viva separada de la carga.

**Independent Test**: Correr la transformación sin base de datos y verificar que devuelve los
cuatro conjuntos normalizados y la cola de revisión.

**Acceptance Scenarios**:

1. **Dado** el archivo de Excel, **cuando** se corre la transformación, **entonces** devuelve
   móviles, viajes y la cola de revisión, aunque no exista conexión a la base de datos.
2. **Dado** que `Registro_Viajes` cita a los choferes por nombre, **when** se corre la
   transformación, **entonces** cada viaje queda cruzado con el código de su móvil cuando el nombre
   se puede resolver sin ambigüedad.
3. **Dado** que `Registro_Viajes` escribe `"MARCELO RODRIGUEZ"` y `Choferes_y_Moviles` escribe
   `"Marcelo Rodriguez"`, **when** se corre el cruce, **entonces** los dos nombres caen en el mismo
   chofer porque la comparación ignora mayúsculas y acentos.
4. **Dado** que las tablas `choferes` y `servicios` todavía no existen, **cuando** se corre la
   migración completa, **entonces** los conjuntos transformados de esas entidades no se escriben y
   el reporte dice cuántos quedaron pendientes y por qué.

---

### Edge Cases

- **Códigos con prefijo ausente**: `"03"` y `"MOV-03"` se normalizan al mismo código, así que una
  fila que repite el móvil con otro formato se detecta como duplicado y no como un móvil nuevo.
- **Mismo móvil con dos nombres distintos**: `"Jorge 'El Negro'"` y `"Jorge Almada"` aparecen con el
  mismo código `MOV-05`. Se tratan como el mismo móvil con dos versiones; **no** se decide cuál
  nombre es el vigente.
- **Celda vacía en una columna obligatoria**: se omite la fila y se reporta. No se inventa un valor
  por defecto para cumplir el `NOT NULL`.
- **Texto donde debería haber un teléfono**: `"No tiene whatsapp"` no es un teléfono. Se guarda
  `NULL` y se reporta; no se convierte en dígitos.
- **Anotación que no es un dato**: `"Rompió el elástico"` y `"De franco"` no son estados de un
  enum. Se mapean a un estado provisional, se conserva el texto y se reporta para confirmar.
- **Dólares en una columna de pesos**: `"U$S 15"` y `"U$S 0.5"` se leen con su moneda explícita y
  **no** se convierten a pesos, porque el tipo de cambio y su fecha no están confirmados.
- **Fecha con año de dos dígitos**: `"16/05/26"` se proyecta a 2026. Se reporta como supuesto, porque
  si algún viaje fuera de 1900 la proyección lo manda al siglo equivocado.
- **Fecha que no existe en el calendario**: un `"31/02/2026"` se rechaza en vez de "corregirse" a
  marzo.
- **Hora con AM/PM fuera de rango**: un `"13:00 PM"` se rechaza en vez de convertirlo a 25:00.
- **Dos cantidades en la celda de bultos**: `"10 cajas y 1 heladera"` no se resuelve ni suma ni
  elige: la cantidad queda en `NULL`.
- **Texto de cobro que dice "pagó" pero no es un cobro completo**: `"Pagó mitad resta factura"` se
  detecta como cobro parcial, no como cobrado, y el saldo queda sin calcular.
- **Saldo que se podría calcular pero no se debe**: el saldo solo se calcula cuando el texto dice
  que el cobro está completo, o cuando dice explícitamente cuánto se pagó antes.
- **Razón social repetida en el archivo**: se conserva la primera fila y se reporta la segunda, sin
  fusionar los datos de las dos.
- **Acentos corruptos en el archivo**: se comparan los textos sin acentos, así que un valor escrito
  con la codificación rota sigue coincidiendo con su equivalente acentuado.
- **Renglón vacío al final de la hoja**: se ignora; no se reporta como dato faltante.
- **Falta alguna de las tres hojas**: el script falla antes de migrar nada, en vez de migrar la mitad
  y dejar el archivo a medias.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El script MUST leer las tres hojas esperadas del archivo de Excel y MUST fallar con un
  error explícito antes de escribir nada si falta alguna.
- **FR-002**: La extracción MUST entregar cada fila con su número de fila original del Excel, para
  que cualquier caso reportado se pueda rastrear hasta la celda de origen.
- **FR-003**: El script MUST normalizar los tres conjuntos de datos (móviles/choferes, clientes y
  viajes) sin escribir en la base de datos, de modo que la transformación sea ejecutable y testeable
  sin conexión.
- **FR-004**: El script MUST cargar los clientes usando `ClienteRepo` de H1, construyendo la entidad
  `Cliente` a través de su API, y MUST NOT escribir `INSERT` a mano ni redefinir la entidad `Cliente`.
- **FR-005**: La carga MUST ser idempotente: correrla dos veces contra la misma base MUST NOT crear
  clientes duplicados, reconociendo los ya existentes por `razon_social_key` (comparación sin
  mayúsculas, minúsculas, acentos ni espacios sobrantes).
- **FR-006**: La carga MUST informar cuántos clientes se agregaron, cuántos se reconocieron como ya
  existentes y cuántos se omitieron por datos inválidos.
- **FR-007**: Una fila que no se puede transformar MUST omitirse sin abortar la migración de las
  demás filas, y MUST quedar registrada en la cola de revisión.
- **FR-008**: Los códigos con prefijo inconsistente MUST normalizarse a un formato único
  (`MOV-00`, `CLI-000`, `VJ-0000`), aceptando el número con o sin prefijo, con o sin guion y con
  ceros de relleno.
- **FR-009**: Un código que aparece en más de una fila MUST tratarse como el mismo registro con
  dos versiones: MUST conservar una versión como provisional y MUST reportar el choque con las
  diferencias campo por campo, sin elegir cuál versión es la vigente.
- **FR-010**: Los teléfonos MUST normalizarse dejando solo dígitos, y MUST quedar en `NULL` cuando la
  celda no contiene un teléfono (vacía, o una anotación como `"No tiene whatsapp"`).
- **FR-011**: El script MUST NOT decidir cómo se guardan los teléfonos con código de país ni qué se
  hace con el `0` inicial: esa regla sigue abierta (DD-4, AGENTS.md §11). Solo MUST marcar qué
  valores venían con prefijo internacional.
- **FR-012**: `Tipo_Vehiculo` MUST normalizarse contra un catálogo fijo de tipos de vehículo; un
  valor fuera del catálogo MUST quedar sin normalizar y MUST reportarse, sin forzar el más parecido.
- **FR-013**: `Capacidad_Carga` MUST normalizarse a kilogramos numéricos, reconociendo `kg`, `kgs`,
  `kilo(s)`, `tn`, `t`, `ton(s)`, `tonelada(s)`, con y sin unidad escrita.
- **FR-014**: Cuando `Capacidad_Carga` no trae unidad, el script MUST asumir `kg` (la unidad de todas
  las celdas que sí la traen) y MUST reportar el supuesto, porque si la celda iba en toneladas la
  capacidad quedaría 1000 veces menor.
- **FR-015**: Los montos MUST normalizarse resolviendo el separador decimal argentino (punto de
  miles, coma decimal) a un decimal en una sola moneda.
- **FR-016**: Un monto escrito en dólares MUST conservar su moneda y MUST NOT convertirse a pesos;
  MUST quedar marcado para confirmar el tipo de cambio con el cliente.
- **FR-017**: `Estado_Actual` MUST mapearse a un enum reducido (`disponible` / `ocupado` /
  `inactivo`) y el texto original MUST conservarse como observación, sin descartarse.
- **FR-018**: Un `Estado_Actual` que admite más de una lectura MUST mapearse a un estado provisional
  y MUST reportarse para confirmación.
- **FR-019**: `Condicion_IVA` MUST normalizarse contra un catálogo fijo (`Responsable Inscripto`,
  `Consumidor Final`, `Exento`), aunque la columna no tenga destino en el modelo todavía.
- **FR-020**: `ID_Cliente`, `Localidad_Barrio`, `Condicion_IVA` e `Historial_Pagos` MUST quedar
  reportadas como columnas sin mapeo, y MUST NOT agregar columnas nuevas a la entidad `Cliente`.
- **FR-021**: `Historial_Pagos` MUST conservarse íntegra como texto y MUST NOT traducirse a
  `tiene_cuenta_corriente` ni a ningún otro dato estructurado.
- **FR-022**: `Fecha_Servicio` MUST parsearse a fecha ISO reconociendo `dd/mm/aaaa`, `aaaa-mm-dd`,
  `"<día> de <mes> <año>"` y `dd/mm/aa`, probando los formatos uno por uno contra cada celda en vez
  de asumir el formato por la posición de la columna.
- **FR-023**: Un año de dos dígitos MUST proyectarse al siglo XXI siguiendo el criterio de
  `strptime("%y")`, y el caso MUST reportarse como supuesto.
- **FR-024**: Una fecha que no existe en el calendario MUST rechazarse en vez de corregirse.
- **FR-025**: `Hora_Inicio` y `Hora_Fin` MUST normalizarse a 24 horas, reconociendo el formato 12
  horas con AM/PM cuando está escrito y el 24 horas cuando no.
- **FR-026**: `Km_Recorridos` MUST normalizarse resolviendo la coma decimal argentina.
- **FR-027**: `Bultos_Estimados` MUST extraer la cantidad solo cuando la celda tiene exactamente un
  número; MUST dejar la cantidad en `NULL` cuando no hay número, cuando hay más de uno o cuando la
  celda describe un servicio en vez de bultos, conservando siempre el texto original.
- **FR-028**: `Estado_Cobro` MUST descomponerse en medio de pago, estado del cobro y saldo
  pendiente, reconociendo cada concepto por palabras clave.
- **FR-029**: `Estado_Cobro` MUST evaluarse como parcial o pendiente **antes** que como cobrado, de
  modo que un texto que dice "pagó" sin decir "pagó todo" no se cuente como cobro completo.
- **FR-030**: El saldo pendiente MUST calcularse solo cuando el texto dice que el cobro está completo
  (saldo cero), cuando dice que está pendiente (saldo igual al monto), o cuando dice explícitamente
  cuánto se pagó antes. En cualquier otro caso MUST quedar en `NULL`.
- **FR-031**: Un `Estado_Cobro` que no se puede mapear a un medio de pago o a un estado con confianza
  MUST quedar en `NULL` en ese campo y MUST reportarse, sin forzarlo a una categoría.
- **FR-032**: El cruce de viajes con choferes MUST hacerse por nombre normalizado (sin mayúsculas ni
  acentos), y MUST quedar sin resolver cuando el nombre no está en la planilla o cuando corresponde
  a más de un móvil.
- **FR-033**: Los conjuntos transformados de `Chofer`, `Vehiculo`, `Servicio` y `Pago` MUST NOT
  escribirse en la base mientras sus tablas no existan, y el reporte MUST decir cuántos quedaron
  pendientes y por qué.
- **FR-034**: El script MUST generar un reporte Markdown con, en secciones separadas: las
  transformaciones aplicadas, los casos para revisión humana, los gaps de mapeo y el resumen de lo
  cargado y lo pendiente.
- **FR-035**: Cada caso de revisión MUST citar la hoja, el número de fila original y el valor
  textual que había en la celda, para poder buscarlo en el Excel.
- **FR-036**: Los casos de revisión MUST distinguir entre los que bloquean la carga de los que solo
  necesitan confirmación.
- **FR-037**: Las funciones de normalización MUST ser puras: sin acceso a la base de datos, sin
  lectura de archivos y sin depender de la hora actual, de modo que se testeen sin fixtures.
- **FR-038**: El script MUST NOT contener reglas de negocio de la Capa de Aplicación: solo
  extracción, transformación y carga.

### Contrato de la migración

No hay contrato de API: la migración no expone endpoints. Se ejecuta desde la línea de comandos y
escribe un archivo.

```
python -m scripts.migracion                       # usa la ruta por defecto y la base de app/core/config.py
python -m scripts.migracion --archivo <ruta>      # otro archivo de Excel
python -m scripts.migracion --reporte <ruta>      # otro destino para el reporte
python -m scripts.migracion --solo-transformacion  # no toca la base: normaliza y genera el reporte
python -m scripts.migracion --simular             # no escribe nada: informa qué se cargaría
```

Artefactos: la escritura en la base y el archivo `backend/data/reporte_migracion.md`.

### Key Entities

- **Cliente** (ya existente, H1): `id`, `razon_social`, `razon_social_key`, `telefono`,
  `direccion_habitual`, `tiene_cuenta_corriente`, `activo`, `creado_en`, `actualizado_en`. Única
  entidad que esta historia escribe.
- **ClienteMigrable** (intermedio de la migración, no tabla): un cliente ya normalizado, con los
  cuatro campos que H1 define más los campos de la planilla que no tienen destino
  (`codigo_origen`, `localidad_barrio`, `condicion_iva`, `historial_pagos`), que se conservan solo
  para el reporte.
- **Movil** (intermedio, sin tabla): un móvil = un chofer con su vehículo. `codigo`, `nombre_chofer`,
  `telefono`, `tipo_vehiculo`, `capacidad_kg`, `tarifa_hora_base`, `tarifa_km_excedente`,
  `moneda_tarifa`, `estado`, `observaciones`, `filas_de_origen`.
- **Viaje** (intermedio, sin tabla): un viaje de `Registro_Viajes` normalizado, con los datos de
  `Fecha_Servicio`, horarios, kilómetros, bultos y monto, más lo que se pudo descomponer de
  `Estado_Cobro` (`pago_medio`, `pago_estado`, `pago_saldo`).
- **RevisionHumana** (cola, sin tabla): un caso que la migración no resolvió sola, con `hoja`,
  `fila`, `clave`, `motivo`, `gravedad`, `valor_original` y `detalle`.
- **Chofer**, **Vehiculo**, **TipoVehiculo**, **Servicio**, **Pago**: entidades del dominio que
  esta historia **no** define. Sus datos quedan transformados y pendientes.

### Gaps de mapeo

Columnas de la planilla que no tienen destino en el modelo actual. Se reportan en vez de resolverlas,
porque agregar una columna a una entidad ya mergeada requiere acordarlo con quien la implementó
(AGENTS.md §5):

| Columna de la planilla | Por qué no tiene destino | Qué se hace |
|---|---|---|
| `ID_Cliente` | `Cliente` genera su propio `id` con identity y no guarda el código de la planilla | Se conserva en el reporte como `codigo_origen`; no se forzó un `id` |
| `Localidad_Barrio` | No existe campo de localidad ni de barrio en `Cliente` | Se conserva en el reporte; no se agregó columna |
| `Condicion_IVA` | Los datos fiscales están fuera del alcance de H1 (se agrupan en H2) | Se normaliza a un catálogo de tres valores y se reporta, lista para H2 |
| `Historial_Pagos` | No hay ningún campo de historial de pagos; es una nota en palabras | Se conserva íntegra; no se tradujo a `tiene_cuenta_corriente` |

### Decisiones pendientes de confirmación con el cliente

Estos puntos no están confirmados por el cliente. La migración se implementa con los supuestos
temporales indicados y, si el cliente decide distinto, se actualiza primero esta sección y luego el
código (AGENTS.md §5):

- **DP-01 — Catálogos de la migración**: no existe un catálogo oficial de tipos de vehículo, de
  estados de móvil, de condiciones de IVA ni de medios de pago. Se armaron a partir de los valores
  que aparecen en la planilla. **[Supuesto temporal]**
- **DP-02 — Estado del móvil**: `"En taller hasta el martes"` se mapea a `inactivo` (el móvil no se
  puede agendar) y `"De franco"` a `disponible` (es una ausencia, no una baja). Son las lecturas
  más restrictiva y más permisiva respectivamente; ambas se reportan. **[Supuesto temporal]**
- **DP-03 — Tipo de cambio**: los valores en dólares no se convierten. Falta que el cliente indique
  el tipo de cambio y desde qué fecha se aplica. **[Supuesto temporal]**
- **DP-04 — Año de dos dígitos**: `"16/05/26"` se proyecta a 2026 con el criterio de
  `strptime("%y")`. Ningún dato de la planilla lo confirma. **[Supuesto temporal]**
- **DP-05 — Unidad implícita de la capacidad de carga**: las celdas sin unidad se asumen en `kg`.
  **[Supuesto temporal]**
- **DP-06 — Cuenta corriente a partir del historial de pagos**: se asume que un cliente migrating
  desde la planilla **no** tiene cuenta corriente. Traducir `"Fiado de palabra"` a `true` sería
  inventar la política de cuenta corriente, que sigue abierta (AGENTS.md §6). **[Supuesto temporal]**
- **DP-07 — Dirección no estructurada**: `"Retira en depósito"` no es una dirección postal, pero
  `Cliente` exige `direccion_habitual` y no tiene forma de marcarlo. Se guarda el texto tal cual y
  se reporta. **[Supuesto temporal]**
- **DP-08 — Cálculo del saldo pendiente**: se asume que el saldo solo se puede calcular cuando el
  texto del cobro lo dice. No hay regla de negocio para calcularlo por omisión. **[Supuesto
  temporal]**
- **DP-09 — Alcance de la carga**: se asume que la migración carga solo `clientes`, porque es la
  única entidad con tabla. Crear las tablas de choferes, servicios y pagos es trabajo de H4, H5/H6 y
  H10. **[Supuesto temporal]**

## Plan de implementación

*Esta sección es el resultado de `/plan`: qué capas toca la historia y por qué.*

### Capas (AGENTS.md §2)

| Capa | Se toca | Cómo |
|---|---|---|
| Presentación (`app/api/`) | **No** | La migración no expone endpoints |
| Aplicación (`app/application/`) | **No** | Ninguna regla de negocio nueva: la máquina de estados de `Servicio` y la política de cuenta corriente siguen sin implementarse |
| Dominio (`app/domain/`) | **No** | No se define ni se modifica ninguna entidad; `Cliente` se consume tal como H1 lo dejó |
| Infraestructura (`app/infrastructure/`) | **Sí, solo lectura** | Se usa `ClienteRepo` como único punto de acceso a PostgreSQL, vía la regla de oro de AGENTS.md §2 |

`backend/scripts/` queda fuera de `app/` a propósito: es código de una sola vez, no parte del
desplegable, y por eso no se mete en la pirámide de capas. Igual respeta el mismo criterio: el
script no contiene reglas de negocio, solo transformación de datos.

### Módulos

```
backend/scripts/migracion/
├── catalogos.py       # tablas de texto (tipos de vehículo, estados, IVA, medios de pago).
│                      #   PROVISIONALES: no están en ninguna spec, se arman de los valores
│                      #   de la planilla y se reportan (DP-01).
├── extraccion.py      # lectura del Excel con openpyxl. Devuelve filas con su número original.
│                      #   No normaliza ni decide nada.
├── normalizacion.py   # funciones PURAS: texto, códigos, teléfonos, fechas, horas, montos,
│                      #   capacidad, catálogos, bultos, estado de cobro. Sin base, sin
│                      #   archivos y sin hora actual.
├── transformacion.py  # cada hoja → registros normalizados + cola de revisión. No escribe nada.
├── revision.py        # la cola: qué es un caso, por qué y con qué gravedad.
├── carga.py           # ÚNICO módulo que escribe. Usa ClienteRepo. Idempotente.
├── reporte.py         # arma el Markdown del reporte.
└── __main__.py        # CLI: orquesta lectura → transformación → carga → reporte.
```

### Contrato entre los módulos

```
extraccion ──> transformacion ──> carga      (escribe en la base, vía ClienteRepo)
                      │
                      └───────> revision ──> reporte ──> backend/data/reporte_migracion.md
```

La transformación no importa nada de infraestructura ni de dominio salvo los validadores y la
clave de normalización que H1 ya definió (`TELEFONO_DIGITOS_MIN/MAX`, `normalizar_razon_social`),
que se reusan para no duplicar la regla de comparación de textos.

### Idempotencia

Se apoya en el `UNIQUE` de `razon_social_key` que H1 ya definió (DD-2): antes de insertar se consulta
`ClienteRepo.existe_razon_social`, y si ya está se reconoce el cliente y no se inserta. Un
`INSERT` directo habría duplicado clientes en cada corrida, que es exactamente lo que hace
inrecuperable una migración.

### Verificación

- **Tests unitarios** de `normalizacion.py`: fechas, montos, teléfonos, códigos, horas, capacidad,
  bultos y estado de cobro. Sin base de datos, sin fixtures, sin archivos.
- **Test de idempotencia** con un doble de `ClienteRepo` que cuenta las inserciones.
- **Trazabilidad FR ↔ test**: cada requisito funcional de la lista de arriba tiene al menos un test
  que lo cubre, igual que en H1 (T057).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los criterios de aceptación de esta spec tienen al menos un test
  automatizado que los cubre y pasa en verde.
- **SC-002**: Con la base vacía, una sola corrida del script deja los 10 clientes de
  `Clientes_Cotizaciones` consultables por `GET /api/clientes`.
- **SC-003**: Correr el script dos veces seguidas no cambia el total de clientes.
- **SC-004**: El 100 % de las celdas de las tres hojas que no se pudieron transformar aparecen en
  la sección de revisión humana del reporte, con su hoja, su fila y su valor original.
- **SC-005**: El 100 % de los textos libres que se mapearon a un valor de catálogo tienen su texto
  original conservado y visible en el reporte.
- **SC-006**: El reporte nombra explícitamente las cuatro columnas de la planilla sin destino en el
  modelo, y ninguna migración agrega columnas a `Cliente`.
- **SC-007**: Ningún monto en dólares aparece convertido a pesos en el reporte ni en la base.
- **SC-008**: Ningún cliente migrado queda con `tiene_cuenta_corriente = true`, y el 100 % de las
  notas de `Historial_Pagos` quedan íntegras en el reporte.
- **SC-009**: El script corre sin conexión a la base cuando se invoca con `--solo-transformacion`, y
  produce el mismo reporte.
- **SC-010**: El script falla con un mensaje explícito, sin escribir nada, si al archivo le falta
  alguna de las tres hojas.

## Assumptions

- La base de datos es PostgreSQL y las migraciones se gestionan con Alembic (AGENTS.md §3); el
  script usa la conexión que ya define `app/core/config.py`.
- H1 está mergeada en `main` y su tabla ya fue creada con Alembic antes de correr esta migración.
- La entidad `Cliente` no se modifica en esta historia: si aparece un campo que falta, se reporta
  como gap.
- El archivo de Excel es la fuente de verdad histórica y no se modifica.
- La migración es de una sola ejecución, ejecutada por el equipo con acceso a la base. No hay
  usuarios concurrentes migrando al mismo tiempo.
- Los catálogos de `catalogos.py` son provisorios y su confirmación corresponde a las historias que
  los van a necesitar de verdad (`TipoVehiculo` en H4, los medios de pago en H10).
- La zona horaria no afecta esta historia: las fechas se migran como fechas sin hora y las horas
  como hora local del cliente, sin convertir.