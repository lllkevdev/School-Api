from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from datetime import date, datetime, timedelta, timezone
import hashlib

from database.connection import Base
from core.security import hash_password
from models.curso import Curso
from models.usuario import Usuario
from models.alumno import Alumno
from models.inscripcion import Inscripcion
from models.invitacion import Invitacion
from schemas.invitacion import InvitacionAceptar, InvitacionCrear
from schemas.roles import Rol
from services.invitacion_service import (
    aceptar_invitacion,
    crear_invitacion,
    listar_invitaciones,
    revocar_invitacion,
)


def crear_db_test():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def test_crear_invitacion_exitoso():
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

        datos = InvitacionCrear(alumno_id=alumno.id, curso_id=curso.id, email="alumno@familia.com")
        invitacion, error, token = crear_invitacion(db, datos, docente)
        assert error is None
        assert invitacion is not None
        assert token is not None
    engine.dispose()


def test_crear_invitacion_alumno_inexistente():
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

        datos = InvitacionCrear(alumno_id=999, curso_id=curso.id, email="alumno@familia.com")
        invitacion, error, token = crear_invitacion(db, datos, docente)
        assert invitacion is None
        assert error == "alumno_inexistente"
    engine.dispose()


def test_crear_invitacion_curso_inexistente():
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

        datos = InvitacionCrear(alumno_id=alumno.id, curso_id=999, email="alumno@familia.com")
        invitacion, error, token = crear_invitacion(db, datos, docente)
        assert invitacion is None
        assert error == "curso_inexistente"
    engine.dispose()


def test_crear_invitacion_curso_inactivo():
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

        datos = InvitacionCrear(alumno_id=alumno.id, curso_id=curso.id, email="alumno@familia.com")
        invitacion, error, token = crear_invitacion(db, datos, docente)
        assert invitacion is None
        assert error == "curso_inactivo"
    engine.dispose()


def test_listar_invitaciones():
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

        token_hash = hashlib.sha256(b"token" * 4).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
        )
        db.add(invitacion)
        db.commit()

        invitaciones = listar_invitaciones(db, docente)
        assert len(invitaciones) == 1
    engine.dispose()


def test_revocar_invitacion_exitoso():
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

        token_hash = hashlib.sha256(b"token" * 4).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
        )
        db.add(invitacion)
        db.commit()
        db.refresh(invitacion)

        revocada, error = revocar_invitacion(db, invitacion.id, docente)
        assert revocada is True
        assert error is None
    engine.dispose()


def test_revocar_invitacion_usada():
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

        token_hash = hashlib.sha256(b"token" * 4).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
            aceptada_en=datetime.now(timezone.utc),
        )
        db.add(invitacion)
        db.commit()
        db.refresh(invitacion)

        revocada, error = revocar_invitacion(db, invitacion.id, docente)
        assert revocada is False
        assert error == "invitacion_usada"
    engine.dispose()


def test_revocar_invitacion_revocada():
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

        token_hash = hashlib.sha256(b"token" * 4).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
            revocada_en=datetime.now(timezone.utc),
        )
        db.add(invitacion)
        db.commit()
        db.refresh(invitacion)

        revocada, error = revocar_invitacion(db, invitacion.id, docente)
        assert revocada is False
        assert error == "invitacion_revocada"
    engine.dispose()


def test_aceptar_invitacion_token_invalido():
    engine = crear_db_test()
    with Session(engine) as db:
        datos = InvitacionAceptar(token="a" * 32, password="password123")
        usuario, error = aceptar_invitacion(db, datos)
        assert usuario is None
        assert error == "invitacion_invalida"
    engine.dispose()


def test_aceptar_invitacion_revocada():
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

        token = "a" * 32
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
            revocada_en=datetime.now(timezone.utc),
        )
        db.add(invitacion)
        db.commit()

        datos = InvitacionAceptar(token=token, password="password123")
        usuario, error = aceptar_invitacion(db, datos)
        assert usuario is None
        assert error == "invitacion_revocada"
    engine.dispose()


