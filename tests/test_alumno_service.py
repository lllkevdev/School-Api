from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database.connection import Base
from models.alumno import Alumno
from models.curso import Curso
from models.inscripcion import Inscripcion
from models.usuario import Usuario
from schemas.alumno import AlumnoCrear
from schemas.roles import Rol
from services.alumno_service import (
    buscar_alumno,
    crear_alumno,
    desactivar_alumno,
    obtener_alumnos,
)


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_crear_alumno_exitoso():
    engine = crear_db_test()
    from datetime import date

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Docente",
            email="docente@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(usuario)
        db.commit()

        datos = AlumnoCrear(
            nombre="Juan",
            apellido="Perez",
            documento_identidad="ABC12345",
            fecha_nacimiento=date(2005, 1, 1),
        )
        alumno, error = crear_alumno(db, datos, usuario)

        assert error is None
        assert alumno is not None
        assert alumno.id is not None
        assert alumno.nombre == "Juan"
        assert alumno.activo is True

    engine.dispose()


def test_crear_alumno_documento_duplicado():
    engine = crear_db_test()
    from datetime import date

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Docente",
            email="docente@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(usuario)
        db.commit()

        datos = AlumnoCrear(
            nombre="Juan",
            apellido="Perez",
            documento_identidad="ABC12345",
            fecha_nacimiento=date(2005, 1, 1),
        )
        crear_alumno(db, datos, usuario)

        datos2 = AlumnoCrear(
            nombre="Pedro",
            apellido="Lopez",
            documento_identidad="ABC12345",
            fecha_nacimiento=date(2006, 1, 1),
        )
        alumno, error = crear_alumno(db, datos2, usuario)
        assert alumno is None
        assert error == "documento_duplicado"

    engine.dispose()


def test_obtener_alumnos_admin_ve_todos():
    engine = crear_db_test()
    from datetime import date

    with Session(engine) as db:
        docente1 = Usuario(
            nombre="Doc1",
            email="d1@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        docente2 = Usuario(
            nombre="Doc2",
            email="d2@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add_all([docente1, docente2])
        db.commit()

        curso1 = Curso(
            docente_id=docente1.id,
            nombre_materia="Matematica",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        curso2 = Curso(
            docente_id=docente2.id,
            nombre_materia="Historia",
            division="B",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add_all([curso1, curso2])
        db.commit()

        alumno1 = Alumno(
            nombre="A1",
            apellido="X",
            documento_identidad="111",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        alumno2 = Alumno(
            nombre="A2",
            apellido="Y",
            documento_identidad="222",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add_all([alumno1, alumno2])
        db.commit()

        ins1 = Inscripcion(alumno_id=alumno1.id, curso_id=curso1.id)
        ins2 = Inscripcion(alumno_id=alumno2.id, curso_id=curso2.id)
        db.add_all([ins1, ins2])
        db.commit()

        alumnos_doc1 = obtener_alumnos(db, docente1)
        assert {alumno.id for alumno in alumnos_doc1} == {
            alumno1.id,
            alumno2.id,
        }

    engine.dispose()


def test_admin_ve_y_desactiva_alumno_sin_inscripcion():
    engine = crear_db_test()
    from datetime import date

    with Session(engine) as db:
        admin = Usuario(
            nombre="Admin",
            email="admin@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(admin)
        db.commit()

        alumno = Alumno(
            nombre="Sin",
            apellido="Curso",
            documento_identidad="333",
            fecha_nacimiento=date(2005, 1, 1),
            activo=True,
        )
        db.add(alumno)
        db.commit()

        alumnos = obtener_alumnos(db, admin)
        assert [item.id for item in alumnos] == [alumno.id]

        encontrado, error = buscar_alumno(db, alumno.id, admin)
        assert error is None
        assert encontrado is not None

        desactivado, error = desactivar_alumno(db, alumno.id, admin)
        assert error is None
        assert desactivado is not None
        assert desactivado.activo is False

    engine.dispose()


def test_buscar_alumno_exitoso():
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

        encontrado, error = buscar_alumno(db, alumno.id, docente)
        assert error is None
        assert encontrado is not None
        assert encontrado.id == alumno.id

    engine.dispose()


def test_buscar_alumno_no_existe():
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

        encontrado, error = buscar_alumno(db, 999, docente)
        assert encontrado is None
        assert error == "alumno_inexistente"

    engine.dispose()


def test_buscar_alumno_sin_permiso():
    engine = crear_db_test()
    from datetime import date

    with Session(engine) as db:
        docente1 = Usuario(
            nombre="Doc1",
            email="d1@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        docente2 = Usuario(
            nombre="Doc2",
            email="d2@test.com",
            password_hash="hash",
            rol=Rol.ALUMNO,
            activo=True,
        )
        db.add_all([docente1, docente2])
        db.commit()

        curso1 = Curso(
            docente_id=docente1.id,
            nombre_materia="Mat",
            division="A",
            anio_lectivo=2026,
            cantidad_periodos=3,
            activo=True,
        )
        db.add(curso1)
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

        ins = Inscripcion(alumno_id=alumno.id, curso_id=curso1.id)
        db.add(ins)
        db.commit()

        encontrado, error = buscar_alumno(db, alumno.id, docente2)
        assert encontrado is None
        assert error == "permiso"

    engine.dispose()


def test_desactivar_alumno_exitoso():
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

        desactivado, error = desactivar_alumno(db, alumno.id, docente)
        assert error is None
        assert desactivado is not None
        assert desactivado.activo is False

    engine.dispose()


def test_desactivar_alumno_ya_inactivo():
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
            activo=False,
        )
        db.add(alumno)
        db.commit()

        ins = Inscripcion(alumno_id=alumno.id, curso_id=curso.id)
        db.add(ins)
        db.commit()

        desactivado, error = desactivar_alumno(db, alumno.id, docente)
        assert desactivado is None
        assert error == "alumno_inactivo"

    engine.dispose()
