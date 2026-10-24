from sqlalchemy.orm import Session
from sqlalchemy import select

from models.curso import Curso
from models.evaluacion import Evaluacion
from models.usuario import Usuario


def obtener_curso_propietario(
    db: Session,
    curso_id: int,
    usuario: Usuario,
) -> Curso | None:
    return db.scalar(
        select(Curso).where(
            Curso.id == curso_id,
            Curso.docente_id == usuario.id,
        )
    )


def obtener_evaluacion_propietario(
    db: Session,
    evaluacion_id: int,
    usuario: Usuario,
) -> tuple[Evaluacion | None, Curso | None]:
    evaluacion = db.scalar(
        select(Evaluacion).where(Evaluacion.id == evaluacion_id)
    )
    if evaluacion is None:
        return None, None
    curso = db.scalar(
        select(Curso).where(
            Curso.id == evaluacion.curso_id,
            Curso.docente_id == usuario.id,
        )
    )
    if curso is None:
        return None, None
    return evaluacion, curso
