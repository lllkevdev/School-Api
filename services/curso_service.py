from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.propiedad import obtener_curso_propietario
from models.curso import Curso
from models.evaluacion import Evaluacion
from models.inscripcion import Inscripcion
from models.invitacion import Invitacion
from models.usuario import Usuario
from schemas.curso import CursoActualizar, CursoCrear


def listar_cursos_por_alumno(
    db: Session,
    alumno_id: int,
) -> list[Curso]:
    cursos = db.scalars(
        select(Curso).join(Inscripcion).where(
            Inscripcion.alumno_id == alumno_id,
            Curso.activo == True,
        ).distinct()
    ).all()
    return list(cursos)


def crear_curso(
    db: Session,
    datos: CursoCrear,
    usuario: Usuario,
) -> tuple[Curso | None, str | None]:

    nuevo_curso = Curso(
        docente_id=usuario.id,
        nombre_materia=datos.nombre_materia.strip(),
        division=datos.division.strip(),
        anio_lectivo=datos.anio_lectivo,
        cantidad_periodos=datos.cantidad_periodos,
    )

    try:
        db.add(nuevo_curso)
        db.commit()
        db.refresh(nuevo_curso)
    except IntegrityError:
        db.rollback()
        raise

    return nuevo_curso, None


def listar_cursos(
    db: Session,
    usuario: Usuario,
) -> list[Curso]:
    cursos = db.scalars(
        select(Curso).where(Curso.docente_id == usuario.id)
    ).all()
    return list(cursos)


def obtener_curso(
    db: Session,
    curso_id: int,
    usuario: Usuario,
) -> tuple[Curso | None, str | None]:
    curso = obtener_curso_propietario(db, curso_id, usuario)
    if curso is None:
        return None, "curso_inexistente"
    return curso, None


def actualizar_curso(
    db: Session,
    curso_id: int,
    datos: CursoActualizar,
    usuario: Usuario,
) -> tuple[Curso | None, str | None]:
    curso = obtener_curso_propietario(db, curso_id, usuario)
    if curso is None:
        return None, "curso_inexistente"

    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        return None, "sin_cambios"

    if "nombre_materia" in cambios and cambios["nombre_materia"] is not None:
        cambios["nombre_materia"] = cambios["nombre_materia"].strip()
    if "division" in cambios and cambios["division"] is not None:
        cambios["division"] = cambios["division"].strip()

    for campo, valor in cambios.items():
        setattr(curso, campo, valor)

    try:
        db.commit()
        db.refresh(curso)
    except IntegrityError:
        db.rollback()
        raise

    return curso, None


def archivar_curso(
    db: Session,
    curso_id: int,
    usuario: Usuario,
) -> tuple[Curso | None, str | None]:
    curso = obtener_curso_propietario(db, curso_id, usuario)
    if curso is None:
        return None, "curso_inexistente"

    if not curso.activo:
        return None, "curso_inactivo"

    return _cambiar_estado_curso(db, curso, False)


def reactivar_curso(
    db: Session,
    curso_id: int,
    usuario: Usuario,
) -> tuple[Curso | None, str | None]:
    curso = obtener_curso_propietario(db, curso_id, usuario)
    if curso is None:
        return None, "curso_inexistente"

    if curso.activo:
        return None, "curso_activo"

    return _cambiar_estado_curso(db, curso, True)


def _cambiar_estado_curso(
    db: Session,
    curso: Curso,
    activo: bool,
) -> tuple[Curso | None, str | None]:
    curso.activo = activo

    try:
        db.commit()
        db.refresh(curso)
    except IntegrityError:
        db.rollback()
        raise

    return curso, None


def eliminar_curso(
    db: Session,
    curso_id: int,
    usuario: Usuario,
) -> tuple[bool, str | None]:
    curso = obtener_curso_propietario(db, curso_id, usuario)
    if curso is None:
        return False, "curso_inexistente"

    inscripciones = db.scalar(select(Inscripcion.id).where(Inscripcion.curso_id == curso.id))
    if inscripciones is not None:
        return False, "tiene_inscripciones"

    evaluaciones = db.scalar(select(Evaluacion.id).where(Evaluacion.curso_id == curso.id))
    if evaluaciones is not None:
        return False, "tiene_evaluaciones"

    invitaciones = db.scalar(select(Invitacion.id).where(Invitacion.curso_id == curso.id))
    if invitaciones is not None:
        return False, "tiene_invitaciones"

    try:
        db.delete(curso)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    return True, None