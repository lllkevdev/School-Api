from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core import config
from core.errores import error_to_http
from core.permisos import requiere_permiso
from database.dependencies import get_db
from models.usuario import Usuario
from schemas.alumno import AlumnoRespuesta
from schemas.permisos import Permiso
from schemas.perfil import PerfilActualizar, PerfilRespuesta
from schemas.usuario import UsuarioRespuesta
from services.foto_service import (
    actualizar_foto,
    eliminar_foto,
    obtener_ruta_foto,
)
from services.perfil_service import actualizar_perfil


router = APIRouter(
    prefix="/perfil",
    tags=["Perfil"],
)


def _construir_perfil(usuario: Usuario) -> PerfilRespuesta:
    return PerfilRespuesta(
        usuario=UsuarioRespuesta.model_validate(usuario),
        alumno=(
            AlumnoRespuesta.model_validate(usuario.alumno)
            if usuario.alumno is not None
            else None
        ),
    )


@router.get("/me", response_model=PerfilRespuesta)
def obtener_mi_perfil(
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_MI_PERFIL)
    ),
):
    return _construir_perfil(usuario)


@router.patch("/me", response_model=PerfilRespuesta)
def actualizar_mi_perfil(
    datos: PerfilActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_MI_PERFIL)
    ),
):
    actualizado, error = actualizar_perfil(db, usuario, datos)
    error_to_http(error)

    return _construir_perfil(actualizado)


@router.get("/me/foto", response_class=FileResponse)
def obtener_mi_foto(
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.VER_MI_PERFIL)
    ),
):
    ruta = obtener_ruta_foto(usuario)

    if ruta is None:
        error_to_http("foto_no_encontrada")

    return FileResponse(
        ruta,
        media_type="image/webp",
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post("/me/foto", response_model=PerfilRespuesta)
async def subir_mi_foto(
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_MI_PERFIL)
    ),
):
    contenido = await foto.read(config.MAX_FOTO_BYTES + 1)
    await foto.close()

    actualizado, error = actualizar_foto(db, usuario, contenido)
    error_to_http(error)

    return _construir_perfil(actualizado)


@router.delete("/me/foto", response_model=PerfilRespuesta)
def eliminar_mi_foto(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        requiere_permiso(Permiso.MODIFICAR_MI_PERFIL)
    ),
):
    actualizado, error = eliminar_foto(db, usuario)
    error_to_http(error)

    return _construir_perfil(actualizado)
