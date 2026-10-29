"""Repositorio SQLAlchemy para cuentas de Usuario (H9)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.errores import ChoferConUsuarioExistente, UsuarioDuplicado
from app.domain.usuario import Usuario
from app.infrastructure.models.usuario import UsuarioORM


def a_dominio(orm: UsuarioORM) -> Usuario:
    return Usuario(
        id=orm.id,
        username=orm.username,
        password_hash=orm.password_hash,
        rol=orm.rol,
        id_chofer=orm.id_chofer,
        activo=orm.activo,
        creado_en=orm.creado_en,
        actualizado_en=orm.actualizado_en,
        creado_por_id=orm.creado_por_id,
        modificado_por_id=orm.modificado_por_id,
    )


def a_orm(usuario: Usuario) -> UsuarioORM:
    return UsuarioORM(
        id=usuario.id,
        username=usuario.username,
        password_hash=usuario.password_hash,
        rol=usuario.rol,
        id_chofer=usuario.id_chofer,
        activo=usuario.activo,
        creado_por_id=usuario.creado_por_id,
        modificado_por_id=usuario.modificado_por_id,
    )


class UsuarioRepo:
    def __init__(self, db: Session) -> None:
        self._db = db

    def crear(self, usuario: Usuario) -> Usuario:
        orm = a_orm(usuario)
        self._db.add(orm)
        try:
            self._db.commit()
        except IntegrityError as error:
            self._db.rollback()
            if usuario.id_chofer is not None and self.obtener_por_id_chofer(usuario.id_chofer):
                raise ChoferConUsuarioExistente(usuario.id_chofer) from error
            raise UsuarioDuplicado(usuario.username) from error
        self._db.refresh(orm)
        return a_dominio(orm)

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        orm = self._db.get(UsuarioORM, usuario_id)
        if orm is None:
            return None
        return a_dominio(orm)

    def obtener_por_username(self, username: str) -> Usuario | None:
        consulta = select(UsuarioORM).where(UsuarioORM.username == username.strip().casefold())
        orm = self._db.scalar(consulta)
        return a_dominio(orm) if orm is not None else None

    def obtener_por_id_chofer(self, chofer_id: int) -> Usuario | None:
        consulta = select(UsuarioORM).where(UsuarioORM.id_chofer == chofer_id)
        orm = self._db.scalar(consulta)
        return a_dominio(orm) if orm is not None else None

    def listar(self) -> list[Usuario]:
        consulta = select(UsuarioORM).order_by(UsuarioORM.id)
        return [a_dominio(orm) for orm in self._db.scalars(consulta).all()]
