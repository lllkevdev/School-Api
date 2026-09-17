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




def test_eliminar_calificacion(client):
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

