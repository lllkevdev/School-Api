from models.usuario import Usuario
from core.permisos import Rol
from models.materia import Materia
from models.alumno import Alumno
from models.calificacion import Calificacion
from  services.calificacion_service import buscar_calificaciones

def test_crear_calificacion(client):
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
            "nota": 8.5,
            "periodo": 2,
        }
    )

    assert response.status_code == 201

    assert response.json()["nota"] == 8.5
    assert response.json()["periodo"] == 2




def test_crear_calificacion_alumno_inexistente(client):
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
            "alumno_id": 999,
            "materia_id": materia_id,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    assert response.status_code == 404
    print(response.json())
    assert response.json() == {"detail": "El alumno no existe"}




def test_crear_calificacion_materia_inexistente(client):
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
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": 999,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "La materia no existe"}




def test_crear_calificacion_nota_menor_al_minimo(client):
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
            "nota": 0,
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "nota" in str(response.json())




def test_crear_calificacion_nota_mayor_al_maximo(client):
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
            "nota": 11,
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "nota" in str(response.json())




def test_crear_calificacion_periodo_menor_al_minimo(client):
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
            "nota": 8.5,
            "periodo": 0,
        }
    )

    assert response.status_code == 422
    assert "periodo" in str(response.json())




def test_crear_calificacion_periodo_mayor_al_maximo(client):
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
            "nota": 8.5,
            "periodo": 5,
        }
    )

    assert response.status_code == 422
    assert "periodo" in str(response.json())




def test_actualizar_calificacion(client):
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
            "nota": 8.5,
            "periodo": 2,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "nota": 9.0,
            "periodo": 3,
        }
    )

    assert response.status_code == 200

    assert response.json()["nota"] == 9.0
    assert response.json()["periodo"] == 3
    assert response.json()["alumno_id"] == alumno_id
    assert response.json()["materia_id"] == materia_id




def test_actualizar_calificacion_inexistente(client):
    response = client.patch(
        "/calificaciones/999",
        json={
            "nota": 9.0,
            "periodo": 3,
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Calificación no encontrada"}




def test_eliminar_calificacion(client, usuario_admin):
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
            "nota": 8.5,
            "periodo": 2,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.delete(f"/calificaciones/{calificacion_id}")

    assert response.status_code == 204

    response = client.get(f"/calificaciones/{calificacion_id}")
    assert response.status_code == 404





def test_eliminar_calificacion_inexistente(client):
    response = client.delete("/calificaciones/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Calificación no encontrada"}





def test_obtener_calificacion_por_id(client):
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
            "nota": 8.5,
            "periodo": 2,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.get(f"/calificaciones/{calificacion_id}")

    assert response.status_code == 200

    assert response.json()["nota"] == 8.5
    assert response.json()["periodo"] == 2
    assert response.json()["alumno_id"] == alumno_id
    assert response.json()["materia_id"] == materia_id





def test_obtener_calificacion_inexistente(client):
    response = client.get("/calificaciones/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Calificación no encontrada"}





def test_crear_calificacion_sin_nota(client):
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
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "nota" in str(response.json())





def test_crear_calificacion_sin_periodo(client):
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
            "nota": 8.5,
        }
    )

    assert response.status_code == 422
    assert "periodo" in str(response.json())



def test_crear_calificacion_sin_alumno_id(client):
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
            "materia_id": materia_id,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "alumno_id" in str(response.json())





def test_crear_calificacion_sin_materia_id(client):
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
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "materia_id" in str(response.json())






def test_obtener_calificaciones_alumno(client):
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
            "nota": 8.5,
            "periodo": 2,
        }
    )

    response = client.get(f"/calificaciones/alumno/{alumno_id}")

    assert response.status_code == 200

    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["nota"] == 8.5
    assert response.json()[0]["periodo"] == 2





def test_obtener_calificaciones_alumno_por_periodo(client):
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
            "nota": 8.5,
            "periodo": 1,
        }
    )
    response2 = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 9.0,
            "periodo": 2,
        }
    )

    response = client.get(f"/calificaciones/alumno/{alumno_id}?periodo=2")

    assert response.status_code == 200

    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["nota"] == 9.0
    assert response.json()[0]["periodo"] == 2





