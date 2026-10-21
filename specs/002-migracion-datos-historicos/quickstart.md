# Quickstart: H13 — Migración de datos históricos

Guía para correr el script que lleva los datos del Excel del cliente al modelo relacional.
Vale para el backend tal como quedó al cierre de H13.

## Prerrequisitos

- El archivo del cliente en `raw-data/Caso 2 Fletes_Mudanzas_Express_Datos.xlsx`. No está en el
  repo (es insumo de la cátedra): si falta, el script lo dice y termina.
- Python 3.12+ y las dependencias del backend (`pip install -e ".[dev]"` desde `backend/`).
- PostgreSQL **solo** para los modos que escriben. Ver "Sin base de datos" más abajo.

## Los tres modos

Desde `backend/`:

### 1. Solo transformación — no necesita PostgreSQL

```bash
python -m scripts.migracion --solo-transformacion
```

Lee el Excel, normaliza las tres hojas y escribe `backend/data/reporte_migracion.md`. No abre
conexión a la base. Es el modo para ver el reporte y el que puede correr en CI.

### 2. Simular — se conecta, no escribe

```bash
python -m scripts.migracion --simular
```

Conecta y lee la base para saber qué clientes ya existen, e informa cuántos se cargarían, sin
insertar nada. Sirve para ver el plan de carga contra la base real.

### 3. Cargar — escribe de verdad

```bash
python -m scripts.migracion
```

Carga los clientes que falten. Es idempotente: podés correrlo las veces que quieras, los que ya
están se reconocen por `razon_social_key` y no se duplican. Para verificarlo:

```bash
python -m scripts.migracion   # 1ª vez: N clientes cargados
python -m scripts.migracion   # 2ª vez: 0 cargados, N ya existentes
```

## Otros parámetros

| Flag | Para qué |
|---|---|
| `--archivo RUTA` | Usar otro archivo de Excel en vez del de `raw-data/`. |
| `--reporte RUTA` | Escribir el reporte en otro lado. Por defecto `backend/data/reporte_migracion.md`. |

## Prerrequisitos de la base

La tabla `clientes` tiene que existir (la crea H1):

```bash
alembic upgrade head
```

## Sin base de datos

Si no tenés PostgreSQL a mano, el modo 1 te alcanza para todo lo que esta historia verifica. Para
probar la idempotencia contra el repositorio real sin tocar una base instalada:

```bash
python -m pytest tests/unit/scripts/migracion/test_carga.py
```

## Qué se carga y qué no

**Se carga**: los clientes, por `ClienteRepo` (el mismo de H1). Nada más.

**No se carga todavía**: choferes, vehículos, servicios y pagos. Esas tablas no existen en el
modelo todavía, y crearlas implicaría decidir la máquina de estados de `Servicio` y el catálogo de
medios de pago, que el cliente todavía no confirmó (`AGENTS.md` §6).

Los datos de esas hojas **sí están transformados y probados**: cuando las historias de esos modelos
existan, solo hay que agregar el módulo de carga correspondiente, sin tocar la normalización.

## Antes de tomar la base como fuente de verdad

El reporte tiene una sección de casos **bloqueantes** (5 en el archivo del cliente) y otra de casos
que solo necesitan confirmación (32). Los bloqueantes son:

- 2 móviles duplicados por código: `MOV-01` (`MOV-01`/`MOV01`) y `MOV-05` (dos nombres distintos).
- 2 montos en dólares (`U$S`), sin tipo de cambio confirmado.
- 1 dirección no estructurada: `"Retira en depósito"`.

Mientras esos estén sin resolver, la base no tiene por qué ser la fuente de verdad: el reporte
cita siempre hoja, número de fila del Excel y valor original, para que cada caso se pueda buscar
en la planilla.