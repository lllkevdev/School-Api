from core.dependencies import get_usuario_actual
from core.config import SECRET_KEY
from core.security import create_access_token

from models.usuario import Usuario 
from schemas.roles import Rol
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import pytest
import jwt

def test_get_usuario_actual_devuelve_usuario(db):
    usuario = Usuario(
        nombre="Usuario Test",
        email="usuario@test.com",
        password_hash="hash",
        rol=Rol.ADMIN,
        activo=True,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    token = create_access_token(
        user_id=usuario.id,
        secret_key=SECRET_KEY,
        expires_minutes=30,
    )

    resultado = get_usuario_actual(
        token=token,
        db=db,
    )

    assert isinstance(resultado, Usuario)
    assert resultado.id == usuario.id
    assert resultado.email == "usuario@test.com"


def test_get_usuario_actual_usuario_inexistente(db):
    token = create_access_token(
        user_id=999999,
        secret_key=SECRET_KEY,
        expires_minutes=30,
    )

    with pytest.raises(HTTPException) as error:
        get_usuario_actual(
            token=token,
            db=db,
        )

    assert error.value.status_code == 401
    assert error.value.detail == "No autenticado"


def test_get_usuario_actual_usuario_inactivo(db):
    usuario = Usuario(
        nombre="Usuario Inactivo",
        email="inactivo@test.com",
        password_hash="hash",
        rol=Rol.ADMIN,
        activo=False,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    token = create_access_token(
        user_id=usuario.id,
        secret_key=SECRET_KEY,
        expires_minutes=30,
    )

    with pytest.raises(HTTPException) as error:
        get_usuario_actual(
            token=token,
            db=db,
        )

    assert error.value.status_code == 401
    assert error.value.detail == "No autenticado"


def test_get_usuario_actual_token_invalido(db):
    token = "token-invalido"

    with pytest.raises(HTTPException) as error:
        get_usuario_actual(
            token=token,
            db=db,
        )

    assert error.value.status_code == 401
    assert error.value.detail == "No autenticado"


def test_get_usuario_actual_token_expirado(db):
    usuario = Usuario(
        nombre="Usuario Expirado",
        email="expirado@test.com",
        password_hash="hash",
        rol=Rol.ADMIN,
        activo=True,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    payload = {
        "sub": str(usuario.id),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as error:
        get_usuario_actual(
            token=token,
            db=db,
        )

    assert error.value.status_code == 401
    assert error.value.detail == "No autenticado"


def test_get_usuario_actual_token_sin_sub(db):
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as error:
        get_usuario_actual(
            token=token,
            db=db,
        )

    assert error.value.status_code == 401
    assert error.value.detail == "No autenticado"


def test_get_usuario_actual_token_sub_invalido(db):
    payload = {
        "sub": "abc",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as error:
        get_usuario_actual(
            token=token,
            db=db,
        )

    assert error.value.status_code == 401
    assert error.value.detail == "No autenticado"