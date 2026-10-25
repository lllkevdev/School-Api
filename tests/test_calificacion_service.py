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
from schemas.calificacion import CalificacionActualizar, CalificacionCrear
from schemas.roles import Rol
from services.calificacion_service import (
    actualizar_calificacion,
    crear_calificacion,
    eliminar_calificacion,
    generar_csv_calificaciones,
    listar_calificaciones,
    listar_calificaciones_alumno,
    obtener_historial_alumno,
    obtener_promedio_alumno,
    obtener_promedio_por_curso,
)


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_listar_calificaciones_alumno():
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
            nota=8.5,
        )
        db.add(cal)
        db.commit()

        calificaciones = listar_calificaciones_alumno(db, alumno.id)
        assert len(calificaciones) == 1

    engine.dispose()


def test_obtener_historial_alumno():
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
            nota=7.0,
        )
        db.add(cal)
        db.commit()

        historial = obtener_historial_alumno(db, alumno.id)
        assert len(historial) == 1

    engine.dispose()


def test_obtener_promedio_alumno_sin_calificaciones():
    engine = crear_db_test()

    with Session(engine) as db:
        promedio, error = obtener_promedio_alumno(db, 999)
        assert promedio is None
        assert error == "calificaciones"

    engine.dispose()


def test_obtener_promedio_alumno_exitoso():
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

        eval1 = Evaluacion(
            curso_id=curso.id,
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        eval2 = Evaluacion(
            curso_id=curso.id,
            titulo="P2",
            fecha=date(2026, 6, 1),
            periodo=1,
        )
        db.add_all([eval1, eval2])
        db.commit()

        cal1 = Calificacion(alumno_id=alumno.id, evaluacion_id=eval1.id, curso_id=curso.id, nota=8.0)
        cal2 = Calificacion(alumno_id=alumno.id, evaluacion_id=eval2.id, curso_id=curso.id, nota=10.0)
        db.add_all([cal1, cal2])
        db.commit()

        promedio, error = obtener_promedio_alumno(db, alumno.id)
        assert error is None
        assert promedio == 9.0

    engine.dispose()


def test_obtener_promedio_por_curso_exitoso():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        cal = Calificacion(alumno_id=alumno.id, evaluacion_id=eval.id, curso_id=curso.id, nota=7.5)
        db.add(cal)
        db.commit()

        promedio, error = obtener_promedio_por_curso(db, curso.id, docente)
        assert error is None
        assert promedio == 7.5

    engine.dispose()


def test_generar_csv_calificaciones():
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
            nombre="Juan",
            apellido="Perez",
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        cal = Calificacion(alumno_id=alumno.id, evaluacion_id=eval.id, curso_id=curso.id, nota=8.0)
        db.add(cal)
        db.commit()

        csv = generar_csv_calificaciones(db, curso.id, docente)
        assert csv is not None
        assert "alumno_id,nombre,apellido,evaluacion_id,nota,curso_id" in csv
        assert "Juan" in csv

    engine.dispose()


def test_crear_calificacion_exitoso():
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
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        datos = CalificacionCrear(alumno_id=alumno.id, evaluacion_id=eval.id, nota=9.0)
        calificacion, error = crear_calificacion(db, datos, docente)
        assert error is None
        assert calificacion is not None
        assert calificacion.curso_id == curso.id

    engine.dispose()


def test_crear_calificacion_evaluacion_inexistente():
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

        datos = CalificacionCrear(alumno_id=alumno.id, evaluacion_id=999, nota=9.0)
        calificacion, error = crear_calificacion(db, datos, docente)
        assert calificacion is None
        assert error == "evaluacion_inexistente"

    engine.dispose()


def test_crear_calificacion_curso_inactivo():
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

        ins = Inscripcion(alumno_id=alumno.id, curso_id=curso.id)
        db.add(ins)
        db.commit()

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        datos = CalificacionCrear(alumno_id=alumno.id, evaluacion_id=eval.id, nota=9.0)
        calificacion, error = crear_calificacion(db, datos, docente)
        assert calificacion is None
        assert error == "curso_inactivo"

    engine.dispose()


def test_crear_calificacion_alumno_no_inscripto():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        datos = CalificacionCrear(alumno_id=alumno.id, evaluacion_id=eval.id, nota=9.0)
        calificacion, error = crear_calificacion(db, datos, docente)
        assert calificacion is None
        assert error == "alumno_no_inscripto"

    engine.dispose()


def test_crear_calificacion_duplicada():
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
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        datos = CalificacionCrear(alumno_id=alumno.id, evaluacion_id=eval.id, nota=9.0)
        crear_calificacion(db, datos, docente)
        calificacion, error = crear_calificacion(db, datos, docente)
        assert calificacion is None
        assert error == "calificacion_duplicada"

    engine.dispose()


def test_actualizar_calificacion_exitoso():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        cal = Calificacion(alumno_id=alumno.id, evaluacion_id=eval.id, curso_id=curso.id, nota=7.0)
        db.add(cal)
        db.commit()

        datos = CalificacionActualizar(nota=9.5)
        actualizado, error = actualizar_calificacion(db, cal.id, datos, docente)
        assert error is None
        assert actualizado.nota == 9.5

    engine.dispose()


def test_listar_calificaciones_por_curso():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        cal = Calificacion(alumno_id=alumno.id, evaluacion_id=eval.id, curso_id=curso.id, nota=7.0)
        db.add(cal)
        db.commit()

        calificaciones, error = listar_calificaciones(db, curso.id, docente)
        assert error is None
        assert calificaciones is not None
        assert len(calificaciones) == 1

    engine.dispose()


def test_eliminar_calificacion_exitoso():
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

        eval = Evaluacion(
            curso_id=curso.id,
            titulo="P1",
            fecha=date(2026, 5, 1),
            periodo=1,
        )
        db.add(eval)
        db.commit()

        cal = Calificacion(alumno_id=alumno.id, evaluacion_id=eval.id, curso_id=curso.id, nota=7.0)
        db.add(cal)
        db.commit()

        eliminado, error = eliminar_calificacion(db, cal.id, docente)
        assert eliminado is True
        assert error is None

    engine.dispose()
