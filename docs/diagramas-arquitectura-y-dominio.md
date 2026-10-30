# Diagramas de Arquitectura, Dominio, Base de Datos y Estados

**Proyecto**: Fletes y Mudanzas Express (MVP 1)  
**Cátedra**: Trabajo Integrador de Prácticas Pre-Profesionales 1 (2026) — Licenciatura en Sistemas, UNLa  

Este documento contiene los diagramas estructurales y de comportamiento generados a partir de la arquitectura implementada en el repositorio.

---

## 1. Diagrama de Arquitectura en 4 Capas (Monolito Modular + Next.js 16)

El sistema evita microservicios prematuros y organiza el backend en **4 capas concéntricas** con inversión de dependencias mediante `Protocol` de Python, consumidas por el frontend **Next.js 16 (App Router)** a través de un contrato OpenAPI tipado.

```mermaid
flowchart TD
    subgraph Cliente["Navegador Web (Desktop / Mobile)"]
        UI["Componentes React 19 + RHF + Zod"]
        Theme["Tema Claro/Oscuro (useSyncExternalStore)"]
    end

    subgraph Frontend["Frontend — Next.js 16 (App Router)"]
        RSC["Server Components (/, /agenda, /servicios, /clientes, /choferes, /vehiculos)"]
        SA["Server Actions (features/*/actions.ts + revalidatePath)"]
        HTTP["Cliente HTTP Resiliente (lib/api/http.ts · Fallback backend:8000 / localhost:8000)"]
        Types["Tipos Autogenerados (src/types/openapi.d.ts)"]
    end

    subgraph Backend["Backend — FastAPI Monolito Modular en Capas"]
        subgraph Capa1["1. Capa de Presentación (app/api/)"]
            Routers["Routers FastAPI (clientes, choferes, vehiculos, servicios)"]
            Schemas["Schemas Pydantic v2 (extra='forbid')"]
            AuthPort["Puerto de Autorización (require_rol)"]
        end

        subgraph Capa2["2. Capa de Aplicación (app/application/)"]
            GCli["GestorClientes"]
            GCho["GestorChoferes"]
            GVeh["GestorVehiculos"]
            GSer["GestorServicios (Alta, Disponibilidad, Estados, Cancelación)"]
            Calc["CalculadoraCotizacion (Contexto Strategy)"]
            Strat["Estrategia: PorHoraYKm (Decimal ROUND_HALF_UP)"]
            Ports["Puertos / Protocols (Repositorios abstractos)"]
        end

        subgraph Capa3["3. Capa de Dominio (app/domain/)"]
            Ent["Entidades Puras: Cliente, Chofer, Vehiculo, TipoVehiculo, Servicio"]
            Err["Jerarquía de Excepciones de Dominio (404 / 409 / 422)"]
        end

        subgraph Capa4["4. Capa de Infraestructura (app/infrastructure/)"]
            Repos["Repositorios SQLAlchemy (ClienteRepo, ChoferRepo, VehiculoRepo, ServicioRepo)"]
            ORM["Modelos ORM + Migraciones Alembic (0001..0005)"]
        end
    end

    DB[("PostgreSQL 16")]

    UI --> RSC
    UI --> SA
    RSC --> HTTP
    SA --> HTTP
    HTTP -.->|"Tipado estático"| Types
    HTTP ==>|"REST JSON"| Routers
    Routers --> AuthPort
    Routers --> Schemas
    Routers --> GCli & GCho & GVeh & GSer
    GSer --> Calc
    Calc --> Strat
    GCli & GCho & GVeh & GSer --> Ent
    GCli & GCho & GVeh & GSer --> Ports
    Repos -.->|"Implementa"| Ports
    Repos --> ORM
    ORM ==> DB
```

---

## 2. Diagrama Entidad-Relación (ERD) de Base de Datos (Migraciones `0001` a `0005`)

Representa el esquema relacional persistido en PostgreSQL 16 mediante Alembic.