def test_obtener_calificaciones_detalle(client):
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
            "nota": 8.5,
            "periodo": 1,
        }
    )

    response = client.get("/calificaciones/detalle")

    assert response.status_code == 200

    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["nota"] == 8.5
    assert response.json()[0]["periodo"] == 1
    assert response.json()[0]["alumno"] == "Juan Pérez"
    assert response.json()[0]["materia"] == "Matemáticas"




def test_obtener_promedio_del_alumno(client):
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
        "/materias/",
        json={
            "nombre": "Historia",
        }
    )

    materia_id2 = response.json()["id"]

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8,
            "periodo": 1,
        }
    )
    
    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id2,
            "nota": 10,
            "periodo": 1,
        }
    )

    response = client.get(f"/calificaciones/alumno/{alumno_id}/promedio")
    assert response.status_code == 200

    assert isinstance(response.json(), dict)
    assert response.json()["promedio"] == 9.0





def test_obtener_promedio_alumno_sin_calificaciones(client):
    data = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = data.json()["id"]

    response = client.get(f"/calificaciones/alumno/{alumno_id}/promedio")

    assert response.status_code == 404

    assert isinstance(response.json(), dict)
    assert response.json() == {
        "detail" : "No se encontraron calificaciones para el alumno"
    }




def test_obtener_estadisticas_alumno(client):
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
        "/materias/",
        json={
            "nombre": "Historia",
        }
    )

    materia_id2 = response.json()["id"]

    response = client.post(
        "/materias/",
        json={
            "nombre": "Programacion",
        }
    )

    materia_id3 = response.json()["id"]

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 7,
            "periodo": 1,
        }
    )

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id2,
            "nota": 9,
            "periodo": 1,
        }
    )


    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id3,
            "nota": 8,
            "periodo": 1,
        }
    )


    response = client.get(f"/calificaciones/alumno/{alumno_id}/estadisticas")

    assert response.status_code == 200

    assert response.json()["promedio"] == 8.0
    assert response.json()["nota_maxima"] == 9
    assert response.json()["nota_minima"] == 7
    assert response.json()["cantidad_calificaciones"] == 3





def test_actualizar_nota(client):
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
            "nota": 7,
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "nota" : 9
        }
    )

    assert response.status_code == 200
    assert response.json()["nota"] == 9




def test_actualizar_periodo(client):
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
            "nota": 7,
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "periodo" : 2
        }
    )

    assert response.status_code == 200
    assert response.json()["periodo"] == 2
    assert response.json()["nota"] == 7





def test_actualizar_nota_invalida(client):
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
            "nota": 7,
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "nota" : 15
        }
    )

    assert response.status_code == 422





def test_obtener_estadisticas_de_alumno_inexistente(client):
    response = client.get("/calificaciones/alumno/9999/estadisticas")

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "El alumno no existe"
    }






def test_obtener_promedio_del_alumno_con_decimales(client):
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
        "/materias/",
        json={
            "nombre": "Historia",
        }
    )

    materia_id2 = response.json()["id"]


    response = client.post(
        "/materias/",
        json={
            "nombre": "Programacion"
        }
    )

    materia_id3 = response.json()["id"]

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 7,
            "periodo": 1,
        }
    )
    
    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id2,
            "nota": 8,
            "periodo": 1,
        }
    )

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id3,
            "nota": 10,
            "periodo": 1
        }
    )

    response = client.get(f"/calificaciones/alumno/{alumno_id}/promedio")

    assert response.status_code == 200

    assert response.json()["promedio"] == 8.33





def test_estadisticas_sin_calificaciones(client):
    data = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = data.json()["id"]

    response = client.get(f"/calificaciones/alumno/{alumno_id}/estadisticas")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "No se encontraron calificaciones para el alumno"
    }





def test_cambiar_materia_de_una_calificacion(client):
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
        "/materias/",
        json={
            "nombre": "Historia",
        }
    )

    materia_id2 = response.json()["id"]


    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 10,
            "periodo": 1
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "materia_id": materia_id2
        }
    )


    assert response.status_code == 200
    assert response.json()["materia_id"] == materia_id2
    assert response.json()["nota"] == 10
    assert response.json()["periodo"] == 1





def test_actualizar_calificacion_materia_inexistente(client):
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

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "materia_id": 999
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "La materia no existe"
    }




