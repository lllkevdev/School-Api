from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db
from core.permisos import requiere_permiso
from core.errores import error_to_http
from schemas.permisos import Permiso
from schemas.invitacion import InvitacionCrear, InvitacionRespuesta, InvitacionAceptar
from models.usuario import Usuario
from services.invitacion_service import (
    crear_invitacion,
    listar_invitaciones,
    revocar_invitacion,
    aceptar_invitacion,
)


router = APIRouter(
    prefix="/invitaciones",
    tags=["Invitaciones"],
)


@router.post(
    "/",
    response_model=InvitacionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    datos: InvitacionCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.CREAR_INVITACION)
    ),
):
    invitacion, error, _ = crear_invitacion(db, datos, usuario)
    error_to_http(error)
    return invitacion


@router.get(
    "/",
    response_model=list[InvitacionRespuesta],
)
def listar(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_INVITACIONES)
    ),
):
    return listar_invitaciones(db, usuario)


@router.post(
    "/{invitacion_id}/revocar",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revocar(
    invitacion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.REVOCAR_INVITACION)
    ),
):
    ok, error = revocar_invitacion(db, invitacion_id, usuario)
    error_to_http(error)
    return None


@router.post(
    "/aceptar",
    status_code=status.HTTP_200_OK,
)
def aceptar(
    datos: InvitacionAceptar,
    db: Session = Depends(get_db),
):
    usuario, error = aceptar_invitacion(db, datos)
    error_to_http(error)
    return {"mensaje": "Invitación aceptada correctamente"}
