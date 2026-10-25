from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database.connection import Base
from models.curso import Curso
from models.evaluacion import Evaluacion
from models.inscripcion import Inscripcion
from models.usuario import Usuario
from models.alumno import Alumno
from schemas.curso import CursoActualizar, CursoCrear
from schemas.roles import Rol
from services.curso_service import (
    actualizar_curso,
    eliminar_curso,
    listar_cursos,
    listar_cursos_por_alumno,
    obtener_curso,
)


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_listar_cursos_por_alumno():
    engine = crear_db_test()
    from datetime import date

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

        cursos = listar_cursos_por_alumno(db, alumno.id)
        assert len(cursos) == 1
        assert cursos[0].id == curso.id

    engine.dispose()


def test_listar_cursos_por_docente():
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

        cursos = listar_cursos(db, docente)
        assert len(cursos) == 1
        assert cursos[0].docente_id == docente.id

    engine.dispose()


def test_obtener_curso_exitoso():
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

        obtenido, error = obtener_curso(db, curso.id, docente)
        assert error is None
        assert obtenido is not None
        assert obtenido.id == curso.id

    engine.dispose()


def test_obtener_curso_inexistente():
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

        obtenido, error = obtener_curso(db, 999, docente)
        assert obtenido is None
        assert error == "curso_inexistente"

    engine.dispose()


def test_actualizar_curso_exitoso():
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

        datos = CursoCrear(
            nombre_materia="Matematica",
            division="A",
            anio_lectivo=2026,
        )
        curso, _ = crear_curso_completo(db, datos, docente)
        datos_act = CursoActualizar(nombre_materia="  Fisica  ", division="  B  ")
        actualizado, error = actualizar_curso(db, curso.id, datos_act, docente)

        assert error is None
        assert actualizado is not None
        assert actualizado.nombre_materia == "Fisica"
        assert actualizado.division == "B"

    engine.dispose()


def crear_curso_completo(db, datos, usuario):
    from services.curso_service import crear_curso

    return crear_curso(db, datos, usuario)


def test_actualizar_curso_sin_cambios():
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

        datos = CursoCrear(
            nombre_materia="Matematica",
            division="A",
            anio_lectivo=2026,
        )
        curso, _ = crear_curso_completo(db, datos, docente)
        datos_act = CursoActualizar()
        actualizado, error = actualizar_curso(db, curso.id, datos_act, docente)

        assert actualizado is None
        assert error == "sin_cambios"

    engine.dispose()


def test_eliminar_curso_exitoso():
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

        datos = CursoCrear(
            nombre_materia="Matematica",
            division="A",
            anio_lectivo=2026,
        )
        curso, _ = crear_curso_completo(db, datos, docente)
        eliminado, error = eliminar_curso(db, curso.id, docente)

        assert eliminado is True
        assert error is None

    engine.dispose()


def test_eliminar_curso_tiene_inscripciones():
    engine = crear_db_test()
    from datetime import date

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

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        ins = Inscripcion(alumno_id=alumno.id, curso_id=curso.id)
        db.add(ins)
        db.commit()

        eliminado, error = eliminar_curso(db, curso.id, docente)
        assert eliminado is False
        assert error == "tiene_inscripciones"

    engine.dispose()


def test_eliminar_curso_tiene_evaluaciones():
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

        from datetime import date as d
        eval = Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=d(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        eliminado, error = eliminar_curso(db, curso.id, docente)
        assert eliminado is False
        assert error == "tiene_evaluaciones"

    engine.dispose()


def test_eliminar_curso_inexistente():
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

        eliminado, error = eliminar_curso(db, 999, docente)
        assert eliminado is False
        assert error == "curso_inexistente"

    engine.dispose()
