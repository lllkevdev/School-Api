from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db
from core.permisos import requiere_permiso
from core.errores import error_to_http
from core.dependencies import get_alumno_actual
from schemas.permisos import Permiso
from schemas.inscripcion import InscripcionCrear, InscripcionRespuesta
from models.usuario import Usuario
from models.alumno import Alumno
from services.inscripcion_service import (
    crear_inscripcion,
    eliminar_inscripcion,
    listar_inscripciones_por_curso,
    listar_inscripciones_por_alumno,
)


router = APIRouter(
    prefix="/inscripciones",
    tags=["Inscripciones"],
)


@router.get(
    "/mis-inscripciones",
    response_model=list[InscripcionRespuesta],
)
def mis_inscripciones(
    db: Session = Depends(get_db),
    alumno: Alumno = Depends(get_alumno_actual),
):
    return listar_inscripciones_por_alumno(db, alumno.id)


@router.post(
    "/",
    response_model=InscripcionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    datos: InscripcionCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.CREAR_INSCRIPCION)
    ),
):
    inscripcion, error = crear_inscripcion(db, datos, usuario)
    error_to_http(error)

    return inscripcion


@router.get(
    "/curso/{curso_id}",
    response_model=list[InscripcionRespuesta],
)
def listar_por_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_INSCRIPCIONES)
    ),
):
    inscripciones, error = listar_inscripciones_por_curso(db, curso_id, usuario)
    error_to_http(error)
    return inscripciones


@router.delete(
    "/{inscripcion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.ELIMINAR_INSCRIPCION)
    ),
):
    eliminado, error = eliminar_inscripcion(db, inscripcion_id, usuario)
    error_to_http(error)

    return None
