from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db
from core.permisos import requiere_permiso
from core.errores import error_to_http
from schemas.auth import TokenResponse
from schemas.permisos import Permiso
from schemas.invitacion import (
    InvitacionAceptar,
    InvitacionCreadaRespuesta,
    InvitacionCrear,
    InvitacionRespuesta,
)
from models.usuario import Usuario
from services.auth_service import crear_token_usuario
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
    response_model=InvitacionCreadaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    datos: InvitacionCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.CREAR_INVITACION)
    ),
):
    invitacion, error, token = crear_invitacion(db, datos, usuario)
    error_to_http(error)

    respuesta = InvitacionRespuesta.model_validate(invitacion)
    return InvitacionCreadaRespuesta(
        **respuesta.model_dump(),
        token=token,
    )


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
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def aceptar(
    datos: InvitacionAceptar,
    db: Session = Depends(get_db),
):
    usuario, error = aceptar_invitacion(db, datos)
    error_to_http(error)

    try:
        return crear_token_usuario(usuario)
    except ValueError as error:
        error_to_http(str(error))
