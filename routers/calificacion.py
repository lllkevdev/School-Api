from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from database.dependencies import get_db

from schemas.calificacion import (
    Calificacion,
    CalificacionRespuesta,
    CalificacionDetalle, 
    CalificacionActualizar,
    CalificacionAlumno,
    EstadisticasAlumno,
    PromedioAlumno,
)

from services.calificacion_service import (
    crear_calificacion,
    obtener_calificaciones,
    buscar_calificaciones,
    obtener_calificaciones_detalle,
    actualizar_calificacion,
    eliminar_calificacion,
    obtener_calificaciones_alumno,
    obtener_calificaciones_alumno_join,
    obtener_promedio_alumno,
    obtener_estadisticas_alumno
) 


router = APIRouter(
    prefix="/calificaciones",
    tags=["Calificaciones"]
)

ERRORES_HTTP = {
    "alumno": (404, "El alumno no existe"),
    "materia": (404, "La materia no existe"),
    "calificacion": (404, "Calificación no encontrada"),
    "calificaciones": (404, "No se encontraron calificaciones para el alumno"),
    "conflicto": (409, "Ya existe una calificación para ese alumno, materia y periodo"),
}


def error_to_http(error: str | None) -> None:
    """Convierte un código de error del service en una HTTPException."""
    if error is None:
        return
    status_code, detail = ERRORES_HTTP.get(error, (400, error))
    raise HTTPException(status_code=status_code, detail=detail)

@router.post(
    "/",
    response_model=CalificacionRespuesta,
    status_code=status.HTTP_201_CREATED
)
def crear(
    calificacion: Calificacion,
    db: Session = Depends(get_db)
):
    resultado, error = crear_calificacion(
        db,
        calificacion
    )

    error_to_http(error)

    return resultado




@router.get(
    "/",
    response_model=list[CalificacionRespuesta]
)
def obtener(db: Session = Depends(get_db)):
    return obtener_calificaciones(db)




@router.get(
    "/detalle",
    response_model=list[CalificacionDetalle]
)
def obtener_detalle(db: Session = Depends(get_db)):
    return obtener_calificaciones_detalle(db)




@router.get(
    "/alumno/{alumno_id}",
    response_model=list[CalificacionAlumno]
)
def obtener_por_alumno(
    alumno_id: int = Path(gt=0),
    periodo: int | None = Query(default=None, ge=1, le=3),
    db: Session = Depends(get_db)
):
    calificaciones, error = obtener_calificaciones_alumno(
        db,
        alumno_id,
        periodo,
    )

    error_to_http(error)

    return calificaciones


@router.get(
    "/alumno/{alumno_id}/join",
    response_model=list[CalificacionAlumno]
)
def obtener_por_alumno_join(
    alumno_id: int = Path(gt=0),
    db: Session = Depends(get_db)
):
    calificaciones, error = obtener_calificaciones_alumno_join(
        db,
        alumno_id
    )

    error_to_http(error)

    return calificaciones




@router.get(
    "/alumno/{alumno_id}/promedio",
    response_model=PromedioAlumno
)
def obtener_promedio(
    alumno_id: int = Path(gt=0),
    periodo: int | None = Query(default=None, ge=1, le=3),
    db: Session = Depends(get_db)
):
    resultado, error = obtener_promedio_alumno(
        db,
        alumno_id,
        periodo
    )

    error_to_http(error)

    return resultado


@router.get(
    "/alumno/{alumno_id}/estadisticas",
    response_model=EstadisticasAlumno
)
def obtener_estadisticas(
    alumno_id: int = Path(gt=0),
    periodo: int | None = Query(default=None, ge=1, le=3),
    db: Session = Depends(get_db)
):
    resultado, error = obtener_estadisticas_alumno(
        db,
        alumno_id,
        periodo
    )

    error_to_http(error)

    return resultado




@router.get(
    "/{calificacion_id}",
    response_model=CalificacionRespuesta
)
def obtener_por_id(
    calificacion_id: int,
    db: Session = Depends(get_db)
):
    calificacion = buscar_calificaciones(
        db,
        calificacion_id
    )

    if calificacion is None:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    return calificacion



@router.patch(
    "/{calificacion_id}",
    response_model=CalificacionRespuesta
)
def actualizar(
    calificacion_id: int,
    datos: CalificacionActualizar,
    db: Session = Depends(get_db)
):
    calificacion, error = actualizar_calificacion(
        db,
        calificacion_id,
        datos
    )

    error_to_http(error)

    return calificacion




@router.delete(
    "/{calificacion_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar(
    calificacion_id: int,
    db: Session = Depends(get_db)
):
    calificacion = eliminar_calificacion(
        db,
        calificacion_id
    )

    if calificacion is None:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    return


