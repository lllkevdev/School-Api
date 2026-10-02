from models.alumno import Alumno
from models.materia import Materia
from models.inscripcion import Inscripcion
from models.calificacion import Calificacion
from tests.conftest import client, db


def test_crear_inscripcion(client):
    alumno = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = alumno.json()["id"]

    materia = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = materia.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["alumno_id"] == alumno_id
    assert data["materia_id"] == materia_id





def test_crear_inscripcion_alumno_inexistente(client):
    materia = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = materia.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": 999999,
            "materia_id": materia_id,
        }
    )

    assert response.status_code == 404




def test_crear_inscripcion_materia_inexistente(client):
    alumno = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = alumno.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": 999999,
        }
    )

    assert response.status_code == 404



def test_crear_inscripcion_duplicada(client):
    alumno = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = alumno.json()["id"]

    materia = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = materia.json()["id"]

    primera = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert primera.status_code == 201

    segunda = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert segunda.status_code == 409
    assert segunda.json()["detail"] == "El alumno ya esta inscripto en la materia"  


def test_crear_inscripcion_sin_permiso_maestro(
    client,
    db,
    usuario_maestro,
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
        }
    )

    assert response.status_code == 403




def test_eliminar_inscripcion(client, db):
    alumno = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = alumno.json()["id"]

    materia = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = materia.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert response.status_code == 201

    inscripcion = db.query(Inscripcion).filter(
        Inscripcion.alumno_id == alumno_id,
        Inscripcion.materia_id == materia_id,
    ).first()

    assert inscripcion is not None

    inscripcion_id = inscripcion.id

    response = client.delete(
        f"/inscripciones/{inscripcion_id}"
    )

    assert response.status_code == 204




def test_eliminar_inscripcion_elimina_calificacion(
    client_fk,
    db_fk,
):
    alumno = client_fk.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = alumno.json()["id"]

    materia = client_fk.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = materia.json()["id"]

    inscripcion = client_fk.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert inscripcion.status_code == 201

    response = client_fk.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    assert response.status_code == 201

    calificacion_id = response.json()["id"]

    inscripcion_db = db_fk.query(Inscripcion).filter(
        Inscripcion.alumno_id == alumno_id,
        Inscripcion.materia_id == materia_id,
    ).first()

    assert inscripcion_db is not None

    response = client_fk.delete(
        f"/inscripciones/{inscripcion_db.id}"
    )

    assert response.status_code == 204

    response = client_fk.get(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 404


def test_eliminar_inscripcion_sin_permiso_maestro(
    client,
    db,
    usuario_maestro,
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
        f"/inscripciones/{inscripcion.id}"
    )

    assert response.status_code == 403



def test_eliminar_inscripcion_sin_permiso_alumno(
    client,
    db,
    usuario_alumno,
):
    materia = Materia(
        nombre="Matemáticas",
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
        f"/inscripciones/{inscripcion.id}"
    )

    assert response.status_code == 403
