def test_admin_puede_listar_alumnos(client, auth_headers_admin):
    respuesta = client.get("/alumnos/", headers=auth_headers_admin)

    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)


def test_alumno_no_puede_listar_alumnos(client, auth_headers_alumno):
    respuesta = client.get("/alumnos/", headers=auth_headers_alumno)

    assert respuesta.status_code == 403


def test_listar_alumnos_sin_token(client):
    respuesta = client.get("/alumnos/")

    assert respuesta.status_code == 401


def test_admin_puede_crear_alumno(client, auth_headers_admin):
    respuesta = client.post(
        "/alumnos/",
        headers=auth_headers_admin,
        json={
            "nombre": "Alumno",
            "apellido": "Nuevo",
            "documento_identidad": "99887766",
            "fecha_nacimiento": "2005-03-15",
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["documento_identidad"] == "99887766"


def test_alumno_no_puede_crear_alumno(client, auth_headers_alumno):
    respuesta = client.post(
        "/alumnos/",
        headers=auth_headers_alumno,
        json={
            "nombre": "Alumno",
            "apellido": "Nuevo",
            "documento_identidad": "11223344",
            "fecha_nacimiento": "2005-03-15",
        },
    )

    assert respuesta.status_code == 403
