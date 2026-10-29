"""Puertos de la capa de Aplicación para Autenticación y Gestión de Usuarios (H9)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.domain.chofer import Chofer
from app.domain.usuario import Usuario
from app.infrastructure.security.jwt_service import PayloadToken


@dataclass(frozen=True)
class SesionEmitida:
    access_token: str
    expires_in: int
    usuario: Usuario


@runtime_checkable
class UsuarioRepository(Protocol):
    def crear(self, usuario: Usuario) -> Usuario: ...

    def obtener_por_id(self, usuario_id: int) -> Usuario | None: ...

    def obtener_por_username(self, username: str) -> Usuario | None: ...

    def obtener_por_id_chofer(self, chofer_id: int) -> Usuario | None: ...

    def listar(self) -> list[Usuario]: ...


@runtime_checkable
class HasherPasswordPort(Protocol):
    def hashear(self, password: str) -> str: ...

    def verificar(self, password: str, password_hash: str) -> bool: ...


@runtime_checkable
class ServicioTokenPort(Protocol):
    @property
    def ttl_segundos(self) -> int: ...

    def emitir(
        self,
        *,
        usuario_id: int,
        username: str,
        rol: str,
        id_chofer: int | None = None,
    ) -> str: ...

    def verificar(self, token: str) -> PayloadToken: ...


@runtime_checkable
class ConsultaChoferAuth(Protocol):
    def obtener_por_id(self, chofer_id: int) -> Chofer | None: ...
