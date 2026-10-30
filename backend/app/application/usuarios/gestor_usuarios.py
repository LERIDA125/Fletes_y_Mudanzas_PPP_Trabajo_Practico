from app.application.autenticacion.puertos import UsuarioRepository
from app.core.seguridad import hashear_password
from app.domain.errores import ChoferInvalido, ChoferYaVinculado, UsernameDuplicado
from app.domain.rol import ROL_CHOFER
from app.domain.usuario import Usuario, validar_password


class GestorUsuarios:
    """Reglas de negocio de alta de cuentas de usuario (capa de Aplicación)."""

    def __init__(self, repositorio_usuarios: UsuarioRepository) -> None:
        self._repo = repositorio_usuarios

    def registrar(
        self,
        *,
        username: str,
        password: str,
        rol: str,
        id_chofer: int | None,
        creado_por: int | None,
    ) -> Usuario:
        usuario = Usuario.crear(username=username, rol=rol, id_chofer=id_chofer)
        validar_password(password, usuario.username)

        if self._repo.existe_username(usuario.username):
            raise UsernameDuplicado(usuario.username)

        if usuario.rol == ROL_CHOFER and usuario.id_chofer is not None:
            if not self._repo.chofer_esta_activo(usuario.id_chofer):
                raise ChoferInvalido(usuario.id_chofer)
            if self._repo.chofer_tiene_cuenta(usuario.id_chofer):
                raise ChoferYaVinculado(usuario.id_chofer)

        return self._repo.crear(
            usuario,
            password_hash=hashear_password(password),
            creado_por=creado_por,
        )
