from app.main import app
from core.dependencies import get_usuario_actual
from core.permisos import Rol
from models.alumno import Alumno
from models.calificacion import Calificacion
from models.materia import Materia
from models.usuario import Usuario
from models.inscripcion import Inscripcion
from services.calificacion_service import buscar_calificaciones


def asegurar_inscripcion(db, alumno_id, materia_id):
    inscripcion = db.query(Inscripcion).filter(
        Inscripcion.alumno_id == alumno_id,
        Inscripcion.materia_id == materia_id,
    ).first()

    if inscripcion is None:
        db.add(Inscripcion(
            alumno_id=alumno_id,
            materia_id=materia_id,
        ))
        db.commit()


# ============================================================
# CREAR CALIFICACIÓN
# ============================================================


def test_crear_calificacion(client):
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
    assert response.json() == {
        "detail": "El alumno no existe"
    }


def test_crear_calificacion_materia_inexistente(client):
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
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": 999,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "La materia no existe"
    }


def test_crear_calificacion_sin_nota(client):
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
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "nota" in str(response.json())


def test_crear_calificacion_sin_periodo(client):
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
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "materia_id" in str(response.json())



def test_no_se_puede_crear_calificacion_duplicada(client):
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
            "nota": 8,
            "periodo": 2,
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 9,
            "periodo": 2,
        }
    )

    assert response.status_code == 409


def test_crear_calificacion_alumno_no_inscripto(
    client,
):
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
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8,
            "periodo": 1,
        }
    )

    assert response.status_code == 409


# ============================================================
# VALIDACIONES DE NOTA Y PERÍODO
# ============================================================

def test_crear_calificacion_nota_menor_al_minimo(client):
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
            "nota": 0,
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "nota" in str(response.json())


def test_crear_calificacion_nota_mayor_al_maximo(client):
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
            "nota": 11,
            "periodo": 2,
        }
    )

    assert response.status_code == 422
    assert "nota" in str(response.json())


def test_crear_calificacion_periodo_menor_al_minimo(client):
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
            "periodo": 0,
        }
    )

    assert response.status_code == 422
    assert "periodo" in str(response.json())


def test_crear_calificacion_periodo_mayor_al_maximo(client):
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
            "periodo": 5,
        }
    )

    assert response.status_code == 422
    assert "periodo" in str(response.json())


# ============================================================
# OBTENER CALIFICACIONES
# ============================================================

