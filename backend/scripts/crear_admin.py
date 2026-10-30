import sys
from getpass import getpass

from sqlalchemy import select

from app.application.usuarios.gestor_usuarios import GestorUsuarios
from app.domain.errores import DatoInvalido, UsernameDuplicado
from app.domain.rol import ROL_ADMIN
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.models.rol import RolORM
from app.infrastructure.models.usuario import UsuarioORM
from app.infrastructure.repositories.usuario_repo import UsuarioRepo


class ErrorProvisionAdmin(Exception):
    pass


def crear_primer_admin(username: str, password: str) -> str:
    with SessionLocal() as db:
        rol_admin = db.scalar(select(RolORM).where(RolORM.codigo == ROL_ADMIN).with_for_update())
        if rol_admin is None:
            raise ErrorProvisionAdmin(
                "No existe el rol ADMIN. Aplicá las migraciones antes de ejecutar este comando."
            )

        admin_existente = db.scalar(
            select(UsuarioORM.id).where(UsuarioORM.rol_id == rol_admin.id).limit(1)
        )
        if admin_existente is not None:
            raise ErrorProvisionAdmin(
                "Ya existe una cuenta ADMIN. Las cuentas adicionales se crean desde el sistema."
            )

        gestor = GestorUsuarios(UsuarioRepo(db))
        creado = gestor.registrar(
            username=username,
            password=password,
            rol=ROL_ADMIN,
            id_chofer=None,
            creado_por=None,
        )

    return creado.username


def main() -> int:
    try:
        username = input("Nombre de usuario: ")
        password = getpass("Contraseña: ")
        confirmacion = getpass("Confirmá la contraseña: ")
        if password != confirmacion:
            print("Las contraseñas no coinciden.", file=sys.stderr)
            return 1

        creado = crear_primer_admin(username, password)
    except (DatoInvalido, ErrorProvisionAdmin, UsernameDuplicado) as error:
        print(f"No se pudo crear el administrador: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperación cancelada.", file=sys.stderr)
        return 130

    print(f"Administrador {creado!r} creado correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
