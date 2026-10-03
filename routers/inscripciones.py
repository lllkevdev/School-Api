from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db
from schemas.inscripcion import Inscripcion
from schemas.permisos import Permiso
from services.inscripcion_service import (
    crear_inscripcion,
    eliminar_inscripcion,
)
from core.permisos import requiere_permiso
from core.errores import error_to_http


router = APIRouter(
    prefix="/inscripciones",
    tags=["Inscripciones"],
)


@router.post(
    "/",
    response_model=Inscripcion,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    inscripcion: Inscripcion,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.CREAR_INSCRIPCION)),
):
    resultado, error = crear_inscripcion(
        db,
        inscripcion,
    )

    error_to_http(error)

    return resultado


@router.delete(
    "/{inscripcion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.ELIMINAR_INSCRIPCION)),
):
    resultado, error = eliminar_inscripcion(
        db,
        inscripcion_id,
    )

    error_to_http(error)

    return None