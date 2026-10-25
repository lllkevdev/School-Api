from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from datetime import date

from database.connection import Base
from models.curso import Curso
from models.evaluacion import Evaluacion
from models.calificacion import Calificacion
from models.usuario import Usuario
from models.alumno import Alumno
from schemas.evaluacion import EvaluacionActualizar, EvaluacionCrear
from schemas.roles import Rol
from services.evaluacion_service import (
    actualizar_evaluacion,
    crear_evaluacion,
    eliminar_evaluacion,
    listar_evaluaciones_por_curso,
    obtener_evaluacion,
)


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_crear_evaluacion_exitoso():
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

        datos = EvaluacionCrear(
            curso_id=curso.id,
            titulo="  Parcial 1  ",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        evaluacion, error = crear_evaluacion(db, datos, docente)

        assert error is None
        assert evaluacion is not None
        assert evaluacion.titulo == "Parcial 1"
        assert evaluacion.periodo == 1

    engine.dispose()


def test_crear_evaluacion_curso_inexistente():
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

        datos = EvaluacionCrear(
            curso_id=999,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        evaluacion, error = crear_evaluacion(db, datos, docente)
        assert evaluacion is None
        assert error == "curso_inexistente"

    engine.dispose()


def test_crear_evaluacion_curso_inactivo():
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
            activo=False,
        )
        db.add(curso)
        db.commit()

        datos = EvaluacionCrear(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        evaluacion, error = crear_evaluacion(db, datos, docente)
        assert evaluacion is None
        assert error == "curso_inactivo"

    engine.dispose()


def test_crear_evaluacion_periodo_invalido():
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
            cantidad_periodos=2,
            activo=True,
        )
        db.add(curso)
        db.commit()

        datos = EvaluacionCrear(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=3,
        )
        evaluacion, error = crear_evaluacion(db, datos, docente)
        assert evaluacion is None
        assert error == "periodo_invalido"

    engine.dispose()


def test_listar_evaluaciones_por_curso():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        evaluaciones, error = listar_evaluaciones_por_curso(db, curso.id, docente)
        assert error is None
        assert evaluaciones is not None
        assert len(evaluaciones) == 1

    engine.dispose()


def test_obtener_evaluacion_exitoso():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        evaluacion, error = obtener_evaluacion(db, eval.id, docente)
        assert error is None
        assert evaluacion is not None

    engine.dispose()


def test_actualizar_evaluacion_exitoso():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        datos = EvaluacionActualizar(titulo="  Final  ", periodo=2)
        actualizado, error = actualizar_evaluacion(db, eval.id, datos, docente)
        assert error is None
        assert actualizado.titulo == "Final"
        assert actualizado.periodo == 2

    engine.dispose()


def test_actualizar_evaluacion_sin_cambios():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        datos = EvaluacionActualizar()
        actualizado, error = actualizar_evaluacion(db, eval.id, datos, docente)
        assert actualizado is None
        assert error == "sin_cambios"

    engine.dispose()


def test_actualizar_evaluacion_periodo_invalido():
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
            cantidad_periodos=2,
            activo=True,
        )
        db.add(curso)
        db.commit()

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        datos = EvaluacionActualizar(periodo=3)
        actualizado, error = actualizar_evaluacion(db, eval.id, datos, docente)
        assert actualizado is None
        assert error == "periodo_invalido"

    engine.dispose()


def test_eliminar_evaluacion_exitoso():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="Parcial 1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        eliminado, error = eliminar_evaluacion(db, eval.id, docente)
        assert eliminado is True
        assert error is None

    engine.dispose()


def test_eliminar_evaluacion_tiene_calificaciones():
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

        alumno = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
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

        eliminado, error = eliminar_evaluacion(db, eval.id, docente)
        assert eliminado is False
        assert error == "tiene_calificaciones"

    engine.dispose()
