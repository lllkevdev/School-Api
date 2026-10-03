from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.alumno import Alumno
from schemas.alumno import (
    Alumno as AlumnoSchema,
    AlumnoActualizar
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

    
    db.add(nuevo_alumno)
    db.commit()
    db.refresh(nuevo_alumno)

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
) -> tuple[Alumno | None, str | None]:

    alumno = db.query(Alumno).filter(
        Alumno.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno"

    cambios = datos.model_dump(exclude_unset=True)

    for campo, valor in cambios.items():
        setattr(alumno, campo, valor)
    
    db.commit()
    db.refresh(alumno)

    return alumno, None


def reemplazar_alumno(
    db: Session,
    alumno_id: int,
    datos: AlumnoSchema
) -> tuple[Alumno | None, str | None]:

    alumno = db.query(Alumno).filter(
        Alumno.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno"

    alumno.nombre = datos.nombre
    alumno.apellido = datos.apellido
    alumno.edad = datos.edad

    db.commit()
    db.refresh(alumno)

    return alumno, None


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
            return None, "tiene_calificaciones_alumno"
    
    if alumno.calificaciones:
        for calificacion in list(alumno.calificaciones):
            db.delete(calificacion)

    for inscripcion in list(alumno.inscripciones):
        db.delete(inscripcion)

    db.delete(alumno)
    db.commit()

    return alumno, None