def test_obtener_calificacion_por_id(client):
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

    calificacion_id = response.json()["id"]

    response = client.get(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 200
    assert response.json()["nota"] == 8.5
    assert response.json()["periodo"] == 2
    assert response.json()["alumno_id"] == alumno_id
    assert response.json()["materia_id"] == materia_id


def test_obtener_calificaciones_alumno(client, usuario_admin):
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

    client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8.5,
            "periodo": 2,
        }
    )

    response = client.get(
        f"/calificaciones/alumno/{alumno_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["nota"] == 8.5
    assert data[0]["periodo"] == 2


def test_obtener_calificaciones_alumno_por_periodo(client):
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

    client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8.5,
            "periodo": 1,
        }
    )

    client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 9.0,
            "periodo": 2,
        }
    )

    response = client.get(
        f"/calificaciones/alumno/{alumno_id}?periodo=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["nota"] == 9.0
    assert data[0]["periodo"] == 2



def test_obtener_calificaciones_alumno_inexistente(client):
    response = client.get(
        "/calificaciones/alumno/999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "El alumno no existe"
    }


# ============================================================
# DETALLE Y ESTADÍSTICAS
# ============================================================


def test_obtener_calificaciones_detalle(client):
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

    client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8.5,
            "periodo": 1,
        }
    )

    response = client.get(
        "/calificaciones/detalle"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["nota"] == 8.5
    assert data[0]["periodo"] == 1
    assert data[0]["alumno"] == "Juan Pérez"
    assert data[0]["materia"] == "Matemáticas"




def test_obtener_estadisticas_alumno(client):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = response.json()["id"]

    materias = []

    for nombre in ["Matemáticas", "Historia", "Programacion"]:
        response = client.post(
            "/materias/",
            json={"nombre": nombre}
        )
        materias.append(response.json()["id"])

    notas = [7, 9, 8]

    for materia_id, nota in zip(materias, notas):
        response = client.post(
            "/inscripciones/",
            json={
                "alumno_id": alumno_id,
                "materia_id": materia_id,
            }
        )

        assert response.status_code == 201

        client.post(
            "/calificaciones/",
            json={
                "alumno_id": alumno_id,
                "materia_id": materia_id,
                "nota": nota,
                "periodo": 1,
            }
        )

    response = client.get(
        f"/calificaciones/alumno/{alumno_id}/estadisticas"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3

    matematicas = next(
        item for item in data
        if item["materia"] == "Matemáticas"
    )

    historia = next(
        item for item in data
        if item["materia"] == "Historia"
    )

    programacion = next(
        item for item in data
        if item["materia"] == "Programacion"
    )

    assert matematicas["alumno"] == "Juan Pérez"
    assert matematicas["periodo_1"] == 7
    assert matematicas["periodo_2"] is None
    assert matematicas["periodo_3"] is None
    assert matematicas["promedio"] == 7.0

    assert historia["alumno"] == "Juan Pérez"
    assert historia["periodo_1"] == 9
    assert historia["periodo_2"] is None
    assert historia["periodo_3"] is None
    assert historia["promedio"] == 9.0

    assert programacion["alumno"] == "Juan Pérez"
    assert programacion["periodo_1"] == 8
    assert programacion["periodo_2"] is None
    assert programacion["periodo_3"] is None
    assert programacion["promedio"] == 8.0




def test_obtener_estadisticas_de_alumno_inexistente(client):
    response = client.get(
        "/calificaciones/alumno/9999/estadisticas"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "El alumno no existe"
    }


def test_estadisticas_sin_calificaciones(client):
    response = client.post(
        "/alumnos/",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "edad": 20,
        }
    )

    alumno_id = response.json()["id"]

    response = client.get(
        f"/calificaciones/alumno/{alumno_id}/estadisticas"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "No se encontraron calificaciones para el alumno"
    }


# ============================================================
# ACTUALIZAR CALIFICACIÓN
# ============================================================


def test_actualizar_calificacion(client):
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
    assert response.json() == {
        "detail": "Calificación no encontrada"
    }


def test_actualizar_nota(client):
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
            "nota": 7,
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={"nota": 9}
    )

    assert response.status_code == 200
    assert response.json()["nota"] == 9




def test_actualizar_periodo(client):
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
            "nota": 7,
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={"periodo": 2}
    )

    assert response.status_code == 200
    assert response.json()["periodo"] == 2
    assert response.json()["nota"] == 7


def test_actualizar_nota_invalida(client):
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
            "nota": 7,
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={"nota": 15}
    )

    assert response.status_code == 422




def test_cambiar_materia_de_una_calificacion(client):
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
        json={"nombre": "Matemáticas"}
    )

    materia_id = response.json()["id"]

    response = client.post(
        "/materias/",
        json={"nombre": "Historia"}
    )

    materia_id2 = response.json()["id"]

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id2,
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 10,
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={"materia_id": materia_id2}
    )

    assert response.status_code == 200
    assert response.json()["materia_id"] == materia_id2
    assert response.json()["nota"] == 10
    assert response.json()["periodo"] == 1



def test_actualizar_calificacion_materia_inexistente(client):
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
        json={"nombre": "Matemáticas"}
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
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={"materia_id": 999}
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "La materia no existe"
    }


def test_actualizar_calificacion_alumno_inexistente(client):
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
        json={"nombre": "Matemáticas"}
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
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={"alumno_id": 999}
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "El alumno no existe"
    }


