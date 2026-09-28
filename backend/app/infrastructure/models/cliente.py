from datetime import datetime

from sqlalchemy import Boolean, DateTime, Identity, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ClienteORM(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(120), nullable=False)
    razon_social_key: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    direccion_habitual: Mapped[str] = mapped_column(String(250), nullable=False)
    tiene_cuenta_corriente: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_clientes_activo_razon_social_key", "activo", "razon_social_key"),)
