from models.materia import Materia
from models.usuario import Usuario
from models.inscripcion import Inscripcion
from models.alumno import Alumno
from models.calificacion import Calificacion

from schemas.roles import Rol


def test_crear_materia(client, usuario_admin):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    assert response.status_code == 201
    assert response.json()["nombre"] == "Matemáticas"


def test_obtener_materia_no_existente(client):
    response = client.get("/materias/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Materia no encontrada"}


def test_actualizar_materia(client, usuario_admin):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = response.json()["id"]

    response = client.put(
        f"/materias/{materia_id}",
        json={
            "nombre": "Física",
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == materia_id
    assert response.json()["nombre"] == "Física"


def test_actualizar_materia_parcialmente(client, usuario_admin):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    print(response.status_code)
    print(response.json())

    materia_id = response.json()["id"]

    response = client.patch(
        f"/materias/{materia_id}",
        json={
            "nombre": "Física",
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == materia_id
    assert response.json()["nombre"] == "Física"


def test_eliminar_materia(client, usuario_admin):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = response.json()["id"]

    response = client.delete(f"/materias/{materia_id}")

    assert response.status_code == 204

    response = client.get(f"/materias/{materia_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Materia no encontrada"}


def test_crear_materia_sin_nombre(client, usuario_admin):
    response = client.post(
        "/materias/",
        json={}
    )

    assert response.status_code == 422
    assert "nombre" in str(response.json())


def test_crear_materia_nombre_demasiado_corto(client, usuario_admin):
    response = client.post(
        "/materias/",
        json={
            "nombre": "A",
        }
    )

    assert response.status_code == 422
    assert "nombre" in str(response.json())


def test_crear_materia_duplicada(client, usuario_admin):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas"
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas"
        }
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Ya existe una materia con ese nombre"
    }


def test_actualizar_materia_parcialmente_no_existente(client, usuario_admin):
    response = client.patch(
        "/materias/999",
        json={
            "nombre": "Física",
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Materia no encontrada"}


def test_eliminar_materia_no_existente(client, usuario_admin):
    response = client.delete("/materias/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Materia no encontrada"}


def test_no_se_puede_actualizar_materia_con_nombre_duplicado(
    client,
    usuario_admin
):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    response = client.post(
        "/materias/",
        json={
            "nombre": "Historia",
        }
    )

    materia_id = response.json()["id"]

    response = client.put(
        f"/materias/{materia_id}",
        json={
            "nombre": "Matemáticas"
        }
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Ya existe una materia con ese nombre"
    }


def test_no_se_puede_actualizar_materia_parcialmente_con_nombre_duplicado(
    client,
    usuario_admin
):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    response = client.post(
        "/materias/",
        json={
            "nombre": "Historia",
        }
    )

    materia_id = response.json()["id"]

    response = client.patch(
        f"/materias/{materia_id}",
        json={
            "nombre": "Matemáticas"
        }
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Ya existe una materia con ese nombre"
    }


def test_no_se_puede_actualizar_materia_con_patch_vacio(
    client,
    usuario_admin
):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Historia",
        }
    )

    materia_id = response.json()["id"]

    response = client.patch(
        f"/materias/{materia_id}",
        json={}
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Debe proporcionar al menos un campo para actualizar"
    }


def test_crear_materia_sin_permiso(client, usuario_maestro):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemática"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"


def test_crear_materia_con_permiso(client, usuario_admin):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemática"
        }
    )

    assert response.status_code == 201


def test_actualizar_materia_sin_permiso(client, db, usuario_maestro):
    materia = Materia(nombre="Matematica")

    db.add(materia)
    db.commit()
    db.refresh(materia)

    materia_id = materia.id

    response = client.put(
        f"/materias/{materia_id}",
        json={
            "nombre": "Historia"
        }
    )

    assert response.status_code == 403


def test_actualizar_materia_parcialmente_sin_permiso(client, db, usuario_maestro):
    materia = Materia(nombre="Matematica")

    db.add(materia)
    db.commit()
    db.refresh(materia)

    materia_id = materia.id


    response = client.patch(
        f"/materias/{materia_id}",
        json={
            "nombre": "Historia"
        }
    )

    assert response.status_code == 403


def test_eliminar_materia_sin_permiso(client, db, usuario_maestro):
    materia = Materia(nombre="Matematica")

    db.add(materia)
    db.commit()
    db.refresh(materia)

    materia_id = materia.id

    response = client.delete(f"/materias/{materia_id}")

    assert response.status_code == 403


def test_materia_asignada_a_maestro(db):
    maestro = Usuario(
        nombre="Juan",
        email="juan@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    materia = Materia(
        nombre="Matematica",
        maestro=maestro
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    assert materia.maestro.id == maestro.id
    assert materia.maestro.email == "juan@test.com"
    assert materia in maestro.materias


def test_eliminar_materia_con_inscripcion_sin_calificacion(client, db):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20,
    )

    materia = Materia(
        nombre="Matematica",
    )

    db.add_all([alumno, materia])
    db.commit()

    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        materia_id=materia.id,
    )

    db.add(inscripcion)
    db.commit()

    response = client.delete(f"/materias/{materia.id}")

    assert response.status_code == 204

    inscripcion_existente = db.query(Inscripcion).filter(
        Inscripcion.materia_id == materia.id
    ).first()

    assert inscripcion_existente is None


def test_no_eliminar_materia_con_calificaciones(client, db, usuario_admin):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20,
    )

    materia = Materia(
        nombre="Matematica",
    )

    db.add_all([alumno, materia])
    db.commit()

    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        materia_id=materia.id,
    )

    db.add(inscripcion)
    db.commit()

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1,
    )

    db.add(calificacion)
    db.commit()

    response = client.delete(
        f"/materias/{materia.id}"
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": "No se puede eliminar la materia porque tiene calificaciones asociadas"
    }