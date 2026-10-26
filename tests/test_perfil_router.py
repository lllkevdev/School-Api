import pytest

from models.usuario import Usuario


def test_obtener_perfil_admin(client, auth_headers_admin):
    respuesta = client.get("/perfil/me", headers=auth_headers_admin)

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["usuario"]["email"] == "admin@test.com"
    assert datos["usuario"]["rol"] == "admin"
    assert datos["usuario"]["foto_perfil"] is None
    assert datos["alumno"] is None
    assert "password_hash" not in datos["usuario"]


def test_obtener_perfil_alumno(client, auth_headers_alumno, usuario_alumno):
    respuesta = client.get("/perfil/me", headers=auth_headers_alumno)

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["usuario"]["rol"] == "alumno"
    assert datos["usuario"]["alumno_id"] == usuario_alumno.id
    assert datos["alumno"]["id"] == usuario_alumno.id
    assert datos["alumno"]["documento_identidad"] == "12345678"
    assert "password_hash" not in datos["usuario"]


def test_obtener_perfil_sin_token(client):
    respuesta = client.get("/perfil/me")

    assert respuesta.status_code == 401


def test_actualizar_perfil_admin(client, db, auth_headers_admin):
    respuesta = client.patch(
        "/perfil/me",
        headers=auth_headers_admin,
        json={
            "nombre": "  Docente  ",
            "apellido": "  Actualizado  ",
            "telefono": "  123456  ",
        },
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["usuario"]["nombre"] == "Docente"
    assert datos["usuario"]["apellido"] == "Actualizado"
    assert datos["usuario"]["telefono"] == "123456"

    db.expire_all()
    usuario = db.get(Usuario, datos["usuario"]["id"])

    assert usuario is not None
    assert usuario.nombre == "Docente"
    assert usuario.apellido == "Actualizado"
    assert usuario.telefono == "123456"


def test_actualizar_perfil_alumno_no_modifica_datos_academicos(
    client,
    auth_headers_alumno,
    usuario_alumno,
):
    respuesta = client.patch(
        "/perfil/me",
        headers=auth_headers_alumno,
        json={
            "nombre": "Juan Carlos",
            "telefono": "555-1234",
        },
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["usuario"]["nombre"] == "Juan Carlos"
    assert datos["alumno"]["nombre"] == "Juan"
    assert datos["alumno"]["documento_identidad"] == "12345678"
    assert datos["alumno"]["id"] == usuario_alumno.id


def test_actualizar_perfil_permite_limpiar_telefono(
    client,
    auth_headers_admin,
):
    client.patch(
        "/perfil/me",
        headers=auth_headers_admin,
        json={"telefono": "123456"},
    )

    respuesta = client.patch(
        "/perfil/me",
        headers=auth_headers_admin,
        json={"telefono": None},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"]["telefono"] is None


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("email", "otro@test.com"),
        ("rol", "alumno"),
        ("activo", False),
        ("alumno_id", 1),
        ("documento_identidad", "99887766"),
    ],
)
def test_actualizar_perfil_rechaza_campos_no_editables(
    client,
    auth_headers_admin,
    campo,
    valor,
):
    respuesta = client.patch(
        "/perfil/me",
        headers=auth_headers_admin,
        json={campo: valor},
    )

    assert respuesta.status_code == 422


def test_actualizar_perfil_sin_cambios(client, auth_headers_admin):
    respuesta = client.patch(
        "/perfil/me",
        headers=auth_headers_admin,
        json={},
    )

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Debe proporcionar al menos un campo para actualizar"
    )


@pytest.mark.parametrize("campo", ["nombre", "apellido"])
def test_actualizar_perfil_rechaza_nombre_nulo(
    client,
    auth_headers_admin,
    campo,
):
    respuesta = client.patch(
        "/perfil/me",
        headers=auth_headers_admin,
        json={campo: None},
    )

    assert respuesta.status_code == 422


def test_actualizar_perfil_sin_token(client):
    respuesta = client.patch(
        "/perfil/me",
        json={"nombre": "Docente"},
    )

    assert respuesta.status_code == 401
