from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db
from core.dependencies import get_alumno_actual
from core.permisos import requiere_permiso
from core.errores import error_to_http
from schemas.permisos import Permiso
from schemas.evaluacion import (
    EvaluacionCrear,
    EvaluacionActualizar,
    EvaluacionAlumnoRespuesta,
    EvaluacionRespuesta,
)
from models.usuario import Usuario
from models.alumno import Alumno
from services.evaluacion_service import (
    crear_evaluacion,
    listar_evaluaciones_alumno,
    listar_evaluaciones_por_curso,
    obtener_evaluacion,
    actualizar_evaluacion,
    eliminar_evaluacion,
)


router = APIRouter(
    prefix="/evaluaciones",
    tags=["Evaluaciones"],
)


@router.post(
    "/",
    response_model=EvaluacionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    datos: EvaluacionCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.CREAR_EVALUACION)
    ),
):
    evaluacion, error = crear_evaluacion(db, datos, usuario)
    error_to_http(error)

    return evaluacion


@router.get(
    "/curso/{curso_id}",
    response_model=list[EvaluacionRespuesta],
)
def listar_por_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_EVALUACIONES)
    ),
):
    evaluaciones, error = listar_evaluaciones_por_curso(db, curso_id, usuario)
    error_to_http(error)
    return evaluaciones


@router.get(
    "/mis-evaluaciones",
    response_model=list[EvaluacionAlumnoRespuesta],
)
def mis_evaluaciones(
    db: Session = Depends(get_db),
    alumno: Alumno = Depends(get_alumno_actual),
):
    return listar_evaluaciones_alumno(db, alumno.id)


@router.get(
    "/{evaluacion_id}",
    response_model=EvaluacionRespuesta,
)
def obtener(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_EVALUACIONES)
    ),
):
    evaluacion, error = obtener_evaluacion(db, evaluacion_id, usuario)
    error_to_http(error)
    return evaluacion


@router.patch(
    "/{evaluacion_id}",
    response_model=EvaluacionRespuesta,
)
def actualizar(
    evaluacion_id: int,
    datos: EvaluacionActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_EVALUACION)
    ),
):
    evaluacion, error = actualizar_evaluacion(db, evaluacion_id, datos, usuario)
    error_to_http(error)
    return evaluacion


@router.put(
    "/{evaluacion_id}",
    response_model=EvaluacionRespuesta,
)
def actualizar_put(
    evaluacion_id: int,
    datos: EvaluacionActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_EVALUACION)
    ),
):
    evaluacion, error = actualizar_evaluacion(db, evaluacion_id, datos, usuario)
    error_to_http(error)
    return evaluacion


@router.delete(
    "/{evaluacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.ELIMINAR_EVALUACION)
    ),
):
    ok, error = eliminar_evaluacion(db, evaluacion_id, usuario)
    error_to_http(error)
    return None