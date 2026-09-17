from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models.alumno import Alumno as AlumnoModel
from models.materia import Materia as MateriaModel
from models.calificacion import Calificacion as CalificacionModel
from schemas.calificacion import (
    Calificacion as CalificacionSchema,
    CalificacionActualizar,
    PromedioAlumno,
    EstadisticasAlumno,
    CalificacionDetalle,
    CalificacionAlumno
)



def crear_calificacion(
    db: Session,
    calificacion: CalificacionSchema
) -> tuple[CalificacionModel | None, str | None]:

    alumno = db.query(AlumnoModel).filter(
        AlumnoModel.id == calificacion.alumno_id
    ).first()

    if alumno is None:
        return None, "alumno"

    materia = db.query(MateriaModel).filter(
        MateriaModel.id == calificacion.materia_id
    ).first()

    if materia is None:
        return None, "materia"

    nueva_calificacion = CalificacionModel(
        alumno_id=calificacion.alumno_id,
        materia_id=calificacion.materia_id,
        nota=calificacion.nota,
        periodo=calificacion.periodo
    )

    try:
        db.add(nueva_calificacion)
        db.commit()
        db.refresh(nueva_calificacion)
    except IntegrityError:
        db.rollback()
        return None, "conflicto"

    return nueva_calificacion, None




def obtener_calificaciones(
    db: Session
) -> list[CalificacionModel]:
    return db.query(CalificacionModel).all()


def buscar_calificaciones(
        db: Session,
        calificacion_id: int
) -> CalificacionModel | None:

    return db.query(CalificacionModel).filter(
        CalificacionModel.id == calificacion_id
    ).first()



def obtener_calificaciones_detalle(
    db: Session
) -> list[CalificacionDetalle]:

    calificaciones = (
        db.query(CalificacionModel)
        .options(
            joinedload(CalificacionModel.alumno),
            joinedload(CalificacionModel.materia)
        )
        .all()
    )


    resultado = []

    for calificacion in calificaciones:
        resultado.append(
            CalificacionDetalle(
                id=calificacion.id,
                alumno=f"{calificacion.alumno.nombre} {calificacion.alumno.apellido}",
                materia=calificacion.materia.nombre,
                nota=calificacion.nota,
                periodo=calificacion.periodo
            )
        )
    return resultado


