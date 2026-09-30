# Reporte de migración de datos históricos

- **Archivo de origen**: `C:\Users\pikor\OneDrive\Documentos\Fletes_y_Mudanzas_PPP_Trabajo_Practico\raw-data\Caso 2 Fletes_Mudanzas_Express_Datos.xlsx`
- **Generado**: 2026-09-30
- **Filas leídas**: 10 clientes, 8 móviles, 10 viajes
- **Casos para revisión humana**: 37 (5 bloqueantes, 32 para confirmar)

> Los casos de esta revisión se dejaron **a propósito**: donde el dato era ambiguo, la migración lo dejó señalado en vez de inventar una regla de negocio (AGENTS.md §6).

## Resumen

| Conjunto | Registros | Destino | Estado |
| --- | --- | --- | --- |
| Clientes | 10 | tabla `clientes` | cargados: **0**, ya existentes: **10**, omitidos: **0** |
| Móviles / choferes | 8 | tabla `choferes` + `vehiculos` | **pendiente: la tabla no existe** |
| Viajes / servicios | 10 | tabla `servicios` | **pendiente: la tabla no existe** |
| Pagos | 10 (derivados de `Estado_Cobro`) | tabla `pagos` | **pendiente: la tabla no existe** |

Las tres últimas filas no se escribieron. Crear esas tablas implica decidir la máquina de estados de `Servicio` y el catálogo de medios de pago, que el cliente todavía no confirmó (AGENTS.md §6). Los datos ya están normalizados y probados: cuando esas historias existan, solo hay que agregar el módulo de carga correspondiente, sin tocar la normalización.

## Textos que se conservaron como observación

Estos valores se mapearon a un valor de catálogo, pero el texto original queda guardado porque es la única evidencia de qué quiso decir quien llevaba la planilla.

- Móvil `MOV-01` (Marcelo Rodriguez): estado `disponible` — texto original: «Disponible»
- Móvil `MOV-02` (El Ruso): estado `inactivo` — texto original: «En taller hasta el martes»
- Móvil `MOV-03` (Cacho Benitez): estado `disponible` — texto original: «Libre»
- Móvil `MOV-04` (Hernan Perez): estado `disponible` — texto original: «Disponible»
- Móvil `MOV-05` (Jorge 'El Negro'): estado `inactivo` — texto original: «Suspendido por choque»
- Móvil `MOV-06` (Tito): estado `disponible` — texto original: «Disponible»
- Móvil `MOV-07` (Esteban Quito): estado `disponible` — texto original: «De franco»
- Móvil `MOV-08` (Santi Gonzalez): estado `disponible` — texto original: «Disponible»
- Viaje `VJ-2002`: bultos sin cantidad — texto original: «10 cajas y 1 heladera»
- Viaje `VJ-2003`: bultos sin cantidad — texto original: «Archivadores pesados»
- Viaje `VJ-2004`: bultos sin cantidad — texto original: «4 mancuernas y 2 bancos»
- Viaje `VJ-2006`: bultos sin cantidad — texto original: «Sonido y luces»
- Viaje `VJ-2007`: bultos sin cantidad — texto original: «Mudanza de depto chico»
- Viaje `VJ-2009`: bultos sin cantidad — texto original: «Bolsas de harina»
- Viaje `VJ-2010`: bultos sin cantidad — texto original: «1 sillon 3 cuerpos»

## Transformaciones aplicadas

Cada fila dice de qué columna sale el dato, cómo queda después y por qué se normaliza así.

