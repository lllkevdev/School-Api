from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.inscripcion import Inscripcion
from models.curso import Curso
from models.alumno import Alumno
from models.usuario import Usuario
from schemas.alumno import AlumnoCrear
from schemas.roles import Rol


def crear_alumno(
    db: Session,
    datos: AlumnoCrear,
    usuario: Usuario,
) -> tuple[Alumno | None, str | None]:

    alumno_existente = db.scalar(
        select(Alumno).where(
            Alumno.documento_identidad == datos.documento_identidad,
        )
    )

    if alumno_existente is not None:
        return None, "documento_duplicado"

    nuevo_alumno = Alumno(
        nombre=datos.nombre,
        apellido=datos.apellido,
        documento_identidad=datos.documento_identidad,
        fecha_nacimiento=datos.fecha_nacimiento,
    )

    try:
        db.add(nuevo_alumno)
        db.commit()
        db.refresh(nuevo_alumno)
    except IntegrityError:
        db.rollback()
        raise

    return nuevo_alumno, None


def obtener_alumnos(
    db: Session,
    usuario: Usuario,
) -> list[Alumno]:

    if usuario.rol == Rol.ADMIN:
        alumnos = db.scalars(
            select(Alumno).order_by(Alumno.id)
        ).all()
        return list(alumnos)

    alumnos = db.scalars(
        select(Alumno).join(Inscripcion).join(Curso).where(
            Curso.docente_id == usuario.id,
        ).distinct()
    ).all()

    return list(alumnos)


def buscar_alumno(
    db: Session,
    alumno_id: int,
    usuario: Usuario,
) -> tuple[Alumno | None, str | None]:

    alumno = db.scalar(
        select(Alumno).where(
            Alumno.id == alumno_id
        )
    )

    if alumno is None:
        return None, "alumno_inexistente"

    if usuario.rol == Rol.ADMIN:
        return alumno, None

    alumno_accesible = db.scalar(
        select(Alumno).join(Inscripcion).join(Curso).where(
            Alumno.id == alumno_id,
            Curso.docente_id == usuario.id,
        )
    )

    if alumno_accesible is None:
        return None, "permiso"

    return alumno, None



def desactivar_alumno(
    db: Session,
    alumno_id: int,
    usuario: Usuario,
) -> tuple[Alumno | None, str | None]:

    alumno, error = buscar_alumno(db, alumno_id, usuario)

    if error is not None:
        return None, error

    if alumno is None:
        return None, "alumno_inexistente"

    if not alumno.activo:
        return None, "alumno_inactivo"

    alumno.activo = False

    try:
        db.commit()
        db.refresh(alumno)
    except IntegrityError:
        db.rollback()
        raise

    return alumno, None