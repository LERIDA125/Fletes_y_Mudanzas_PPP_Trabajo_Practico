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
| `/cotizaciones` | **Cotizador comercial** | Ingresá tipo de camión (chico/grande), km de distancia, activá extras (escaleras, embalaje) y observá el cálculo del total estimado en tiempo real. |
| `/servicios` | **Servicios (Backend Real)** | Conectado a FastAPI. Formulario de cotización oficial contra backend, listado de servicios persistidos y paginación. |
| `/choferes` | **Equipo de choferes** | Tarjetas de disponibilidad (*Libres hoy*, *En viaje*, *Licencia*), tarifario sugerido y listado conectado a backend con buscador debounced. |
| `/vehiculos` | **Flota de vehículos** | Tarjetas de estado de flota (Sprinter, Daily, Master, Ducato) y tabla completa conectada a la base de datos. |
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
