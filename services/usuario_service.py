from sqlalchemy import select
from sqlalchemy.orm import Session

from models.usuario import Usuario
from schemas.usuario import (
    UsuarioCrear, 
    MaestroCrear,
    MaestroActualizar
)
from schemas.roles import Rol
from core.security import hash_password

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


def crear_maestro(db: Session, maestro: MaestroCrear) -> Usuario:
    nuevo_maestro = Usuario(
        nombre=maestro.nombre,
        apellido=maestro.apellido,
        email=maestro.email,
        telefono=maestro.telefono,
        password_hash=hash_password(maestro.password),
        rol=Rol.MAESTRO,
    )

    try:
        db.add(nuevo_maestro)
        db.commit()
        db.refresh(nuevo_maestro)
        return nuevo_maestro
    except IntegrityError:
        db.rollback()
        raise


def obtener_maestros(db: Session) -> list[Usuario]:
    return db.scalars(
        select(Usuario).where(
            Usuario.rol == Rol.MAESTRO,
            Usuario.activo.is_(True),
        )
    ).all()


def actualizar_maestro(
    db: Session,
    maestro_id: int,
    datos: MaestroActualizar,
) -> tuple[Usuario | None, str | None]:
    maestro = db.scalar(
        select(Usuario).where(
            Usuario.id == maestro_id,
            Usuario.rol == Rol.MAESTRO,
        )
    )

    if maestro is None:
        return None, "maestro_no_encontrado"

    cambios = datos.model_dump(exclude_unset=True)

    for campo, valor in cambios.items():
        setattr(maestro, campo, valor)

    try:
        db.commit()
        db.refresh(maestro)
        return maestro, None
    except IntegrityError:
        db.rollback()
        raise


def desactivar_maestro(
    db: Session,
    maestro_id: int,
) -> tuple[Usuario | None, str | None]:
    maestro = db.scalar(
        select(Usuario).where(
            Usuario.id == maestro_id,
            Usuario.rol == Rol.MAESTRO,
        )
    )

    if maestro is None:
        return None, "maestro_no_encontrado"

    maestro.activo = False

    db.commit()
    db.refresh(maestro)

    return maestro, None