def test_actualizar_calificacion_genera_duplicado(client):
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
        "/materias/",
        json={
            "nombre": "Historia",
        }
    )

    materia_id2 = response.json()["id"]

    # Inscribimos al alumno en ambas materias
    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/inscripciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id2,
        }
    )

    assert response.status_code == 201

    # Primera calificación
    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "nota": 8,
            "periodo": 1,
        }
    )

    assert response.status_code == 201

    # Segunda calificación
    response = client.post(
        "/calificaciones/",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id2,
            "nota": 7,
            "periodo": 1,
        }
    )

    assert response.status_code == 201

    calificacion_id = response.json()["id"]

    # Intentamos mover Historia → Matemáticas
    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "materia_id": materia_id,
        }
    )

    assert response.status_code == 409


def test_admin_puede_cambiar_alumno_de_una_calificacion(client, db):
    alumno_original = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20,
    )

    alumno_nuevo = Alumno(
        nombre="Pedro",
        apellido="Gomez",
        edad=21,
    )

    materia = Materia(
        nombre="Matemáticas",
    )

    db.add_all([
        alumno_original,
        alumno_nuevo,
        materia,
    ])
    db.commit()

    db.refresh(alumno_original)
    db.refresh(alumno_nuevo)
    db.refresh(materia)

    inscripcion_original = Inscripcion(
        alumno_id=alumno_original.id,
        materia_id=materia.id,
    )

    inscripcion_nueva = Inscripcion(
        alumno_id=alumno_nuevo.id,
        materia_id=materia.id,
    )

    db.add_all([
        inscripcion_original,
        inscripcion_nueva,
    ])
    db.commit()

    asegurar_inscripcion(db, alumno_original.id, materia.id)
    calificacion = Calificacion(
        alumno_id=alumno_original.id,
        materia_id=materia.id,
        nota=7,
        periodo=1,
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.patch(
        f"/calificaciones/{calificacion.id}",
        json={
            "alumno_id": alumno_nuevo.id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["alumno_id"] == alumno_nuevo.id
    assert data["materia_id"] == materia.id
    assert data["nota"] == 7
    assert data["periodo"] == 1



def test_no_se_puede_cambiar_materia_sin_inscripcion(client):
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
        json={"nombre": "Matemáticas"}
    )

    materia_id = response.json()["id"]

    response = client.post(
        "/materias/",
        json={"nombre": "Historia"}
    )

    materia_id2 = response.json()["id"]

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
            "nota": 8,
            "periodo": 1,
        }
    )

    calificacion_id = response.json()["id"]

    response = client.patch(
        f"/calificaciones/{calificacion_id}",
        json={
            "materia_id": materia_id2,
        },
    )

    assert response.status_code == 409


# ===========================================================
# ELIMINAR CALIFICACIÓN
# ============================================================


def test_eliminar_calificacion(client, usuario_admin):
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
        json={"nombre": "Matemáticas"}
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

    calificacion_id = response.json()["id"]

    response = client.delete(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/calificaciones/{calificacion_id}"
    )

    assert response.status_code == 404


def test_eliminar_calificacion_inexistente(client):
    response = client.delete(
        "/calificaciones/999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Calificación no encontrada"
    }


