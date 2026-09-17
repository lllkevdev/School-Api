from urllib import response

from fastapi.testclient import TestClient
from app import main

from database.dependencies import get_db
from tests.conftest import override_get_db

main.app.dependency_overrides[get_db] = override_get_db

client = TestClient(main.app)



def test_obtener_alumnos():
    response = client.get("/alumnos/")
    
    assert response.status_code == 200



def test_no_eliminar_alumno_con_calificaciones(client):
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
    assert response.json() == {"detail": "No se puede eliminar el alumno porque tiene calificaciones asociadas"}



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



def test_obtener_alumno_por_id(client):
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



def test_eliminar_alumno_sin_calificaciones(client):
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



def test_actualizar_alumno(client):
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



def test_actualizar_alumno_parcialmente(client):
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



def test_actualizar_parcialmente_alumno_no_existente(client):
    response = client.patch(
        "/alumnos/999",
        json={
            "nombre": "Juan Carlos",
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Alumno no encontrado"}



def test_actualizar_alumno_no_existente(client):
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




def test_obtener_alumno_con_calificaciones(client):
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





def test_obtener_promedio_alumno_por_periodo(client):
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
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 6,
            "periodo": 1
        }
    )



    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 10,
            "periodo": 2
        }
    )


    response = client.get(
        f"/calificaciones/alumno/{alumno_id}/promedio?periodo=2"
    )

    data = response.json()

    print(response.url)
    print(data)
    
    assert response.status_code == 200

    assert data["promedio"] == 10.0
    assert data["alumno"] == "Juan Pérez"




def test_obtener_estadisticas_alumno_por_periodo(client):
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
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 6,
            "periodo": 1
        }
    )



    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 10,
            "periodo": 2
        }
    )

    response = client.get(
        f"/calificaciones/alumno/{alumno_id}/estadisticas?periodo=2"
    )

    data = response.json()

    assert response.status_code == 200

    assert data["cantidad_calificaciones"] == 1
    assert data["promedio"] == 10
    assert data["nota_maxima"] == 10
    assert data["nota_minima"] == 10