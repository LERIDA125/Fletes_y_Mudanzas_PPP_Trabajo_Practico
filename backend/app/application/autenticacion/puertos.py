from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from app.domain.usuario import Usuario


@dataclass(frozen=True)
class CredencialesUsuario:
    """Cuenta de usuario con el hash necesario para autenticar, sin exponerlo hacia afuera."""

    usuario: Usuario
    password_hash: str


@runtime_checkable
class UsuarioRepository(Protocol):
    """Puerto de persistencia de cuentas de usuario. Lo implementa app/infrastructure/."""

    def obtener_por_id(self, usuario_id: int) -> Usuario | None: ...

    def obtener_credenciales(self, username: str) -> CredencialesUsuario | None: ...

    def registrar_acceso(self, usuario_id: int, momento: datetime) -> None: ...

    def crear(
        self,
        usuario: Usuario,
        *,
        password_hash: str,
        creado_por: int | None,
    ) -> Usuario: ...

    def existe_username(self, username: str) -> bool: ...

    def chofer_esta_activo(self, chofer_id: int) -> bool: ...

    def chofer_tiene_cuenta(self, chofer_id: int) -> bool: ...
