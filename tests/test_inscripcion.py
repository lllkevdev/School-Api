from models.alumno import Alumno
from models.materia import Materia
from models.inscripcion import Inscripcion


def test_crear_inscripcion(client, auth_headers_admin):
    alumno = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        },
        headers=auth_headers_admin
    )

    assert alumno.status_code == 201
    alumno_id = alumno.json()["id"]

    materia = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        },
        headers=auth_headers_admin
    )

    assert materia.status_code == 201
    materia_id = materia.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 201

    data = response.json()

    assert data["alumno_id"] == alumno_id
    assert data["materia_id"] == materia_id


def test_crear_inscripcion_alumno_inexistente(
    client,
    auth_headers_admin
):
    materia = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        },
        headers=auth_headers_admin
    )

    assert materia.status_code == 201
    materia_id = materia.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": 999999,
            "materia_id": materia_id,
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 404


def test_crear_inscripcion_materia_inexistente(
    client,
    auth_headers_admin
):
    alumno = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        },
        headers=auth_headers_admin
    )

    assert alumno.status_code == 201
    alumno_id = alumno.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": 999999,
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 404


def test_crear_inscripcion_duplicada(
    client,
    auth_headers_admin
):
    alumno = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        },
        headers=auth_headers_admin
    )

    assert alumno.status_code == 201
    alumno_id = alumno.json()["id"]

    materia = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        },
        headers=auth_headers_admin
    )

    assert materia.status_code == 201
    materia_id = materia.json()["id"]

    primera = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        },
        headers=auth_headers_admin
    )

    assert primera.status_code == 201

    segunda = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        },
        headers=auth_headers_admin
    )

    assert segunda.status_code == 409
    assert segunda.json()["detail"] == (
        "El alumno ya esta inscripto en la materia"
    )


def test_crear_inscripcion_sin_permiso_maestro(
    client,
    db,
    auth_headers_maestro,
):
    alumno = Alumno(
        nombre="Juan",
        apellido="Pérez",
        edad=20,
    )

    materia = Materia(
        nombre="Matemáticas",
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno.id,
            "materia_id": materia.id,
        },
        headers=auth_headers_maestro
    )

    assert response.status_code == 403


def test_eliminar_inscripcion(
    client,
    db,
    auth_headers_admin
):
    alumno = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        },
        headers=auth_headers_admin
    )

    assert alumno.status_code == 201
    alumno_id = alumno.json()["id"]

    materia = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        },
        headers=auth_headers_admin
    )

    assert materia.status_code == 201
    materia_id = materia.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 201

    inscripcion = db.query(Inscripcion).filter(
        Inscripcion.alumno_id == alumno_id,
        Inscripcion.materia_id == materia_id,
    ).first()

    assert inscripcion is not None

    inscripcion_id = inscripcion.id

    response = client.delete(
        f"/inscripciones/{inscripcion_id}",
        headers=auth_headers_admin
    )

    assert response.status_code == 204


def test_eliminar_inscripcion_elimina_calificacion(
    client_fk,
    db_fk,
    auth_headers_admin,
):
    alumno = client_fk.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        },
        headers=auth_headers_admin
    )

    assert alumno.status_code == 201
    alumno_id = alumno.json()["id"]

    materia = client_fk.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        },
        headers=auth_headers_admin
    )

    assert materia.status_code == 201
    materia_id = materia.json()["id"]

    inscripcion = client_fk.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        },
        headers=auth_headers_admin
    )

    assert inscripcion.status_code == 201

    response = client_fk.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8.5,
            "periodo": 2,
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 201

    calificacion_id = response.json()["id"]

    inscripcion_db = db_fk.query(Inscripcion).filter(
        Inscripcion.alumno_id == alumno_id,
        Inscripcion.materia_id == materia_id,
    ).first()

    assert inscripcion_db is not None

    response = client_fk.delete(
        f"/inscripciones/{inscripcion_db.id}",
        headers=auth_headers_admin
    )

    assert response.status_code == 204

    response = client_fk.get(
        f"/calificaciones/{calificacion_id}",
        headers=auth_headers_admin
    )

    assert response.status_code == 404


def test_eliminar_inscripcion_sin_permiso_maestro(
    client,
    db,
    auth_headers_maestro,
):
    alumno = Alumno(
        nombre="Juan",
        apellido="Pérez",
        edad=20,
    )

    materia = Materia(
        nombre="Matemáticas",
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        materia_id=materia.id,
    )

    db.add(inscripcion)
    db.commit()
    db.refresh(inscripcion)

    response = client.delete(
        f"/inscripciones/{inscripcion.id}",
        headers=auth_headers_maestro
    )

    assert response.status_code == 403


def test_eliminar_inscripcion_sin_permiso_alumno(
    client,
    db,
    usuario_alumno,
    auth_headers_alumno,
):
    materia = Materia(
        nombre="Matemáticas"
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    inscripcion = Inscripcion(
        alumno_id=usuario_alumno.id,
        materia_id=materia.id,
    )

    db.add(inscripcion)
    db.commit()
    db.refresh(inscripcion)

    assert inscripcion is not None

    response = client.delete(
        f"/inscripciones/{inscripcion.id}",
        headers=auth_headers_alumno
    )

    assert response.status_code == 403


def test_eliminar_inscripcion_inexistente(
    client,
    auth_headers_admin,
):
    response = client.delete(
        "/inscripciones/999999",
        headers=auth_headers_admin
    )

    assert response.status_code == 404