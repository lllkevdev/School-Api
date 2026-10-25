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