def test_actualizar_calificacion_alumno_inexistente(client):
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

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "alumno_id": 999
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "El alumno no existe"
    }




def test_obtener_calificaciones_alumno_inexistente(client):
    response = client.get(
        "/calificaciones/alumno/999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "El alumno no existe"
    }




def test_no_se_puede_eliminar_materia_con_calificaciones(client):
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

    response = client.delete(
        f"/materias/{materia_id}"
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "No se puede eliminar la materia porque tiene calificaciones asociadas"
    }




def test_no_se_puede_crear_calificacion_con_nota_invalida(client):
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
            "nota": 11,
            "periodo": 1
        }
    )

    assert response.status_code == 422




def test_no_se_puede_crear_calificacion_con_periodo_invalido(client):
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
            "nota": 10,
            "periodo": 4
        }
    )

    assert response.status_code == 422





def test_crear_calificacion_sin_permiso(client, usuario_alumno):
    response = client.post(
        "/calificaciones/",
        json={}
    )

    assert response.status_code == 403





def test_crear_calificacion_maestro(client, usuario_maestro):
    response = client.post(
        "/calificaciones/",
        json={}
    )

    assert response.status_code == 422






def test_actualizar_calificacion_sin_permiso(client, usuario_alumno):
    response = client.patch(
        "/calificaciones/1",
        json={}
    )

    assert response.status_code == 403






def test_eliminar_calificacion_sin_permiso(client, usuario_alumno):
    response = client.delete("/calificaciones/1")

    assert response.status_code == 403




def test_alumno_no_puede_ver_todas_las_calificaciones(client, usuario_alumno):
    response = client.get("/calificaciones/")

    assert response.status_code == 403



def test_alumno_no_puede_ver_detalle_de_todas_las_calificaciones(
    client,
    usuario_alumno
):
    response = client.get("/calificaciones/detalle")

    assert response.status_code == 403




def test_obtener_calificaciones_por_alumno_alumno(client, usuario_alumno):
    response = client.get("/calificaciones/alumno/1")

    assert response.status_code != 403





def test_obtener_calificaciones_join_alumno2(client, usuario_alumno):
    response = client.get("/calificaciones/alumno/1/join")

    assert response.status_code != 403





def test_obtener_promedio_alumno2(client, usuario_alumno):
    response = client.get("/calificaciones/alumno/1/promedio")

    assert response.status_code != 403






def test_obtener_estadisticas_alumno2(client, usuario_alumno):
    response = client.get("/calificaciones/alumno/1/estadisticas")

    assert response.status_code != 403





