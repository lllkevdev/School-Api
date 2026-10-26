from datetime import date, datetime, timedelta, timezone

from core.security import hash_password
from models.alumno import Alumno
from models.curso import Curso
from models.evaluacion import Evaluacion
from models.inscripcion import Inscripcion
from models.invitacion import Invitacion
from models.usuario import Usuario
from schemas.roles import Rol


def crear_curso(db, docente, nombre_materia="Matematica", activo=True):
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


def crear_otro_docente(db):
    docente = Usuario(
        nombre="Otro",
        email="otro.curso@test.com",
        password_hash=hash_password("123456"),
        rol=Rol.ADMIN,
        activo=True,
    )
    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente


def crear_alumno(db):
    alumno = Alumno(
        nombre="Alumno",
        apellido="Curso",
        documento_identidad="55667788",
        fecha_nacimiento=date(2005, 1, 1),
        activo=True,
    )
    db.add(alumno)
    db.commit()
    db.refresh(alumno)
    return alumno


def test_actualizar_curso(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin)

    respuesta = client.patch(
        f"/cursos/{curso.id}",
        headers=auth_headers_admin,
        json={
            "nombre_materia": "  Fisica  ",
            "division": "  B  ",
            "cantidad_periodos": 4,
        },
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["nombre_materia"] == "Fisica"
    assert datos["division"] == "B"
    assert datos["cantidad_periodos"] == 4

    db.refresh(curso)
    assert curso.nombre_materia == "Fisica"
    assert curso.division == "B"
    assert curso.cantidad_periodos == 4


def test_actualizar_curso_ajeno(client, auth_headers_admin, db):
    otro = crear_otro_docente(db)
    curso = crear_curso(db, otro)

    respuesta = client.patch(
        f"/cursos/{curso.id}",
        headers=auth_headers_admin,
        json={"nombre_materia": "Fisica"},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Curso no encontrado"


def test_archivar_y_reactivar_curso(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin)

    archivado = client.patch(
        f"/cursos/{curso.id}/archivar",
        headers=auth_headers_admin,
    )

    assert archivado.status_code == 200
    assert archivado.json()["activo"] is False
    db.refresh(curso)
    assert curso.activo is False

    reactivado = client.patch(
        f"/cursos/{curso.id}/reactivar",
        headers=auth_headers_admin,
    )

    assert reactivado.status_code == 200
    assert reactivado.json()["activo"] is True
    db.refresh(curso)
    assert curso.activo is True


def test_archivar_curso_ya_archivado(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin, activo=False)

    respuesta = client.patch(
        f"/cursos/{curso.id}/archivar",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El curso está inactivo"


def test_reactivar_curso_activo(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin)

    respuesta = client.patch(
        f"/cursos/{curso.id}/reactivar",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El curso ya está activo"


def test_archivar_curso_ajeno(client, auth_headers_admin, db):
    otro = crear_otro_docente(db)
    curso = crear_curso(db, otro)

    respuesta = client.patch(
        f"/cursos/{curso.id}/archivar",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Curso no encontrado"


def test_alumno_no_puede_archivar_curso(client, auth_headers_alumno, db):
    otro = crear_otro_docente(db)
    curso = crear_curso(db, otro)

    respuesta = client.patch(
        f"/cursos/{curso.id}/archivar",
        headers=auth_headers_alumno,
    )

    assert respuesta.status_code == 403


def test_eliminar_curso_vacio(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin)

    respuesta = client.delete(
        f"/cursos/{curso.id}",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 204
    assert db.get(Curso, curso.id) is None


def test_eliminar_curso_con_inscripciones(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin)
    alumno = crear_alumno(db)
    db.add(Inscripcion(alumno_id=alumno.id, curso_id=curso.id))
    db.commit()

    respuesta = client.delete(
        f"/cursos/{curso.id}",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert "inscripciones" in respuesta.json()["detail"]


def test_eliminar_curso_con_evaluaciones(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin)
    db.add(
        Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
    )
    db.commit()

    respuesta = client.delete(
        f"/cursos/{curso.id}",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert "evaluaciones" in respuesta.json()["detail"]


def test_eliminar_curso_con_invitaciones(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin)
    alumno = crear_alumno(db)
    db.add(
        Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=usuario_admin.id,
            email="invitado@test.com",
            token_hash="hash-curso-con-invitacion",
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
        )
    )
    db.commit()

    respuesta = client.delete(
        f"/cursos/{curso.id}",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert "invitaciones" in respuesta.json()["detail"]
