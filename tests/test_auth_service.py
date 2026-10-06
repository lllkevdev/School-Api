import pytest

from services.auth_service import autenticar_usuario
from services.usuario_service import crear_usuario
from schemas.auth import LoginRequest
from schemas.usuario import UsuarioCrear


def test_autenticar_usuario_correctamente(db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="alumno",
    )

    usuario = crear_usuario(db, usuario_data)

    login = LoginRequest(
        email="juan@test.com",
        password="12345678",
    )

    resultado = autenticar_usuario(
        db,
        login,
    )

    assert resultado.access_token
    assert resultado.token_type == "bearer"


def test_autenticar_usuario_inexistente(db):
    login = LoginRequest(
        email="noexiste@test.com",
        password="12345678",
    )

    with pytest.raises(ValueError, match="credenciales"):
        autenticar_usuario(
            db,
            login,
        )


def test_autenticar_usuario_password_incorrecta(db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="alumno",
    )

    crear_usuario(db, usuario_data)

    login = LoginRequest(
        email="juan@test.com",
        password="password-incorrecta",
    )

    with pytest.raises(ValueError, match="credenciales"):
        autenticar_usuario(
            db,
            login,
        )


def test_autenticar_usuario_inactivo(db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="alumno",
    )

    usuario = crear_usuario(db, usuario_data)

    usuario.activo = False
    db.commit()

    login = LoginRequest(
        email="juan@test.com",
        password="12345678",
    )

    with pytest.raises(ValueError, match="credenciales"):
        autenticar_usuario(
            db,
            login,
        )