from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database.connection import Base
from models.curso import Curso
from models.usuario import Usuario
from schemas.roles import Rol
from schemas.curso import CursoCrear
from services.curso_service import crear_curso


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_crear_curso_asigna_docente_y_guarda_datos():
    engine = crear_db_test()

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Docente",
            email="docente@test.com",
            password_hash="hash_de_prueba",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        datos = CursoCrear(
            nombre_materia="Matemática",
            division="2° A",
            anio_lectivo=2026,
        )

        curso, error = crear_curso(db, datos, usuario)

        assert error is None
        assert curso is not None
        assert curso.id is not None
        assert curso.docente_id == usuario.id
        assert curso.nombre_materia == "Matemática"
        assert curso.division == "2° A"
        assert curso.anio_lectivo == 2026
        assert curso.cantidad_periodos == 3
        assert curso.activo is True

    engine.dispose()


def test_crear_curso_elimina_espacios_exteriores():
    engine = crear_db_test()

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Docente",
            email="docente@test.com",
            password_hash="hash_de_prueba",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        datos = CursoCrear(
            nombre_materia="  Matemática  ",
            division="  2° A  ",
            anio_lectivo=2026,
        )

        curso, error = crear_curso(db, datos, usuario)

        assert error is None
        assert curso is not None
        assert curso.nombre_materia == "Matemática"
        assert curso.division == "2° A"

    engine.dispose()