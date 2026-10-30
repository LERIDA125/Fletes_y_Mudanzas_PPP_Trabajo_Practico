"""Repositorio en memoria de usuarios para testear la capa de Aplicación."""

from dataclasses import replace
from datetime import UTC, datetime

from app.application.autenticacion.puertos import CredencialesUsuario, UsuarioRepository
from app.domain.usuario import Usuario


class FakeUsuarioRepo(UsuarioRepository):
    def __init__(self) -> None:
        self._por_username: dict[str, CredencialesUsuario] = {}
        self._por_id: dict[int, Usuario] = {}
        self._choferes_activos: set[int] = set()
        self._siguiente_id = 1
        self.llamadas_acceso: list[tuple[int, datetime]] = []

    def agregar(
        self,
        usuario: Usuario,
        *,
        password_hash: str = "hash",
        chofer_activo: bool | None = None,
    ) -> Usuario:
        if usuario.id is None:
            usuario = replace(usuario, id=self._siguiente_id)
            self._siguiente_id += 1
        if chofer_activo is not None:
            usuario = replace(usuario, chofer_activo=chofer_activo)
        self._por_id[usuario.id] = usuario
        self._por_username[usuario.username] = CredencialesUsuario(
            usuario=usuario,
            password_hash=password_hash,
        )
        return usuario

    def marcar_chofer_activo(self, chofer_id: int) -> None:
        self._choferes_activos.add(chofer_id)

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        return self._por_id.get(usuario_id)

    def obtener_credenciales(self, username: str) -> CredencialesUsuario | None:
        return self._por_username.get(username)

    def registrar_acceso(self, usuario_id: int, momento: datetime) -> None:
        self.llamadas_acceso.append((usuario_id, momento))

    def crear(
        self,
        usuario: Usuario,
        *,
        password_hash: str,
        creado_por: int | None,
    ) -> Usuario:
        creado = replace(
            usuario,
            id=self._siguiente_id,
            creado_por=creado_por,
            creado_en=datetime.now(UTC),
            actualizado_en=datetime.now(UTC),
        )
        self._siguiente_id += 1
        self._por_id[creado.id] = creado
        self._por_username[creado.username] = CredencialesUsuario(
            usuario=creado,
            password_hash=password_hash,
        )
        return creado

    def existe_username(self, username: str) -> bool:
        return username in self._por_username

    def chofer_esta_activo(self, chofer_id: int) -> bool:
        return chofer_id in self._choferes_activos

    def chofer_tiene_cuenta(self, chofer_id: int) -> bool:
        return any(usuario.id_chofer == chofer_id for usuario in self._por_id.values())
