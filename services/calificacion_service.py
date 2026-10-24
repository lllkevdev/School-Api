from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.calificacion import Calificacion
from models.curso import Curso
from models.evaluacion import Evaluacion
from models.inscripcion import Inscripcion
from models.usuario import Usuario
from models.alumno import Alumno
from schemas.calificacion import (
    CalificacionActualizar,
    CalificacionCrear,
)


def listar_calificaciones_alumno(
    db: Session,
    alumno_id: int,
) -> list[Calificacion]:
    calificaciones = db.scalars(
        select(Calificacion).where(Calificacion.alumno_id == alumno_id)
    ).all()
    return list(calificaciones)


def obtener_promedio_alumno(
    db: Session,
    alumno_id: int,
) -> tuple[float | None, str | None]:
    calificaciones = db.scalars(
        select(Calificacion).where(Calificacion.alumno_id == alumno_id)
    ).all()
    if not calificaciones:
        return None, "calificaciones"
    total = sum(c.nota for c in calificaciones)
    promedio = total / len(calificaciones)
    return round(promedio, 2), None


def obtener_historial_alumno(
    db: Session,
    alumno_id: int,
) -> list[Calificacion]:
    calificaciones = db.scalars(
        select(Calificacion).where(Calificacion.alumno_id == alumno_id)
    ).all()
    return list(calificaciones)


def obtener_promedio_por_curso(
    db: Session,
    curso_id: int,
    usuario: Usuario,
) -> tuple[float | None, str | None]:
    from core.propiedad import obtener_curso_propietario

    curso = obtener_curso_propietario(db, curso_id, usuario)
    if curso is None:
        return None, "curso_inexistente"

    calificaciones = db.scalars(
        select(Calificacion).where(Calificacion.curso_id == curso.id)
    ).all()
    if not calificaciones:
        return None, "calificaciones"
    total = sum(c.nota for c in calificaciones)
    promedio = total / len(calificaciones)
    return round(promedio, 2), None


def generar_csv_calificaciones(
    db: Session,
    curso_id: int,
    usuario: Usuario,
):
    from core.propiedad import obtener_curso_propietario
    from models.alumno import Alumno

    curso = obtener_curso_propietario(db, curso_id, usuario)
    if curso is None:
        return None, "curso_inexistente"

    calificaciones = db.scalars(
        select(Calificacion).where(Calificacion.curso_id == curso.id)
    ).all()

    lineas = ["alumno_id,nombre,apellido,evaluacion_id,nota,curso_id"]
    for c in calificaciones:
        alumno = db.get(Alumno, c.alumno_id)
        nombre = alumno.nombre if alumno else ""
        apellido = alumno.apellido if alumno else ""
        lineas.append(f"{c.alumno_id},{nombre},{apellido},{c.evaluacion_id},{c.nota},{c.curso_id}")

    return "\n".join(lineas) + "\n"


def crear_calificacion(
        db: Session,
        datos: CalificacionCrear,
        usuario: Usuario,
) -> tuple[Calificacion | None, str | None]:

    evaluacion = db.scalar(
        select(Evaluacion).join(Curso).where(
            Evaluacion.id == datos.evaluacion_id,
            Curso.docente_id == usuario.id,
        )
    )

    if evaluacion is None:
        return None, "evaluacion_inexistente"

    if not evaluacion.curso.activo:
        return None, "curso_inactivo"

    inscripcion = db.scalar(
        select(Inscripcion.id).where(
            Inscripcion.alumno_id == datos.alumno_id,
            Inscripcion.curso_id == evaluacion.curso_id,
        )
    )

    if inscripcion is None:
        return None, "alumno_no_inscripto"

    calificacion_existente = db.scalar(
        select(Calificacion.id).where(
            Calificacion.alumno_id == datos.alumno_id,
            Calificacion.evaluacion_id == datos.evaluacion_id,
        )
    )

    if calificacion_existente is not None:
        return None, "calificacion_duplicada"

    nueva_calificacion = Calificacion(
        alumno_id=datos.alumno_id,
        evaluacion_id=evaluacion.id,
        curso_id=evaluacion.curso_id,
        nota=datos.nota,
    )

    try:
        db.add(nueva_calificacion)
        db.commit()
        db.refresh(nueva_calificacion)
    except IntegrityError:
        db.rollback()
        raise

    return nueva_calificacion, None


def actualizar_calificacion(
    db: Session,
    calificacion_id: int,
    datos: CalificacionActualizar,
    usuario: Usuario,
) -> tuple[Calificacion | None, str | None]:

    calificacion = db.scalar(
        select(Calificacion).join(Curso).where(
            Calificacion.id == calificacion_id,
            Curso.docente_id == usuario.id,
        )
    )

    if calificacion is None:
        return None, "calificacion_inexistente"

    calificacion.nota = datos.nota

    try:
        db.commit()
        db.refresh(calificacion)
    except IntegrityError:
        db.rollback()
        raise

    return calificacion, None


def listar_calificaciones(
    db: Session,
    curso_id: int,
    usuario: Usuario,
) -> tuple[list[Calificacion] | None, str | None]:

    curso = db.scalar(
        select(Curso).where(
            Curso.id == curso_id,
            Curso.docente_id == usuario.id,
        )
    )

    if curso is None:
        return None, "curso_inexistente"

    calificaciones = db.scalars(
        select(Calificacion).where(
            Calificacion.curso_id == curso.id,
        )
    ).all()

    return calificaciones, None


def eliminar_calificacion(
    db: Session,
    calificacion_id: int,
    usuario: Usuario,
) -> tuple[bool, str | None]:

    calificacion = db.scalar(
        select(Calificacion).join(Curso).where(
            Calificacion.id == calificacion_id,
            Curso.docente_id == usuario.id,
        )
    )

    if calificacion is None:
        return False, "calificacion_inexistente"

    try:
        db.delete(calificacion)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    return True, None