
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.errores import error_to_http
from database.dependencies import get_db
from schemas.usuario import (
    MaestroCrear,
    MaestroActualizar,
    UsuarioRespuesta
)
from services.usuario_service import (
    crear_maestro, 
    obtener_maestros,
    actualizar_maestro,
    desactivar_maestro
)
from core.permisos import requiere_permiso
from schemas.permisos import Permiso


router = APIRouter(
    prefix="/maestros",
    tags=["Maestros"],
)


@router.post(
    "/",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear(
    maestro: MaestroCrear,
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.CREAR_MAESTRO)),
):
    return crear_maestro(db, maestro)


@router.get(
    "/",
    response_model=list[UsuarioRespuesta],
)
def obtener(
    db: Session = Depends(get_db),
    _ = Depends(requiere_permiso(Permiso.VER_MAESTROS)),
):
    return obtener_maestros(db)


@router.patch("/{maestro_id}", response_model=UsuarioRespuesta)
def actualizar(
    maestro_id: int,
    datos: MaestroActualizar,
    db: Session = Depends(get_db),
    _=Depends(requiere_permiso(Permiso.MODIFICAR_MAESTRO)),
):
    maestro, error = actualizar_maestro(db, maestro_id, datos)
    error_to_http(error)
    return maestro


@router.delete("/{maestro_id}", response_model=UsuarioRespuesta)
def desactivar(
    maestro_id: int,
    db: Session = Depends(get_db),
    _=Depends(requiere_permiso(Permiso.ELIMINAR_MAESTRO)),
):
    maestro, error = desactivar_maestro(db, maestro_id)
    error_to_http(error)
    return maestro