"""Modelos de persistencia.

Importar este paquete registra las tablas en Base.metadata, que es lo que usa Alembic
para el autogenerate.
"""

from app.infrastructure.models.cliente import ClienteORM

__all__ = ["ClienteORM"]
