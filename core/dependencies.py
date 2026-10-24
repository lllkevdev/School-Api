from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.dependencies import get_db
from core.security import decode_access_token
from core.config import SECRET_KEY
from core.errores import error_to_http
from models.usuario import Usuario
from models.alumno import Alumno
import jwt


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    try:
        payload = decode_access_token(
            token,
            SECRET_KEY,
        )
    except jwt.InvalidTokenError:
        error_to_http("no_autenticado")

    user_id = payload.get("sub")

    if user_id is None:
        error_to_http("no_autenticado")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        error_to_http("no_autenticado")

    usuario = db.scalar(
        select(Usuario).where(Usuario.id == user_id)
    )

    if usuario is None:
        error_to_http("no_autenticado")

    if not usuario.activo:
        error_to_http("no_autenticado")

    return usuario


def get_alumno_actual(
    usuario: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> Alumno:
    if usuario.alumno_id is None:
        error_to_http("no_autenticado")

    alumno = db.scalar(
        select(Alumno).where(Alumno.id == usuario.alumno_id)
    )

    if alumno is None:
        error_to_http("alumno_inexistente")

    if not alumno.activo:
        error_to_http("alumno_inactivo")

    return alumno