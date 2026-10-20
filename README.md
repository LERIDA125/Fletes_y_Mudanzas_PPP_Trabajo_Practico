# Fletes y Mudanzas Express 🚚📦

> **Sistema de gestión integral para transporte urbano y logística liviana.**  
> Trabajo Integrador de Prácticas Pre-Profesionales 1 (2026) — Licenciatura en Sistemas, **Universidad Nacional de Lanús (UNLa)**.

---

## 📌 1. Acerca del Proyecto

**Fletes y Mudanzas Express** es un sistema web concebido para reemplazar la gestión histórica basada en planillas de cálculo (Excel), centralizando y automatizando las operaciones críticas de la empresa:
- Gestión de **Clientes** y condiciones comerciales (cuentas corrientes).
- Gestión de **Choferes** y control de saldos/rendiciones.
- Parque automotor y **Vehículos** clasificados por tipo y capacidad.
- Agendamiento y disponibilidad de **Servicios**.
- Motor de **Cotizaciones** dinámico basado en estrategias configurables.
- Flujos de **Pagos**, **Cuentas Corrientes** y **Rendición de Servicios**.
- Migración y consolidación de datos históricos.

---

## 🏗️ 2. Arquitectura: Monolito Modular en 4 Capas

El sistema sigue una arquitectura en capas estricta orientada al dominio y desacoplada de la infraestructura, garantizando adaptabilidad ante cambios de reglas de negocio (`AGENTS.md`):

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Presentación (app/api/)                                  │
│    FastAPI Routers, Schemas Pydantic, Control de Roles JWT  │
└──────────────────────────────┬──────────────────────────────┘
                               │ delega en
┌──────────────────────────────▼──────────────────────────────┐
│ 2. Aplicación (app/application/)                            │
│    Reglas de negocio, Validadores, Orquestadores, Puertos   │
└──────────────┬──────────────────────────────┬───────────────┘
               │ opera con                    │ persiste vía
