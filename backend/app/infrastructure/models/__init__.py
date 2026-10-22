"""Modelos de persistencia.

Importar este paquete registra las tablas en Base.metadata, que es lo que usa Alembic
para el autogenerate.
"""

from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.cliente import ClienteORM
from app.infrastructure.models.servicio import ServicioORM
from app.infrastructure.models.tipo_vehiculo import TipoVehiculoORM
from app.infrastructure.models.vehiculo import VehiculoORM

__all__ = ["ChoferORM", "ClienteORM", "ServicioORM", "TipoVehiculoORM", "VehiculoORM"]
