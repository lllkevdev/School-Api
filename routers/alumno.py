from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db

from schemas.alumno import ( 
    Alumno, 
    AlumnoRespuesta,
    AlumnoActualizar,
)
from services.alumno_service import (
    crear_alumno,
    obtener_alumnos,
    buscar_alumno,
    actualizar_alumno,
    reemplazar_alumno,
    eliminar_alumno,
)
from core.permisos import requiere_permiso
from core.permisos import get_usuario_actual

from schemas.permisos import Permiso

from core.errores import error_to_http


router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"]
)


@router.post(
    "/",
    response_model=AlumnoRespuesta,
    status_code=status.HTTP_201_CREATED
)
def crear(alumno: Alumno,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.CREAR_ALUMNO))
):
    return crear_alumno(db, alumno)


@router.get("/", response_model=list[AlumnoRespuesta])
def obtener(
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_ALUMNOS))
):
    return obtener_alumnos(db)


@router.get(
    "/{alumno_id}",
    response_model=AlumnoRespuesta
)
def obtener_por_id(
    alumno_id: int, 
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_actual)
):
    alumno, error = buscar_alumno(
        db, 
        alumno_id,
        usuario
    )

    error_to_http(error)

    return alumno


@router.patch(
    "/{alumno_id}",
    response_model=AlumnoRespuesta
)
def actualizar(
    alumno_id: int,
    datos: AlumnoActualizar,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.MODIFICAR_ALUMNO))
):
    alumno, error = actualizar_alumno(
        db, 
        alumno_id, 
        datos
    )
    error_to_http(error)

    return alumno


@router.put(
    "/{alumno_id}",
    response_model=AlumnoRespuesta
)
def actualizar_alumno_put(
    alumno_id: int,
    datos: Alumno,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.MODIFICAR_ALUMNO))
):
    alumno, error = reemplazar_alumno(
        db, 
        alumno_id, 
        datos
    )
    error_to_http(error)

    return alumno


@router.delete(
    "/{alumno_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    alumno_id: int, 
    forzar: bool = False,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.ELIMINAR_ALUMNO))
):
    alumno, error = eliminar_alumno(
        db,
        alumno_id,
        forzar
    )
    error_to_http(error)
    
    return