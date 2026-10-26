from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.security import hash_password
from models.alumno import Alumno
from models.curso import Curso
from models.inscripcion import Inscripcion
from models.usuario import Usuario
from schemas.alumno import AlumnoConInscripcionCrear
from schemas.roles import Rol
from services.alumno_service import crear_alumno_con_inscripcion


def crear_curso(
    db: Session,
    docente: Usuario,
    nombre_materia: str = "Matemática",
    activo: bool = True,
) -> Curso:
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


def crear_alumno(
    db: Session,
    documento_identidad: str = "40111222",
    nombre: str = "Sofía",
    activo: bool = True,
) -> Alumno:
    alumno = Alumno(
        nombre=nombre,
        apellido="Pérez",
        documento_identidad=documento_identidad,
        fecha_nacimiento=date(2009, 3, 10),
        activo=activo,
    )
    db.add(alumno)
    db.commit()
    db.refresh(alumno)
    return alumno


def datos_alta(
    curso: Curso,
    documento_identidad: str = "40111222",
    nombre: str = "Sofía",
    confirmar_existente: bool = False,
) -> dict:
    return {
        "nombre": nombre,
        "apellido": "Pérez",
        "documento_identidad": documento_identidad,
        "fecha_nacimiento": "2009-03-10",
        "curso_id": curso.id,
        "confirmar_existente": confirmar_existente,
    }


def test_alta_crea_alumno_e_inscripcion(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    curso = crear_curso(db, usuario_admin)

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        json=datos_alta(curso),
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 201

    datos = respuesta.json()

    assert datos["requiere_confirmacion"] is False
    assert datos["alumno"]["documento_identidad"] == "40111222"
    assert datos["inscripcion"]["curso_id"] == curso.id

    alumno = db.scalar(
        select(Alumno).where(
            Alumno.documento_identidad == "40111222",
        )
    )
    inscripcion = db.scalar(
        select(Inscripcion).where(
            Inscripcion.alumno_id == alumno.id,
            Inscripcion.curso_id == curso.id,
        )
    )

    assert alumno is not None
    assert inscripcion is not None


def test_alta_con_documento_existente_requiere_confirmacion(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    curso = crear_curso(db, usuario_admin)
    alumno = crear_alumno(db, nombre="Original")

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        json=datos_alta(curso, nombre="Distinto"),
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["requiere_confirmacion"] is True
    assert datos["inscripcion"] is None
    assert datos["alumno"]["id"] == alumno.id
    assert datos["alumno"]["nombre"] == "Original"

    db.refresh(alumno)

    assert alumno.nombre == "Original"
    assert db.scalar(
        select(Inscripcion).where(
            Inscripcion.alumno_id == alumno.id,
            Inscripcion.curso_id == curso.id,
        )
    ) is None


def test_alta_confirmada_inscribe_alumno_existente_sin_modificarlo(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    curso = crear_curso(db, usuario_admin)
    alumno = crear_alumno(db, nombre="Original")

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        json=datos_alta(
            curso,
            nombre="Distinto",
            confirmar_existente=True,
        ),
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 201

    datos = respuesta.json()

    assert datos["requiere_confirmacion"] is False
    assert datos["alumno"]["id"] == alumno.id
    assert datos["alumno"]["nombre"] == "Original"
    assert datos["inscripcion"]["alumno_id"] == alumno.id
    assert datos["inscripcion"]["curso_id"] == curso.id

    db.refresh(alumno)

    assert alumno.nombre == "Original"


def test_alta_rechaza_inscripcion_duplicada(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    curso = crear_curso(db, usuario_admin)
    alumno = crear_alumno(db)

    db.add(
        Inscripcion(
            alumno_id=alumno.id,
            curso_id=curso.id,
        )
    )
    db.commit()

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        json=datos_alta(curso),
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        "El alumno ya está inscripto en el curso"
    )


def test_alta_rechaza_alumno_inactivo(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    curso = crear_curso(db, usuario_admin)
    alumno = crear_alumno(db, activo=False)

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        json=datos_alta(curso),
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        "El alumno ya está desactivado"
    )

    assert db.scalar(
        select(Inscripcion).where(
            Inscripcion.alumno_id == alumno.id,
        )
    ) is None


def test_alta_rechaza_curso_de_otro_docente(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    otro_docente = Usuario(
        nombre="Otro",
        email="otro@test.com",
        password_hash=hash_password("123456"),
        rol=Rol.ADMIN,
        activo=True,
    )
    db.add(otro_docente)
    db.commit()
    db.refresh(otro_docente)

    curso_ajeno = crear_curso(db, otro_docente, "Historia")

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        json=datos_alta(curso_ajeno),
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Curso no encontrado"

    assert db.scalar(
        select(Alumno).where(
            Alumno.documento_identidad == "40111222",
        )
    ) is None


def test_alta_rechaza_curso_inactivo(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
):
    curso = crear_curso(db, usuario_admin, activo=False)

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        json=datos_alta(curso),
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El curso está inactivo"

    assert db.scalar(
        select(Alumno).where(
            Alumno.documento_identidad == "40111222",
        )
    ) is None


def test_alta_rechaza_alumno(
    client,
    db,
    usuario_admin,
    auth_headers_alumno,
):
    curso = crear_curso(db, usuario_admin)

    respuesta = client.post(
        "/alumnos/con-inscripcion",
        json=datos_alta(curso),
        headers=auth_headers_alumno,
    )

    assert respuesta.status_code == 403


def test_alta_hace_rollback_si_falla_la_transaccion(
    db,
    usuario_admin,
    monkeypatch,
):
    curso = crear_curso(db, usuario_admin)
    datos = AlumnoConInscripcionCrear(
        **datos_alta(curso),
    )

    def commit_fallido(self):
        raise IntegrityError(
            "INSERT INTO alumnos",
            {},
            Exception("fallo simulado"),
        )

    monkeypatch.setattr(Session, "commit", commit_fallido)

    with pytest.raises(IntegrityError):
        crear_alumno_con_inscripcion(db, datos, usuario_admin)

    monkeypatch.undo()

    assert db.scalar(
        select(Alumno).where(
            Alumno.documento_identidad == "40111222",
        )
    ) is None
    assert db.scalar(
        select(Inscripcion).where(
            Inscripcion.curso_id == curso.id,
        )
    ) is None
