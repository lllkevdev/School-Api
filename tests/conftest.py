import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database.connection import Base
from database.dependencies import get_db
from models.alumno import Alumno
from models.calificacion import Calificacion
from models.usuario import Usuario
from models.inscripcion import Inscripcion
from app.main import app
from core.security import hash_password
from schemas.roles import Rol
from models.curso import Curso
from models.evaluacion import Evaluacion
from models.invitacion import Invitacion

# URL de la base de tests: configurable por entorno, con fallback a SQLite local
# para que la suite funcione en cualquier máquina sin un Postgres preconfigurado.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+pysqlite:///./school_test.db"
)

connect_args = (
    {"check_same_thread": False}
    if TEST_DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args=connect_args,
    poolclass=StaticPool if TEST_DATABASE_URL.startswith("sqlite") else None,
    )

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
@pytest.fixture(scope="session", autouse=True)
def preparar_base_de_datos():
    """Crea (y al final elimina) las tablas una sola vez por sesión de tests."""
    Base.metadata.create_all(bind=engine)

    yield
    Base.metadata.drop_all(bind=engine)

def limpiar_db(db):
    try:
        db.query(Calificacion).delete()
    except Exception:
        pass
    try:
        db.query(Evaluacion).delete()
    except Exception:
        pass
    try:
        db.query(Invitacion).delete()
    except Exception:
        pass
    try:
        db.query(Inscripcion).delete()
    except Exception:
        pass
    try:
        db.query(Curso).delete()
    except Exception:
        pass
    try:
        db.query(Usuario).delete()
    except Exception:
        pass
    try:
        db.query(Alumno).delete()
    except Exception:
        pass
    db.commit()


@pytest.fixture
def db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        limpiar_db(db)
        db.close()


@pytest.fixture
def db_fk():
    connection = engine.connect()

    if TEST_DATABASE_URL.startswith("sqlite"):
        connection.exec_driver_sql("PRAGMA foreign_keys=ON")

    TestingSessionFK = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
    )

    db = TestingSessionFK()

    try:
        yield db
    finally:
        db.rollback()
        limpiar_db(db)

        if TEST_DATABASE_URL.startswith("sqlite"):
            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")

        db.close()
        connection.close()


@pytest.fixture
def client_fk(db_fk):
    def obtener_db():
        return db_fk

    app.dependency_overrides[get_db] = obtener_db

    yield TestClient(app)

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(db):
    def obtener_db():
        return db

    app.dependency_overrides[get_db] = obtener_db

    yield TestClient(app)

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def usuario_admin(db):
    usuario = Usuario(
        nombre="Admin",
        email="admin@test.com",
        password_hash=hash_password("123456"),
        rol=Rol.ADMIN,
        activo=True
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    yield usuario


@pytest.fixture()
def auth_headers_admin(client, usuario_admin):
    response = client.post(
        "/auth/login",
        json={
            "email": usuario_admin.email,
            "password": "123456"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }



@pytest.fixture()
def usuario_alumno(db):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    usuario = Usuario(
        nombre="Juan",
        email="juan.alumno@test.com",
        password_hash=hash_password("123456"),
        rol=Rol.ALUMNO,
        alumno_id=alumno.id,
        activo=True
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    yield alumno


@pytest.fixture()
def auth_headers_alumno(client, usuario_alumno):
    response = client.post(
        "/auth/login",
        json={
            "email": "juan.alumno@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }