from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from database.dependencies import get_db
from core.permisos import requiere_permiso
from core.errores import error_to_http
from core.dependencies import get_alumno_actual
from schemas.permisos import Permiso
from schemas.calificacion import (
    CalificacionCrear,
    CalificacionActualizar,
    CalificacionRespuesta,
)
from models.usuario import Usuario
from models.alumno import Alumno
from services.calificacion_service import (
    crear_calificacion,
    actualizar_calificacion,
    listar_calificaciones,
    eliminar_calificacion,
    listar_calificaciones_alumno,
    obtener_promedio_alumno,
    obtener_historial_alumno,
    obtener_promedio_por_curso,
    generar_csv_calificaciones,
)


router = APIRouter(
    prefix="/calificaciones",
    tags=["Calificaciones"],
)


@router.get(
    "/mis-calificaciones",
    response_model=list[CalificacionRespuesta],
)
def mis_calificaciones(
    db: Session = Depends(get_db),
    alumno: Alumno = Depends(get_alumno_actual),
):
    return listar_calificaciones_alumno(db, alumno.id)


@router.get(
    "/mi-promedio",
)
def mi_promedio(
    db: Session = Depends(get_db),
    alumno: Alumno = Depends(get_alumno_actual),
):
    promedio, error = obtener_promedio_alumno(db, alumno.id)
    error_to_http(error)
    return {"promedio": promedio}


@router.get(
    "/mi-historial",
    response_model=list[CalificacionRespuesta],
)
def mi_historial(
    db: Session = Depends(get_db),
    alumno: Alumno = Depends(get_alumno_actual),
):
    return obtener_historial_alumno(db, alumno.id)


@router.get(
    "/curso/{curso_id}/promedio",
)
def promedio_por_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_CALIFICACIONES)
    ),
):
    promedio, error = obtener_promedio_por_curso(db, curso_id, usuario)
    error_to_http(error)
    return {"promedio": promedio}


@router.get(
    "/curso/{curso_id}/export",
)
def exportar_calificaciones(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_CALIFICACIONES)
    ),
):
    csv_data, error = generar_csv_calificaciones(db, curso_id, usuario)
    error_to_http(error)
    buffer = io.StringIO(csv_data)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=calificaciones_curso_{curso_id}.csv"
        },
    )


@router.post(
    "/",
    response_model=CalificacionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    datos: CalificacionCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.CREAR_CALIFICACION)
    ),
):
    calificacion, error = crear_calificacion(db, datos, usuario)
    error_to_http(error)

    return calificacion


@router.get(
    "/curso/{curso_id}",
    response_model=list[CalificacionRespuesta],
)
def listar_por_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_CALIFICACIONES)
    ),
):
    calificaciones, error = listar_calificaciones(db, curso_id, usuario)
    error_to_http(error)

    return calificaciones


@router.patch(
    "/{calificacion_id}",
    response_model=CalificacionRespuesta,
)
def actualizar(
    calificacion_id: int,
    datos: CalificacionActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_CALIFICACION)
    ),
):
    calificacion, error = actualizar_calificacion(
        db,
        calificacion_id,
        datos,
        usuario,
    )
    error_to_http(error)

    return calificacion


@router.delete(
    "/{calificacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    calificacion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.ELIMINAR_CALIFICACION)
    ),
):
    eliminado, error = eliminar_calificacion(db, calificacion_id, usuario)
    error_to_http(error)

    return None