from sqlalchemy import select
from sqlalchemy.orm import Session

from models.usuario import Usuario
from models.evaluacion import Evaluacion
from models.curso import Curso
from schemas.evaluacion import EvaluacionCrear


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

    db.add(nueva_evaluacion)
    db.commit()
    db.refresh(nueva_evaluacion)

    return nueva_evaluacion, None