# Quickstart: H8 — Gestión de Servicios, Cotizaciones y Operaciones

Guía para levantar el frontend Next.js y el backend FastAPI de **Fletes y Mudanzas Express**, probar las vistas operativas (Dashboard, Agenda, Clientes, Choferes, Vehículos, Cotizaciones, Servicios y Rendiciones) y verificar el funcionamiento del Modo Oscuro.

---

## 1. Prerrequisitos

- **Node.js**: v20+ o v22+ con `npm`.
- **Python**: v3.12+ (para el backend).
- **PostgreSQL**: local o vía Docker Compose.

---

## 2. Levantar el proyecto

### Opción A — Todo el entorno con Docker Compose

```bash
docker compose up -d --build
```

- **Frontend**: `http://localhost:3000`
- **Backend Swagger**: `http://localhost:8000/docs`

> El servicio `frontend` espera a que el backend responda `/health` antes de arrancar. Las
> llamadas Server-Side usan `API_URL=http://backend:8000`; si esa variable falta, el cliente
> HTTP reintenta contra `http://backend:8000` y `http://localhost:8000`. Aunque la API falle,
> los botones “Nuevo …” y sus modales siguen visibles en `/choferes`, `/vehiculos` y
> `/servicios`. El modal de servicio se abre solo al entrar desde el Dashboard con
> `/servicios?nuevo=1`.

### Opción B — Frontend local

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:3000`.

### Opción C — Backend local

```bash
cd backend
python -m venv .venv
# En Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

---

## 3. Vistas disponibles y cómo probarlas

| Ruta | Descripción | Qué probar |
|---|---|---|
| `/` | **Dashboard principal** | Resumen operativo del día: KPIs (*Servicios del día*, *Choferes disponibles*, *Dinero por cobrar*, *Pendiente de rendición*) y tabla de próximos servicios. |
| `/agenda` | **Agenda operativa** | Grilla mensual de 31 días. Clickeá en cualquier día para filtrar turnos y abrir el modal "Nuevo turno". |
| `/cotizaciones` | **Cotizador comercial** | Elegí tipo de vehículo, horas estimadas y distancia; el importe se calcula en el backend con las tarifas vigentes. |
| `/servicios` | **Servicios (Backend Real)** | Alta con cliente existente o nuevo, cotización oficial, disponibilidad de choferes/vehículos y listado paginado. |
| `/choferes` | **Equipo de choferes** | Listado real con buscador y paginación; alta y edición de choferes desde el botón "+ Nuevo chofer". |
| `/vehiculos` | **Flota de vehículos** | Tarifas reales por tipo de vehículo con edición, y listado real con alta/edición desde "+ Nuevo vehículo". |
| `/clientes` | **Padrón de clientes** | Contador de clientes activos y tabla con búsqueda y paginación oficial. |
| `/rendiciones` | **Control financiero** | Métricas de liquidación, tabla de arqueo (`#REN-024`) y modal de detalle de gastos y saldo. |

### Cancelar un servicio

Con un servicio ya creado, la cancelación se prueba desde Swagger o con `curl`:

```bash
curl -X PATCH http://localhost:8000/api/servicios/1/cancelar \
  -H "Content-Type: application/json" \
  -d '{"motivo":"El cliente reprogramó el viaje"}'
```

La respuesta devuelve `estado: "cancelado"`, el motivo recortado y `hora_fin` con la hora del
servidor. Sin motivo responde 422; un servicio finalizado, cobrado o ya cancelado responde 409.

---

## 4. Modo Oscuro (Dark Mode)

En la esquina superior derecha del encabezado se encuentra el selector de tema:
- **Botón Sol / Luna**: Alterna instantáneamente entre Modo Claro y Modo Oscuro.
- **Persistencia**: Se almacena en `localStorage` bajo la clave `theme`.
- **Sin parpadeos (FOUC)**: El script inline en `<head>` previene destellos blancos antes del render inicial.
- **Sincronización React 19**: Utiliza `useSyncExternalStore` para reaccionar a cambios de atributos DOM sin efectos colaterales.

---

## 5. Pruebas y verificación de código

Para ejecutar toda la suite de linters, formateo, TypeScript y Vitest:

```bash
cd frontend
npm run verificar
```

Resultado esperado:
- **ESLint**: 0 errores, 0 advertencias.
- **Prettier**: 100% de archivos formateados.
- **TypeScript**: 0 errores de compilación (`next typegen && tsc --noEmit`).
- **Vitest**: 52 tests unitarios pasando al 100% (`10/10` suites).
