from schemas.roles import Rol


def test_admin_puede_crear_maestro(client, auth_headers_admin):
    response = client.post(
        "/maestros/",
        headers=auth_headers_admin,
        json={
            "nombre": "Carlos",
            "apellido": "Perez",
            "email": "carlos.nuevo@test.com",
            "telefono": "2601234567",
            "password": "12345678",
        },
    )

    assert response.status_code == 201

    datos = response.json()
    assert datos["nombre"] == "Carlos"
    assert datos["apellido"] == "Perez"
    assert datos["email"] == "carlos.nuevo@test.com"
    assert datos["rol"] == Rol.MAESTRO.value
    assert "password_hash" not in datos


def test_admin_puede_listar_maestros(
    client,
    auth_headers_admin,
    usuario_maestro,
):
    response = client.get(
        "/maestros/",
        headers=auth_headers_admin,
    )

    assert response.status_code == 200

    maestros = response.json()
    assert len(maestros) == 1
    assert maestros[0]["email"] == usuario_maestro.email
    assert maestros[0]["rol"] == Rol.MAESTRO.value
    assert "password_hash" not in maestros[0]


def test_maestro_no_puede_crear_otro_maestro(
    client,
    auth_headers_maestro,
):
    response = client.post(
        "/maestros/",
        headers=auth_headers_maestro,
        json={
            "nombre": "Pedro",
            "apellido": "Gomez",
            "email": "pedro.nuevo@test.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 403


def test_alumno_no_puede_listar_maestros(
    client,
    auth_headers_alumno,
):
    response = client.get(
        "/maestros/",
        headers=auth_headers_alumno,
    )

    assert response.status_code == 403



def test_admin_puede_actualizar_maestro(
    client,
    auth_headers_admin,
    usuario_maestro,
):
    response = client.patch(
        f"/maestros/{usuario_maestro.id}",
        headers=auth_headers_admin,
        json={"telefono": "2602222222"},
    )

    assert response.status_code == 200
    assert response.json()["telefono"] == "2602222222"
    assert response.json()["rol"] == Rol.MAESTRO.value
    assert "password_hash" not in response.json()


def test_admin_no_puede_actualizar_usuario_que_no_es_maestro(
    client,
    auth_headers_admin,
    usuario_admin,
):
    response = client.patch(
        f"/maestros/{usuario_admin.id}",
        headers=auth_headers_admin,
        json={"nombre": "Otro Nombre"},
    )

    assert response.status_code == 404


def test_maestro_no_puede_actualizar_otro_maestro(
    client,
    auth_headers_maestro,
    usuario_maestro,
):
    response = client.patch(
        f"/maestros/{usuario_maestro.id}",
        headers=auth_headers_maestro,
        json={"nombre": "Otro Nombre"},
    )

    assert response.status_code == 403


def test_admin_puede_desactivar_maestro(
    client,
    usuario_maestro,
    auth_headers_admin,
):
    respuesta = client.delete(
        f"/maestros/{usuario_maestro.id}",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False


def test_maestro_no_puede_desactivar_otro_maestro(
    client,
    usuario_maestro,
    auth_headers_maestro,
):
    respuesta = client.delete(
        f"/maestros/{usuario_maestro.id}",
        headers=auth_headers_maestro,
    )

    assert respuesta.status_code == 403


def test_admin_no_puede_desactivar_usuario_que_no_es_maestro(
    client,
    usuario_admin,
    auth_headers_admin,
):
    respuesta = client.delete(
        f"/maestros/{usuario_admin.id}",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 404


def test_admin_no_puede_desactivar_maestro_inexistente(
    client,
    auth_headers_admin,
):
    respuesta = client.delete(
        "/maestros/99999",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 404