| Hoja | Columna | Normalización | Criterio |
| --- | --- | --- | --- |
| Choferes_y_Moviles | `Cod_Movil` | `MOV-01` | Se normaliza a `MOV-00`, aceptando el número con o sin prefijo, con o sin guion y con ceros de relleno: `"MOV-01"`, `"MOV01"` y `"03"` son el mismo código. |
| Choferes_y_Moviles | `Nombre_Chofer` | minúsculas, sin acentos | Solo para comparar. El nombre que se muestra se conserva tal como está escrito. |
| Choferes_y_Moviles | `Telefono_Contacto` | solo dígitos | Se quitan `+`, espacios y guiones. Las anotaciones que no son un teléfono quedan en `NULL`. No se decide cómo se guardan los teléfonos con código de país: esa regla sigue abierta. |
| Choferes_y_Moviles | `Tipo_Vehiculo` | catálogo fijo | Se resuelve contra un catálogo de tipos de vehículo. Un valor fuera del catálogo queda sin normalizar y se reporta, sin forzar el más parecido. |
| Choferes_y_Moviles | `Capacidad_Carga` | kilogramos | `kg`, `kgs`, `kilo(s)` valen 1; `tn`, `t`, `ton(s)`, `tonelada(s)` valen 1000. Las celdas sin unidad se asumen en kg y se reportan como supuesto. |
| Choferes_y_Moviles | `Tarifa_Hora_Base`, `Tarifa_Km_Excedente` | decimal con moneda explícita | Se resuelve el separador argentino (punto de miles, coma decimal). Los valores en dólares conservan su moneda y **no** se convierten: falta el tipo de cambio. |
| Choferes_y_Moviles | `Estado_Actual` | `disponible` / `ocupado` / `inactivo` | Se mapea al enum reducido y el texto original se conserva como observación. Los textos que admiten más de una lectura se mapean a un estado provisional y se reportan. |
| Clientes_Cotizaciones | `ID_Cliente` | `CLI-000` | Se normaliza el prefijo para poder detectar filas repetidas. **No** se usa como `id`: `Cliente` genera el suyo. |
| Clientes_Cotizaciones | `Nombre_o_Empresa` | minúsculas, sin acentos | Solo para comparar contra `razon_social_key`, que es el `UNIQUE` de H1 (DD-2). El texto que se muestra no se toca. |
| Clientes_Cotizaciones | `Telefono` | solo dígitos | Igual que el de los choferes. |
| Clientes_Cotizaciones | `Direccion_Habitual` | sin cambios | Se conserva tal cual. Los valores que no son una dirección postal (por ejemplo una instrucción de retiro) se marcan, porque `Cliente` no tiene forma de distinguirlos. |
| Clientes_Cotizaciones | `Condicion_IVA` | catálogo fijo | Se resuelve contra `Responsable Inscripto` / `Consumidor Final` / `Exento`. No tiene destino en el modelo todavía, pero se normaliza para cuando exista. |
| Clientes_Cotizaciones | `Historial_Pagos` | sin cambios | Es una nota en palabras, no un dato estructurado. **No** se traduce a `tiene_cuenta_corriente` ni a nada más: ese campo queda siempre en `false`. |
| Registro_Viajes | `Nro_Viaje` | `VJ-0000` | Mismo criterio que `Cod_Movil`, con ancho de 4 dígitos. |
| Registro_Viajes | `Fecha_Servicio` | fecha ISO | Se prueban los cuatro formatos contra cada celda y gana el que encaja, así que el formato se detecta por contenido y no por posición de columna. Los años de dos dígitos se proyectan al siglo XXI y se reportan como supuesto. |
| Registro_Viajes | `Hora_Inicio`, `Hora_Fin` | 24 horas | Se reconoce el formato 12 horas con AM/PM cuando está escrito. Una hora con AM/PM fuera del rango 1-12 se rechaza en vez de 'corregirse'. |
| Registro_Viajes | `Km_Recorridos` | decimal con punto | Se resuelve la coma decimal argentina. |
| Registro_Viajes | `Bultos_Estimados` | entero o `NULL` | Solo se extrae la cantidad cuando hay **exactamente un** número. Sin número, con más de uno, o cuando la celda describe un servicio, queda en `NULL` y el texto se conserva. |
| Registro_Viajes | `Monto_Cobrado` | decimal con moneda explícita | Igual que las tarifas. Los dólares no se convierten. |
| Registro_Viajes | `Estado_Cobro` | medio de pago + estado + saldo | La celda mezcla tres conceptos y se separan por palabras clave. Se evalúa como parcial o pendiente **antes** que como cobrado, para que un texto que dice 'pagó' sin decir 'pagó todo' no cuente como cobro completo. El saldo solo se calcula cuando el texto lo dice. |

Los catálogos que usó la migración **no están confirmados por el cliente** (DP-01). Se armaron a partir de los valores que aparecen en la planilla.

- Tipos de vehículo: Utilitario, Furgón Chico, Furgón Mediano, Furgón Grande, Camioneta, Camioneta Mediana, Camioneta Grande, Camión Mudancero
- Estados de móvil: disponible, ocupado, inactivo
- Condiciones de IVA: Responsable Inscripto, Consumidor Final, Exento
- Medios de pago (PROPUESTOS, no confirmados): Efectivo, Transferencia bancaria, Cheque
- Estados de cobro: cobrado, parcial, pendiente

Cuando la historia que modele cada entidad (H4 para choferes y vehículos, H10 para pagos) defina su catálogo propio, estos valores se reemplazan por los de esa spec.

