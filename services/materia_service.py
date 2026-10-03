from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.materia import Materia
from schemas.materia import (
    Materia as MateriaSchema,
    MateriaActualizar as MateriaActualizarSchema
)


def crear_materia(
    db: Session,
    materia: MateriaSchema
) -> tuple[Materia | None, str | None]:

    nueva_materia = Materia(
        nombre=materia.nombre
    )

    try:
        db.add(nueva_materia)
        db.commit()
        db.refresh(nueva_materia)

        return nueva_materia, None

    except IntegrityError:
        db.rollback()
        return None, "materia_conflicto"


def obtener_materias(
    db: Session
) -> list[Materia]:
    
    return db.query(Materia).all()


def buscar_materia(
    db: Session,
    materia_id: int
) -> tuple[Materia | None, str | None]:

    materia = db.query(Materia).filter(
        Materia.id == materia_id
    ).first()

    if materia is None:
        return None, "materia"

    return materia, None


def actualizar_materia(
    db: Session,
    materia_id: int,
    materia: MateriaSchema
) -> tuple[Materia | None, str | None]:

    materia_existente, error = buscar_materia(
        db,
        materia_id
    )

    if error:
        return None, error

    if materia_existente is None:
        return None, "materia"

    materia_existente.nombre = materia.nombre

    try:
        db.commit()
        db.refresh(materia_existente)
        return materia_existente, None

    except IntegrityError:
        db.rollback()
        return None, "materia_conflicto"


def actualizar_materia_parcialmente(
    db: Session, 
    materia_id: int, 
    materia: MateriaActualizarSchema
) -> tuple[Materia | None, str | None]:
    
    materia_existente, error = buscar_materia(db, materia_id)

    if error:
        return None, error

    if not materia_existente:
        return None,"materia"

    cambios = materia.model_dump(exclude_unset=True)

    if not cambios:
        return None, "sin_cambios"

    if materia.nombre is not None:
        materia_existente.nombre = materia.nombre

    try:
        db.commit()
        db.refresh(materia_existente)
        return materia_existente, None
    except IntegrityError:
        db.rollback()
        return None, "materia_conflicto"


def eliminar_materia(
    db: Session, 
    materia_id: int
)-> tuple[Materia | None, str | None]:
    
    materia, error= buscar_materia(db, materia_id)

    if error:
        return None, error

    if materia is None:
        return None, "materia"

    if materia.calificaciones:
        return None, "tiene_calificaciones"
    

    for inscripcion in list(materia.inscripciones):
        db.delete(inscripcion)

    db.delete(materia)
    db.commit()

    return materia, None