from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database.connection import Base
from models.usuario import Usuario
from schemas.roles import Rol
from schemas.usuario import UsuarioActualizar, UsuarioCrear, UsuarioRegistro
from services.usuario_service import (
    actualizar_usuario,
    buscar_usuario_por_email,
    crear_usuario,
)


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_buscar_usuario_por_email_encontrado():
    engine = crear_db_test()

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

        encontrado = buscar_usuario_por_email(db, "docente@test.com")
        assert encontrado is not None
        assert encontrado.email == "docente@test.com"

    engine.dispose()


def test_buscar_usuario_por_email_no_encontrado():
    engine = crear_db_test()

    with Session(engine) as db:
        encontrado = buscar_usuario_por_email(db, "noexiste@test.com")
        assert encontrado is None

    engine.dispose()


def test_crear_usuario_con_usuario_crear():
    engine = crear_db_test()

    with Session(engine) as db:
        datos = UsuarioCrear(
            nombre="  Juan  ",
            apellido="  Perez  ",
            email="  JUAN@TEST.COM  ",
            password="password123",
            rol=Rol.ADMIN,
        )
        usuario = crear_usuario(db, datos)

        assert usuario.id is not None
        assert usuario.nombre == "Juan"
        assert usuario.apellido == "Perez"
        assert usuario.email == "juan@test.com"
        assert usuario.rol == Rol.ADMIN
        assert usuario.activo is True

    engine.dispose()


def test_crear_usuario_sin_apellido_asigna_vacio():
    engine = crear_db_test()

    with Session(engine) as db:
        datos = UsuarioCrear(
            nombre="Maria",
            email="maria@test.com",
            password="password123",
        )
        usuario = crear_usuario(db, datos)

        assert usuario.apellido == ""
        assert usuario.rol == Rol.ADMIN

    engine.dispose()


def test_crear_usuario_con_usuario_registro():
    engine = crear_db_test()

    with Session(engine) as db:
        datos = UsuarioRegistro(
            nombre="Ana",
            email="ana@test.com",
            password="password123",
        )
        usuario = crear_usuario(db, datos)
        assert usuario.email == "ana@test.com"

    engine.dispose()


def test_crear_usuario_email_duplicado_lanza_integrity_error():
    engine = crear_db_test()

    with Session(engine) as db:
        datos = UsuarioCrear(
            nombre="Juan",
            email="duplicado@test.com",
            password="password123",
        )
        crear_usuario(db, datos)

        datos2 = UsuarioCrear(
            nombre="Pedro",
            email="duplicado@test.com",
            password="password123",
        )
        try:
            crear_usuario(db, datos2)
            assert False, "Debería haber levantado IntegrityError"
        except IntegrityError:
            pass

    engine.dispose()


def test_actualizar_usuario_exitoso():
    engine = crear_db_test()

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Juan",
            email="juan@test.com",
            password_hash="hash",
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        datos = UsuarioActualizar(nombre="  Pedro  ", email="  PEDRO@TEST.COM  ")
        actualizado, error = actualizar_usuario(db, usuario.id, datos)

        assert error is None
        assert actualizado is not None
        assert actualizado.nombre == "Pedro"
        assert actualizado.email == "pedro@test.com"

    engine.dispose()


def test_actualizar_usuario_no_encontrado():
    engine = crear_db_test()

    with Session(engine) as db:
        datos = UsuarioActualizar(nombre="Pedro")
        actualizado, error = actualizar_usuario(db, 999, datos)

        assert actualizado is None
        assert error == "usuario_no_encontrado"

    engine.dispose()


def test_actualizar_usuario_integrity_error():
    engine = crear_db_test()

    with Session(engine) as db:
        u1 = Usuario(nombre="Juan", email="juan@test.com", password_hash="hash", rol=Rol.ADMIN)
        u2 = Usuario(nombre="Pedro", email="pedro@test.com", password_hash="hash", rol=Rol.ADMIN)
        db.add_all([u1, u2])
        db.commit()
        db.refresh(u2)

        datos = UsuarioActualizar(email="juan@test.com")
        try:
            actualizar_usuario(db, u2.id, datos)
            assert False, "Debería haber levantado IntegrityError"
        except IntegrityError:
            pass

    engine.dispose()
