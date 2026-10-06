from core.security import hash_password
from models.materia import Materia
from models.usuario import Usuario
from models.alumno import Alumno
from schemas.roles import Rol
from core.permisos import requiere_permiso_calificaciones

def test_login_y_acceso_endpoint_protegido(db, client):
    usuario = Usuario(
        nombre="Admin Test",
        email="admin@test.com",
        password_hash=hash_password("password123"),
        rol=Rol.ADMIN,
        activo=True,
    )

    materia = Materia(
        nombre="Matemática",
    )

    db.add(usuario)
    db.add(materia)
    db.commit()
    db.refresh(usuario)
    db.refresh(materia)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "admin@test.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        f"/materias/{materia.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200


def test_usuario_autenticado_sin_permiso_recibe_403(db, client):
    usuario = Usuario(
        nombre="Alumno Test",
        email="alumno@test.com",
        password_hash=hash_password("password123"),
        rol=Rol.ALUMNO,
        activo=True,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "alumno@test.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/calificaciones/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "No tiene permiso para realizar esta acción"
    )


def test_admin_autenticado_puede_acceder_calificaciones(db, client):
    usuario = Usuario(
        nombre="Admin Calificaciones",
        email="admin-calificaciones@test.com",
        password_hash=hash_password("password123"),
        rol=Rol.ADMIN,
        activo=True,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "admin-calificaciones@test.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/calificaciones/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200


def test_requiere_permiso_calificaciones_acepta_usuario(db):
    usuario = Usuario(
        nombre="Admin Permisos",
        email="admin-permisos@test.com",
        password_hash=hash_password("password123"),
        rol=Rol.ADMIN,
        activo=True,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    resultado = requiere_permiso_calificaciones(
        usuario=usuario
    )

    assert resultado is True


def test_alumno_autenticado_puede_acceder_a_mis_calificaciones(
    db,
    client,
):
    alumno = Alumno(
        nombre="Alumno",
        apellido="Test",
        edad=20,
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    usuario = Usuario(
        nombre="Usuario Alumno",
        email="alumno-auth@test.com",
        password_hash=hash_password("password123"),
        rol=Rol.ALUMNO,
        activo=True,
        alumno_id=alumno.id,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    response_login = client.post(
        "/auth/login",
        json={
            "email": "alumno-auth@test.com",
            "password": "password123",
        },
    )

    assert response_login.status_code == 200

    token = response_login.json()["access_token"]

    response = client.get(
        "/calificaciones/alumno/mis-calificaciones",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json() == []