```mermaid
erDiagram
    CLIENTES {
        int id PK "IDENTITY"
        varchar_120 razon_social "NOT NULL"
        varchar_120 razon_social_key UK "NOT NULL (normalizada sin acentos)"
        varchar_30 telefono "NOT NULL (7..20 digitos)"
        varchar_250 direccion_habitual "NOT NULL"
        boolean tiene_cuenta_corriente "NOT NULL DEFAULT false"
        boolean activo "NOT NULL DEFAULT true"
        timestamptz creado_en "NOT NULL DEFAULT now()"
        timestamptz actualizado_en "NOT NULL DEFAULT now()"
    }

    CHOFERES {
        int id PK "IDENTITY"
        varchar_120 nombre_completo "NOT NULL"
        varchar_30 telefono "NOT NULL (7..20 digitos)"
        boolean activo "NOT NULL DEFAULT true"
        numeric_12_2 saldo_a_favor "NOT NULL DEFAULT 0.00"
        timestamptz creado_en "NOT NULL DEFAULT now()"
        timestamptz actualizado_en "NOT NULL DEFAULT now()"
    }

    TIPOS_VEHICULO {
        int id PK "IDENTITY"
        varchar_80 descripcion "NOT NULL"
        varchar_80 descripcion_key UK "NOT NULL (normalizada)"
        numeric_10_2 capacidad_carga_kg "NOT NULL (> 0)"
        numeric_12_2 tarifa_hora_base "NOT NULL (>= 0)"
        numeric_12_2 tarifa_km_excedente "NOT NULL (>= 0)"
        boolean activo "NOT NULL DEFAULT true"
        timestamptz creado_en "NOT NULL DEFAULT now()"
        timestamptz actualizado_en "NOT NULL DEFAULT now()"
    }

    VEHICULOS {
        int id PK "IDENTITY"
        varchar_15 patente "NOT NULL (formato visual)"
        varchar_15 patente_norm UK "NOT NULL (AAA123 o AA123ABC)"
        int id_tipo_vehiculo FK "NOT NULL"
        int id_chofer_habitual FK "NULLABLE"
        boolean activo "NOT NULL DEFAULT true"
        timestamptz creado_en "NOT NULL DEFAULT now()"
        timestamptz actualizado_en "NOT NULL DEFAULT now()"
    }

    SERVICIOS {
        int id PK "IDENTITY"
        int id_cliente FK "NOT NULL"
        int id_tipo_vehiculo FK "NOT NULL"
        int id_chofer FK "NULLABLE"
        int id_vehiculo FK "NULLABLE"
        date fecha "NULLABLE"
        time hora_inicio "NULLABLE"
        time hora_fin "NULLABLE (obligatorio si cancelado)"
        numeric_10_2 horas_estimadas "NOT NULL (>= 1)"
        numeric_10_2 distancia_ida_km "NOT NULL (>= 0)"
        numeric_10_2 distancia_total_km "NOT NULL (snapshot)"
        numeric_10_2 km_franquicia_aplicados "NOT NULL (snapshot = 10)"
        numeric_10_2 km_excedente "NOT NULL (snapshot)"
        numeric_12_2 tarifa_hora_aplicada "NOT NULL (snapshot)"
        numeric_12_2 tarifa_km_aplicada "NOT NULL (snapshot)"
        numeric_12_2 precio_total "NOT NULL (snapshot ARS)"
        varchar_20 estado "NOT NULL (CHECK estado valido)"
        varchar_255 motivo_cancelacion "NULLABLE (CHECK obligatorio si cancelado)"
        timestamptz creado_en "NOT NULL DEFAULT now()"
        timestamptz actualizado_en "NOT NULL DEFAULT now()"
    }

    TIPOS_VEHICULO ||--o{ VEHICULOS : "categoriza"
    CHOFERES |o--o{ VEHICULOS : "conduce habitualmente"
    CLIENTES ||--o{ SERVICIOS : "contrata"
    TIPOS_VEHICULO ||--o{ SERVICIOS : "define tarifa de"
    CHOFERES |o--o{ SERVICIOS : "asignado a"
    VEHICULOS |o--o{ SERVICIOS : "asignado a"
```

> **Nota**: este ERD refleja las migraciones `0001` a `0005`. El modelo RBAC objetivo del Ticket 1
> (`roles`, `usuarios` y la relación con `choferes`) se especifica en
> [`especificacion-rbac.md`](./especificacion-rbac.md), sección 6.

---

## 3. Diagrama de Clases del Dominio y Patrón Strategy de Cotización

Muestra las entidades de dominio puras (`app/domain/`) junto con el patrón **Strategy** implementado en `app/application/cotizacion/` para aislar los cambios en la fórmula tarifaria del cliente.

