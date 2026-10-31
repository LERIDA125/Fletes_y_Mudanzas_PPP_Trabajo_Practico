import sys
from getpass import getpass

from sqlalchemy import select

from app.application.autenticacion.gestor_autenticacion import GestorAutenticacion
from app.domain.errores import DatoInvalido, UsernameDuplicado
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.models.usuario import UsuarioORM
from app.infrastructure.repositories.usuario_repo import UsuarioRepo
from app.infrastructure.security.jwt_service import JWTService
from app.infrastructure.security.password_hasher import PasswordHasher


class ErrorProvisionAdmin(Exception):
    pass


def crear_primer_admin(username: str, password: str) -> str:
    with SessionLocal() as db:
        admin_existente = db.scalar(
            select(UsuarioORM.id).where(UsuarioORM.rol == "admin").limit(1)
        )
        if admin_existente is not None:
            raise ErrorProvisionAdmin(
                "Ya existe una cuenta ADMIN. Las cuentas adicionales se crean desde el sistema."
            )

        gestor = GestorAutenticacion(
            repositorio_usuarios=UsuarioRepo(db),
            hasher=PasswordHasher(),
            tokens=JWTService(secret_key="provision-local"),
        )
        creado = gestor.crear_usuario(
            username=username,
            password=password,
            rol="admin",
            id_chofer=None,
            creado_por_id=None,
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
