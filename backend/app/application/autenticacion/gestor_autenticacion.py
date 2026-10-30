from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from app.application.autenticacion.puertos import UsuarioRepository
from app.core.seguridad import DURACION_TOKEN_SEGUNDOS, crear_token_acceso, verificar_password
from app.domain.errores import CredencialesInvalidas
from app.domain.rol import ROL_CHOFER
from app.domain.usuario import normalizar_username


@dataclass(frozen=True)
class TokenAcceso:
    access_token: str
    expires_in: int


class GestorAutenticacion:
    """Casos de uso de login y perfil autenticado (capa de Aplicación)."""

    def __init__(
        self,
        repositorio_usuarios: UsuarioRepository,
        *,
        verificar: Callable[[str, str], bool] = verificar_password,
        emitir_token: Callable[..., str] = crear_token_acceso,
    ) -> None:
        self._repo = repositorio_usuarios
        self._verificar = verificar
        self._emitir_token = emitir_token

    def autenticar(self, *, username: str, password: str) -> TokenAcceso:
        credenciales = self._repo.obtener_credenciales(normalizar_username(username))
        if credenciales is None:
            raise CredencialesInvalidas()

        usuario = credenciales.usuario
        password_valida = self._verificar(password, credenciales.password_hash)
        chofer_inactivo = usuario.rol == ROL_CHOFER and usuario.chofer_activo is not True

        if not password_valida or not usuario.activo or chofer_inactivo:
            raise CredencialesInvalidas()

        if usuario.id is None:
            raise CredencialesInvalidas()

        token = self._emitir_token(
            usuario_id=usuario.id,
            username=usuario.username,
            rol=usuario.rol,
        )
        self._repo.registrar_acceso(usuario.id, datetime.now(UTC))
        return TokenAcceso(access_token=token, expires_in=DURACION_TOKEN_SEGUNDOS)
