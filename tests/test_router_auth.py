from services.usuario_service import crear_usuario
from schemas.usuario import UsuarioCrear


def test_login_correcto(client, db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="alumno",
    )

    crear_usuario(db, usuario_data)

    response = client.post(
        "/auth/login",
        json={
            "email": "juan@test.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_usuario_inexistente(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "noexiste@test.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


def test_login_password_incorrecta(client, db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="alumno",
    )

    crear_usuario(db, usuario_data)

    response = client.post(
        "/auth/login",
        json={
            "email": "juan@test.com",
            "password": "password-incorrecta",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


def test_login_usuario_inactivo(client, db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="alumno",
    )

    usuario = crear_usuario(db, usuario_data)

    usuario.activo = False
    db.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "juan@test.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"