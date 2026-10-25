from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from services.usuario_service import (
    buscar_usuario_por_email,
    crear_usuario,
)
from schemas.auth import LoginRequest, TokenResponse
from schemas.usuario import UsuarioRegistro
from core.security import verify_password, create_access_token
from core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from models.usuario import Usuario


def crear_token_usuario(usuario: Usuario) -> TokenResponse:
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY no configurada")

    access_token = create_access_token(
        user_id=usuario.id,
        secret_key=SECRET_KEY,
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


def autenticar_usuario(
    db: Session,
    login: LoginRequest,
) -> TokenResponse:

    usuario = buscar_usuario_por_email(
        db,
        login.email,
    )

    if usuario is None:
        raise ValueError("credenciales")

    if not verify_password(
        login.password,
        usuario.password_hash,
    ):
        raise ValueError("credenciales")

    if not usuario.activo:
        raise ValueError("credenciales")

    return crear_token_usuario(usuario)


def registrar_usuario(
    db: Session,
    datos: UsuarioRegistro,
) -> tuple[Usuario | None, str | None]:
    if buscar_usuario_por_email(db, str(datos.email)) is not None:
        return None, "email_duplicado"

    try:
        usuario = crear_usuario(db, datos)
    except IntegrityError:
        return None, "email_duplicado"

    return usuario, None