## Casos para revisión humana

Quedaron **37 casos** para que una persona los resuelva. Cada uno cita la hoja, el número de fila del Excel y el valor que había, para poder buscarlo en la planilla.

## Bloqueantes (5)

Estos casos impiden que el dato llegue a su destino con un valor confiable. Hay que resolverlos antes de que la base sea la fuente de verdad.

| Hoja | Fila | Clave | Motivo | Valor original | Qué pasó |
| --- | --- | --- | --- | --- | --- |
| Choferes_y_Moviles | 8 | `MOV-05` | moneda_extranjera | `U$S 15` | El valor está en dólares (15 USD). No se convirtió a pesos: falta que el cliente confirme el tipo de cambio y desde qué fecha se aplica. |
| Choferes_y_Moviles | 8 | `MOV-05` | moneda_extranjera | `U$S 0.5` | El valor está en dólares (0.5 USD). No se convirtió a pesos: falta que el cliente confirme el tipo de cambio y desde qué fecha se aplica. |
| Choferes_y_Moviles | 2 | `MOV-01` | duplicado | `Marcelo Rodriguez; MARCELO RODRIGUEZ` | El código MOV-01 aparece en las filas 2, 3 del Excel, con nombres «Marcelo Rodriguez; MARCELO RODRIGUEZ». Se trataron como el mismo móvil con dos versiones y se conservó la primera fila como provisional; NO se decidió cuál es la vigente. Difieren en: teléfono: fila 2 «11-4455-6677» vs fila 3 «+5491144556677»; capacidad de carga: fila 2 «1500 kg» vs fila 3 «1,5 tn»; tarifa por hora: fila 2 «$12.500» vs fila 3 «12500»; tarifa por km: fila 2 «$450» vs fila 3 «450,00»; estado: fila 2 «Disponible» vs fila 3 «En viaje». |
| Choferes_y_Moviles | 7 | `MOV-05` | duplicado | `Jorge 'El Negro'; Jorge Almada` | El código MOV-05 aparece en las filas 7, 8 del Excel, con nombres «Jorge 'El Negro'; Jorge Almada». Se trataron como el mismo móvil con dos versiones y se conservó la primera fila como provisional; NO se decidió cuál es la vigente. Difieren en: nombre del chofer: fila 7 «Jorge 'El Negro'» vs fila 8 «Jorge Almada»; teléfono: fila 7 «15-2233-4455» vs fila 8 «+54 9 11 2233 4455»; tipo de vehículo: fila 7 «Camión Mudancero» vs fila 8 «Camion 3500kg»; capacidad de carga: fila 7 «3,5 toneladas» vs fila 8 «3500»; tarifa por hora: fila 7 «18.000,50» vs fila 8 «U$S 15»; tarifa por km: fila 7 «650,50» vs fila 8 «U$S 0.5»; estado: fila 7 «Suspendido por choque» vs fila 8 «Rompió el elástico». |
| Clientes_Cotizaciones | 6 | `CLI-105` | direccion_no_estructurada | `Retira en depósito` | «Retira en depósito» no es una dirección postal sino una instrucción de retiro. El `Cliente` de H1 exige `direccion_habitual` y no tiene forma de marcar que el texto no es una dirección, así que se conservó tal cual. Hay que acordarlo con quien hizo H1: agregar un campo, o aceptar el texto libre con una convención. |

## Para confirmar (32)

El dato se cargó o se transformó con un supuesto explícito. Conviene revisarlos, pero no frena la migración.