def test_maestro_puede_eliminar_calificacion_de_su_materia(
    client,
    db,
    usuario_maestro,
):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20,
    )

    materia = Materia(
        nombre="Matemáticas",
        maestro_id=usuario_maestro.id,
    )

    db.add_all([alumno, materia])
    db.commit()

    db.refresh(alumno)
    db.refresh(materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1,
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.delete(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 404


def test_maestro_no_puede_eliminar_calificacion_de_materia_ajena(
    client,
    db,
    usuario_maestro,
):
    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO,
    )

    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20,
    )

    db.add_all([otro_maestro, alumno])
    db.commit()

    db.refresh(otro_maestro)
    db.refresh(alumno)

    materia = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id,
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1,
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.delete(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 403


def test_alumno_no_puede_eliminar_calificacion(
        client,
        db,
        usuario_alumno
):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    materia = Materia(
        nombre="Matematicas",
    )

    db.add_all([alumno, materia])
    db.commit()

    db.refresh(alumno)
    db.refresh(materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.delete(
        f"/calificaciones/{calificacion.id}"
    )

    assert response.status_code == 403

# ============================================================
# PERMISOS GENERALES
# ============================================================

def test_crear_calificacion_sin_permiso(client, usuario_alumno):
    response = client.post(
        "/calificaciones/",
        json={}
    )

    assert response.status_code == 403


def test_actualizar_calificacion_sin_permiso(client, usuario_alumno):
    response = client.patch(
        "/calificaciones/1",
        json={}
    )

    assert response.status_code == 403


def test_eliminar_calificacion_sin_permiso(client, usuario_alumno):
    response = client.delete(
        "/calificaciones/1"
    )

    assert response.status_code == 403


def test_alumno_no_puede_ver_todas_las_calificaciones(
    client,
    usuario_alumno
):
    response = client.get(
        "/calificaciones/"
    )

    assert response.status_code == 403


def test_alumno_no_puede_ver_detalle_de_todas_las_calificaciones(
    client,
    usuario_alumno
):
    response = client.get(
        "/calificaciones/detalle"
    )

    assert response.status_code == 403


def test_maestro_no_puede_ver_todas_las_calificaciones(
    client,
    usuario_maestro
):
    response = client.get(
        "/calificaciones/"
    )

    assert response.status_code == 403


def test_maestro_no_puede_ver_detalle_de_todas_las_calificaciones(
    client,
    usuario_maestro
):
    response = client.get(
        "/calificaciones/detalle"
    )

    assert response.status_code == 403


# ============================================================
# PERMISOS DE ALUMNO
# ============================================================

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

    asegurar_inscripcion(db, usuario_alumno.id, materia.id)
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

    asegurar_inscripcion(db, otro_alumno.id, materia.id)
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

    asegurar_inscripcion(db, otro_alumno.id, materia.id)
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

    asegurar_inscripcion(db, usuario_alumno.id, materia.id)
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


def test_alumno_puede_ver_sus_mis_calificaciones(
    client,
    db,
    usuario_alumno
):
    materia = Materia(
        nombre="Matematica"
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    asegurar_inscripcion(db, usuario_alumno.id, materia.id)
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
        "/calificaciones/alumno/mis-calificaciones"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["materia"] == "Matematica"
    assert data[0]["nota"] == 8
    assert data[0]["periodo"] == 1


def test_maestro_no_puede_ver_mis_calificaciones(
    client,
    usuario_maestro
):
    response = client.get(
        "/calificaciones/alumno/mis-calificaciones"
    )

    assert response.status_code == 403



def test_alumno_puede_ver_mi_promedio(
    client,
    db,
    usuario_alumno
):
    materia = Materia(
        nombre="Matematica"
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

    asegurar_inscripcion(db, usuario_alumno.id, materia.id)
    calificacion = Calificacion(
        alumno_id=usuario_alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    db.add(calificacion)
    db.commit()

    response = client.get(
        "/calificaciones/alumno/mi-promedio"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["alumno"] == "Juan Perez"
    assert data["promedio"] == 8.0


def test_alumno_sin_calificaciones_no_puede_ver_promedio(
    client,
    db,
    usuario_alumno
):
    materia = Materia(
        nombre="Matematica"
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

    response = client.get(
        "/calificaciones/alumno/mi-promedio"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "No se encontraron calificaciones para el alumno"
    )




def test_maestro_no_puede_ver_mi_promedio(
    client,
    usuario_maestro
):
    response = client.get(
        "/calificaciones/alumno/mi-promedio"
    )

    assert response.status_code == 403


def test_alumno_puede_ver_mis_estadisticas(
    client,
    db,
    usuario_alumno
):
    materia = Materia(
        nombre="Matematica"
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    asegurar_inscripcion(db, usuario_alumno.id, materia.id)
    calificacion_1 = Calificacion(
        alumno_id=usuario_alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=1
    )

    asegurar_inscripcion(db, usuario_alumno.id, materia.id)
    calificacion_2 = Calificacion(
        alumno_id=usuario_alumno.id,
        materia_id=materia.id,
        nota=10,
        periodo=2
    )

    db.add_all([
        calificacion_1,
        calificacion_2
    ])

    db.commit()

    response = client.get(
        "/calificaciones/alumno/mi-estadisticas"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    estadistica = data[0]

    assert estadistica["alumno"] == "Juan Perez"
    assert estadistica["materia"] == "Matematica"
    assert estadistica["periodo_1"] == 8
    assert estadistica["periodo_2"] == 10
    assert estadistica["periodo_3"] is None
    assert estadistica["promedio"] == 9.0


def test_maestro_no_puede_ver_mis_estadisticas(
    client,
    usuario_maestro
):
    response = client.get(
        "/calificaciones/alumno/mi-estadisticas"
    )

    assert response.status_code == 403


# ============================================================
# PERMISOS DE MAESTRO
# ============================================================

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

    asegurar_inscripcion(db, alumno.id, materia.id)
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

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    materia = Materia(
        nombre="Historia",
        maestro=otro_maestro
    )

    db.add_all([
        otro_maestro,
        alumno,
        materia
    ])
    db.commit()
    db.refresh(otro_maestro)
    db.refresh(alumno)
    db.refresh(materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
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

    asegurar_inscripcion(db, alumno.id, materia_maestro.id)
    calificacion_propia = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia_maestro.id,
        nota=8,
        periodo=1
    )

    asegurar_inscripcion(db, alumno.id, materia_otro_maestro.id)
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

    data = response.json()

    assert len(data) == 1
    assert data[0]["materia"] == "Matematica"
    assert data[0]["nota"] == 8


def test_maestro_puede_ver_estadisticas_de_alumno_en_su_materia(
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

    db.add_all([
        alumno,
        materia
    ])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
    db.add_all([
        Calificacion(
            alumno_id=alumno.id,
            materia_id=materia.id,
            nota=8,
            periodo=1
        ),
        Calificacion(
            alumno_id=alumno.id,
            materia_id=materia.id,
            nota=10,
            periodo=2
        )
    ])

    db.commit()

    response = client.get(
        f"/calificaciones/alumno/{alumno.id}/estadisticas"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    estadistica = data[0]

    assert estadistica["alumno"] == "Pedro Gomez"
    assert estadistica["materia"] == "Matematica"
    assert estadistica["periodo_1"] == 8
    assert estadistica["periodo_2"] == 10
    assert estadistica["periodo_3"] is None
    assert estadistica["promedio"] == 9.0


def test_maestro_no_puede_ver_estadisticas_de_materia_de_otro_maestro(
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

    materia = Materia(
        nombre="Historia",
        maestro=otro_maestro
    )

    db.add_all([
        otro_maestro,
        alumno,
        materia
    ])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
    db.add(
        Calificacion(
            alumno_id=alumno.id,
            materia_id=materia.id,
            nota=9,
            periodo=1
        )
    )

    db.commit()

    response = client.get(
        f"/calificaciones/alumno/{alumno.id}/estadisticas"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "No se encontraron calificaciones para el alumno"
    }



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

    materia = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([
        otro_maestro,
        materia,
        alumno
    ])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        materia_id=materia.id,
    )

    db.add(inscripcion)
    db.commit()

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

    db.add_all([
        materia,
        alumno
    ])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        materia_id=materia.id,
    )

    db.add(inscripcion)
    db.commit()

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



def test_maestro_puede_ver_sus_mis_calificaciones(
    client,
    db
):
    maestro = Usuario(
        nombre="Carlos",
        email="carlos@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    otro_maestro = Usuario(
        nombre="Pedro",
        email="pedro@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add_all([
        maestro,
        otro_maestro
    ])
    db.commit()
    db.refresh(maestro)
    db.refresh(otro_maestro)

    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    materia_propia = Materia(
        nombre="Matematica",
        maestro_id=maestro.id
    )

    materia_ajena = Materia(
        nombre="Historia",
        maestro_id=otro_maestro.id
    )

    db.add_all([
        alumno,
        materia_propia,
        materia_ajena
    ])
    db.commit()

    asegurar_inscripcion(db, alumno.id, materia_propia.id)
    asegurar_inscripcion(db, alumno.id, materia_ajena.id)
    db.add_all([
        Calificacion(
            alumno_id=alumno.id,
            materia_id=materia_propia.id,
            nota=10,
            periodo=1
        ),
        Calificacion(
            alumno_id=alumno.id,
            materia_id=materia_ajena.id,
            nota=5,
            periodo=1
        )
    ])

    db.commit()

    def usuario_maestro_override():
        return {
            "id": maestro.id,
            "rol": Rol.MAESTRO
        }

    app.dependency_overrides[
        get_usuario_actual
    ] = usuario_maestro_override

    response = client.get(
        "/calificaciones/maestro/mis-calificaciones"
    )

    app.dependency_overrides.pop(
        get_usuario_actual,
        None
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["materia"] == "Matematica"
    assert data[0]["nota"] == 10
    assert data[0]["periodo"] == 1


def test_maestro_sin_materias_obtiene_lista_vacia(
    client,
    db
):
    maestro = Usuario(
        nombre="Carlos",
        email="carlos@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(maestro)
    db.commit()
    db.refresh(maestro)

    def usuario_maestro_override():
        return {
            "id": maestro.id,
            "rol": Rol.MAESTRO
        }

    app.dependency_overrides[
        get_usuario_actual
    ] = usuario_maestro_override

    response = client.get(
        "/calificaciones/maestro/mis-calificaciones"
    )

    app.dependency_overrides.pop(
        get_usuario_actual,
        None
    )

    assert response.status_code == 200
    assert response.json() == []


def test_alumno_no_puede_ver_calificaciones_del_maestro(
    client,
    db
):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    usuario = Usuario(
        nombre="Juan",
        email="juan@test.com",
        password_hash="hash",
        rol=Rol.ALUMNO,
        alumno_id=alumno.id
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    def usuario_alumno_override():
        return {
            "id": usuario.id,
            "rol": Rol.ALUMNO,
            "alumno_id": alumno.id
        }

    app.dependency_overrides[
        get_usuario_actual
    ] = usuario_alumno_override

    response = client.get(
        "/calificaciones/maestro/mis-calificaciones"
    )

    app.dependency_overrides.pop(
        get_usuario_actual,
        None
    )

    assert response.status_code == 403


# ============================================================
# MODIFICACIÓN POR MAESTRO
# ============================================================

def test_modificar_calificacion_a_otra_materia_suya(
    db,
    client,
    usuario_maestro
):
    alumno = Alumno(
        nombre="Kevin",
        apellido="Baez",
        edad=25
    )

    materia = Materia(
        nombre="Matematica",
        maestro=usuario_maestro
    )

    otra_materia = Materia(
        nombre="Fisica",
        maestro=usuario_maestro
    )

    db.add_all([
        alumno,
        materia,
        otra_materia
    ])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)
    db.refresh(otra_materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
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
        json={"materia_id": otra_materia.id}
    )

    assert response.status_code == 403


def test_modificar_calificacion_de_materia_sin_maestro(
    db,
    client,
    usuario_maestro
):
    alumno = Alumno(
        nombre="Kevin",
        apellido="Baez",
        edad=25
    )

    materia = Materia(
        nombre="Matematica"
    )

    db.add_all([
        alumno,
        materia
    ])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
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

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "No tiene permiso para modificar esta calificacion"
    )


# ============================================================
# ELIMINACIÓN POR MAESTRO
# ============================================================

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

    db.add_all([
        alumno,
        materia
    ])
    db.commit()
    db.refresh(alumno)
    db.refresh(materia)

    asegurar_inscripcion(db, alumno.id, materia.id)
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

    assert db.query(Calificacion).filter(
        Calificacion.id == calificacion_id
    ).first() is not None


# ============================================================
# PERMISOS DE ADMIN
# ============================================================

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

    db.add_all([
        alumno1,
        alumno2,
        materia
    ])
    db.commit()

    asegurar_inscripcion(db, alumno1.id, materia.id)
    asegurar_inscripcion(db, alumno2.id, materia.id)
    db.add_all([
        Calificacion(
            alumno_id=alumno1.id,
            materia_id=materia.id,
            nota=8,
            periodo=1
        ),
        Calificacion(
            alumno_id=alumno2.id,
            materia_id=materia.id,
            nota=9,
            periodo=1
        )
    ])

    db.commit()

    response = client.get(
        "/calificaciones/"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


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

    db.add_all([
        alumno,
        materia
    ])
    db.commit()

    asegurar_inscripcion(db, alumno.id, materia.id)
    db.add(
        Calificacion(
            alumno_id=alumno.id,
            materia_id=materia.id,
            nota=8,
            periodo=1
        )
    )

    db.commit()

    response = client.get(
        "/calificaciones/detalle"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["alumno"] == "Carlos Gomez"
    assert data[0]["materia"] == "Matematica"
    assert data[0]["nota"] == 8
    assert data[0]["periodo"] == 1



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

    materia = Materia(
        nombre="Historia",
        maestro=otro_maestro
    )

    alumno = Alumno(
        nombre="Carlos",
        apellido="Gomez",
        edad=20
    )

    db.add_all([
        otro_maestro,
        materia,
        alumno
    ])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        materia_id=materia.id,
    )

    db.add(inscripcion)
    db.commit()

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

    db.add_all([
        otro_maestro,
        materia,
        alumno
    ])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    asegurar_inscripcion(db, alumno.id, materia.id)
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
        json={"nota": 9}
    )

    assert response.status_code == 200
    assert response.json()["nota"] == 9


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

    db.add_all([
        otro_maestro,
        materia,
        alumno
    ])
    db.commit()
    db.refresh(materia)
    db.refresh(alumno)

    asegurar_inscripcion(db, alumno.id, materia.id)
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

    assert db.query(Calificacion).filter(
        Calificacion.id == calificacion_id
    ).first() is None


# ============================================================
# SERVICE: AUTORIZACIÓN DE RECURSO
# ============================================================

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

    asegurar_inscripcion(db, alumno.id, materia.id)
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







def test_maestro_no_puede_cambiar_alumno_de_una_calificacion(
    client,
    db,
    usuario_maestro,
):
    alumno_original = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20,
    )

    alumno_nuevo = Alumno(
        nombre="Pedro",
        apellido="Gomez",
        edad=21,
    )

    db.add_all([alumno_original, alumno_nuevo])
    db.commit()
    db.refresh(alumno_original)
    db.refresh(alumno_nuevo)

    materia = Materia(
        nombre="Matematica",
        maestro_id=usuario_maestro.id,
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    asegurar_inscripcion(db, alumno_original.id, materia.id)
    calificacion = Calificacion(
        alumno_id=alumno_original.id,
        materia_id=materia.id,
        nota=7,
        periodo=1,
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    response = client.patch(
        f"/calificaciones/{calificacion.id}",
        json={
            "alumno_id": alumno_nuevo.id,
        },
    )

    assert response.status_code == 403