"""Schemas de entrada y salida de vehículos en la capa de Presentación."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.schemas.comun import Pagina
from app.application.vehiculos.puertos import VehiculoListadoItem
from app.domain.vehiculo import Vehiculo, normalizar_patente


class VehiculoBase(BaseModel):
    """Base compatible con ERD (H13)."""

    patente: str = Field(
        min_length=6,
        max_length=15,
        description="Patente del vehículo. Formato argentino: AAA 123 o AA 123 ABC.",
        examples=["ABC 123"],
    )
    id_tipo_vehiculo: int = Field(gt=0, description="Identificador del tipo de vehículo.")
    id_chofer_habitual: int | None = Field(
        default=None, description="Identificador del chofer habitual. Opcional."
    )

    @field_validator("patente", mode="before")
    @classmethod
    def _normalizar_patente(cls, valor: object) -> object:
        return normalizar_patente(valor) if isinstance(valor, str) else valor


class VehiculoCreate(VehiculoBase):
    """Los datos requeridos del alta de un vehículo."""

    model_config = ConfigDict(extra="forbid")


class VehiculoUpdate(VehiculoCreate):
    """La edición toma los mismos datos obligatorios que el alta (DD-5)."""


class VehiculoRead(VehiculoBase):
    """Vehículo tal como lo devuelve el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        description="Identificador del vehículo, asignado por el sistema.",
        validation_alias="id",
    )
    activo: bool = Field(
        default=True,
        description="False cuando el vehículo fue dado de baja.",
    )
    creado_por_id: int | None = Field(
        default=None, description="ID del usuario que creó el vehículo."
    )
    modificado_por_id: int | None = Field(
        default=None, description="ID del último usuario que modificó el vehículo."
    )
    creado_en: datetime | None = Field(
        default=None,
        description="Fecha de alta, asignada por el sistema.",
    )
    actualizado_en: datetime | None = Field(
        default=None,
        description="Fecha de la última modificación.",
    )
    descripcion_tipo_vehiculo: str | None = Field(
        default=None,
        description="Descripción legible del tipo de vehículo asociado.",
    )
    capacidad_carga_kg: float | None = Field(
        default=None,
        description="Capacidad de carga en kilogramos del tipo de vehículo asociado.",
    )
    nombre_chofer_habitual: str | None = Field(
        default=None,
        description="Nombre completo del chofer habitual, si está asignado.",
    )

    @property
    def id_vehiculo(self) -> int:
        """Alias para compatibilidad con el ERD (H13)."""
        return self.id

    @classmethod
    def de_vehiculo(cls, vehiculo: Vehiculo) -> VehiculoRead:
        return cls.model_validate(vehiculo, from_attributes=True)

    @classmethod
    def de_listado(cls, item: VehiculoListadoItem) -> VehiculoListadoRead:
        vehiculo = item.vehiculo
        return VehiculoListadoRead(
            id=vehiculo.id,
            patente=vehiculo.patente,
            id_tipo_vehiculo=vehiculo.id_tipo_vehiculo,
            id_chofer_habitual=vehiculo.id_chofer_habitual,
            activo=vehiculo.activo,
            creado_por_id=vehiculo.creado_por_id,
            modificado_por_id=vehiculo.modificado_por_id,
            creado_en=vehiculo.creado_en,
            actualizado_en=vehiculo.actualizado_en,
            descripcion_tipo_vehiculo=item.descripcion_tipo_vehiculo,
            capacidad_carga_kg=float(item.capacidad_carga_kg),
            nombre_chofer_habitual=item.nombre_chofer_habitual,
        )


class VehiculoListadoRead(VehiculoRead):
    creado_en: datetime
    descripcion_tipo_vehiculo: str
    capacidad_carga_kg: float
    nombre_chofer_habitual: str | None


class VehiculoListado(Pagina[VehiculoListadoRead]):
    """Página de vehículos con el total de los que cumplen el filtro."""
