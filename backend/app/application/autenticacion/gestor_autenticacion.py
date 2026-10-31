"""Gestor de Aplicación para Autenticación, Multi-Admin y Usuarios de Chofer (H9)."""

from __future__ import annotations

from app.application.autenticacion.puertos import (
    ConsultaChoferAuth,
    HasherPasswordPort,
    ServicioTokenPort,
    SesionEmitida,
    UsuarioRepository,
)
from app.domain.errores import (
    ChoferConUsuarioExistente,
    ChoferInvalido,
    CredencialesInvalidas,
    UsuarioDuplicado,
)
from app.domain.usuario import Usuario, normalizar_username, validar_password_en_claro


class GestorAutenticacion:
    def __init__(
        self,
        *,
        repositorio_usuarios: UsuarioRepository,
        hasher: HasherPasswordPort,
        tokens: ServicioTokenPort,
        consulta_choferes: ConsultaChoferAuth | None = None,
    ) -> None:
        self._usuarios = repositorio_usuarios
        self._hasher = hasher
        self._tokens = tokens
        self._choferes = consulta_choferes

    def iniciar_sesion(self, *, username: str, password: str) -> SesionEmitida:
        username_key = username.strip().casefold()
        if not username_key or not password:
            raise CredencialesInvalidas()

        usuario = self._usuarios.obtener_por_username(username_key)
        if usuario is None or not usuario.activo or usuario.id is None:
            raise CredencialesInvalidas()

        if not self._hasher.verificar(password, usuario.password_hash):
            raise CredencialesInvalidas()

        access_token = self._tokens.emitir(
            usuario_id=usuario.id,
            username=usuario.username,
            rol=usuario.rol,
            id_chofer=usuario.id_chofer,
        )
        return SesionEmitida(
            access_token=access_token,
            expires_in=self._tokens.ttl_segundos,
            usuario=usuario,
        )

    def resolver_token(self, token: str) -> Usuario:
        payload = self._tokens.verificar(token)
        usuario = self._usuarios.obtener_por_id(payload.usuario_id)
        if usuario is None or not usuario.activo:
            raise CredencialesInvalidas("La cuenta ya no se encuentra activa")
        return usuario

    def crear_usuario(
        self,
        *,
        username: str,
        password: str,
        rol: str,
        id_chofer: int | None = None,
        creado_por_id: int | None = None,
    ) -> Usuario:
        username_norm = normalizar_username(username)
        password_limpio = validar_password_en_claro(password)

        if self._usuarios.obtener_por_username(username_norm) is not None:
            raise UsuarioDuplicado(username_norm)

        rol_norm = rol.strip().casefold()
        if rol_norm == "chofer" and id_chofer is not None:
            if self._choferes is not None:
                chofer = self._choferes.obtener_por_id(id_chofer)
                if chofer is None or not chofer.activo:
                    raise ChoferInvalido(id_chofer)
            if self._usuarios.obtener_por_id_chofer(id_chofer) is not None:
                raise ChoferConUsuarioExistente(id_chofer)

        password_hash = self._hasher.hashear(password_limpio)
        nuevo = Usuario.crear(
            username=username_norm,
            password_hash=password_hash,
            rol=rol_norm,
            id_chofer=id_chofer,
            creado_por_id=creado_por_id,
        )
        return self._usuarios.crear(nuevo)

    def listar_usuarios(self) -> list[Usuario]:
        return self._usuarios.listar()
