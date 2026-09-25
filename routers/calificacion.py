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

from core.permisos import Permiso, requiere_permiso
from core.dependencies import get_usuario_actual



router = APIRouter(
    prefix="/calificaciones",
    tags=["Calificaciones"]
)

from core.errores import error_to_http

@router.post(
    "/",
    response_model=CalificacionRespuesta,
    status_code=status.HTTP_201_CREATED
)
def crear(
    calificacion: Calificacion,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.CREAR_CALIFICACION)),
    usuario: dict = Depends(get_usuario_actual)
):
    resultado, error = crear_calificacion(
        db,
        calificacion,
        usuario
    )

    error_to_http(error)

    return resultado





@router.get(
    "/",
    response_model=list[CalificacionRespuesta]
)
def obtener(
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_TODAS_CALIFICACIONES))
):
    return obtener_calificaciones(db)




@router.get(
    "/detalle",
    response_model=list[CalificacionDetalle]
)
def obtener_detalle(
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_TODAS_CALIFICACIONES))
):
    return obtener_calificaciones_detalle(db)




@router.get(
    "/alumno/{alumno_id}",
    response_model=list[CalificacionAlumno]
)
def obtener_por_alumno(
    alumno_id: int = Path(gt=0),
    periodo: int | None = Query(default=None, ge=1, le=3),
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_CALIFICACION)),
    usuario: dict = Depends(get_usuario_actual)
):
    calificaciones, error = obtener_calificaciones_alumno(
        db,
        alumno_id,
        usuario,
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
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_CALIFICACION))
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
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_CALIFICACION))
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
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_CALIFICACION))
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
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_CALIFICACION)),
    usuario = Depends(get_usuario_actual)
):
    calificacion, error = buscar_calificaciones(
        db,
        calificacion_id,
        usuario
    )

    error_to_http(error)

    return calificacion



@router.patch(
    "/{calificacion_id}",
    response_model=CalificacionRespuesta
)
def actualizar(
    calificacion_id: int,
    datos: CalificacionActualizar,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.MODIFICAR_CALIFICACION)),
    usuario = Depends(get_usuario_actual)
):
    calificacion, error = actualizar_calificacion(
        db,
        calificacion_id,
        datos,
        usuario
    )

    error_to_http(error)

    return calificacion




@router.delete(
    "/{calificacion_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar(
    calificacion_id: int,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.ELIMINAR_CALIFICACION)),
    usuario = Depends(get_usuario_actual)
):
    calificacion, error = eliminar_calificacion(
        db,
        calificacion_id,
        usuario
    )

    error_to_http(error)

    return 