def test_aceptar_invitacion_usada():
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

        token = "b" * 32
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
            aceptada_en=datetime.now(timezone.utc),
        )
        db.add(invitacion)
        db.commit()

        datos = InvitacionAceptar(token=token, password="password123")
        usuario, error = aceptar_invitacion(db, datos)
        assert usuario is None
        assert error == "invitacion_usada"
    engine.dispose()


def test_aceptar_invitacion_expirada():
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

        token = "c" * 32
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.add(invitacion)
        db.commit()

        datos = InvitacionAceptar(token=token, password="password123")
        usuario, error = aceptar_invitacion(db, datos)
        assert usuario is None
        assert error == "invitacion_expirada"
    engine.dispose()


def test_aceptar_invitacion_exitoso_crea_usuario():
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

        token = "d" * 32
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
        )
        db.add(invitacion)
        db.commit()

        datos = InvitacionAceptar(token=token, password="password123")
        usuario, error = aceptar_invitacion(db, datos)
        assert error is None
        assert usuario is not None
        assert usuario.nombre == alumno.nombre
        assert usuario.apellido == alumno.apellido
        assert usuario.rol == Rol.ALUMNO
        assert usuario.alumno_id == alumno.id
        assert usuario.activo is True

        inscripcion = db.scalar(
            select(Inscripcion).where(
                Inscripcion.alumno_id == alumno.id,
                Inscripcion.curso_id == curso.id,
            )
        )
        assert inscripcion is not None
    engine.dispose()


def test_aceptar_invitacion_usuario_existente_mismo_alumno():
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

        usuario_existente = Usuario(
            nombre="A",
            apellido="X",
            email="alumno@familia.com",
            password_hash=hash_password("password123"),
            rol=Rol.ALUMNO,
            alumno_id=alumno.id,
            activo=True,
        )
        db.add(usuario_existente)
        db.commit()

        token = "e" * 32
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
        )
        db.add(invitacion)
        db.commit()

        datos = InvitacionAceptar(token=token, password="password123")
        usuario, error = aceptar_invitacion(db, datos)
        assert error is None
        assert usuario is not None
        assert usuario.id == usuario_existente.id
    engine.dispose()


def test_aceptar_invitacion_usuario_existente_password_incorrecta():
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

        db.add(
            Usuario(
                nombre="A",
                apellido="X",
                email="alumno@familia.com",
                password_hash=hash_password("password123"),
                rol=Rol.ALUMNO,
                alumno_id=alumno.id,
                activo=True,
            )
        )
        db.commit()

        token = "g" * 32
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        db.add(
            Invitacion(
                alumno_id=alumno.id,
                curso_id=curso.id,
                docente_id=docente.id,
                email="alumno@familia.com",
                token_hash=token_hash,
                expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
            )
        )
        db.commit()

        datos = InvitacionAceptar(token=token, password="incorrecta")
        usuario, error = aceptar_invitacion(db, datos)
        assert usuario is None
        assert error == "credenciales"
    engine.dispose()


def test_aceptar_invitacion_conflicto():
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

        usuario_existente = Usuario(
            nombre="A",
            apellido="X",
            email="alumno@familia.com",
            password_hash="hash",
            rol=Rol.ALUMNO,
            alumno_id=alumno2.id,
            activo=True,
        )
        db.add(usuario_existente)
        db.commit()

        token = "f" * 32
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invitacion = Invitacion(
            alumno_id=alumno1.id,
            curso_id=curso.id,
            docente_id=docente.id,
            email="alumno@familia.com",
            token_hash=token_hash,
            expira_en=datetime.now(timezone.utc) + timedelta(hours=48),
        )
        db.add(invitacion)
        db.commit()

        datos = InvitacionAceptar(token=token, password="password123")
        usuario, error = aceptar_invitacion(db, datos)
        assert usuario is None
        assert error == "invitacion_conflicto"
    engine.dispose()
