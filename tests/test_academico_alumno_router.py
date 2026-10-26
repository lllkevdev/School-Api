from datetime import date

from core.security import hash_password
from models.alumno import Alumno
from models.calificacion import Calificacion
from models.curso import Curso
from models.evaluacion import Evaluacion
from models.inscripcion import Inscripcion
from models.usuario import Usuario
from schemas.roles import Rol


def crear_curso(db, docente, nombre_materia, activo=True):
    curso = Curso(
        docente_id=docente.id,
        nombre_materia=nombre_materia,
        division="A",
        anio_lectivo=2026,
        cantidad_periodos=3,
        activo=activo,
    )
    db.add(curso)
    db.commit()
    db.refresh(curso)
    return curso


def crear_evaluacion(db, curso, titulo, fecha, periodo=1):
    evaluacion = Evaluacion(
        curso_id=curso.id,
        titulo=titulo,
        fecha=fecha,
        periodo=periodo,
    )
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)
    return evaluacion


def inscribir(db, alumno, curso):
    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        curso_id=curso.id,
    )
    db.add(inscripcion)
    db.commit()
    db.refresh(inscripcion)
    return inscripcion


def calificar(db, alumno, evaluacion, curso, nota):
    calificacion = Calificacion(
        alumno_id=alumno.id,
        evaluacion_id=evaluacion.id,
        curso_id=curso.id,
        nota=nota,
    )
    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)
    return calificacion


def crear_otro_docente(db):
    docente = Usuario(
        nombre="Otro",
        email="otro.docente@test.com",
        password_hash=hash_password("123456"),
        rol=Rol.ADMIN,
        activo=True,
    )
    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente


def test_mis_evaluaciones_solo_cursos_del_alumno(
    client,
    db,
    usuario_admin,
    usuario_alumno,
    auth_headers_alumno,
):
    otro_docente = crear_otro_docente(db)
    curso_propio = crear_curso(db, usuario_admin, "Matemática")
    curso_ajeno = crear_curso(db, otro_docente, "Historia")

    inscribir(db, usuario_alumno, curso_propio)

    evaluacion_propia = crear_evaluacion(
        db,
        curso_propio,
        "Parcial de Matemática",
        date(2026, 5, 10),
    )
    crear_evaluacion(
        db,
        curso_ajeno,
        "Parcial de Historia",
        date(2026, 5, 11),
    )

    respuesta = client.get(
        "/evaluaciones/mis-evaluaciones",
        headers=auth_headers_alumno,
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert len(datos) == 1
    assert datos[0]["id"] == evaluacion_propia.id
    assert datos[0]["titulo"] == "Parcial de Matemática"
    assert datos[0]["curso"]["id"] == curso_propio.id
    assert datos[0]["curso"]["nombre_materia"] == "Matemática"
    assert datos[0]["curso"]["division"] == "A"
    assert datos[0]["curso"]["anio_lectivo"] == 2026


def test_mis_evaluaciones_sin_cursos(
    client,
    usuario_alumno,
    auth_headers_alumno,
):
    respuesta = client.get(
        "/evaluaciones/mis-evaluaciones",
        headers=auth_headers_alumno,
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_mis_evaluaciones_sin_token(client):
    respuesta = client.get("/evaluaciones/mis-evaluaciones")

    assert respuesta.status_code == 401


def test_mis_evaluaciones_rechaza_docente(
    client,
    auth_headers_admin,
):
    respuesta = client.get(
        "/evaluaciones/mis-evaluaciones",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 401


def test_mis_calificaciones_incluye_curso_y_evaluacion(
    client,
    db,
    usuario_admin,
    usuario_alumno,
    auth_headers_alumno,
):
    curso = crear_curso(db, usuario_admin, "Matemática")
    evaluacion = crear_evaluacion(
        db,
        curso,
        "Parcial 1",
        date(2026, 5, 10),
        periodo=2,
    )

    inscribir(db, usuario_alumno, curso)
    calificacion = calificar(
        db,
        usuario_alumno,
        evaluacion,
        curso,
        8.5,
    )

    respuesta = client.get(
        "/calificaciones/mis-calificaciones",
        headers=auth_headers_alumno,
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert len(datos) == 1
    assert datos[0]["id"] == calificacion.id
    assert datos[0]["nota"] == 8.5
    assert datos[0]["curso"]["id"] == curso.id
    assert datos[0]["curso"]["nombre_materia"] == "Matemática"
    assert datos[0]["evaluacion"]["id"] == evaluacion.id
    assert datos[0]["evaluacion"]["titulo"] == "Parcial 1"
    assert datos[0]["evaluacion"]["fecha"] == "2026-05-10"
    assert datos[0]["evaluacion"]["periodo"] == 2


def test_mis_calificaciones_no_incluye_otros_alumnos(
    client,
    db,
    usuario_admin,
    usuario_alumno,
    auth_headers_alumno,
):
    otro_alumno = Alumno(
        nombre="Otro",
        apellido="Alumno",
        documento_identidad="87654321",
        fecha_nacimiento=date(2005, 1, 1),
        activo=True,
    )
    db.add(otro_alumno)
    db.commit()
    db.refresh(otro_alumno)

    curso = crear_curso(db, usuario_admin, "Matemática")
    evaluacion = crear_evaluacion(
        db,
        curso,
        "Parcial 1",
        date(2026, 5, 10),
    )

    inscribir(db, usuario_alumno, curso)
    inscribir(db, otro_alumno, curso)

    calificar(db, usuario_alumno, evaluacion, curso, 7.0)
    calificar(db, otro_alumno, evaluacion, curso, 10.0)

    respuesta = client.get(
        "/calificaciones/mis-calificaciones",
        headers=auth_headers_alumno,
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert len(datos) == 1
    assert datos[0]["alumno_id"] == usuario_alumno.id
    assert datos[0]["nota"] == 7.0


def test_mis_calificaciones_sin_calificaciones(
    client,
    usuario_alumno,
    auth_headers_alumno,
):
    respuesta = client.get(
        "/calificaciones/mis-calificaciones",
        headers=auth_headers_alumno,
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_mis_calificaciones_sin_token(client):
    respuesta = client.get("/calificaciones/mis-calificaciones")

    assert respuesta.status_code == 401


def test_mis_calificaciones_rechaza_docente(
    client,
    auth_headers_admin,
):
    respuesta = client.get(
        "/calificaciones/mis-calificaciones",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 401