def test_alumno_puede_ver_su_calificacion(
    db,
    client,
    usuario_alumno
):
    materia = Materia(
        nombre="Matematica"
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=usuario_alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.get(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 200
    assert response.json()["nota"] == 8



def test_alumno_no_puede_ver_calificacion_de_otro_alumno(
    db,
    client,
    usuario_alumno
):
    otro_alumno = Alumno(
        nombre="Pedro",
        apellido="Lopez",
        edad=21
    )

    materia = Materia(
        nombre="Historia"
    )

    db.add_all([otro_alumno, materia])
    db.commit()
    db.refresh(otro_alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=otro_alumno.id,
        materia_id=materia.id,
        nota=9,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.get(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 403



def test_maestro_puede_ver_calificacion_de_su_materia2(
    db,
    client,
    usuario_maestro
):
    materia = Materia(
        nombre="Matematica",
        maestro_id=usuario_maestro.id
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([materia, alumno])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.get(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 200
    assert response.json()["nota"] == 8



def test_maestro_no_puede_ver_calificacion_de_materia_de_otro_maestro(
    db,
    client,
    usuario_maestro
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(otro_maestro)
    db.commit()
    db.refresh(otro_maestro)

    materia = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([materia, alumno])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=9,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.get(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 403



def test_modificar_una_calificacion_que_no_le_pertenece(db, client, usuario_maestro):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(otro_maestro)
    db.commit()
    db.refresh(otro_maestro)

    materia = Materia(
        nombre = "Matemática",
        maestro = otro_maestro
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)


    alumno = Alumno(
        nombre="Kevin",
        apellido="Baez",
        edad=25
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)


    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)


    response = client.patch(
        f"/calificaciones/{calificacion.id}",
        json={
            "nota": 9
        }
    )

    assert response.status_code == 403

    assert response.json()["detail"] == "No tiene permiso para modificar esta calificacion"





def test_modificar_calificacion_de_su_materia(client, db, usuario_maestro):
    materia = Materia(
        nombre="Matemática",
        maestro=usuario_maestro
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)


    alumno = Alumno(
        nombre="Kevin",
        apellido="Baez",
        edad=25
    ) 

    db.add(alumno)
    db.commit()
    db.refresh(alumno)


    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)


    response = client.patch(
        f"/calificaciones/{calificacion.id}",
        json={
            "nota": 9
        }
    )

    assert response.status_code == 200





def  test_modificar_una_calificacion_que_no_le_pertenece2(db, client, usuario_maestro):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(otro_maestro)
    db.commit()
    db.refresh(otro_maestro)

    alumno = Alumno(
        nombre="Kevin",
        apellido="Baez",
        edad=25
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)


    materia = Materia(
        nombre="Matematica",
        maestro=usuario_maestro
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    otra_materia = Materia(
        nombre="Fisica",
        maestro=otro_maestro
    )

    db.add(otra_materia)
    db.commit()
    db.refresh(otra_materia)

    response = client.patch(
        f"/calificaciones/{calificacion.id}",
        json={"materia_id": otra_materia.id}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para modificar esta calificacion"





def test_modificar_calificacion_a_otra_materia_suya(db, client, usuario_maestro):
    alumno = Alumno(
        nombre="Kevin",
        apellido="Baez",
        edad=25
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)


    materia = Materia(
        nombre="Matematica",
        maestro=usuario_maestro
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    otra_materia = Materia(
        nombre="Fisica",
        maestro=usuario_maestro
    )

    db.add(otra_materia)
    db.commit()
    db.refresh(otra_materia)

    response = client.patch(
        f"/calificaciones/{calificacion.id}",
        json={"materia_id": otra_materia.id}
    )

    assert response.status_code == 200
    assert response.json()["materia_id"] == otra_materia.id





def test_modificar_calificacion_de_materia_sin_maestro(db, client, usuario_maestro):
    alumno = Alumno(
        nombre="Kevin",
        apellido="Baez",
        edad=25
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)


    materia = Materia(
        nombre="Matematica"
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)


    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)


    response = client.patch(
    f"/calificaciones/{calificacion.id}",
        json={ 
            "nota": 9
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tiene permiso para modificar esta calificacion"




def test_admin_puede_modificar_calificacion_de_cualquier_materia(
    db,
    client,
    usuario_admin
):
    maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(maestro)
    db.commit()
    db.refresh(maestro)

    alumno = Alumno(
        nombre="Kevin",
        apellido="Baez",
        edad=25
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    materia = Materia(
        nombre="Matematica",
        maestro=maestro
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.patch(
        f"/calificaciones/{calificacion.id}",
        json={"nota": 9}
    )

    assert response.status_code == 200
    assert response.json()["nota"] == 9







def test_eliminar_calificacion_maestro_de_su_materia(
    client,
    db,
    usuario_maestro
):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    materia = Materia(
        nombre="Matematica",
        maestro_id=usuario_maestro.id
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    calificacion_id = calificacion.id

    response = client.delete(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 204

    calificacion_eliminada = db.query(Calificacion).filter(
        Calificacion.id == calificacion_id
    ).first()

    assert calificacion_eliminada is None






def test_eliminar_calificacion_maestro_de_materia_ajena(
    client,
    db,
    usuario_maestro
):
    maestro_otro = Usuario(
        nombre="Otro Maestro",
        email="otro_maestro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(maestro_otro)
    db.commit()
    db.refresh(maestro_otro)

    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    materia = Materia(
        nombre="Matematica",
        maestro_id=maestro_otro.id
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    calificacion_id = calificacion.id

    response = client.delete(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 403

    calificacion_existente = db.query(Calificacion).filter(
        Calificacion.id == calificacion_id
    ).first()

    assert calificacion_existente is not None





def test_eliminar_calificacion_maestro_materia_sin_maestro(
    client,
    db,
    usuario_maestro
):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    materia = Materia(
        nombre="Matematica",
        maestro_id=None
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    calificacion_id = calificacion.id

    response = client.delete(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 403

    calificacion_existente = db.query(Calificacion).filter(
        Calificacion.id == calificacion_id
    ).first()

    assert calificacion_existente is not None




def test_eliminar_calificacion_admin(
    client,
    db,
    usuario_admin
):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    materia = Materia(
        nombre="Matematica",
        maestro_id=usuario_admin
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    calificacion_id = calificacion.id

    response = client.delete(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 204

    calificacion_eliminada = db.query(Calificacion).filter(
        Calificacion.id == calificacion_id
    ).first()

    assert calificacion_eliminada is None





def test_alumno_puede_ver_su_propia_calificacion(db):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )
    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    materia = Materia(
        nombre="Matematica"
    )
    db.add(materia)
    db.commit()
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )
    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    usuario = {
        "id": 1,
        "rol": Rol.ALUMNO,
        "alumno_id": alumno.id
    }

    resultado, error = buscar_calificaciones(
        db,
        calificacion.id,
        usuario
    )

    assert error is None
    assert resultado is not None
    assert resultado.id == calificacion.id



def test_maestro_puede_ver_calificacion_de_su_materia(
    db,
    client,
    usuario_maestro
):
    alumno = Alumno(
        nombre="Pedro",
        apellido="Gomez",
        edad=20
    )

    materia = Materia(
        nombre="Matematica",
        maestro_id=usuario_maestro.id
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.get(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 200



def test_maestro_no_puede_ver_calificacion_de_otro_maestro(
    db,
    client,
    usuario_maestro
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(otro_maestro)
    db.commit()
    db.refresh(otro_maestro)

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    materia = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=9,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.get(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 403





def test_alumno_no_puede_ver_calificaciones_de_otro_alumno(
    db,
    client,
    usuario_alumno
):
    otro_alumno = Alumno(
        nombre="Pedro",
        apellido="Gomez",
        edad=21
    )

    materia = Materia(
        nombre="Matematica"
    )

    db.add_all([otro_alumno, materia])
    db.commit()
    db.refresh(otro_alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=otro_alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()

    response = client.get(
        f"/calificaciones/alumno/{otro_alumno.id}"
    )

    assert response.status_code == 403




def test_alumno_puede_ver_sus_calificaciones(
    db,
    client,
    usuario_alumno
):
    materia = Materia(
        nombre="Matematica"
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=usuario_alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()

    response = client.get(
        f"/calificaciones/alumno/{usuario_alumno.id}"
    )

    assert response.status_code == 200





def test_maestro_puede_ver_calificaciones_de_alumno_en_su_materia(
    db,
    client,
    usuario_maestro
):
    alumno = Alumno(
        nombre="Pedro",
        apellido="Gomez",
        edad=20
    )

    materia = Materia(
        nombre="Matematica",
        maestro_id=usuario_maestro.id
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()

    response = client.get(
        f"/calificaciones/alumno/{alumno.id}"
    )

    assert response.status_code == 200





def test_maestro_no_puede_ver_calificaciones_de_materia_de_otro_maestro(
    db,
    client,
    usuario_maestro
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(otro_maestro)
    db.commit()
    db.refresh(otro_maestro)

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=21
    )

    materia = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    db.add_all([alumno, materia])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=9,
        periodo=1
    )

    db.add(calificacion)
    db.commit()

    response = client.get(
        f"/calificaciones/alumno/{alumno.id}"
    )

    assert response.status_code == 200
    assert response.json() == []





def test_maestro_solo_ve_sus_calificaciones_de_un_alumno(
    db,
    client,
    usuario_maestro
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=21
    )

    materia_maestro = Materia(
        nombre="Matematica",
        maestro_id=usuario_maestro.id
    )

    materia_otro_maestro = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    db.add_all([
        otro_maestro,
        alumno,
        materia_maestro,
        materia_otro_maestro
    ])
    db.commit()

    db.refresh(otro_maestro)
    db.refresh(alumno)
    db.refresh(materia_maestro)
    db.refresh(materia_otro_maestro)

    calificacion_propia = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia_maestro.id,
        nota=8,
        periodo=1
    )

    calificacion_ajena = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia_otro_maestro.id,
        nota=9,
        periodo=1
    )

    db.add_all([
        calificacion_propia,
        calificacion_ajena
    ])
    db.commit()

    response = client.get(
        f"/calificaciones/alumno/{alumno.id}"
    )

    assert response.status_code == 200

    datos = response.json()

    assert len(datos) == 1
    assert datos[0]["materia"] == "Matematica"
    assert datos[0]["nota"] == 8





def test_maestro_no_puede_crear_calificacion_en_materia_de_otro_maestro(
    db,
    client,
    usuario_maestro
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(otro_maestro)
    db.commit()
    db.refresh(otro_maestro)

    materia = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([materia, alumno])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno.id,
            "materia_id": materia.id,
            "nota": 8,
            "periodo": 1
        }
    )

    assert response.status_code == 403






def test_maestro_puede_crear_calificacion_en_materia_propia(
    db,
    client,
    usuario_maestro
):
    materia = Materia(
        nombre="Matematica",
        maestro_id=usuario_maestro.id
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([materia, alumno])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno.id,
            "materia_id": materia.id,
            "nota": 8,
            "periodo": 1
        }
    )

    assert response.status_code == 201






def test_admin_puede_crear_calificacion_en_cualquier_materia(
    db,
    client,
    usuario_admin
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(otro_maestro)
    db.commit()
    db.refresh(otro_maestro)

    materia = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([materia, alumno])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno.id,
            "materia_id": materia.id,
            "nota": 8,
            "periodo": 1
        }
    )

    assert response.status_code == 201



def test_admin_puede_ver_todas_las_calificaciones(
    db,
    client,
    usuario_admin
):
    alumno1 = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    alumno2 = Alumno(
        nombre="Maria",
        apellido="Lopez",
        edad=21
    )

    materia = Materia(
        nombre="Matematica"
    )

    db.add_all([alumno1, alumno2, materia])
    db.commit()

    calificacion1 = Calificacion(
        alumno_id=alumno1.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    calificacion2 = Calificacion(
        alumno_id=alumno2.id,
        materia_id=materia.id,
        nota=9,
        periodo=1
    )

    db.add_all([calificacion1, calificacion2])
    db.commit()

    response = client.get("/calificaciones/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2



def test_maestro_no_puede_ver_todas_las_calificaciones(
    db,
    client,
    usuario_maestro
):
    response = client.get("/calificaciones/")

    assert response.status_code == 403





def test_admin_puede_ver_detalle_de_todas_las_calificaciones(
    db,
    client,
    usuario_admin
):
    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    materia = Materia(
        nombre="Matematica"
    )

    db.add_all([alumno, materia])
    db.commit()

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()

    response = client.get("/calificaciones/detalle")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["alumno"] == "Carlos Gomez"
    assert data[0]["materia"] == "Matematica"
    assert data[0]["nota"] == 8
    assert data[0]["periodo"] == 1




def test_maestro_no_puede_ver_detalle_de_todas_las_calificaciones(
    client,
    usuario_maestro
):
    response = client.get("/calificaciones/detalle")

    assert response.status_code == 403





def test_alumno_no_puede_modificar_calificacion(
    client,
    usuario_alumno
):
    response = client.patch(
        "/calificaciones/1",
        json={
            "nota": 9
        }
    )

    assert response.status_code == 403




def test_admin_puede_modificar_cualquier_calificacion(
    db,
    client,
    usuario_admin
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    materia = Materia(
        nombre="Historia",
        maestro=otro_maestro
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([otro_maestro, materia, alumno])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=6,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.patch(
        f"/calificaciones/{calificacion.id}",
        json={
            "nota": 9
        }
    )

    assert response.status_code == 200
    assert response.json()["nota"] == 9






def test_alumno_no_puede_eliminar_calificacion(
    client,
    usuario_alumno
):
    response = client.delete("/calificaciones/1")

    assert response.status_code == 403





def test_admin_puede_eliminar_cualquier_calificacion(
    db,
    client,
    usuario_admin
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    materia = Materia(
        nombre="Historia",
        maestro=otro_maestro
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([otro_maestro, materia, alumno])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    calificacion_id = calificacion.id

    response = client.delete(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 204

    eliminada = db.query(Calificacion).filter(
        Calificacion.id == calificacion_id
    ).first()

    assert eliminada is None