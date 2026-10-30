from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.autenticacion.puertos import CredencialesUsuario
from app.domain.errores import ChoferYaVinculado, UsernameDuplicado
from app.domain.rol import ROL_CHOFER
from app.domain.usuario import Usuario
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.rol import RolORM
from app.infrastructure.models.usuario import UsuarioORM


def _a_dominio(
    orm: UsuarioORM,
    rol_codigo: str,
    chofer_activo: bool | None,
) -> Usuario:
    return Usuario(
        id=orm.id,
        username=orm.username,
        rol=rol_codigo,
        activo=orm.activo,
        id_chofer=orm.id_chofer,
        chofer_activo=chofer_activo,
        creado_por=orm.creado_por,
        creado_en=orm.creado_en,
        actualizado_en=orm.actualizado_en,
    )


class UsuarioRepo:
    """Único punto de acceso a PostgreSQL para cuentas de usuario."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _consulta_con_rol_y_chofer(self):
        return (
            select(UsuarioORM, RolORM.codigo, ChoferORM.activo)
            .join(RolORM, UsuarioORM.rol_id == RolORM.id)
            .outerjoin(ChoferORM, UsuarioORM.id_chofer == ChoferORM.id)
        )

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        consulta = self._consulta_con_rol_y_chofer().where(UsuarioORM.id == usuario_id)
        fila = self._db.execute(consulta).first()
        if fila is None:
            return None

        orm, rol_codigo, chofer_activo = fila
        return _a_dominio(orm, rol_codigo, chofer_activo)

    def obtener_credenciales(self, username: str) -> CredencialesUsuario | None:
        consulta = self._consulta_con_rol_y_chofer().where(UsuarioORM.username == username)
        fila = self._db.execute(consulta).first()
        if fila is None:
            return None

        orm, rol_codigo, chofer_activo = fila
        return CredencialesUsuario(
            usuario=_a_dominio(orm, rol_codigo, chofer_activo),
            password_hash=orm.password_hash,
        )

    def crear(
        self,
        usuario: Usuario,
        *,
        password_hash: str,
        creado_por: int | None,
    ) -> Usuario:
        rol = self._db.scalar(select(RolORM).where(RolORM.codigo == usuario.rol))
        if rol is None:
            raise RuntimeError(f"El rol {usuario.rol!r} no está sembrado en la base")

        orm = UsuarioORM(
            username=usuario.username,
            password_hash=password_hash,
            rol_id=rol.id,
            id_chofer=usuario.id_chofer,
            creado_por=creado_por,
        )
        self._db.add(orm)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            restriccion = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            if restriccion == "uq_usuarios_id_chofer" and usuario.id_chofer is not None:
                raise ChoferYaVinculado(usuario.id_chofer) from exc
            raise UsernameDuplicado(usuario.username) from exc

        self._db.refresh(orm)
        chofer_activo = True if usuario.rol == ROL_CHOFER else None
        return _a_dominio(orm, usuario.rol, chofer_activo)

    def registrar_acceso(self, usuario_id: int, momento: datetime) -> None:
        self._db.execute(
            update(UsuarioORM)
            .where(UsuarioORM.id == usuario_id)
            .values(ultimo_acceso=momento)
        )
        self._db.commit()

    def existe_username(self, username: str) -> bool:
        consulta = select(UsuarioORM.id).where(UsuarioORM.username == username).limit(1)
        return self._db.scalar(consulta) is not None

    def chofer_esta_activo(self, chofer_id: int) -> bool:
        consulta = (
            select(ChoferORM.id)
            .where(ChoferORM.id == chofer_id, ChoferORM.activo.is_(True))
            .limit(1)
        )
        return self._db.scalar(consulta) is not None

    def chofer_tiene_cuenta(self, chofer_id: int) -> bool:
        consulta = select(UsuarioORM.id).where(UsuarioORM.id_chofer == chofer_id).limit(1)
        return self._db.scalar(consulta) is not None
