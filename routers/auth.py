from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.dependencies import get_db
from schemas.auth import LoginRequest, TokenResponse
from services.auth_service import autenticar_usuario
from core.errores import error_to_http


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


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