from datetime import date

from models.alumno import Alumno
from models.curso import Curso


def crear_alumno_y_curso(db, usuario_admin):
    alumno = Alumno(
        nombre="Alumno",
        apellido="Invitado",
        documento_identidad="55667788",
        fecha_nacimiento=date(2005, 4, 10),
        activo=True,
    )
    curso = Curso(
        docente_id=usuario_admin.id,
        nombre_materia="Matemática",
        division="2A",
        anio_lectivo=2026,
        cantidad_periodos=3,
        activo=True,
    )
    db.add_all([alumno, curso])
    db.commit()
    db.refresh(alumno)
    db.refresh(curso)
    return alumno, curso


def crear_invitacion_api(
    client,
    auth_headers_admin,
    alumno,
    curso,
    email="familia@test.com",
):
    return client.post(
        "/invitaciones/",
        headers=auth_headers_admin,
        json={
            "alumno_id": alumno.id,
            "curso_id": curso.id,
            "email": email,
        },
    )


def test_crear_invitacion_devuelve_token_y_lista(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    alumno, curso = crear_alumno_y_curso(db, usuario_admin)

    creada = crear_invitacion_api(
        client,
        auth_headers_admin,
        alumno,
        curso,
    )

    assert creada.status_code == 201

    datos = creada.json()

    assert datos["alumno_id"] == alumno.id
    assert datos["curso_id"] == curso.id
    assert datos["email"] == "familia@test.com"
    assert len(datos["token"]) >= 32

    listado = client.get(
        "/invitaciones/",
        headers=auth_headers_admin,
    )

    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == datos["id"]
    assert listado.json()[0]["revocada"] is False


def test_revocar_invitacion(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    alumno, curso = crear_alumno_y_curso(db, usuario_admin)

    creada = crear_invitacion_api(
        client,
        auth_headers_admin,
        alumno,
        curso,
    )

    assert creada.status_code == 201

    invitacion_id = creada.json()["id"]

    revocada = client.post(
        f"/invitaciones/{invitacion_id}/revocar",
        headers=auth_headers_admin,
    )

    assert revocada.status_code == 204

    listado = client.get(
        "/invitaciones/",
        headers=auth_headers_admin,
    )

    assert listado.json()[0]["revocada"] is True


def test_aceptar_invitacion_crea_cuenta_y_la_inscribe(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    alumno, curso = crear_alumno_y_curso(db, usuario_admin)

    creada = crear_invitacion_api(
        client,
        auth_headers_admin,
        alumno,
        curso,
        email="nuevo.alumno@test.com",
    )

    assert creada.status_code == 201

    aceptada = client.post(
        "/invitaciones/aceptar",
        json={
            "token": creada.json()["token"],
            "password": "password123",
        },
    )

    assert aceptada.status_code == 200

    token = aceptada.json()["access_token"]

    perfil = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert perfil.status_code == 200

    datos_perfil = perfil.json()

    assert datos_perfil["rol"] == "alumno"
    assert datos_perfil["email"] == "nuevo.alumno@test.com"
    assert datos_perfil["alumno_id"] == alumno.id
    assert datos_perfil["nombre"] == alumno.nombre
    assert datos_perfil["apellido"] == alumno.apellido

    cursos = client.get(
        "/cursos/mis-cursos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert cursos.status_code == 200
    assert [item["id"] for item in cursos.json()] == [curso.id]

    login = client.post(
        "/auth/login",
        json={
            "email": "nuevo.alumno@test.com",
            "password": "password123",
        },
    )

    assert login.status_code == 200


def test_aceptar_invitacion_token_invalido(client):
    respuesta = client.post(
        "/invitaciones/aceptar",
        json={
            "token": "a" * 32,
            "password": "password123",
        },
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Invitación inválida"
