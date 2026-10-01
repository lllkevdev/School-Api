from fastapi import APIRouter, Depends, Path, Query, status
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
    obtener_promedio_alumno,
    obtener_estadisticas_alumno,
    obtener_calificaciones_maestro,
)

from core.permisos import (
    Permiso,
    requiere_permiso,
    requiere_permiso_calificaciones,
)

from core.dependencies import get_usuario_actual
from core.errores import error_to_http


router = APIRouter(
    prefix="/calificaciones",
    tags=["Calificaciones"]
)


# ============================================================
# ADMIN
# ============================================================

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


# ============================================================
# CONSULTAS COMPARTIDAS
# ADMIN → VER_CALIFICACION
# MAESTRO → VER_CALIFICACIONES_MAESTRO
# ALUMNO → VER_MIS_CALIFICACIONES
# ============================================================

@router.get(
    "/{calificacion_id}",
    response_model=CalificacionRespuesta
)
def obtener_por_id(
    calificacion_id: int,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso_calificaciones),
    usuario: dict = Depends(get_usuario_actual)
):
    calificacion, error = buscar_calificaciones(
        db,
        calificacion_id,
        usuario
    )

    error_to_http(error)

    return calificacion


# ============================================================
# ALUMNO
# ============================================================



@router.get(
    "/alumno/mis-calificaciones",
    response_model=list[CalificacionAlumno]
)
def obtener_mis_calificaciones(
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_MIS_CALIFICACIONES)),
    usuario: dict = Depends(get_usuario_actual)
):
    calificaciones, error = obtener_calificaciones_alumno(
        db,
        usuario["alumno_id"],
        usuario
    )

    error_to_http(error)

    return calificaciones


@router.get(
    "/alumno/mi-promedio",
    response_model=PromedioAlumno
)
def obtener_mi_promedio(
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_MIS_CALIFICACIONES)),
    usuario: dict = Depends(get_usuario_actual)
):
    resultado, error = obtener_promedio_alumno(
        db,
        usuario["alumno_id"],
        usuario
    )

    error_to_http(error)

    return resultado


@router.get(
    "/alumno/mi-estadisticas",
    response_model=list[EstadisticasAlumno]
)
def obtener_mis_estadisticas(
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_MIS_CALIFICACIONES)),
    usuario: dict = Depends(get_usuario_actual)
):
    resultado, error = obtener_estadisticas_alumno(
        db,
        usuario["alumno_id"],
        usuario
    )

    error_to_http(error)

    return resultado



# ============================================================
# MAESTRO
# ============================================================



@router.get(
    "/maestro/mis-calificaciones",
    response_model=list[CalificacionAlumno]
)
def obtener_mis_calificaciones_maestro(
    db: Session = Depends(get_db),
    _ = Depends(
        requiere_permiso(Permiso.VER_CALIFICACIONES_MAESTRO)
    ),
    usuario: dict = Depends(get_usuario_actual)
):
    calificaciones = obtener_calificaciones_maestro(
        db,
        usuario["id"]
    )

    return calificaciones



# =====================================================================

@router.get(
    "/alumno/{alumno_id}",
    response_model=list[CalificacionAlumno]
)
def obtener_calificaciones_alumnos(
    alumno_id: int = Path(gt=0),
    periodo: int | None = Query(
        default=None,
        ge=1,
        le=3
    ),
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso_calificaciones),
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
    "/alumno/{alumno_id}/estadisticas",
    response_model=list[EstadisticasAlumno]
)
def obtener_estadisticas(
    alumno_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso_calificaciones),
    usuario: dict = Depends(get_usuario_actual)
):
    resultado, error = obtener_estadisticas_alumno(
        db,
        alumno_id,
        usuario
    )

    error_to_http(error)

    return resultado


# ============================================================
# GESTIÓN DE CALIFICACIONES
# ============================================================


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


@router.patch(
    "/{calificacion_id}",
    response_model=CalificacionRespuesta
)
def actualizar(
    calificacion_id: int,
    datos: CalificacionActualizar,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.MODIFICAR_CALIFICACION)),
    usuario: dict = Depends(get_usuario_actual)
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
    usuario: dict = Depends(get_usuario_actual)
):
    calificacion, error = eliminar_calificacion(
        db,
        calificacion_id,
        usuario
    )

    error_to_http(error)

    return