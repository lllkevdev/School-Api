def test_crear_materia(client):
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




def test_actualizar_materia(client):
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




def test_actualizar_materia_parcialmente(client):
    response = client.post(
        "/materias/",
        json={
            "nombre": "Matemáticas",
        }
    )

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




def test_eliminar_materia(client):
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




def test_crear_materia_sin_nombre(client):
    response = client.post(
        "/materias/",
        json={}
    )

    assert response.status_code == 422
    assert "nombre" in str(response.json())




def test_crear_materia_nombre_demasiado_corto(client):
    response = client.post(
        "/materias/",
        json={
            "nombre": "A",
        }
    )

    assert response.status_code == 422
    assert "nombre" in str(response.json())



def test_crear_materia_duplicada(client):
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




def test_actualizar_materia_parcialmente_no_existente(client):
    response = client.patch(
        "/materias/999",
        json={
            "nombre": "Física",
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Materia no encontrada"}




def test_eliminar_materia_no_existente(client):
    response = client.delete("/materias/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Materia no encontrada"}


def test_no_se_puede_actualizar_materia_con_nombre_duplicado(client):
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




def test_no_se_puede_actualizar_materia_parcialmente_con_nombre_duplicado(client):
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





def test_no_se_puede_actualizar_materia_con_patch_vacio(client):
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