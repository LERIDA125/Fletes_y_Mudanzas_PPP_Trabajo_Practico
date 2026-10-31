from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class VehiculoORM(Base):
    __tablename__ = "vehiculos"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    patente: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    id_tipo_vehiculo: Mapped[int] = mapped_column(
        ForeignKey("tipos_vehiculo.id", ondelete="RESTRICT"), nullable=False
    )
    id_chofer_habitual: Mapped[int | None] = mapped_column(
        ForeignKey("choferes.id", ondelete="RESTRICT"), nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    modificado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_vehiculos_activo_patente", "activo", "patente"),)
