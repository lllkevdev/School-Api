from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from datetime import date

from database.connection import Base
from models.curso import Curso
from models.usuario import Usuario
from models.alumno import Alumno
from models.inscripcion import Inscripcion
from models.evaluacion import Evaluacion
from models.calificacion import Calificacion
from schemas.inscripcion import InscripcionCrear
from schemas.roles import Rol
from services.inscripcion_service import (
    crear_inscripcion,
    eliminar_inscripcion,
    listar_inscripciones_por_alumno,
    listar_inscripciones_por_curso,
)


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_listar_inscripciones_por_alumno():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        curso = Curso(
            docente_id=docente.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add(curso)
        db.commit()

        ins = Inscripcion(alumno_id=alumno.id, curso_id=curso.id)
        db.add(ins)
        db.commit()

        inscripciones = listar_inscripciones_por_alumno(db, alumno.id)
        assert len(inscripciones) == 1

    engine.dispose()


def test_crear_inscripcion_exitoso():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        curso = Curso(
            docente_id=docente.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add(curso)
        db.commit()

        datos = InscripcionCrear(alumno_id=alumno.id, curso_id=curso.id)
        inscripcion, error = crear_inscripcion(db, datos, docente)
        assert error is None
        assert inscripcion is not None

    engine.dispose()


def test_crear_inscripcion_alumno_inexistente():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        curso = Curso(
            docente_id=docente.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add(curso)
        db.commit()

        datos = InscripcionCrear(alumno_id=999, curso_id=curso.id)
        inscripcion, error = crear_inscripcion(db, datos, docente)
        assert inscripcion is None
        assert error == "alumno_inexistente"

    engine.dispose()


def test_crear_inscripcion_curso_inexistente():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        datos = InscripcionCrear(alumno_id=alumno.id, curso_id=999)
        inscripcion, error = crear_inscripcion(db, datos, docente)
        assert inscripcion is None
        assert error == "curso_inexistente"

    engine.dispose()


def test_crear_inscripcion_curso_inactivo():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        curso = Curso(
            docente_id=docente.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=False,
        )
        db.add(curso)
        db.commit()

        datos = InscripcionCrear(alumno_id=alumno.id, curso_id=curso.id)
        inscripcion, error = crear_inscripcion(db, datos, docente)
        assert inscripcion is None
        assert error == "curso_inactivo"

    engine.dispose()


def test_crear_inscripcion_duplicada():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        curso = Curso(
            docente_id=docente.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add(curso)
        db.commit()

        datos = InscripcionCrear(alumno_id=alumno.id, curso_id=curso.id)
        crear_inscripcion(db, datos, docente)
        inscripcion, error = crear_inscripcion(db, datos, docente)
        assert inscripcion is None
        assert error == "inscripcion_duplicada"

    engine.dispose()


def test_listar_inscripciones_por_curso():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        curso = Curso(
            docente_id=docente.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add(curso)
        db.commit()

        ins = Inscripcion(alumno_id=alumno.id, curso_id=curso.id)
        db.add(ins)
        db.commit()

        inscripciones, error = listar_inscripciones_por_curso(db, curso.id, docente)
        assert error is None
        assert inscripciones is not None
        assert len(inscripciones) == 1

    engine.dispose()


def test_eliminar_inscripcion_exitoso():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        curso = Curso(
            docente_id=docente.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add(curso)
        db.commit()

        ins = Inscripcion(alumno_id=alumno.id, curso_id=curso.id)
        db.add(ins)
        db.commit()

        eliminado, error = eliminar_inscripcion(db, ins.id, docente)
        assert eliminado is True
        assert error is None

    engine.dispose()


def test_eliminar_inscripcion_con_calificaciones():
    engine = crear_db_test()

    with Session(engine) as db:
        docente = Usuario(
            nombre="Doc",
            email="d@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(docente)
        db.commit()

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        curso = Curso(
            docente_id=docente.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add(curso)
        db.commit()

        ins = Inscripcion(alumno_id=alumno.id, curso_id=curso.id)
        db.add(ins)
        db.commit()

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        cal = Calificacion(
            alumno_id=alumno.id,
            evaluacion_id=eval.id,
            curso_id=curso.id,
            nota=8.0,
        )
        db.add(cal)
        db.commit()

        eliminado, error = eliminar_inscripcion(db, ins.id, docente)
        assert eliminado is False
        assert error == "inscripcion_con_calificaciones"

    engine.dispose()
