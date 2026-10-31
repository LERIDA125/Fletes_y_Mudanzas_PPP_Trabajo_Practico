# Quickstart: H8 — Gestión de Servicios, Cotizaciones y Operaciones

Guía para levantar el frontend Next.js 16 y el backend FastAPI de **Fletes y Mudanzas Express**, poblar datos iniciales, probar las vistas operativas (Dashboard, Agenda, Clientes, Choferes, Vehículos, Cotizaciones, Servicios y Rendiciones) y verificar el funcionamiento del Modo Oscuro.

---

## 1. Prerrequisitos

- **Node.js**: v20+ o v22+ con `npm`.
- **Python**: v3.12+ (para el backend).
- **PostgreSQL**: v16+ local o vía Docker Compose.

---

## 2. Levantar el proyecto

### Opción A — Todo el entorno con Docker Compose (Recomendada)

```bash
docker compose up -d --build
```

- **Frontend**: `http://localhost:3000`
- **Backend Swagger**: `http://localhost:8000/docs`

> Al iniciar, el contenedor `backend` espera a que PostgreSQL esté saludable, ejecuta automáticamente `alembic upgrade head` y levanta FastAPI. Las llamadas Server-Side usan `API_URL=http://backend:8000`; si esa variable falta, el cliente HTTP reintenta contra `http://backend:8000` y `http://localhost:8000`.

### Opción B — Backend local

```bash
cd backend
python -m venv .venv
# En Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head
python -m scripts.seed                  # opcional: poblar con datos de prueba
uvicorn app.main:app --reload --port 8000
```

### Opción C — Frontend local

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:3000`.

---

## 3. Vistas disponibles y cómo probarlas

| Ruta | Descripción | Qué probar |
|---|---|---|
| `/` | **Dashboard principal** | Resumen operativo en tiempo real conectado al backend: KPIs (*Servicios del día*, *Choferes disponibles*, *Dinero por cobrar*, *Pendiente de rendición*), tabla de viajes y botón de acceso rápido `/servicios?nuevo=1`. |
| `/agenda` | **Agenda operativa** | Calendario mensual alimentado por los servicios reales de la API. Clickeá en cualquier día para ver sus viajes programados o agendar uno nuevo. |
| `/cotizaciones` | **Cotizador comercial** | Elegí tipo de vehículo, horas estimadas y distancia de ida; el importe se calcula en el backend con las tarifas vigentes. |
| `/servicios` | **Servicios (Ciclo completo)** | Alta con cliente existente o nuevo, cotización oficial, disponibilidad de choferes/vehículos, avance de estado (`pendiente → confirmado → en curso → finalizado → cobrado`), cancelación con motivo y eliminación con confirmación. |
| `/choferes` | **Equipo de choferes** | Listado real con buscador y paginación; alta, edición y baja lógica con confirmación (`DialogoChofer` y `DialogoConfirmacion`). |
| `/vehiculos` | **Flota y Tarifas** | Panel de tarifas por tipo de vehículo (`PanelTarifas`) con edición en vivo, y listado real de flota con alta, edición y baja lógica (`DialogoVehiculo`). |
| `/clientes` | **Padrón de clientes** | Contador de clientes activos, buscador con debounce, paginación y menú de acciones para editar o dar de baja con protección de historial (`409 Conflict`). |
| `/rendiciones` | **Control financiero** | Prototipo interactivo de métricas de liquidación, tabla de arqueo (`#REN-024`) y modal de detalle de gastos y saldo. |

### Gestionar el estado o cancelar un servicio

Desde la tabla en `/servicios` (menú de acciones de cada fila) o vía API:

```bash
# Avanzar al siguiente estado de la máquina
curl -X PATCH http://localhost:8000/api/servicios/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado":"confirmado"}'

# Cancelar con motivo obligatorio (registra hora_fin del servidor)
curl -X PATCH http://localhost:8000/api/servicios/1/cancelar \
  -H "Content-Type: application/json" \
  -d '{"motivo":"El cliente reprogramó el viaje"}'
```

---

## 4. Modo Oscuro (Dark Mode)

En la esquina superior derecha del encabezado se encuentra el selector de tema:
- **Botón Sol / Luna**: Alterna instantáneamente entre Modo Claro y Modo Oscuro.
- **Persistencia**: Se almacena en `localStorage` bajo la clave `theme`.
- **Sin parpadeos (FOUC)**: El script inline en `<head>` previene destellos blancos antes del render inicial.
- **Sincronización React 19**: Utiliza `useSyncExternalStore` para reaccionar a cambios de atributos DOM sin efectos colaterales.

---

## 5. Pruebas y verificación de código

```bash
# Backend
cd backend
ruff check .
pytest tests/unit

# Frontend
cd frontend
npm run verificar
```

Resultado esperado:
- **Ruff (Backend)**: `All checks passed!`
- **Pytest Unit (Backend)**: `44 passed`
- **ESLint (Frontend)**: 0 errores, 0 advertencias.
- **Prettier (Frontend)**: 100% de archivos formateados.
- **TypeScript (Frontend)**: 0 errores de compilación (`next typegen && tsc --noEmit`).
- **Vitest (Frontend)**: `80 passed` (`12/12` suites).
