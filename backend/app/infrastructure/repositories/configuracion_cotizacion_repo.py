"""Repositorio de la configuración singleton de cotización."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.configuracion_cotizacion import ConfiguracionCotizacion
from app.infrastructure.models.configuracion_cotizacion import ConfiguracionCotizacionORM


class ConfiguracionCotizacionRepo:
    def __init__(self, db: Session) -> None:
        self._db = db

    def obtener(self) -> ConfiguracionCotizacion | None:
        orm = self._db.scalar(
            select(ConfiguracionCotizacionORM).where(ConfiguracionCotizacionORM.id == 1)
        )
        if orm is None:
            return None
        return ConfiguracionCotizacion(
            recargo_ayudante=orm.recargo_ayudante,
            recargo_escalera=orm.recargo_escalera,
            porcentaje_zona_concurrida=orm.porcentaje_zona_concurrida,
            porcentaje_urgencia_mismo_dia=orm.porcentaje_urgencia_mismo_dia,
        )
