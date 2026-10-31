# Implementation Plan: 010 — Cierre de Viaje, POD y Rendición

**Branch**: `010-cierre-viaje-rendicion` | **Spec**: [spec.md](./spec.md)

**Status**: Draft — Pendiente de aprobación

## 1. Resumen técnico

Se agrega un segundo eje de estado al `Servicio` (`estado_rendicion`) y tres operaciones de negocio
dedicadas (cerrar viaje con remito, aprobar rendición, observar rendición), siguiendo el mismo
criterio que la cancelación en DD-7: **no son un simple cambio de etiqueta**, tienen su propio
endpoint y sus propias invariantes. La foto se guarda detrás de un **puerto de almacenamiento** para
poder cambiar de Base64 a la nube sin tocar Aplicación ni Dominio.

## 2. Cambios por capa

### 2.1 Dominio (`backend/app/domain/`)

- `servicio.py`:
  - Constantes `ESTADOS_RENDICION = ("pendiente", "rendido", "observado")`.
  - Campos nuevos en `Servicio`: `foto_remito_url`, `monto_cobrado_real`, `estado_rendicion`,
    `observacion_rendicion`, `rendido_en`, `rendido_por_id`.
  - `finalizar_con_remito(foto_remito_url, monto_cobrado_real, hora_fin, modificado_por_id)`:
    exige `estado == "en curso"`, URL no vacía, monto `Decimal` finito `>= 0`; pasa a
    `finalizado` + `estado_rendicion = "pendiente"`.
  - `aprobar_rendicion(usuario_id, ahora)` y `observar_rendicion(comentario, usuario_id)`:
    solo desde `pendiente` (observar) o `pendiente|observado` (aprobar).
  - **Ajuste de invariante**: hoy `_validar` prohíbe `hora_fin` fuera de `cancelado`. Se relaja a
    "`hora_fin` permitido en `cancelado` o en servicios cerrados con remito"; `motivo_cancelacion`
    sigue siendo exclusivo de `cancelado`.
- `errores.py`: `RemitoObligatorio`, `MontoCobradoInvalido` (→ 422), `RendicionNoPermitida`
  (→ 409), `ArchivoRemitoInvalido` (→ 422).

### 2.2 Aplicación (`backend/app/application/`)

- `servicios/puertos.py`: nuevo Protocol
  ```python
  class AlmacenamientoRemitos(Protocol):
      def guardar(self, *, id_servicio: int, contenido: bytes, content_type: str) -> str: ...
  ```
- `servicios/gestor_servicios.py`:
  - `finalizar_con_remito(id_servicio, contenido, content_type, monto, usuario)` — valida dueño
    (chofer asignado), tipo y tamaño, guarda la imagen vía puerto, invoca dominio, persiste.
  - `aprobar_rendicion(id_servicio, usuario_id)`, `observar_rendicion(id_servicio, comentario,
    usuario_id)`.
  - `listar_rendiciones(estado: str | None)` → items agrupables por chofer.
  - `cambiar_estado`: si `rol_usuario == "chofer"` y `estado == "finalizado"` → `PermisoDenegado`
    ("Usá el cierre con remito"). El chofer sigue pudiendo pasar a `en curso`.

### 2.3 Infraestructura (`backend/app/infrastructure/`)

- `models/servicio.py`: columnas nuevas + `CheckConstraint`s.
- `repositories/servicio_repo.py`: mapear campos nuevos; `listar_rendiciones(estado)` con join a
  `choferes`/`clientes`.
- `storage/` (nuevo):
  - `remitos_base64.py` — `AlmacenamientoBase64`: devuelve `data:<mime>;base64,<...>` (default MVP).
  - `remitos_vercel_blob.py` — `AlmacenamientoVercelBlob`: `PUT https://blob.vercel-storage.com/...`
    con `BLOB_READ_WRITE_TOKEN` usando `httpx`; devuelve URL pública. (Alternativa equivalente:
    Cloudinary con `CLOUDINARY_URL`.)
- `core/dependencias.py`: `get_almacenamiento_remitos()` elige adaptador **según el entorno**:
  si existe `BLOB_READ_WRITE_TOKEN` → Vercel Blob; si no → Base64.
- `db/bootstrap.py`: `ALTER TABLE servicios ADD COLUMN IF NOT EXISTS ...` para la base de Vercel.

### 2.4 Migración (`backend/alembic/versions/0007_cierre_viaje_rendicion.py`)

- `add_column` de las 6 columnas, FK `rendido_por_id → usuarios.id ON DELETE SET NULL`,
  `CHECK ck_servicios_estado_rendicion_valido` y `CHECK ck_servicios_rendicion_completa`.
- `downgrade` simétrico. No modifica filas existentes (todas quedan con `estado_rendicion NULL`).

### 2.5 Presentación (`backend/app/api/servicios.py` + schemas)

| Método | Ruta | Rol | Body | Respuestas |
|---|---|---|---|---|
| `POST` | `/api/servicios/{id}/finalizar` | `chofer` (asignado) | `multipart/form-data`: `foto` (file), `monto_cobrado_real` (str decimal) | 200, 403, 404, 409, 413, 422 |
| `POST` | `/api/servicios/{id}/rendicion/aprobar` | `admin` | — | 200, 403, 404, 409 |
| `POST` | `/api/servicios/{id}/rendicion/observar` | `admin` | JSON `{ "comentario": str(1..255) }` | 200, 403, 404, 409, 422 |
| `GET` | `/api/rendiciones?estado=pendiente` | `admin` | — | 200 lista agrupable por chofer |

- `ServicioRead` suma: `foto_remito_url`, `monto_cobrado_real`, `estado_rendicion`,
  `observacion_rendicion`, `rendido_en`, `rendido_por_id`.
