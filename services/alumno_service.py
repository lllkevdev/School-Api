from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from schemas.inscripcion import Inscripcion 

from models.alumno import Alumno
from schemas.alumno import (
    Alumno as AlumnoSchema,
    AlumnoActualizar
)
from schemas.calificacion import (
    AlumnoConCalificaciones,
    CalificacionAlumno
)

from core.permisos import Rol

def crear_alumno(
    db: Session,
    alumno: AlumnoSchema
) -> Alumno:

    nuevo_alumno = Alumno(
        nombre=alumno.nombre,
        apellido=alumno.apellido,
        edad=alumno.edad
    )

    try:
        db.add(nuevo_alumno)
        db.commit()
        db.refresh(nuevo_alumno)

    except IntegrityError:
        db.rollback()
        raise

    return nuevo_alumno


def obtener_alumnos(db: Session) -> list[Alumno]:
    return db.query(Alumno).all()





def buscar_alumno(
    db: Session,
    alumno_id: int,
    usuario: dict
) -> tuple[Alumno | None, str | None]:

    alumno = db.query(Alumno).filter(
        Alumno.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno"

    if usuario["rol"] == Rol.ALUMNO:
        if usuario["alumno_id"] != alumno_id:
            return None, "permiso"

    return alumno, None






def actualizar_alumno(
    db: Session,
    alumno_id: int,
    datos: AlumnoActualizar
) -> Alumno | None:

    alumno = db.query(Alumno).filter(
        Alumno.id == alumno_id
    ).first()

    if alumno is None:
        return None

    cambios = datos.model_dump(exclude_unset=True)

    for campo, valor in cambios.items():
        setattr(alumno, campo, valor)

    try:
        db.commit()
        db.refresh(alumno)

    except IntegrityError:
        db.rollback()
        raise

    return alumno




def reemplazar_alumno(
    db: Session,
    alumno_id: int,
    datos: AlumnoSchema
) -> Alumno | None:

    alumno = db.query(Alumno).filter(
        Alumno.id == alumno_id
    ).first()

    if alumno is None:
        return None

    alumno.nombre = datos.nombre
    alumno.apellido = datos.apellido
    alumno.edad = datos.edad

    try:
        db.commit()
        db.refresh(alumno)

    except IntegrityError:
        db.rollback()
        raise

    return alumno




def eliminar_alumno(
    db: Session,
    alumno_id: int,
    forzar: bool = False
) -> tuple[Alumno | None, str | None]:

    alumno = db.query(Alumno).filter(
        Alumno.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno"

    if alumno.calificaciones:
        if not forzar:
            return None, "tiene_calificaciones"

    try:
        if alumno.calificaciones:
            for calificacion in list(alumno.calificaciones):
                db.delete(calificacion)

        for inscripcion in list(alumno.inscripciones):
            db.delete(inscripcion)

        db.delete(alumno)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise

    return alumno, None


def obtener_alumno_con_calificaciones(
    db: Session,
    alumno_id: int,
    usuario: dict
) -> tuple[AlumnoConCalificaciones | None, str | None]:

    alumno, error = buscar_alumno(
        db,
        alumno_id,
        usuario
    )

    if error:
        return None, error

    calificaciones_permitidas = alumno.calificaciones

    if usuario["rol"] == Rol.MAESTRO:
        calificaciones_permitidas = [
            calificacion
            for calificacion in calificaciones_permitidas
            if calificacion.materia.maestro_id == usuario["id"]
        ]

    calificaciones: list[CalificacionAlumno] = []

    for calificacion in calificaciones_permitidas:
        calificaciones.append(
            CalificacionAlumno(
                materia=calificacion.materia.nombre,
                nota=calificacion.nota,
                periodo=calificacion.periodo
            )
        )

    if calificaciones:
        promedio = sum(
            calificacion.nota
            for calificacion in calificaciones
        ) / len(calificaciones)
    else:
        promedio = 0

    return AlumnoConCalificaciones(
        id=alumno.id,
        nombre=alumno.nombre,
        apellido=alumno.apellido,
        calificaciones=calificaciones,
        promedio=round(promedio, 2)
    ), None
