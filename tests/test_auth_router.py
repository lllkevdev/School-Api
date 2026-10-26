from datetime import date

from core.security import hash_password
from models.alumno import Alumno
from models.usuario import Usuario
from schemas.roles import Rol


def test_perfil_actual_admin(client, auth_headers_admin):
    respuesta = client.get("/auth/me", headers=auth_headers_admin)

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["rol"] == "admin"
    assert datos["email"] == "admin@test.com"
    assert datos["alumno_id"] is None
    assert datos["foto_perfil"] is None


def test_perfil_actual_alumno(client, db):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        documento_identidad="87654321",
        fecha_nacimiento=date(2005, 1, 1),
    )
    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    usuario = Usuario(
        nombre="Juan",
        email="juan.perfil@test.com",
        password_hash=hash_password("12345678"),
        rol=Rol.ALUMNO,
        alumno_id=alumno.id,
        activo=True,
    )
    db.add(usuario)
    db.commit()

    login = client.post(
        "/auth/login",
        json={
            "email": "juan.perfil@test.com",
            "password": "12345678",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    respuesta = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["rol"] == "alumno"
    assert datos["email"] == "juan.perfil@test.com"
    assert datos["alumno_id"] == alumno.id


def test_perfil_actual_sin_token(client):
    respuesta = client.get("/auth/me")

    assert respuesta.status_code == 401


def test_registro_admin_exitoso(client):
    respuesta = client.post(
        "/auth/registro",
        json={
            "nombre": "  Nueva  ",
            "apellido": "  Admin  ",
            "email": "  NUEVA.ADMIN@TEST.COM  ",
            "password": "password123",
            "rol": "alumno",
        },
    )

    assert respuesta.status_code == 201

    token = respuesta.json()["access_token"]

    perfil = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert perfil.status_code == 200

    datos = perfil.json()

    assert datos["nombre"] == "Nueva"
    assert datos["apellido"] == "Admin"
    assert datos["email"] == "nueva.admin@test.com"
    assert datos["rol"] == "admin"
    assert datos["alumno_id"] is None


def test_registro_email_duplicado(client):
    datos = {
        "nombre": "Admin",
        "email": "duplicado@test.com",
        "password": "password123",
    }

    primera = client.post("/auth/registro", json=datos)

    assert primera.status_code == 201

    segunda = client.post("/auth/registro", json=datos)

    assert segunda.status_code == 409
    assert segunda.json()["detail"] == "Ya existe una cuenta con ese correo"


def test_registro_datos_invalidos(client):
    respuesta = client.post(
        "/auth/registro",
        json={
            "nombre": "A",
            "email": "email-invalido",
            "password": "corta",
        },
    )

    assert respuesta.status_code == 422
