from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.security import hash_password
from models.usuario import Usuario
from schemas.roles import Rol
from schemas.usuario import UsuarioActualizar, UsuarioRegistro


def buscar_usuario_por_email(
    db: Session,
    email: str,
) -> Usuario | None:
    return db.scalar(
        select(Usuario).where(Usuario.email == email)
    )


def crear_usuario(
    db: Session,
    datos: UsuarioRegistro,
) -> Usuario:
    nuevo_usuario = Usuario(
        nombre=datos.nombre.strip(),
        apellido=datos.apellido.strip(),
        email=str(datos.email).lower(),
        telefono=datos.telefono,
        password_hash=hash_password(datos.password),
        rol=Rol.ADMIN,
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except IntegrityError:
        db.rollback()
        raise


def actualizar_usuario(
    db: Session,
    usuario_id: int,
    datos: UsuarioActualizar,
) -> tuple[Usuario | None, str | None]:
    usuario = db.scalar(
        select(Usuario).where(Usuario.id == usuario_id)
    )

    if usuario is None:
        return None, "usuario_no_encontrado"

    cambios = datos.model_dump(exclude_unset=True)

    if "nombre" in cambios and cambios["nombre"] is not None:
        cambios["nombre"] = cambios["nombre"].strip()

    if "apellido" in cambios and cambios["apellido"] is not None:
        cambios["apellido"] = cambios["apellido"].strip()

    if "email" in cambios and cambios["email"] is not None:
        cambios["email"] = str(cambios["email"]).lower()

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    try:
        db.commit()
        db.refresh(usuario)
        return usuario, None
    except IntegrityError:
        db.rollback()
        raise