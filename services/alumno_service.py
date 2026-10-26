from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.inscripcion import Inscripcion
from models.curso import Curso
from models.alumno import Alumno
from models.usuario import Usuario
from schemas.alumno import (
    AlumnoConInscripcionCrear,
    AlumnoConInscripcionRespuesta,
)


def _codigo_conflicto_alta(
    db: Session,
    documento_identidad: str,
    curso_id: int,
) -> str | None:
    alumno = db.scalar(
        select(Alumno).where(
            Alumno.documento_identidad == documento_identidad,
        )
    )

    if alumno is None:
        return None

    inscripcion = db.scalar(
        select(Inscripcion.id).where(
            Inscripcion.alumno_id == alumno.id,
            Inscripcion.curso_id == curso_id,
        )
    )

    if inscripcion is not None:
        return "inscripcion_duplicada"

    return "documento_duplicado"


def crear_alumno_con_inscripcion(
    db: Session,
    datos: AlumnoConInscripcionCrear,
    usuario: Usuario,
) -> tuple[AlumnoConInscripcionRespuesta | None, str | None]:

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

    alumno = db.scalar(
        select(Alumno).where(
            Alumno.documento_identidad == datos.documento_identidad,
        )
    )

    if alumno is not None:
        inscripcion_existente = db.scalar(
            select(Inscripcion.id).where(
                Inscripcion.alumno_id == alumno.id,
                Inscripcion.curso_id == curso.id,
            )
        )

        if inscripcion_existente is not None:
            return None, "inscripcion_duplicada"

        if not alumno.activo:
            return None, "alumno_inactivo"

        if not datos.confirmar_existente:
            return AlumnoConInscripcionRespuesta(
                alumno=alumno,
                inscripcion=None,
                requiere_confirmacion=True,
            ), None

        inscripcion = Inscripcion(
            alumno_id=alumno.id,
            curso_id=curso.id,
        )

        try:
            db.add(inscripcion)
            db.commit()
            db.refresh(inscripcion)
        except IntegrityError:
            db.rollback()
            codigo = _codigo_conflicto_alta(
                db,
                datos.documento_identidad,
                curso.id,
            )
            if codigo is not None:
                return None, codigo
            raise

        return AlumnoConInscripcionRespuesta(
            alumno=alumno,
            inscripcion=inscripcion,
            requiere_confirmacion=False,
        ), None

    nuevo_alumno = Alumno(
        nombre=datos.nombre,
        apellido=datos.apellido,
        documento_identidad=datos.documento_identidad,
        fecha_nacimiento=datos.fecha_nacimiento,
    )

    try:
        db.add(nuevo_alumno)
        db.flush()

        inscripcion = Inscripcion(
            alumno_id=nuevo_alumno.id,
            curso_id=curso.id,
        )
        db.add(inscripcion)

        db.commit()
        db.refresh(nuevo_alumno)
        db.refresh(inscripcion)
    except IntegrityError:
        db.rollback()
        codigo = _codigo_conflicto_alta(
            db,
            datos.documento_identidad,
            curso.id,
        )
        if codigo is not None:
            return None, codigo
        raise

    return AlumnoConInscripcionRespuesta(
        alumno=nuevo_alumno,
        inscripcion=inscripcion,
        requiere_confirmacion=False,
    ), None


def obtener_alumnos(
    db: Session,
    usuario: Usuario,
) -> list[Alumno]:

    alumnos = db.scalars(
        select(Alumno)
        .join(Inscripcion, Inscripcion.alumno_id == Alumno.id)
        .join(Curso, Curso.id == Inscripcion.curso_id)
        .where(Curso.docente_id == usuario.id)
        .distinct()
        .order_by(Alumno.id)
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

    alumno_accesible = db.scalar(
        select(Alumno.id)
        .join(Inscripcion, Inscripcion.alumno_id == Alumno.id)
        .join(Curso, Curso.id == Inscripcion.curso_id)
        .where(
            Alumno.id == alumno_id,
            Curso.docente_id == usuario.id,
        )
        .limit(1)
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

    curso_ajeno = db.scalar(
        select(Inscripcion.id)
        .join(Curso, Curso.id == Inscripcion.curso_id)
        .where(
            Inscripcion.alumno_id == alumno.id,
            Curso.docente_id != usuario.id,
        )
        .limit(1)
    )

    if curso_ajeno is not None:
        return None, "alumno_compartido"

    alumno.activo = False

    try:
        db.commit()
        db.refresh(alumno)
    except IntegrityError:
        db.rollback()
        raise

    return alumno, None