| Hoja | Fila | Clave | Motivo | Valor original | Qué pasó |
| --- | --- | --- | --- | --- | --- |
| Choferes_y_Moviles | 4 | `MOV-02` | texto_ambiguo | `En taller hasta el martes` | «En taller hasta el martes» admite más de una lectura (disponible / ocupado / inactivo). Se mapeó provisionalmente a «inactivo» y el texto original queda como observación. |
| Choferes_y_Moviles | 5 | `MOV-03` | unidad_implicita | `1000` | La celda no dice la unidad: se asumió kg. Si era toneladas, la capacidad quedó 1000 veces menor. |
| Choferes_y_Moviles | 8 | `MOV-05` | unidad_implicita | `3500` | La celda no dice la unidad: se asumió kg. Si era toneladas, la capacidad quedó 1000 veces menor. |
| Choferes_y_Moviles | 9 | `MOV-06` | dato_incompleto | `No tiene whatsapp` | El teléfono se guardó vacío porque «No tiene whatsapp» no es un teléfono, es una anotación. |
| Choferes_y_Moviles | 9 | `MOV-06` | unidad_implicita | `600` | La celda no dice la unidad: se asumió kg. Si era toneladas, la capacidad quedó 1000 veces menor. |
| Choferes_y_Moviles | 10 | `MOV-07` | texto_ambiguo | `De franco` | «De franco» admite más de una lectura (disponible / ocupado / inactivo). Se mapeó provisionalmente a «disponible» y el texto original queda como observación. |
| Clientes_Cotizaciones | 2 | `columna `ID_Cliente`` | sin_mapeo_en_modelo | `10 celdas (filas 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)` | El `Cliente` de H1 genera su propio `id` con identity y no guarda el código de la planilla. No se forzó un id ni se agregó una columna. No se agregó la columna ni se descartó el valor. |
| Clientes_Cotizaciones | 2 | `columna `Localidad_Barrio`` | sin_mapeo_en_modelo | `10 celdas (filas 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)` | No existe un campo de localidad ni de barrio en el `Cliente` de H1. No se agregó la columna ni se descartó el valor. |
| Clientes_Cotizaciones | 2 | `columna `Condicion_IVA`` | sin_mapeo_en_modelo | `10 celdas (filas 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)` | Los datos fiscales están explícitamente fuera del alcance de H1 (se agrupan en H2). La columna sí se normalizó, a un catálogo de tres valores. No se agregó la columna ni se descartó el valor. |
| Clientes_Cotizaciones | 2 | `columna `Historial_Pagos`` | sin_mapeo_en_modelo | `10 celdas (filas 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)` | No hay ningún campo de historial de pagos. Es una nota en palabras, no un dato estructurado, así que no se tradujo a `tiene_cuenta_corriente` ni a ninguna otra cosa. No se agregó la columna ni se descartó el valor. |
| Registro_Viajes | 3 | `VJ-2002` | texto_ambiguo | `10 cajas y 1 heladera` | «10 cajas y 1 heladera» tiene 2 cantidades (10, 1) y no se sabe cuál es la cantidad de bultos. No se suman ni se elige una. Se dejó `bultos_estimados` en NULL y el texto original se conserva para que alguien lo lea. |
| Registro_Viajes | 3 | `VJ-2002` | texto_ambiguo | `Efectivo chofer en mano` | «Efectivo chofer en mano» no dice si el cobro quedó completo, a medias o pendiente. No se asume, así que el saldo queda sin calcular. |
| Registro_Viajes | 4 | `VJ-2003` | texto_ambiguo | `Archivadores pesados` | «Archivadores pesados» no dice cuántos bultos son Se dejó `bultos_estimados` en NULL y el texto original se conserva para que alguien lo lea. |
| Registro_Viajes | 4 | `VJ-2003` | texto_ambiguo | `Pagó mitad resta factura` | «Pagó mitad resta factura»: Dice que se pagó la mitad, pero no dice con qué medio ni si la factura por el resto cuenta como cobrado. El saldo queda sin calcular a propósito. |
| Registro_Viajes | 4 | `VJ-2003` | texto_ambiguo | `Pagó mitad resta factura` | «Pagó mitad resta factura» no dice con qué medio se cobró. No se fuerza a Efectivo ni a Transferencia. |
| Registro_Viajes | 5 | `VJ-2004` | supuesto_de_anio | `16/05/26` | La fecha «16/05/26» trae un año de dos dígitos y se proyectó a 2026 (mismo criterio que `strptime('%y')`). Si algún viaje fuera de 1900, la proyección lo manda al siglo equivocado. |
| Registro_Viajes | 5 | `VJ-2004` | texto_ambiguo | `4 mancuernas y 2 bancos` | «4 mancuernas y 2 bancos» tiene 2 cantidades (4, 2) y no se sabe cuál es la cantidad de bultos. No se suman ni se elige una. Se dejó `bultos_estimados` en NULL y el texto original se conserva para que alguien lo lea. |
| Registro_Viajes | 5 | `VJ-2004` | texto_ambiguo | `Seña $5000 debe el resto` | «Seña $5000 debe el resto»: El monto de la seña está explícito pero el medio de pago no. El saldo sí se puede calcular. |
| Registro_Viajes | 5 | `VJ-2004` | texto_ambiguo | `Seña $5000 debe el resto` | «Seña $5000 debe el resto» no dice con qué medio se cobró. No se fuerza a Efectivo ni a Transferencia. |
| Registro_Viajes | 6 | `VJ-2005` | texto_ambiguo | `Anotado en la libreta` | «Anotado en la libreta»: No dice medio de pago ni si el cobro está completo. 'La libreta' podría ser la libreta de cuenta corriente del cliente o el cuaderno del chofer: son dos cosas distintas. |
| Registro_Viajes | 6 | `VJ-2005` | texto_ambiguo | `Anotado en la libreta` | «Anotado en la libreta» no dice con qué medio se cobró. No se fuerza a Efectivo ni a Transferencia. |
| Registro_Viajes | 6 | `VJ-2005` | texto_ambiguo | `Anotado en la libreta` | «Anotado en la libreta» no dice si el cobro quedó completo, a medias o pendiente. No se asume, así que el saldo queda sin calcular. |
| Registro_Viajes | 7 | `VJ-2006` | texto_ambiguo | `Sonido y luces` | «Sonido y luces» describe un servicio, no una cantidad de bultos. No se extrajo ningún número. Se dejó `bultos_estimados` en NULL y el texto original se conserva para que alguien lo lea. |
| Registro_Viajes | 7 | `VJ-2006` | texto_ambiguo | `Cheque diferido` | «Cheque diferido»: El medio es cheque, pero 'diferido' no aclara si el cheque está en poder del cliente o si la fecha de cobro vence dentro o fuera del período. No se fuerza el saldo. |
| Registro_Viajes | 8 | `VJ-2007` | texto_ambiguo | `Mudanza de depto chico` | «Mudanza de depto chico» describe un servicio, no una cantidad de bultos. No se extrajo ningún número. Se dejó `bultos_estimados` en NULL y el texto original se conserva para que alguien lo lea. |
| Registro_Viajes | 9 | `VJ-2008` | texto_ambiguo | `Cta Cte` | «Cta Cte»: Es una condición de pago, no un medio de pago. No se sabe si el cobro se hizo y por qué medio, ni si se emitió factura. |
| Registro_Viajes | 9 | `VJ-2008` | texto_ambiguo | `Cta Cte` | «Cta Cte» no dice con qué medio se cobró. No se fuerza a Efectivo ni a Transferencia. |
| Registro_Viajes | 9 | `VJ-2008` | texto_ambiguo | `Cta Cte` | «Cta Cte» no dice si el cobro quedó completo, a medias o pendiente. No se asume, así que el saldo queda sin calcular. |
| Registro_Viajes | 10 | `VJ-2009` | texto_ambiguo | `Bolsas de harina` | «Bolsas de harina» no dice cuántos bultos son Se dejó `bultos_estimados` en NULL y el texto original se conserva para que alguien lo lea. |
| Registro_Viajes | 11 | `VJ-2010` | texto_ambiguo | `1 sillon 3 cuerpos` | «1 sillon 3 cuerpos» tiene 2 cantidades (1, 3) y no se sabe cuál es la cantidad de bultos. No se suman ni se elige una. Se dejó `bultos_estimados` en NULL y el texto original se conserva para que alguien lo lea. |
| Registro_Viajes | 11 | `VJ-2010` | texto_ambiguo | `Seña 50%` | «Seña 50%»: El porcentaje está explícito pero el medio de pago no. El saldo sí se puede calcular. |
| Registro_Viajes | 11 | `VJ-2010` | texto_ambiguo | `Seña 50%` | «Seña 50%» no dice con qué medio se cobró. No se fuerza a Efectivo ni a Transferencia. |

## Gaps de mapeo

Estas columnas de la planilla **no tienen destino** en el modelo que existe hoy. No se agregó ninguna columna a las entidades: hacer eso requiere acordarlo con quien implementó H1, y decidirlo desde una migración no corresponde (AGENTS.md §5).

| Columna | Por qué no tiene destino | Qué se hizo |
| --- | --- | --- |
| `ID_Cliente` | El `Cliente` de H1 genera su propio `id` con identity y no guarda el código de la planilla. No se forzó un id ni se agregó una columna. | Se conserva el valor en este reporte. |
| `Localidad_Barrio` | No existe un campo de localidad ni de barrio en el `Cliente` de H1. | Se conserva el valor en este reporte. |
| `Condicion_IVA` | Los datos fiscales están explícitamente fuera del alcance de H1 (se agrupan en H2). La columna sí se normalizó, a un catálogo de tres valores. | Se conserva el valor en este reporte. |
| `Historial_Pagos` | No hay ningún campo de historial de pagos. Es una nota en palabras, no un dato estructurado, así que no se tradujo a `tiene_cuenta_corriente` ni a ninguna otra cosa. | Se conserva el valor en este reporte. |