```mermaid
classDiagram
    class Cliente {
        +int id
        +str razon_social
        +str razon_social_key
        +str telefono
        +str direccion_habitual
        +bool tiene_cuenta_corriente
        +bool activo
        +crear(...) Cliente
        +actualizar(...) void
        +dar_de_baja() void
    }

    class Chofer {
        +int id
        +str nombre_completo
        +str telefono
        +bool activo
        +Decimal saldo_a_favor
        +crear(...) Chofer
        +actualizar(...) void
        +dar_de_baja() void
    }

    class TipoVehiculo {
        +int id
        +str descripcion
        +str descripcion_key
        +Decimal capacidad_carga_kg
        +Decimal tarifa_hora_base
        +Decimal tarifa_km_excedente
        +bool activo
        +crear(...) TipoVehiculo
        +actualizar(...) void
    }

    class Vehiculo {
        +int id
        +str patente
        +str patente_norm
        +int id_tipo_vehiculo
        +int~None~ id_chofer_habitual
        +bool activo
        +crear(...) Vehiculo
        +actualizar(...) void
    }

    class Servicio {
        +int id
        +int id_cliente
        +int id_tipo_vehiculo
        +int~None~ id_chofer
        +int~None~ id_vehiculo
        +date~None~ fecha
        +time~None~ hora_inicio
        +time~None~ hora_fin
        +Decimal horas_estimadas
        +Decimal distancia_ida_km
        +Decimal distancia_total_km
        +Decimal km_franquicia_aplicados
        +Decimal km_excedente
        +Decimal tarifa_hora_aplicada
        +Decimal tarifa_km_aplicada
        +Decimal precio_total
        +str estado
        +str~None~ motivo_cancelacion
        +crear(...) Servicio
        +transicionar_a(nuevo_estado: str) void
        +cancelar(motivo: str, hora_fin: time) void
    }

    class EstrategiaCotizacion {
        <<interface>>
        +calcular(tarifa_hora: Decimal, tarifa_km: Decimal, horas: Decimal, distancia_ida_km: Decimal) ResultadoCalculo
    }

    class PorHoraYKm {
        +Decimal KM_FRANQUICIA = 10
        +calcular(tarifa_hora: Decimal, tarifa_km: Decimal, horas: Decimal, distancia_ida_km: Decimal) ResultadoCalculo
    }

    class CalculadoraCotizacion {
        -PuertoTarifas repo_tarifas
        -EstrategiaCotizacion estrategia
        +cotizar(id_tipo_vehiculo: int, horas_estimadas: Decimal, distancia_ida_km: Decimal) CotizacionCalculada
    }

    class GestorServicios {
        -RepositorioServicios repo_servicios
        -CalculadoraCotizacion calculadora
        +cotizar(...)
        +consultar_disponibilidad(...)
        +crear(...)
        +listar(...)
        +cambiar_estado(...)
        +cancelar(...)
        +eliminar(...)
    }

    EstrategiaCotizacion <|.. PorHoraYKm : implementa
    CalculadoraCotizacion --> EstrategiaCotizacion : delega cálculo
    GestorServicios --> CalculadoraCotizacion : cotiza y genera snapshot
    GestorServicios --> Servicio : instancia y transiciona
    GestorServicios --> Cliente : reutiliza o crea en alta
    Vehiculo --> TipoVehiculo : pertenece a
    Vehiculo --> Chofer : chofer habitual
```

---

## 4. Diagrama de Máquina de Estados del Servicio (`Servicio`)

Modela las reglas invariantes de transición en `app/domain/servicio.py` y el constraint `CHECK` de PostgreSQL (migraciones `0004` y `0005`).

```mermaid
stateDiagram-v2
    [*] --> pendiente : POST /api/servicios (Alta con snapshot tarifario)

    pendiente --> confirmado : PATCH /api/servicios/{id}/estado {"estado": "confirmado"}
    confirmado --> en_curso : PATCH /api/servicios/{id}/estado {"estado": "en curso"}
    en_curso --> finalizado : PATCH /api/servicios/{id}/estado {"estado": "finalizado"}
    finalizado --> cobrado : PATCH /api/servicios/{id}/estado {"estado": "cobrado"}

    pendiente --> cancelado : PATCH /api/servicios/{id}/cancelar (motivo + hora_fin servidor)
    confirmado --> cancelado : PATCH /api/servicios/{id}/cancelar (motivo + hora_fin servidor)
    en_curso --> cancelado : PATCH /api/servicios/{id}/cancelar (motivo + hora_fin servidor)

    cobrado --> [*]
    cancelado --> [*]

    note right of pendiente
        Transiciones ordinarias solo avanzan
        al estado inmediato siguiente.
        Saltos o retrocesos responden 422.
    end note

    note right of cancelado
        Invariante de cancelación:
        - motivo_cancelacion obligatorio (1..255 chars)
        - hora_fin inyectada por el servidor
        - Prohibido cancelar desde finalizado, cobrado o cancelado (409)
    end note
```

---

## 5. Flujo de Integración Continua (GitHub Actions CI) y Docker Compose

Representa los **4 jobs paralelos/secuenciales** configurados en `.github/workflows/ci.yml` para garantizar que el código funcione en cualquier máquina del equipo.

```mermaid
flowchart LR
    Push["Push / Pull Request a main"] --> Job1 & Job2 & Job3 & Job4

    subgraph Job1["Job 1: lint-and-unit-tests"]
        Ruff["ruff check ."] --> Unit["pytest tests/unit (44 tests con Fakes)"]
    end

    subgraph Job2["Job 2: integration-tests"]
        PG[("Service: Postgres 16")] --> Alembic["alembic upgrade head (0001..0005)"]
        Alembic --> Int["pytest tests/integration (API real)"]
    end

    subgraph Job3["Job 3: frontend"]
        GenAPI["npm run gen:api + git diff --exit-code (Contrato OpenAPI)"]
        GenAPI --> Verif["npm run verificar (ESLint + Prettier + TSC + 80 tests Vitest)"]
        Verif --> Build["npm run build (Next.js 16 Turbopack)"]
    end

    subgraph Job4["Job 4: docker-compose"]
        DCConfig["docker compose config"] --> DCBuild["docker compose build (Backend + Frontend)"]
    end

    Job1 & Job2 & Job3 & Job4 --> Merge["PR Habilitado para Merge a main"]
```