def _buscar_alumno_o_error(
    db: Session,
    alumno_id: int
) -> tuple[AlumnoModel | None, str | None]:
    """Devuelve el alumno o un código de error 'alumno' si no existe."""
    alumno = db.query(AlumnoModel).filter(
        AlumnoModel.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno"

    return alumno, None

def _consulta_calificaciones_alumno(
    db: Session,
    columnas,
    alumno_id: int,
    periodo: int | None = None
):
    """Construye una consulta de agregados filtrada por alumno y periodo."""
    consulta = db.query(*columnas).filter(
        CalificacionModel.alumno_id == alumno_id
    )

    if periodo is not None:
        consulta = consulta.filter(
            CalificacionModel.periodo == periodo
        )

    return consulta

def obtener_promedio_alumno(
        db: Session,
        alumno_id: int,
        periodo: int | None = None
)-> tuple[PromedioAlumno | None, str | None]:

    alumno, error = _buscar_alumno_o_error(db, alumno_id)

    if error is not None:
        return None, error
    consulta = _consulta_calificaciones_alumno(
        db,
        [func.avg(CalificacionModel.nota)],
        alumno_id,
        periodo
    )

    promedio = consulta.scalar()

    if promedio is None:
        return None, "calificaciones"

    promedio = round(promedio, 2)

    resultado = PromedioAlumno(
        alumno=f"{alumno.nombre} {alumno.apellido}",
        promedio=promedio
    )

    return resultado, None



def actualizar_calificacion(
    db: Session,
    calificacion_id: int,
    datos: CalificacionActualizar
)-> tuple[CalificacionModel | None, str | None]:

    cambios = datos.model_dump(exclude_unset=True)

    calificacion = db.query(CalificacionModel).filter(
        CalificacionModel.id == calificacion_id
    ).first()

    if calificacion is None:
        return None, "calificacion"

    if "alumno_id" in cambios:
        alumno= db.query(AlumnoModel).filter(
            AlumnoModel.id == cambios["alumno_id"]
        ).first()

        if alumno is None:
            return None, "alumno"

    if "materia_id" in cambios:
        materia = db.query(MateriaModel).filter(
            MateriaModel.id == cambios["materia_id"]
        ).first()

        if materia is None:
            return None, "materia"

    for campo, valor in cambios.items():
        setattr(calificacion, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None, "conflicto"

    db.refresh(calificacion)

    return calificacion, None



def eliminar_calificacion(
    db: Session,
    calificacion_id: int
) -> CalificacionModel | None:

    calificacion = db.query(CalificacionModel).filter(
        CalificacionModel.id == calificacion_id
    ).first()

    if calificacion is None:
        return None

    try:
        db.delete(calificacion)
        db.commit()
    except IntegrityError:
        db.rollback()
        return None

    return calificacion



def _to_calificacion_alumno(
    calificacion: CalificacionModel,
    materia_nombre: str
) -> CalificacionAlumno:
    return CalificacionAlumno(
        materia=materia_nombre,
        nota=calificacion.nota,
        periodo=calificacion.periodo
    )


def obtener_calificaciones_alumno(
    db: Session,
    alumno_id: int,
    periodo: int | None = None
) -> tuple[list[CalificacionAlumno] | None, str | None]:

    alumno = db.query(AlumnoModel).filter(
        AlumnoModel.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno"

    calificaciones = (
        db.query(CalificacionModel)
        .options(
            joinedload(CalificacionModel.materia)
        )
        .filter(
            CalificacionModel.alumno_id == alumno_id
        )
    )

    if periodo is not None:
        calificaciones = calificaciones.filter(
            CalificacionModel.periodo == periodo
        )

    calificaciones = calificaciones.all()

    resultado = []

    for calificacion in calificaciones:
        resultado.append(
            _to_calificacion_alumno(
                calificacion,
                calificacion.materia.nombre
            )
        )

    return resultado, None



def obtener_calificaciones_alumno_join(
    db: Session,
    alumno_id: int
) -> tuple[list[CalificacionAlumno] | None, str | None]:

    alumno = db.query(AlumnoModel).filter(
        AlumnoModel.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno"

    resultados = (
        db.query(CalificacionModel, MateriaModel)
        .join(
            MateriaModel,
            CalificacionModel.materia_id == MateriaModel.id
        )
        .filter(
            CalificacionModel.alumno_id == alumno_id
        )
        .all()
    )

    resultado = []

    for calificacion, materia in resultados:
        resultado.append(
            _to_calificacion_alumno(
                calificacion,
                materia.nombre
            )
        )

    return resultado, None




def obtener_estadisticas_alumno(
        db: Session,
        alumno_id: int,
        periodo: int | None = None,
)-> tuple[EstadisticasAlumno | None, str | None]:

    alumno, error = _buscar_alumno_o_error(db, alumno_id)

    if error is not None:
        return None, error
    consulta = _consulta_calificaciones_alumno(
        db,
        [
            func.count(CalificacionModel.id),
            func.avg(CalificacionModel.nota),
            func.max(CalificacionModel.nota),
            func.min(CalificacionModel.nota)
        ],
        alumno_id,
        periodo
    )

    estadisticas = consulta.first()

    if estadisticas is None:
        return None, "calificaciones"

    if estadisticas[0] == 0:
        return None, "calificaciones"

    resultado = EstadisticasAlumno(
        alumno=f"{alumno.nombre} {alumno.apellido}",
        cantidad_calificaciones=estadisticas[0],
        promedio=round(estadisticas[1], 2),
        nota_maxima=estadisticas[2],
        nota_minima=estadisticas[3]
    )

    return resultado, None