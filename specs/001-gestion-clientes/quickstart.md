# Quickstart: H1 — Gestión de Clientes

Guía para levantar el entorno y probar los cinco endpoints de la gestión de clientes de
Fletes y Mudanzas Express. Vale para el backend tal como quedó al cierre de H1.

## Prerrequisitos

- Docker Desktop (o Docker Engine) y Docker Compose.
- Opcional, para correr el backend fuera de Docker: Python 3.12 y PostgreSQL en la misma máquina.

## Opción A — Todo con Docker (recomendado)

```bash
# 1. Levantar PostgreSQL + backend (el primer build tarda unos minutos)
docker compose up -d --build

# 2. Aplicar las migraciones a la base (solo la primera vez)
docker compose exec backend alembic upgrade head

# 3. Swagger/OpenAPI
open http://localhost:8000/docs
```

- `GET /health` → `{"estado":"ok"}`.
- El backend de compose se conecta a `postgres:5432` por la red interna de Compose, así que
  los datos persisten en el volumen `postgres_data` aunque reinicies el contenedor. Para
  verificarlo: creá un cliente, `docker compose restart backend` y volvelo a consultar.

## Opción B — Backend local (sin Docker)

```bash
# 1. Crear y activar el entorno (Windows: .venv\Scripts\activate)
python -m venv .venv
pip install -e ".[dev]"

# 2. Configurar la conexión a PostgreSQL
Copy-Item .env.example .env    # Windows
# cp .env.example .env          # Linux/macOS

# 3. Migraciones y servidor
alembic upgrade head
uvicorn app.main:app --reload
```

El `.env` apunta a `postgresql+psycopg://fletes:fletes@localhost:5432/fletes`; ajusted el
puerto/créditos si tu PostgreSQL corre en otro lado.

## Autenticación (stub hasta la historia de autenticación)

El rol va en el header `X-Rol` (ver DD-3 en AGENTS.md §11). No se valida ningún token todavía:

- `X-Rol: admin` → puede crear, listar, ver, modificar y eliminar.
- `X-Rol: chofer` → solo listar y ver detalle (403 en las escrituras).

## Probar los 5 endpoints

```bash
BASE=http://localhost:8000/api/clientes
ADMIN_H="X-Rol: admin"
CHOFER_H="X-Rol: chofer"
BODY='{"razon_social":"Distribuidora del Sur S.A.","telefono":"351 555 0100","direccion_habitual":"Av. Colón 1250, Córdoba","tiene_cuenta_corriente":true}'
```

### 1. Crear un cliente — `POST /api/clientes` (admin) → `201`

```bash
curl -s -X POST "$BASE" -H "$ADMIN_H" -H "Content-Type: application/json" -d "$BODY"
```

Respuesta: el cliente con `id`, `creado_en`, `actualizado_en` y `activo=true` generados por el
sistema. Guardá el `id` para los pasos siguientes.

### 2. Listar y filtrar — `GET /api/clientes` (admin o chofer) → `200`

```bash
curl -s "$BASE" -H "$ADMIN_H"                 # página 1, 20 por página
curl -s "$BASE?q=distribuidora&page=1&size=5" -H "$ADMIN_H"
```

`q` ignora mayúsculas/accentos; el total que cumple el filtro viene en `total`.

### 3. Ver detalle — `GET /api/clientes/{id}` (admin o chofer) → `200`

```bash
curl -s "$BASE/1" -H "$ADMIN_H"
```

Un cliente dado de baja (o un id inexistente) responde `404`.

### 4. Modificar — `PUT /api/clientes/{id}` (admin) → `200`

```bash
curl -s -X PUT "$BASE/1" -H "$ADMIN_H" -H "Content-Type: application/json" \
  -d '{"razon_social":"Distribuidora del Sur S.A.","telefono":"351 555 0199","direccion_habitual":"Av. Colón 1250, Córdoba","tiene_cuenta_corriente":true}'
```

Es un `PUT` completo (DD-5): el body repite los cuatro datos. La fecha de modificación se
actualiza aunque los datos no cambien.

### 5. Eliminar — `DELETE /api/clientes/{id}` (admin) → `204` sin cuerpo

```bash
curl -s -o NUL -w "%{http_code}" -X DELETE "$BASE/1" -H "$ADMIN_H"
```

La baja es lógica (DD-1): la fila queda con `activo=false`, el listado y el detalle dejan de
mostrarla, y la razón social sigue reservada. Eliminar dos veces responde `204` igual.

## Errores esperados

| Código | Cuándo |
|---|---|
| `403` | El rol no permite la operación (chofer intenta escribir) |
| `404` | Id inexistente (o cliente dado de baja) |
| `409` | Razón social duplicada, o baja de un cliente con historial (aún sin servicios, FR-015 queda testeado con un doble) |
| `422` | Algún dato faltante o inválido (no se persiste nada) |

## Tests

```bash
cd backend
pytest tests/unit          # Capa de Aplicación, sin PostgreSQL (prioridad §8)
pytest tests/integration   # contra PostgreSQL real (base fletes_test, se crea sola)
ruff check app tests       # lint
ruff format --check app tests
```

Los tests de integración usan una base propia (`fletes_test`) que el conftest crea
automáticamente: nunca tocan los datos de desarrollo.