from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from sqlalchemy.exc import IntegrityError


from models import calificacion
from models.alumno import Alumno as AlumnoModel
from models.materia import Materia as MateriaModel
from models.calificacion import Calificacion as CalificacionModel
from models.inscripcion import Inscripcion as InscripcionModel

from schemas.calificacion import (
    Calificacion as CalificacionSchema,
    CalificacionActualizar,
    PromedioAlumno,
    EstadisticasAlumno,
    CalificacionDetalle,
    CalificacionAlumno,
)

from core.permisos import Rol


# ============================================================
# CREACIÓN
# ============================================================

def crear_calificacion(
    db: Session,
    calificacion: CalificacionSchema,
    usuario: dict,
) -> tuple[CalificacionModel | None, str | None]:

    alumno = db.query(AlumnoModel).filter(
        AlumnoModel.id == calificacion.alumno_id
    ).first()

    if alumno is None:
        return None, "alumno_calificacion"

    materia = db.query(MateriaModel).filter(
        MateriaModel.id == calificacion.materia_id
    ).first()

    if materia is None:
        return None, "materia_calificacion"

    inscripcion = db.query(InscripcionModel).filter(
        InscripcionModel.alumno_id == calificacion.alumno_id,
        InscripcionModel.materia_id == calificacion.materia_id,
    ).first()

    if inscripcion is None:
        return None, "inscripcion_calificacion"

    if usuario["rol"] == Rol.MAESTRO:
        if usuario["id"] != materia.maestro_id:
            return None, "maestro"

    nueva_calificacion = CalificacionModel(
        alumno_id=calificacion.alumno_id,
        materia_id=calificacion.materia_id,
        nota=calificacion.nota,
        periodo=calificacion.periodo,
    )

    try:
        db.add(nueva_calificacion)
        db.commit()
        db.refresh(nueva_calificacion)
    except IntegrityError:
        db.rollback()
        return None, "conflicto"

    return nueva_calificacion, None


# ============================================================
# CONSULTAS GENERALES — ADMIN
# ============================================================

def obtener_calificaciones(
    db: Session,
) -> list[CalificacionModel]:

    return db.query(CalificacionModel).all()


def obtener_calificaciones_detalle(
    db: Session,
) -> list[CalificacionDetalle]:

    calificaciones = (
        db.query(CalificacionModel)
        .options(
            joinedload(CalificacionModel.alumno),
            joinedload(CalificacionModel.materia),
        )
        .all()
    )

    resultado = []

    for calificacion in calificaciones:
        resultado.append(
            CalificacionDetalle(
                id=calificacion.id,
                alumno=(
                    f"{calificacion.alumno.nombre} "
                    f"{calificacion.alumno.apellido}"
                ),
                materia=calificacion.materia.nombre,
                nota=calificacion.nota,
                periodo=calificacion.periodo,
            )
        )

    return resultado


# ============================================================
# CONSULTA INDIVIDUAL
# ============================================================

def buscar_calificaciones(
    db: Session,
    calificacion_id: int,
    usuario,
) -> tuple[CalificacionModel | None, str | None]:

    calificacion = db.query(CalificacionModel).filter(
        CalificacionModel.id == calificacion_id
    ).first()

    if calificacion is None:
        return None, "calificacion"

    if usuario["rol"] == Rol.MAESTRO:
        if usuario["id"] != calificacion.materia.maestro_id:
            return None, "permiso"

    if usuario["rol"] == Rol.ALUMNO:
        if usuario["alumno_id"] != calificacion.alumno_id:
            return None, "permiso"

    return calificacion, None


# ============================================================
# HELPERS — ALUMNO
# ============================================================

