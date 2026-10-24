from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.propiedad import obtener_curso_propietario, obtener_evaluacion_propietario
from models.usuario import Usuario
from models.evaluacion import Evaluacion
from models.curso import Curso
from models.calificacion import Calificacion
from schemas.evaluacion import EvaluacionActualizar, EvaluacionCrear


def crear_evaluacion(
        db: Session,
        datos: EvaluacionCrear,
        usuario: Usuario,
) -> tuple[Evaluacion | None, str | None]:
    curso = db.scalar(
        select(Curso).where(
            Curso.id == datos.curso_id,
            Curso.docente_id == usuario.id
        )
    )

    if curso is None:
        return None, "curso_inexistente"

    if not curso.activo:
        return None, "curso_inactivo"

    if datos.periodo > curso.cantidad_periodos:
        return None, "periodo_invalido"

    nueva_evaluacion = Evaluacion(
        curso_id=curso.id,
        titulo=datos.titulo.strip(),
        fecha=datos.fecha,
        periodo=datos.periodo,
    )

    try:
        db.add(nueva_evaluacion)
        db.commit()
        db.refresh(nueva_evaluacion)
    except IntegrityError:
        db.rollback()
        raise

    return nueva_evaluacion, None


def listar_evaluaciones_por_curso(
    db: Session,
    curso_id: int,
    usuario: Usuario,
) -> tuple[list[Evaluacion] | None, str | None]:
    curso = obtener_curso_propietario(db, curso_id, usuario)
    if curso is None:
        return None, "curso_inexistente"

    evaluaciones = db.scalars(
        select(Evaluacion).where(Evaluacion.curso_id == curso.id)
    ).all()
    return list(evaluaciones), None


def obtener_evaluacion(
    db: Session,
    evaluacion_id: int,
    usuario: Usuario,
) -> tuple[Evaluacion | None, str | None]:
    evaluacion, curso = obtener_evaluacion_propietario(db, evaluacion_id, usuario)
    if evaluacion is None or curso is None:
        return None, "evaluacion_inexistente"
    return evaluacion, None


def actualizar_evaluacion(
    db: Session,
    evaluacion_id: int,
    datos: EvaluacionActualizar,
    usuario: Usuario,
) -> tuple[Evaluacion | None, str | None]:
    evaluacion, curso = obtener_evaluacion_propietario(db, evaluacion_id, usuario)
    if evaluacion is None or curso is None:
        return None, "evaluacion_inexistente"

    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        return None, "sin_cambios"

    if "titulo" in cambios and cambios["titulo"] is not None:
        cambios["titulo"] = cambios["titulo"].strip()
    if "periodo" in cambios and cambios["periodo"] is not None:
        if cambios["periodo"] > curso.cantidad_periodos:
            return None, "periodo_invalido"

    for campo, valor in cambios.items():
        setattr(evaluacion, campo, valor)

    try:
        db.commit()
        db.refresh(evaluacion)
    except IntegrityError:
        db.rollback()
        raise

    return evaluacion, None


def eliminar_evaluacion(
    db: Session,
    evaluacion_id: int,
    usuario: Usuario,
) -> tuple[bool, str | None]:
    evaluacion, curso = obtener_evaluacion_propietario(db, evaluacion_id, usuario)
    if evaluacion is None or curso is None:
        return False, "evaluacion_inexistente"

    calificacion = db.scalar(select(Calificacion.id).where(Calificacion.evaluacion_id == evaluacion.id))
    if calificacion is not None:
        return False, "tiene_calificaciones"

    try:
        db.delete(evaluacion)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    return True, None