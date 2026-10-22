from sqlalchemy.orm import Session

from models.curso import Curso
from models.usuario import Usuario
from schemas.curso import CursoCrear


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

    db.add(nuevo_curso)
    db.commit()
    db.refresh(nuevo_curso)

    return nuevo_curso, None