from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.dependencies import get_usuario_actual
from core.errores import error_to_http
from core.permisos import requiere_permiso
from database.dependencies import get_db
from models.usuario import Usuario
from schemas.inscripcion import InscripcionCrear, InscripcionRespuesta
from schemas.permisos import Permiso
from services.inscripcion_service import crear_inscripcion, eliminar_inscripcion


router = APIRouter(prefix="/inscripciones", tags=["Inscripciones"])


@router.post(
    "/",
    response_model=InscripcionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    inscripcion: InscripcionCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
    _=Depends(requiere_permiso(Permiso.CREAR_INSCRIPCION)),
):
    resultado, error = crear_inscripcion(db, inscripcion, usuario)
    error_to_http(error)
    return resultado


@router.delete(
    "/{inscripcion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
    _=Depends(requiere_permiso(Permiso.ELIMINAR_INSCRIPCION)),
):
    resultado, error = eliminar_inscripcion(db, inscripcion_id, usuario)
    error_to_http(error)
    return None