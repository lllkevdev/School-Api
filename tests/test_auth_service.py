from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database.connection import Base
from models.usuario import Usuario
from schemas.auth import LoginRequest
from schemas.roles import Rol
from services.auth_service import autenticar_usuario
import core.config as config


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_autenticar_usuario_exitoso():
    engine = crear_db_test()
    from core.security import hash_password

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Docente",
            email="docente@test.com",
            password_hash=hash_password("password123"),
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(usuario)
        db.commit()

        login = LoginRequest(email="docente@test.com", password="password123")
        respuesta = autenticar_usuario(db, login)

        assert respuesta.access_token is not None
        assert respuesta.token_type == "bearer"

    engine.dispose()


def test_autenticar_usuario_email_no_existe():
    engine = crear_db_test()

    with Session(engine) as db:
        login = LoginRequest(email="noexiste@test.com", password="password123")
        try:
            autenticar_usuario(db, login)
            assert False, "Debería haber levantado ValueError"
        except ValueError as e:
            assert str(e) == "credenciales"

    engine.dispose()


def test_autenticar_usuario_password_incorrecta():
    engine = crear_db_test()
    from core.security import hash_password

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Docente",
            email="docente@test.com",
            password_hash=hash_password("password123"),
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(usuario)
        db.commit()

        login = LoginRequest(email="docente@test.com", password="wrongpass")
        try:
            autenticar_usuario(db, login)
            assert False, "Debería haber levantado ValueError"
        except ValueError as e:
            assert str(e) == "credenciales"

    engine.dispose()


def test_autenticar_usuario_inactivo():
    engine = crear_db_test()
    from core.security import hash_password

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Docente",
            email="docente@test.com",
            password_hash=hash_password("password123"),
            rol=Rol.ADMIN,
            activo=False,
        )
        db.add(usuario)
        db.commit()

        login = LoginRequest(email="docente@test.com", password="password123")
        try:
            autenticar_usuario(db, login)
            assert False, "Debería haber levantado ValueError"
        except ValueError as e:
            assert str(e) == "credenciales"

    engine.dispose()


def test_autenticar_usuario_secret_key_no_configurada(monkeypatch):
    engine = crear_db_test()
    from core.security import hash_password
    import services.auth_service as auth_service_mod

    with Session(engine) as db:
        usuario = Usuario(
            nombre="Docente",
            email="docente@test.com",
            password_hash=hash_password("password123"),
            rol=Rol.ADMIN,
            activo=True,
        )
        db.add(usuario)
        db.commit()

        monkeypatch.setattr(config, "SECRET_KEY", None)
        monkeypatch.setattr(auth_service_mod, "SECRET_KEY", None)
        login = LoginRequest(email="docente@test.com", password="password123")
        try:
            autenticar_usuario(db, login)
            assert False, "Debería haber levantado ValueError"
        except ValueError as e:
            assert str(e) == "SECRET_KEY no configurada"

    engine.dispose()
