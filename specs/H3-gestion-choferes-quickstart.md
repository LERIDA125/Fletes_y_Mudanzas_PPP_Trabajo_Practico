# Quickstart: H3 — Gestión de Choferes

Guía para levantar el entorno y probar los cinco endpoints de la gestión de choferes de
Fletes y Mudanzas Express.

## Prerrequisitos

- Docker Desktop (o Docker Engine) y Docker Compose.
- Opcional, para correr el backend fuera de Docker: Python 3.12 y PostgreSQL en la misma máquina.

## Opción A — Todo con Docker (recomendado)

```bash
# 1. Levantar PostgreSQL + backend (el primer build tarda unos minutos)
docker compose up -d --build

# 2. Aplicar las migraciones a la base (incluye la que completa la tabla de choferes)
docker compose exec backend alembic upgrade head

# 3. Swagger/OpenAPI
open http://localhost:8000/docs
```

- `GET /health` → `{"estado":"ok"}`.

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

## Autenticación (stub hasta la historia de autenticación)

El rol va en el header `X-Rol` (ver DD-3 en AGENTS.md §11). No se valida ningún token todavía:

- `X-Rol: admin` → puede crear, listar, ver, modificar y dar de baja.
- `X-Rol: chofer` → solo listar y ver detalle (403 en las escrituras).

## Probar los 5 endpoints

```bash
BASE=http://localhost:8000/api/choferes
ADMIN_H="X-Rol: admin"
CHOFER_H="X-Rol: chofer"
BODY='{"nombre_completo":"Juan Pérez","telefono":"351 555 0100"}'
```

### 1. Crear un chofer — `POST /api/choferes` (admin) → `201`

```bash
curl -s -X POST "$BASE" -H "$ADMIN_H" -H "Content-Type: application/json" -d "$BODY"
```

Respuesta: el chofer con `id`, `creado_en`, `actualizado_en`, `activo=true` y
`saldo_a_favor=0.0` generados por el sistema. `activo` y `saldo_a_favor` no se mandan en el body
(el schema los rechaza con `422`). Guardá el `id` para los pasos siguientes.

### 2. Listar y filtrar — `GET /api/choferes` (admin o chofer) → `200`

```bash
curl -s "$BASE" -H "$ADMIN_H"                 # página 1, 20 por página
curl -s "$BASE?q=juan&page=1&size=5" -H "$ADMIN_H"
```

Devuelve solo choferes **activos**; `q` ignora mayúsculas; el total que cumple el filtro viene en
`total`.

### 3. Ver detalle — `GET /api/choferes/{id}` (admin o chofer) → `200`

```bash
curl -s "$BASE/1" -H "$ADMIN_H"
```

Un chofer dado de baja (o un id inexistente) responde `404`.

### 4. Modificar — `PUT /api/choferes/{id}` (admin) → `200`

```bash
curl -s -X PUT "$BASE/1" -H "$ADMIN_H" -H "Content-Type: application/json" \
  -d '{"nombre_completo":"Juan Pérez","telefono":"351 555 0199"}'
```

Es un `PUT` completo (DD-5): el body repite los dos datos. La fecha de modificación se actualiza
aunque los datos no cambien; `saldo_a_favor` y `activo` no se tocan.

### 5. Dar de baja — `DELETE /api/choferes/{id}` (admin) → `204` sin cuerpo

```bash
curl -s -o NUL -w "%{http_code}" -X DELETE "$BASE/1" -H "$ADMIN_H"
```

La baja es lógica (DD-1): la fila queda con `activo=false`, el listado y el detalle dejan de
mostrarla, y el registro conserva su `id`, su fecha de creación y su `saldo_a_favor`. Dar de baja
dos veces responde `404` la segunda vez.

## Errores esperados

| Código | Cuándo |
|---|---|
| `403` | El rol no permite la operación (chofer intenta escribir) |
| `404` | Id inexistente o chofer dado de baja (detalle, modificación y baja repetida) |
| `422` | Nombre o teléfono faltante/inválido, o intento de mandar `activo`/`saldo_a_favor` |

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
