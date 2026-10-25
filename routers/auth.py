from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db
from schemas.auth import LoginRequest, TokenResponse
from schemas.usuario import UsuarioRegistro, UsuarioRespuesta
from services.auth_service import (
    autenticar_usuario,
    crear_token_usuario,
    registrar_usuario,
)
from core.dependencies import get_usuario_actual
from core.errores import error_to_http
from models.usuario import Usuario


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.get("/me", response_model=UsuarioRespuesta)
def perfil_actual(
    usuario: Usuario = Depends(get_usuario_actual),
):
    return usuario


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return autenticar_usuario(
            db,
            login_data,
        )
    except ValueError as error:
        error_to_http(str(error))


@router.post(
    "/registro",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def registro(
    datos: UsuarioRegistro,
    db: Session = Depends(get_db),
):
    usuario, error = registrar_usuario(db, datos)
    error_to_http(error)

    try:
        return crear_token_usuario(usuario)
    except ValueError as error:
        error_to_http(str(error))