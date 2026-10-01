from urllib import response

from fastapi.testclient import TestClient
from app import main

from database.dependencies import get_db
from tests.conftest import override_get_db

from models.alumno import Alumno
from models.materia import Materia
from models.usuario import Usuario
from models.calificacion import Calificacion

from core.permisos import Rol

from app.main import app

main.app.dependency_overrides[get_db] = override_get_db

client = TestClient(main.app)



def test_obtener_alumnos():
    response = client.get("/alumnos/")
    
    assert response.status_code == 200



def test_maestro_puede_obtener_alumnos(client, usuario_maestro):
    response = client.get("/alumnos/")

    assert response.status_code == 200




def test_alumno_no_puede_obtener_todos_los_alumnos(client, usuario_alumno):
    response = client.get("/alumnos/")

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"



def test_no_eliminar_alumno_con_calificaciones(client, usuario_admin):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = response.json()["id"]

    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = response.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    response = client.delete(f"/alumnos/{alumno_id}")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "No se puede eliminar el alumno porque tiene calificaciones asociadas"
    }



def test_crear_alumno(client):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    print(response.json())

    assert response.status_code == 201
    assert response.json()["nombre"] == "Juan"
    assert response.json()["apellido"] == "Pérez"
    assert response.json()["edad"] == 20   



def test_obtener_alumno_por_id(client, usuario_admin):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = response.json()["id"]

    response = client.get(f"/alumnos/{alumno_id}")

    assert response.status_code == 200
    assert response.json()["id"] == alumno_id
    assert response.json()["nombre"] == "Juan"
    assert response.json()["apellido"] == "Pérez"
    assert response.json()["edad"] == 20



def test_obtener_alumno_no_existente(client):
    response = client.get("/alumnos/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Alumno no encontrado"}



def test_maestro_puede_obtener_alumno_por_id(client, db, usuario_maestro):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    response = client.get(f"/alumnos/{alumno.id}")

    assert response.status_code == 200
    assert response.json()["id"] == alumno.id
    assert response.json()["nombre"] == "Juan"



def test_alumno_no_puede_obtener_otro_alumno(client, db, usuario_alumno):
    otro_alumno = Alumno(
        nombre="Pedro",
        apellido="Gómez",
        edad=22
    )

    db.add(otro_alumno)
    db.commit()
    db.refresh(otro_alumno)

    response = client.get(f"/alumnos/{otro_alumno.id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"



def test_eliminar_alumno_sin_calificaciones(client, usuario_admin):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = response.json()["id"]

    response = client.delete(f"/alumnos/{alumno_id}")

    assert response.status_code == 204

    response = client.get(f"/alumnos/{alumno_id}")
    assert response.status_code == 404



def test_crear_alumno_sin_edad(client):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
        }
    )

    assert response.status_code == 422
    assert "edad" in str(response.json())



def test_crear_alumno_con_edad_invalida(client):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 0,
        }
    )

    assert response.status_code == 422
    assert "edad" in str(response.json())