┌──────────────▼──────────────┐ ┌─────────────▼───────────────┐
│ 3. Dominio (app/domain/)    │ │ 4. Infraestructura (app/infra)
│    Entidades invariantes,   │ │    Repositorios PostgreSQL, │
│    Máquinas de estado       │ │    Modelos ORM, DB Session  │
└─────────────────────────────┘ └─────────────────────────────┘
```

- **Presentación (`app/api/`)**: Expone endpoints REST, valida payloads de entrada/salida y gestiona autorización por roles (`admin` / `chofer`). No alberga lógica de negocio.
- **Aplicación (`app/application/`)**: Resuelve los casos de uso y la lógica operativa (`GestorClientes`, `GestorChoferes`, `GestorVehiculos`, etc.). Se comunica con la persistencia a través de interfaces/puertos desacoplados.
- **Dominio (`app/domain/`)**: Entidades puras con validaciones invariantes y estados de ciclo de vida (`Cliente`, `Chofer`, `Vehiculo`, `Servicio`).
- **Infraestructura (`app/infrastructure/`)**: Implementación concreta de repositorios usando SQLAlchemy 2 y PostgreSQL.

---

## 🛠️ 3. Stack Tecnológico

| Capa / Componente | Tecnología |
|---|---|
| **Lenguaje** | Python 3.12+ |
| **Framework Web** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Servidor ASGI** | [Uvicorn](https://www.uvicorn.org/) |
| **ORM & Database Toolkit** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) |
| **Motor de Base de Datos** | [PostgreSQL 16](https://www.postgresql.org/) (driver `psycopg3`) |
| **Control de Migraciones** | [Alembic](https://alembic.sqlalchemy.org/) |
| **Validación y Configuración** | [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings` |
| **Linter & Formateador** | [Ruff](https://astral.sh/ruff) |
| **Testing** | [Pytest](https://docs.pytest.org/) & HTTPX (`TestClient`) |
| **Contenedores** | Docker & Docker Compose |

---

## 📂 4. Estructura del Repositorio

```text
fletes-mudanzas-express/
├── AGENTS.md                  # Fuente de verdad de arquitectura y convenciones
├── README.md                  # Documentación general del proyecto
├── docker-compose.yml         # Entorno local multi-contenedor (PostgreSQL + Backend)
├── specs/                     # Spec Kit: especificaciones funcionales por historia
│   ├── H1-gestion-clientes.md
│   ├── H3-gestion-choferes.md
│   ├── H4-gestion-vehiculos.md
│   └── H13-migracion-datos-historicos.md
├── raw-data/                  # Planillas Excel para migración de datos
└── backend/
    ├── pyproject.toml         # Configuración del proyecto, dependencias y herramientas
    ├── alembic.ini            # Configuración de migraciones
    ├── alembic/               # Versiones de migraciones versionadas
    │   └── versions/
    ├── app/
    │   ├── main.py            # Instancia FastAPI y registro de routers
    │   ├── core/              # Configuración, settings y dependencias (JWT/Roles)
    │   ├── api/               # Capa 1: Routers y schemas Pydantic
    │   ├── application/       # Capa 2: Casos de uso y reglas de negocio
    │   ├── domain/            # Capa 3: Entidades invariantes y excepciones
    │   └── infrastructure/    # Capa 4: SQLAlchemy ORM, repositorios y DB session
    ├── scripts/               # Scripts de utilidad (ej. migración de Excel)
    └── tests/
        ├── unit/              # Tests unitarios rápidos sin base de datos
        └── integration/       # Tests de endpoints contra PostgreSQL real
```

---

## 🚀 5. Puesta en Marcha Local

### Opción A: Con Docker Compose (Recomendado)

Levanta la base de datos PostgreSQL 16 y el backend en un único comando:

```bash
docker compose up --build
```

El servidor estará accesible en:
- **API**: [http://localhost:8000](http://localhost:8000)
- **Documentación interactiva (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación alternativa (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Opción B: Entorno Virtual Local (Python)

#### 1. Requisitos previos
- Python 3.12 o superior.
- Una instancia de PostgreSQL 16 corriendo localmente.

#### 2. Configurar el entorno virtual
```bash
cd backend
python -m venv .venv

# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate
```

#### 3. Instalar dependencias
```bash
pip install -e ".[dev]"
```

#### 4. Configurar variables de entorno
Crea un archivo `.env` en `backend/` tomando como referencia las configuraciones necesarias:
```env
DATABASE_URL=postgresql+psycopg://fletes:fletes@localhost:5432/fletes
SECRET_KEY=clave_secreta_para_desarrollo
```

#### 5. Ejecutar migraciones de base de datos
```bash
alembic upgrade head
```

#### 6. Iniciar el servidor de desarrollo
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 6. Testing y Calidad de Código

### Tests Unitarios (Capa de Aplicación y Dominio)
Se ejecutan con repositorios en memoria (fakes/dobles) sin requerir PostgreSQL:
```bash
cd backend
pytest tests/unit
```

### Tests de Integración
Ejecutan los endpoints completos contra una instancia real de PostgreSQL:
```bash
cd backend
pytest tests/integration
```

### Linter y Formato
El proyecto utiliza [Ruff](https://astral.sh/ruff) para mantener un código limpio y uniforme:
```bash
# Verificar errores de linting
ruff check .

# Verificar formato de código
ruff format --check .

# Formatear automáticamente
ruff format .
```

---

## 📋 7. Metodología de Trabajo y Convenciones

- **Spec-Driven Development (Spec Kit)**: Ninguna historia de usuario se implementa sin su correspondiente especificación en `/specs/H#-nombre.md`, detallando criterios en formato Dado/Cuando/Entonces.
- **Ramas cortas por historia**: Formato `feature/H#-nombre` (ej. `feature/H3-gestion-choferes`).
- **Conventional Commits**: Mensajes estructurados (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`).
- **Pull Requests obligatorios**: Todo cambio mergeado a `main` requiere revisión cruzada y CI (lint + tests) en verde.
- **Decisiones de Diseño Clave (`AGENTS.md` §11)**:
  - **DD-1**: Baja lógica generalizada con flag `activo = False`.
  - **DD-2**: Clave canónica normalizada (`*_key`) para búsquedas y unicidad insensible a acentos y espacios.
  - **DD-3**: Autorización por puertos y roles (`admin` y `chofer`).
  - **DD-5**: Modificaciones completas vía `PUT` para preservar la coherencia del modelo.

---

## 👥 8. Equipo de Desarrollo

Proyecto desarrollado por el **Equipo de Prácticas Pre-Profesionales 1 (2026)** — UNLa:
- Trabajo colaborativo bajo metodología Scrum / Kanban.
- Plazo: 4 Sprints (8 semanas).
