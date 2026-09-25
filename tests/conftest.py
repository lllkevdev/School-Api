import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.dependencies import get_db
from models.alumno import Alumno
from models.materia import Materia
from models.calificacion import Calificacion
from models.usuario import Usuario
from app.main import app
from core.dependencies import get_usuario_actual
from schemas.roles import Rol
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

engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)

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
        db.query(Calificacion).delete()
        db.query(Alumno).delete()
        db.query(Materia).delete()
        db.query(Usuario).delete()
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
def client(db):
    def obtener_db():
        return db

    app.dependency_overrides[get_db] = obtener_db

    yield TestClient(app)

    app.dependency_overrides.pop(get_db, None)




@pytest.fixture()
def usuario_admin():
    def usuario_admin_override():
        return {
            "rol": Rol.ADMIN
        }

    app.dependency_overrides[get_usuario_actual] = usuario_admin_override

    yield 

    app.dependency_overrides.clear()




@pytest.fixture()
def usuario_maestro(db):
    maestro = Usuario(
        nombre="Juan",
        email="juan@test.com",
        password_hash="hash",
        rol=Rol.MAESTRO
    )

    db.add(maestro)
    db.commit()
    db.refresh(maestro)

    def usuario_maestro_override():
        return {
            "rol": Rol.MAESTRO,
            "id": maestro.id
        }

    app.dependency_overrides[get_usuario_actual] = usuario_maestro_override

    yield maestro

    app.dependency_overrides.clear()





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
        email="juan@test.com",
        password_hash="hash",
        rol=Rol.ALUMNO,
        alumno_id=alumno.id
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    def usuario_alumno_override():
        return {
            "rol": Rol.ALUMNO,
            "id": usuario.id,
            "alumno_id": alumno.id
        }

    app.dependency_overrides[get_usuario_actual] = usuario_alumno_override

    yield alumno

    app.dependency_overrides.clear()