- Requiere dependencia `python-multipart` (FastAPI la exige para `UploadFile`/`Form`).

### 2.6 Frontend — Vista Chofer

- `features/servicios/components/tarjeta-viaje-chofer.tsx`: botón **"Finalizar viaje"** visible
  solo si `estado === "en curso"`; etiqueta de rendición si ya está finalizado.
- Nuevo `features/servicios/components/dialogo-finalizar-viaje.tsx`:
  - `<input type="file" accept="image/*" capture="environment" />` (abre la cámara trasera).
  - Vista previa de la foto + campo `monto_cobrado_real` precargado con `precio_total`
    (editable), validado con Zod.
  - **Compresión en el cliente** con `<canvas>` (lado mayor 1600 px, JPEG calidad 0.7 →
    típicamente 200–400 KB) para no superar el límite de Vercel y ahorrar datos móviles.
- `features/servicios/actions.ts`: Server Action `finalizarViaje(id, formData)` que reenvía el
  `FormData` al backend con el Bearer de la cookie y hace `revalidatePath("/chofer/dashboard")`.

### 2.7 Frontend — Panel Admin "Caja y Rendiciones"

- `app/(admin)/rendiciones/page.tsx`: se reemplazan los datos hardcodeados por datos reales,
  **conservando el diseño actual** (KPIs, tabla, modales).
  - KPI "Pendiente de rendición" = suma real de montos pendientes.
  - Filas **agrupadas por chofer** con subtotal por chofer.
  - Botón "Ver remito" → modal con imagen grande.
  - Botones "Aprobar" y "Observar" (con comentario) → Server Actions + `router.refresh()`.
  - Polling cada 15 s (mismo patrón que `PortalChofer`).
- `features/rendiciones/` (nuevo slice): `actions.ts`, `components/`, `types.ts`.
- `npm run gen:api` para regenerar `openapi.d.ts`.

## 3. Almacenamiento de la foto — análisis

| Opción | Pros | Contras |
|---|---|---|
| **Base64 en la BD** (`data:` URL en `foto_remito_url`) | Cero configuración, sin cuentas externas, funciona hoy en Docker y Vercel | Infla la tabla (~300 KB por viaje); listados deben excluir la columna; **en Vercel sin Postgres externo la base vive en `/tmp` y se pierde en cada *cold start*** |
| **Vercel Blob** | Integrado al proyecto Vercel (Storage → Blob), plan gratuito, URL pública directa | Requiere crear el Blob store y `BLOB_READ_WRITE_TOKEN` |
| **Cloudinary** | Plan gratis generoso, redimensiona y optimiza imágenes solo | Cuenta externa, una credencial más |
| **AWS S3** | Estándar de la industria | Configuración más pesada (IAM, bucket, CORS); excesivo para el MVP |

**Recomendación**: implementar el **puerto** con los dos adaptadores (Base64 + Vercel Blob). Por
defecto Base64 (sale andando ya); si cargan `BLOB_READ_WRITE_TOKEN` en Vercel se pasa a la nube sin
tocar código. Para que el listado no traiga megas de Base64, `GET /api/servicios` devolverá solo
`tiene_remito: bool` y la imagen se pedirá aparte (`GET /api/servicios/{id}/remito`).

> [!WARNING]
> Mientras Vercel use la base SQLite embebida en `/tmp`, **todo** (servicios, usuarios y fotos) se
> reinicia en cada *cold start*. Para una demo con datos persistentes conviene conectar Neon
> (Vercel → Storage → Neon, gratis) además de elegir dónde van las fotos.

## 4. Tests (prioridad AGENTS.md §8)

- **Unit dominio/aplicación** (`tests/unit/test_h10_rendicion.py`), uno por escenario de la spec:
  cierre OK, sin foto, sin monto, monto negativo, chofer ajeno (403), estado inválido (409), atajo
  `PATCH estado=finalizado` bloqueado para chofer, aprobar, observar, doble aprobación (409),
  chofer intentando aprobar (403), selección de adaptador según entorno.
- **Integración** (`tests/integration/`): `POST /finalizar` multipart contra PostgreSQL real.
- **Frontend** (`frontend/tests/`): diálogo de finalizar (requiere foto y monto, envía FormData),
  panel de rendiciones (agrupa por chofer, abre modal, aprueba).
- Decisiones pendientes (admin sin remito, re-subida tras observación) →
  `pytest.mark.skip(reason="regla no confirmada por el cliente, ver spec")`.

## 5. Orden de commits propuesto

1. `docs(010): spec, plan y ssd de cierre de viaje y rendición`
2. `feat(dominio): estado de rendición y cierre con remito en Servicio`
3. `feat(db): migración 0007 y columnas de rendición en ServicioORM + bootstrap`
4. `feat(api): endpoints finalizar, aprobar y observar con puerto de almacenamiento`
5. `feat(chofer): diálogo de finalizar viaje con cámara y compresión`
6. `feat(rendiciones): panel Caja y Rendiciones con datos reales`
7. `test(010): unitarios backend y frontend`

## 6. Riesgos

- **Límite de body en Vercel (~4.5 MB)** → compresión obligatoria en el cliente + validación 4 MB
  en backend.
- **HEIC de iPhone**: `accept="image/*"` con canvas lo convierte a JPEG en la mayoría de los
  navegadores móviles; si el navegador no puede decodificarlo se envía el original y el backend lo
  acepta igual.
- **Compatibilidad hacia atrás**: todas las columnas nuevas son `NULL`; servicios previos no se
  ven afectados y los tests actuales no cambian (salvo el del atajo del chofer, que se actualiza
  porque la regla cambia por spec).
