from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.alumno import Alumno
from models.calificacion import Calificacion
from models.curso import Curso
from models.evaluacion import Evaluacion
from models.inscripcion import Inscripcion as InscripcionModel
from models.usuario import Usuario
from schemas.inscripcion import InscripcionCrear


def crear_inscripcion(
    db: Session,
    inscripcion: InscripcionCrear,
    usuario: Usuario,
) -> tuple[InscripcionModel | None, str | None]:

    alumno = db.scalar(
        select(Alumno).where(
            Alumno.id == inscripcion.alumno_id
        )
    )

    if alumno is None:
        return None, "alumno_inscripcion"

    curso = db.scalar(
        select(Curso).where(
            Curso.id == inscripcion.curso_id,
            Curso.docente_id == usuario.id,
            Curso.activo.is_(True),
        )
    )

    if curso is None:
        return None, "curso_inscripcion"

    nueva_inscripcion = InscripcionModel(
        alumno_id=inscripcion.alumno_id,
        curso_id=inscripcion.curso_id,
    )

    try:
        db.add(nueva_inscripcion)
        db.commit()
        db.refresh(nueva_inscripcion)
    except IntegrityError:
        db.rollback()
        return None, "inscripcion_conflicto"

    return nueva_inscripcion, None


def eliminar_inscripcion(
    db: Session,
    inscripcion_id: int,
    usuario: Usuario,
) -> tuple[bool, str | None]:

    inscripcion = db.scalar(
        select(InscripcionModel)
        .join(Curso)
        .where(
            InscripcionModel.id == inscripcion_id,
            Curso.docente_id == usuario.id,
        )
    )

    if inscripcion is None:
        return False, "inscripcion_inexistente"

    tiene_calificaciones = db.scalar(
        select(Calificacion.id)
        .join(
            Evaluacion,
            Calificacion.evaluacion_id == Evaluacion.id,
        )
        .where(
            Calificacion.alumno_id == inscripcion.alumno_id,
            Evaluacion.curso_id == inscripcion.curso_id,
        )
        .limit(1)
    )

    if tiene_calificaciones is not None:
        return False, "inscripcion_con_calificaciones"

    db.delete(inscripcion)
    db.commit()

    return True, None