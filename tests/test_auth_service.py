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


def test_usuario_inactivo_no_puede_iniciar_sesion(
    client,
    db,
    usuario_maestro,
):
    usuario_maestro.activo = False
    db.commit()

    respuesta = client.post(
        "/auth/login",
        json={
            "email": usuario_maestro.email,
            "password": "123456",
        },
    )

    assert respuesta.status_code == 401
    assert "access_token" not in respuesta.json()


def test_usuario_activo_puede_iniciar_sesion(
    client,
    usuario_maestro,
):
    respuesta = client.post(
        "/auth/login",
        json={
            "email": usuario_maestro.email,
            "password": "123456",
        },
    )

    assert respuesta.status_code == 200
    assert "access_token" in respuesta.json()


def test_token_existente_no_funciona_tras_desactivar_maestro(
    client,
    db,
    usuario_maestro,
    auth_headers_maestro,
):
    # El usuario ya inició sesión y tiene un JWT válido.
    usuario_maestro.activo = False
    db.commit()

    respuesta = client.get(
        "/maestros/",
        headers=auth_headers_maestro,
    )

    assert respuesta.status_code == 401