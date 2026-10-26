from datetime import date

from core.security import hash_password
from models.alumno import Alumno
from models.curso import Curso
from models.inscripcion import Inscripcion
from models.usuario import Usuario
from schemas.roles import Rol


def crear_curso(db, docente, nombre_materia="Matematica"):
    curso = Curso(
        docente_id=docente.id,
        nombre_materia=nombre_materia,
        division="A",
        anio_lectivo=2026,
        cantidad_periodos=3,
        activo=True,
    )
    db.add(curso)
    db.commit()
    db.refresh(curso)
    return curso


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


def crear_alumno(db, documento_identidad="99887766"):
    alumno = Alumno(
        nombre="Alumno",
        apellido="Nuevo",
        documento_identidad=documento_identidad,
        fecha_nacimiento=date(2005, 3, 15),
        activo=True,
    )
    db.add(alumno)
    db.commit()
    db.refresh(alumno)
    return alumno


def datos_alta(curso, documento_identidad="99887766"):
    return {
        "nombre": "Alumno",
        "apellido": "Nuevo",
        "documento_identidad": documento_identidad,
        "fecha_nacimiento": "2005-03-15",
        "curso_id": curso.id,
    }


def test_admin_puede_listar_alumnos(client, auth_headers_admin):
    respuesta = client.get("/alumnos/", headers=auth_headers_admin)

    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)


def test_alumno_no_puede_listar_alumnos(client, auth_headers_alumno):
    respuesta = client.get("/alumnos/", headers=auth_headers_alumno)

    assert respuesta.status_code == 403


def test_listar_alumnos_sin_token(client):
    respuesta = client.get("/alumnos/")

    assert respuesta.status_code == 401


def test_admin_puede_crear_alumno(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    curso = crear_curso(db, usuario_admin)

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        headers=auth_headers_admin,
        json=datos_alta(curso),
    )

    assert respuesta.status_code == 201

    datos = respuesta.json()

    assert datos["alumno"]["documento_identidad"] == "99887766"
    assert datos["inscripcion"]["curso_id"] == curso.id


def test_alumno_no_puede_crear_alumno(client, auth_headers_alumno):
    respuesta = client.post(
        "/alumnos/con-inscripcion",
        headers=auth_headers_alumno,
        json={
            "nombre": "Alumno",
            "apellido": "Nuevo",
            "documento_identidad": "11223344",
            "fecha_nacimiento": "2005-03-15",
            "curso_id": 1,
        },
    )

    assert respuesta.status_code == 403


def test_alta_global_eliminada(client, auth_headers_admin):
    respuesta = client.post(
        "/alumnos/",
        headers=auth_headers_admin,
        json={
            "nombre": "Alumno",
            "apellido": "Nuevo",
            "documento_identidad": "99887766",
            "fecha_nacimiento": "2005-03-15",
        },
    )

    assert respuesta.status_code == 405


def test_listado_excluye_alumnos_de_cursos_ajenos(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    otro_docente = crear_otro_docente(db)
    curso_ajeno = crear_curso(db, otro_docente, "Historia")
    alumno_ajeno = crear_alumno(db)
    db.add(
        Inscripcion(
            alumno_id=alumno_ajeno.id,
            curso_id=curso_ajeno.id,
        )
    )
    db.commit()

    respuesta = client.get("/alumnos/", headers=auth_headers_admin)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_no_puede_ver_alumno_de_curso_ajeno(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    otro_docente = crear_otro_docente(db)
    curso_ajeno = crear_curso(db, otro_docente, "Historia")
    alumno_ajeno = crear_alumno(db)
    db.add(
        Inscripcion(
            alumno_id=alumno_ajeno.id,
            curso_id=curso_ajeno.id,
        )
    )
    db.commit()

    respuesta = client.get(
        f"/alumnos/{alumno_ajeno.id}",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 403


def test_no_puede_desactivar_alumno_compartido(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    otro_docente = crear_otro_docente(db)
    curso_propio = crear_curso(db, usuario_admin)
    curso_ajeno = crear_curso(db, otro_docente, "Historia")
    alumno = crear_alumno(db)

    db.add_all([
        Inscripcion(alumno_id=alumno.id, curso_id=curso_propio.id),
        Inscripcion(alumno_id=alumno.id, curso_id=curso_ajeno.id),
    ])
    db.commit()

    respuesta = client.patch(
        f"/alumnos/{alumno.id}/desactivar",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert "otro docente" in respuesta.json()["detail"]

    db.refresh(alumno)
    assert alumno.activo is True