def _buscar_alumno_o_error(
    db: Session,
    alumno_id: int,
) -> tuple[AlumnoModel | None, str | None]:
    """Devuelve el alumno o un código de error si no existe."""

    alumno = db.query(AlumnoModel).filter(
        AlumnoModel.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno_calificacion"

    return alumno, None


def _consulta_calificaciones_alumno(
    db: Session,
    columnas,
    alumno_id: int,
):
    consulta = db.query(*columnas).filter(
        CalificacionModel.alumno_id == alumno_id
    )

    return consulta


def _to_calificacion_alumno(
    calificacion: CalificacionModel,
    materia_nombre: str,
) -> CalificacionAlumno:

    return CalificacionAlumno(
        materia=materia_nombre,
        nota=calificacion.nota,
        periodo=calificacion.periodo,
    )


# ============================================================
# CONSULTAS DE ALUMNO
# ============================================================

def obtener_calificaciones_alumno(
    db: Session,
    alumno_id: int,
    usuario: dict,
    periodo: int | None = None,
) -> tuple[list[CalificacionAlumno] | None, str | None]:

    alumno = db.query(AlumnoModel).filter(
        AlumnoModel.id == alumno_id
    ).first()

    if alumno is None:
        return None, "alumno_calificacion"

    if usuario["rol"] == Rol.ALUMNO:
        if usuario["alumno_id"] != alumno_id:
            return None, "permiso"

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

        if usuario["rol"] == Rol.MAESTRO:
            if calificacion.materia.maestro_id != usuario["id"]:
                continue

        resultado.append(
            _to_calificacion_alumno(
                calificacion,
                calificacion.materia.nombre,
            )
        )

    return resultado, None


def obtener_promedio_alumno(
    db: Session,
    alumno_id: int,
    usuario: dict,
) -> tuple[PromedioAlumno | None, str | None]:

    alumno, error = _buscar_alumno_o_error(
        db,
        alumno_id,
    )

    if error is not None:
        return None, error

    consulta = _consulta_calificaciones_alumno(
        db,
        [func.avg(CalificacionModel.nota)],
        alumno_id,
    )

    if usuario["rol"] == Rol.ALUMNO:
        consulta = consulta.join(
            InscripcionModel,
            InscripcionModel.materia_id == CalificacionModel.materia_id,
        ).filter(
            InscripcionModel.alumno_id == alumno_id
        )

    promedio = consulta.scalar()

    if promedio is None:
        return None, "calificaciones"

    promedio = round(promedio, 2)

    resultado = PromedioAlumno(
        alumno=f"{alumno.nombre} {alumno.apellido}",
        promedio=promedio,
    )

    return resultado, None


def obtener_estadisticas_alumno(
    db: Session,
    alumno_id: int,
    usuario: dict,
) -> tuple[list[EstadisticasAlumno] | None, str | None]:

    alumno, error = _buscar_alumno_o_error(
        db,
        alumno_id,
    )

    if error is not None:
        return None, error

    if usuario["rol"] == Rol.ALUMNO:
        if usuario["alumno_id"] != alumno_id:
            return None, "permiso"

    consulta = db.query(
        CalificacionModel.materia_id,
        MateriaModel.nombre,
        func.max(
            case(
                (
                    CalificacionModel.periodo == 1,
                    CalificacionModel.nota,
                )
            )
        ),
        func.max(
            case(
                (
                    CalificacionModel.periodo == 2,
                    CalificacionModel.nota,
                )
            )
        ),
        func.max(
            case(
                (
                    CalificacionModel.periodo == 3,
                    CalificacionModel.nota,
                )
            )
        ),
        func.avg(CalificacionModel.nota),
    ).filter(
        CalificacionModel.alumno_id == alumno_id
    ).join(
        MateriaModel,
        CalificacionModel.materia_id == MateriaModel.id,
    ).group_by(
        CalificacionModel.materia_id,
        MateriaModel.nombre,
    )

    if usuario["rol"] == Rol.MAESTRO:
        consulta = consulta.filter(
            MateriaModel.maestro_id == usuario["id"]
        )

    resultados = consulta.all()

    if not resultados:
        return None, "calificaciones"

    resultado = []

    for fila in resultados:
        estadistica = EstadisticasAlumno(
            alumno=f"{alumno.nombre} {alumno.apellido}",
            materia=fila[1],
            periodo_1=fila[2],
            periodo_2=fila[3],
            periodo_3=fila[4],
            promedio=round(fila[5], 2) if fila[5] is not None else None,
        )

        resultado.append(estadistica)

    return resultado, None


# ============================================================
# CONSULTAS DE MAESTRO
# ============================================================

def obtener_calificaciones_maestro(
    db: Session,
    maestro_id: int,
) -> list[CalificacionAlumno]:

    calificaciones = (
        db.query(CalificacionModel)
        .join(
            MateriaModel,
            CalificacionModel.materia_id == MateriaModel.id,
        )
        .options(
            joinedload(CalificacionModel.materia)
        )
        .filter(
            MateriaModel.maestro_id == maestro_id
        )
        .all()
    )

    resultado = []

    for calificacion in calificaciones:
        resultado.append(
            _to_calificacion_alumno(
                calificacion,
                calificacion.materia.nombre,
            )
        )

    return resultado


# ============================================================
# MODIFICACIÓN
# ============================================================

def actualizar_calificacion(
    db: Session,
    calificacion_id: int,
    datos: CalificacionActualizar,
    usuario,
) -> tuple[CalificacionModel | None, str | None]:

    cambios = datos.model_dump(exclude_unset=True)

    calificacion = db.query(CalificacionModel).filter(
        CalificacionModel.id == calificacion_id
    ).first()

    if calificacion is None:
        return None, "calificacion"

    if "alumno_id" in cambios:
        if usuario["rol"] == Rol.MAESTRO:
            return None, "maestro"

        alumno = db.query(AlumnoModel).filter(
            AlumnoModel.id == cambios["alumno_id"]
        ).first()

        if alumno is None:
            return None, "alumno_calificacion"

    if "materia_id" in cambios:
        if usuario["rol"] == Rol.MAESTRO:
            return None, "maestro"
        materia = db.query(MateriaModel).filter(
            MateriaModel.id == cambios["materia_id"]
        ).first()

        if materia is None:
            return None, "materia_calificacion"

        materia_autorizacion = materia

    else:
        materia_autorizacion = calificacion.materia

    if usuario["rol"] == Rol.MAESTRO:
        if usuario["id"] != materia_autorizacion.maestro_id:
            return None, "maestro"

    if "alumno_id" in cambios or "materia_id" in cambios:
        alumno_id = cambios.get("alumno_id", calificacion.alumno_id)
        materia_id = cambios.get("materia_id", calificacion.materia_id)

        inscripcion = db.query(InscripcionModel).filter(
            InscripcionModel.alumno_id == alumno_id,
            InscripcionModel.materia_id == materia_id,
        ).first()

        if inscripcion is None:
            return None, "inscripcion_calificacion"

    for campo, valor in cambios.items():
        setattr(calificacion, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None, "conflicto"

    db.refresh(calificacion)

    return calificacion, None


# ============================================================
# ELIMINACIÓN
# ============================================================

def eliminar_calificacion(
    db: Session,
    calificacion_id: int,
    usuario,
) -> tuple[CalificacionModel | None, str | None]:

    calificacion = db.query(CalificacionModel).filter(
        CalificacionModel.id == calificacion_id
    ).first()

    if calificacion is None:
        return None, "calificacion"

    if usuario["rol"] == Rol.MAESTRO:
        if usuario["id"] != calificacion.materia.maestro_id:
            return None, "maestro"

    try:
        db.delete(calificacion)
        db.commit()
    except IntegrityError:
        db.rollback()
        return None, "conflicto"

    return calificacion, None
