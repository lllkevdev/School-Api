from sqlalchemy.orm import Session

from services.usuario_service import buscar_usuario_por_email
from schemas.auth import LoginRequest, TokenResponse
from core.security import verify_password, create_access_token
from core.config import SECRET_KEY, ACCES_TOKEN_EXPIRE_MINUTES



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

    access_token = create_access_token(
        user_id=usuario.id,
        secret_key=SECRET_KEY,
        expires_minutes=ACCES_TOKEN_EXPIRE_MINUTES,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )