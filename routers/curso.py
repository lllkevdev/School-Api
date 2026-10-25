from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db
from core.permisos import requiere_permiso
from core.errores import error_to_http
from core.dependencies import get_alumno_actual
from schemas.permisos import Permiso
from schemas.curso import CursoCrear, CursoActualizar, CursoRespuesta
from models.usuario import Usuario
from models.alumno import Alumno
from services.curso_service import (
    crear_curso,
    listar_cursos,
    obtener_curso,
    actualizar_curso,
    eliminar_curso,
    listar_cursos_por_alumno,
)


router = APIRouter(
    prefix="/cursos",
    tags=["Cursos"],
)


@router.get(
    "/mis-cursos",
    response_model=list[CursoRespuesta],
)
def mis_cursos(
    db: Session = Depends(get_db),
    alumno: Alumno = Depends(get_alumno_actual),
):
    return listar_cursos_por_alumno(db, alumno.id)


@router.post(
    "/",
    response_model=CursoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    datos: CursoCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.CREAR_CURSO)
    ),
):
    curso, error = crear_curso(db, datos, usuario)
    error_to_http(error)

    return curso


@router.get(
    "/",
    response_model=list[CursoRespuesta],
)
def listar(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_CURSOS)
    ),
):
    return listar_cursos(db, usuario)


@router.get(
    "/{curso_id}",
    response_model=CursoRespuesta,
)
def obtener(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_CURSO)
    ),
):
    curso, error = obtener_curso(db, curso_id, usuario)
    error_to_http(error)
    return curso


@router.patch(
    "/{curso_id}",
    response_model=CursoRespuesta,
)
def actualizar(
    curso_id: int,
    datos: CursoActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_CURSO)
    ),
):
    curso, error = actualizar_curso(db, curso_id, datos, usuario)
    error_to_http(error)
    return curso


@router.put(
    "/{curso_id}",
    response_model=CursoRespuesta,
)
def actualizar_put(
    curso_id: int,
    datos: CursoActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_CURSO)
    ),
):
    curso, error = actualizar_curso(db, curso_id, datos, usuario)
    error_to_http(error)
    return curso


@router.delete(
    "/{curso_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.ELIMINAR_CURSO)
    ),
):
    ok, error = eliminar_curso(db, curso_id, usuario)
    error_to_http(error)
    return None