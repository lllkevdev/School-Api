from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.alumno import Alumno as AlumnoModel
from models.inscripcion import Inscripcion as InscripcionModel
from models.materia import Materia as MateriaModel
from schemas.inscripcion import Inscripcion


def crear_inscripcion(
        db: Session,
        inscripcion: Inscripcion,
) -> tuple[InscripcionModel | None, str | None]:

    alumno = db.query(AlumnoModel).filter(
        AlumnoModel.id == inscripcion.alumno_id
    ).first()

    if alumno is None:
        return None, "alumno_inscripcion"

    materia = db.query(MateriaModel).filter(
        MateriaModel.id == inscripcion.materia_id
    ).first()

    if materia is None:
        return None, "materia_inscripcion"

    nueva_inscripcion = InscripcionModel(
        alumno_id=inscripcion.alumno_id,
        materia_id=inscripcion.materia_id
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
) -> tuple[bool, str | None]:

    inscripcion = db.query(InscripcionModel).filter(
        InscripcionModel.id == inscripcion_id
    ).first()

    if inscripcion is None:
        return False, "inscripcion"

    db.delete(inscripcion)
    db.commit()

    return True, None
