from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from database.dependencies import get_db
from core.permisos import requiere_permiso
from core.errores import error_to_http
from core.dependencies import get_alumno_actual, get_usuario_actual
from schemas.permisos import Permiso
from schemas.alumno import (
    AlumnoConInscripcionCrear,
    AlumnoConInscripcionRespuesta,
    AlumnoCrear,
    AlumnoRespuesta,
)
from models.usuario import Usuario
from models.alumno import Alumno
from services.alumno_service import (
    crear_alumno,
    crear_alumno_con_inscripcion,
    obtener_alumnos,
    buscar_alumno,
    desactivar_alumno,
)


router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"],
)


@router.get(
    "/me",
    response_model=AlumnoRespuesta,
)
def obtener_mi_perfil(
    alumno: Alumno = Depends(get_alumno_actual),
):
    return alumno


@router.post(
    "/",
    response_model=AlumnoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    datos: AlumnoCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.CREAR_ALUMNO)
    ),
):
    alumno, error = crear_alumno(db, datos, usuario)
    error_to_http(error)

    return alumno


@router.post(
    "/con-inscripcion",
    response_model=AlumnoConInscripcionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_con_inscripcion(
    datos: AlumnoConInscripcionCrear,
    response: Response,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.CREAR_ALUMNO)
    ),
):
    resultado, error = crear_alumno_con_inscripcion(db, datos, usuario)
    error_to_http(error)

    if resultado.requiere_confirmacion:
        response.status_code = status.HTTP_200_OK

    return resultado


@router.get(
    "/",
    response_model=list[AlumnoRespuesta],
)
def obtener(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_ALUMNOS)
    ),
):
    return obtener_alumnos(db, usuario)


@router.get(
    "/{alumno_id}",
    response_model=AlumnoRespuesta,
)
def obtener_por_id(
    alumno_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    if usuario.alumno_id is not None and usuario.alumno_id == alumno_id:
        alumno = db.get(Alumno, alumno_id)
        if alumno is None:
            error_to_http("alumno_inexistente")
        return alumno

    if usuario.rol.value == "alumno" or (usuario.alumno_id is not None and usuario.alumno_id != alumno_id):
        error_to_http("alumno_inexistente")

    alumno, error = buscar_alumno(
        db,
        alumno_id,
        usuario,
    )
    error_to_http(error)

    return alumno


@router.patch(
    "/{alumno_id}/desactivar",
    response_model=AlumnoRespuesta,
)
def desactivar(
    alumno_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_ALUMNO)
    ),
):
    alumno, error = desactivar_alumno(
        db,
        alumno_id,
        usuario,
    )
    error_to_http(error)

    return alumno