def test_actualizar_alumno(client, usuario_admin):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = response.json()["id"]

    response = client.put(
        f"/alumnos/{alumno_id}",
        json={
            "nombre": "Juan Carlos",
            "apellido": "Pérez Gómez",
            "edad": 21,
        }
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Juan Carlos"
    assert response.json()["apellido"] == "Pérez Gómez"
    assert response.json()["edad"] == 21



def test_actualizar_alumno_parcialmente(client, usuario_admin):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = response.json()["id"]

    response = client.patch(
        f"/alumnos/{alumno_id}",
        json={
            "nombre": "Juan Carlos",
        }
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Juan Carlos"
    assert response.json()["apellido"] == "Pérez"
    assert response.json()["edad"] == 20



def test_actualizar_parcialmente_alumno_no_existente(client, usuario_admin):
    response = client.patch(
        "/alumnos/999",
        json={
            "nombre": "Juan Carlos",
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Alumno no encontrado"}



def test_actualizar_alumno_no_existente(client, usuario_admin):
    response = client.put(
        "/alumnos/999",
        json={
            "nombre": "Juan Carlos",
            "apellido": "Pérez Gómez",
            "edad": 21,
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Alumno no encontrado"}    




def test_obtener_alumno_con_calificaciones(client, usuario_admin):
    data = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = data.json()["id"]

    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

    materia_id = response.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 10,
            "periodo": 1
        }
    )

    response = client.get(f"/alumnos/{alumno_id}/calificaciones")

    data = response.json()

    assert response.status_code == 200

    assert data["nombre"] == "Juan"
    assert data["calificaciones"][0]["materia"] == "Matemáticas"
    assert data["calificaciones"][0]["nota"] == 10
    assert data["calificaciones"][0]["periodo"] == 1
    assert data["promedio"] == 10.0

    assert len(data["calificaciones"]) == 1






def test_crear_alumno_sin_permiso(client, usuario_maestro):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"




def test_alumno_no_puede_crear_alumno(client, usuario_alumno):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"


def test_alumno_no_puede_actualizar_alumno(client, db, usuario_alumno):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    response = client.put(
        f"/alumnos/{alumno.id}",
        json={
            "nombre": "Juan Carlos",
            "apellido": "Pérez Gómez",
            "edad": 21,
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"


def test_alumno_no_puede_modificar_alumno(client, db, usuario_alumno):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    response = client.patch(
        f"/alumnos/{alumno.id}",
        json={
            "nombre": "Juan Carlos",
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"


def test_alumno_no_puede_eliminar_alumno(client, db, usuario_alumno):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    response = client.delete(
        f"/alumnos/{alumno.id}"
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"


def test_actualizar_alumno_sin_permiso(client, db, usuario_maestro):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    response = client.put(
        f"/alumnos/{alumno.id}",
        json={
            "nombre": "Juan Carlos",
            "apellido": "Pérez Gómez",
            "edad": 21,
        }
    )

    assert response.status_code == 403




def test_modificar_alumno_sin_permiso(client, db, usuario_maestro):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    response = client.patch(
        f"/alumnos/{alumno.id}",
        json={
            "nombre": "Juan Carlos",
            "apellido": "Pérez Gómez",
            "edad": 21,
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"





def test_eliminar_alumno_sin_permiso(client, db, usuario_maestro):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)


    response = client.delete(
        f"/alumnos/{alumno.id}"
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"





def test_alumno_no_puede_ver_calificaciones_de_otro_alumno(
    client,
    db,
    usuario_alumno
):
    otro_alumno = Alumno(
        nombre="Pedro",
        apellido="Gómez",
        edad=22
    )

    db.add(otro_alumno)
    db.commit()
    db.refresh(otro_alumno)

    response = client.get(
        f"/alumnos/{otro_alumno.id}/calificaciones"
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para realizar esta acción"





def test_maestro_solo_puede_ver_calificaciones_de_sus_materias(
    client,
    db,
    usuario_maestro
):
    # Otro maestro
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(otro_maestro)
    db.commit()
    db.refresh(otro_maestro)

    # Alumno
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    # Materia del maestro autenticado
    materia_propia = Materia(
        nombre="Matematicas",
        maestro_id=usuario_maestro.id
    )

    # Materia del otro maestro
    materia_ajena = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    db.add_all([materia_propia, materia_ajena])
    db.commit()
    db.refresh(materia_propia)
    db.refresh(materia_ajena)

    # Calificación de la materia propia
    calificacion_propia = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia_propia.id,
        nota=10,
        periodo=1
    )

    # Calificación de la materia ajena
    calificacion_ajena = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia_ajena.id,
        nota=5,
        periodo=1
    )

    db.add_all([calificacion_propia, calificacion_ajena])
    db.commit()

    response = client.get(
        f"/alumnos/{alumno.id}/calificaciones"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["calificaciones"]) == 1
    assert data["calificaciones"][0]["materia"] == "Matematicas"
    assert data["calificaciones"][0]["nota"] == 10
    assert data["promedio"] == 10.0