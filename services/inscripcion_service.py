from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.alumno import Alumno
from models.curso import Curso
from models.inscripcion import Inscripcion
from models.usuario import Usuario
from models.calificacion import Calificacion
from models.evaluacion import Evaluacion
from schemas.inscripcion import InscripcionCrear


def crear_inscripcion(
    db: Session,
    datos: InscripcionCrear,
    usuario: Usuario,
) -> tuple[Inscripcion | None, str | None]:
    alumno = db.scalar(
        select(Alumno).where(
            Alumno.id == datos.alumno_id,
        )
    )

    if alumno is None:
        return None, "alumno_inexistente"

    curso = db.scalar(
        select(Curso).where(
            Curso.id == datos.curso_id,
            Curso.docente_id == usuario.id,
        )
    )

    if curso is None:
        return None, "curso_inexistente"

    if not curso.activo:
        return None, "curso_inactivo"

    inscripcion_existente = db.scalar(
        select(Inscripcion.id).where(
            Inscripcion.alumno_id == alumno.id,
            Inscripcion.curso_id == curso.id,
        )
    )

    if inscripcion_existente is not None:
        return None, "inscripcion_duplicada"

    nueva_inscripcion = Inscripcion(
        alumno_id=alumno.id,
        curso_id=curso.id,
    )

    try:
        db.add(nueva_inscripcion)
        db.commit()
        db.refresh(nueva_inscripcion)
    except IntegrityError:
        db.rollback()
        raise

    return nueva_inscripcion, None


def eliminar_inscripcion(
    db: Session,
    inscripcion_id: int,
    usuario: Usuario,
) -> tuple[bool, str | None]:

    inscripcion = db.scalar(
        select(Inscripcion).join(Curso).where(
            Inscripcion.id == inscripcion_id,
            Curso.docente_id == usuario.id,
        )
    )

    if inscripcion is None:
        return False, "inscripcion_inexistente"

    calificacion_existente = db.scalar(
        select(Calificacion.id).join(Evaluacion).where(
            Calificacion.alumno_id == inscripcion.alumno_id,
            Evaluacion.curso_id == inscripcion.curso_id,
        )
    )

    if calificacion_existente is not None:
        return False, "inscripcion_con_calificaciones"

    try:
        db.delete(inscripcion)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    return True, None