from sqlalchemy import select
from sqlalchemy.orm import Session

from models.usuario import Usuario
from schemas.usuario import UsuarioCrear
from security.password import hash_password

from sqlalchemy.exc import IntegrityError

def buscar_usuario_por_email(
    db: Session,
    email: str
) -> Usuario | None:
    return db.scalar(
        select(Usuario).where(Usuario.email == email)
    )


def crear_usuario(
    db: Session,
    usuario: UsuarioCrear
) -> Usuario:

    password_hash = hash_password(usuario.password)

    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=password_hash,
        rol=usuario.rol,
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        return nuevo_usuario

    except IntegrityError:
        db.rollback()
        raise