from services.usuario_service import (
    crear_usuario, 
    crear_maestro,
    buscar_usuario_por_email,
    obtener_maestros,
    actualizar_maestro,
    desactivar_maestro
)
from schemas.usuario import (
    UsuarioCrear, 
    MaestroCrear, 
    MaestroActualizar
)
from core.security import verify_password

from models.alumno import Alumno
from models.usuario import Usuario
from schemas.roles import Rol
from models.calificacion import Calificacion
from models.materia import Materia

from app.main import app
from core.security import hash_password

import pytest
from sqlalchemy.exc import IntegrityError


def test_crear_usuario_guarda_password_hasheada(db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="alumno"
    )

    usuario = crear_usuario(db, usuario_data)

    assert usuario.nombre == "Juan"
    assert usuario.email == "juan@test.com"
    assert usuario.rol == "alumno"

    assert usuario.password_hash != "12345678"


def test_buscar_usuario_por_email(db):
    usuario_data = UsuarioCrear(
        nombre="Pedro",
        email="pedro@test.com",
        password="12345678",
        rol="maestro"
    )

    crear_usuario(db, usuario_data)

    usuario = buscar_usuario_por_email(
        db,
        "pedro@test.com"
    )

    assert usuario is not None
    assert usuario.nombre == "Pedro"
    assert usuario.email == "pedro@test.com"
    assert usuario.rol == "maestro"


def test_verificar_password(db):
    usuario_data = UsuarioCrear(
        nombre="Ana",
        email="ana@test.com",
        password="12345678",
        rol="alumno"
    )

    usuario = crear_usuario(db, usuario_data)

    assert verify_password(
        "12345678",
        usuario.password_hash
    ) is True

    assert verify_password(
        "contraseña_incorrecta",
        usuario.password_hash
    ) is False


def test_usuario_puede_asociarse_a_un_alumno(db):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    usuario = Usuario(
        nombre="Juan Perez",
        email="juan@example.com",
        password_hash="hash",
        rol=Rol.ALUMNO,
        alumno_id=alumno.id
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    assert usuario.alumno_id == alumno.id
    assert usuario.alumno.id == alumno.id


def test_alumno_puede_ver_su_calificacion(client, db):
    alumno = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )
    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    materia = Materia(nombre="Matematica")
    db.add(materia)
    db.commit()
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        nota=8,
        periodo=2
    )
    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    usuario = Usuario(
        nombre="Juan Perez",
        email="juan@example.com",
        password_hash=hash_password("123456"),
        rol=Rol.ALUMNO,
        alumno_id=alumno.id,
        activo=True
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    login_response = client.post(
        "/auth/login",
        json={
            "email": usuario.email,
            "password": "123456"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get(
        f"/calificaciones/{calificacion.id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == calificacion.id


def test_alumno_no_puede_ver_calificacion_de_otro_alumno(
    client,
    db
):
    alumno_1 = Alumno(
        nombre="Juan",
        apellido="Perez",
        edad=20
    )

    alumno_2 = Alumno(
        nombre="Pedro",
        apellido="Gomez",
        edad=21
    )

    db.add_all([
        alumno_1,
        alumno_2
    ])
    db.commit()
    db.refresh(alumno_1)
    db.refresh(alumno_2)

    materia = Materia(
        nombre="Matematica"
    )

    db.add(materia)
    db.commit()
    db.refresh(materia)

    calificacion = Calificacion(
        alumno_id=alumno_1.id,
        materia_id=materia.id,
        nota=8,
        periodo=2
    )

    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)

    usuario = Usuario(
        nombre="Pedro Gomez",
        email="pedro@example.com",
        password_hash=hash_password("123456"),
        rol=Rol.ALUMNO,
        alumno_id=alumno_2.id,
        activo=True
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    login_response = client.post(
        "/auth/login",
        json={
            "email": usuario.email,
            "password": "123456"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get(
        f"/calificaciones/{calificacion.id}",
        headers=headers
    )

    assert response.status_code == 403


def test_crear_usuario_email_duplicado(db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="alumno"
    )

    crear_usuario(db, usuario_data)

    segundo_usuario = UsuarioCrear(
        nombre="Pedro",
        email="juan@test.com",
        password="12345678",
        rol="maestro"
    )

    with pytest.raises(IntegrityError):
        crear_usuario(db, segundo_usuario)


def test_crear_usuario_rol_invalido(db):
    usuario_data = UsuarioCrear(
        nombre="Juan",
        email="juan@test.com",
        password="12345678",
        rol="director"
    )

    with pytest.raises(Exception):
        crear_usuario(db, usuario_data)


def test_crear_usuario_activo_por_defecto(db):
    usuario_data = UsuarioCrear(
        nombre="Carlos",
        email="carlos@test.com",
        password="12345678",
        rol="alumno"
    )

    usuario = crear_usuario(db, usuario_data)

    assert usuario.activo is True


def test_crear_maestro_guarda_datos_y_rol_correctamente(db):
    maestro_data = MaestroCrear(
        nombre="Carlos",
        apellido="Perez",
        email="carlos.maestro@test.com",
        telefono="2601234567",
        password="12345678",
    )

    maestro = crear_maestro(db, maestro_data)

    assert maestro.nombre == "Carlos"
    assert maestro.apellido == "Perez"
    assert maestro.email == "carlos.maestro@test.com"
    assert maestro.telefono == "2601234567"
    assert maestro.rol == Rol.MAESTRO
    assert maestro.activo is True


def test_crear_maestro_guarda_password_hasheada(db):
    maestro_data = MaestroCrear(
        nombre="Ana",
        apellido="Gomez",
        email="ana.maestra@test.com",
        password="12345678",
    )

    maestro = crear_maestro(db, maestro_data)

    assert maestro.password_hash != "12345678"
    assert verify_password(
        "12345678",
        maestro.password_hash,
    ) is True


def test_crear_maestro_email_duplicado(db):
    primer_maestro = MaestroCrear(
        nombre="Carlos",
        apellido="Perez",
        email="duplicado@test.com",
        password="12345678",
    )

    segundo_maestro = MaestroCrear(
        nombre="Ana",
        apellido="Gomez",
        email="duplicado@test.com",
        password="87654321",
    )

    crear_maestro(db, primer_maestro)

    with pytest.raises(IntegrityError):
        crear_maestro(db, segundo_maestro)


def test_obtener_maestros_solo_devuelve_usuarios_maestro(db):
    crear_usuario(
        db,
        UsuarioCrear(
            nombre="Admin",
            email="admin-lista@test.com",
            password="12345678",
            rol="admin",
        ),
    )

    crear_maestro(
        db,
        MaestroCrear(
            nombre="Carlos",
            apellido="Perez",
            email="carlos-lista@test.com",
            password="12345678",
        ),
    )

    maestros = obtener_maestros(db)

    assert len(maestros) == 1
    assert maestros[0].email == "carlos-lista@test.com"
    assert maestros[0].rol == Rol.MAESTRO



def test_actualizar_telefono_maestro(db):
    maestro = crear_maestro(
        db,
        MaestroCrear(
            nombre="Carlos",
            apellido="Perez",
            email="carlos.actualizar@test.com",
            telefono="2601111111",
            password="12345678",
        ),
    )

    actualizado, error = actualizar_maestro(
        db,
        maestro.id,
        MaestroActualizar(telefono="2602222222"),
    )

    assert error is None
    assert actualizado is not None
    assert actualizado.telefono == "2602222222"
    assert actualizado.nombre == "Carlos"
    assert actualizado.email == "carlos.actualizar@test.com"


def test_actualizar_no_modifica_usuario_que_no_es_maestro(db):
    usuario = crear_usuario(
        db,
        UsuarioCrear(
            nombre="Admin",
            email="admin.actualizar@test.com",
            password="12345678",
            rol="admin",
        ),
    )

    resultado, error = actualizar_maestro(
        db,
        usuario.id,
        MaestroActualizar(nombre="Otro Nombre"),
    )

    assert resultado is None
    assert error == "maestro_no_encontrado"
    assert usuario.nombre == "Admin"


def test_actualizar_maestro_inexistente(db):
    resultado, error = actualizar_maestro(
        db,
        99999,
        MaestroActualizar(nombre="Carlos"),
    )

    assert resultado is None
    assert error == "maestro_no_encontrado"


def test_desactivar_maestro(db):
    maestro = crear_maestro(
        db,
        MaestroCrear(
            nombre="Carlos",
            apellido="Perez",
            email="carlos.desactivar@test.com",
            password="12345678",
        ),
    )

    desactivado, error = desactivar_maestro(db, maestro.id)

    assert error is None
    assert desactivado is not None
    assert desactivado.activo is False

    # El registro sigue existiendo en la base de datos.
    maestro_guardado = db.get(Usuario, maestro.id)

    assert maestro_guardado is not None
    assert maestro_guardado.activo is False


def test_desactivar_no_modifica_usuario_que_no_es_maestro(db):
    usuario = crear_usuario(
        db,
        UsuarioCrear(
            nombre="Admin",
            email="admin.desactivar@test.com",
            password="12345678",
            rol="admin",
        ),
    )

    resultado, error = desactivar_maestro(db, usuario.id)

    assert resultado is None
    assert error == "maestro_no_encontrado"
    assert usuario.activo is True


def test_desactivar_maestro_inexistente(db):
    resultado, error = desactivar_maestro(db, 99999)

    assert resultado is None
    assert error == "maestro_no_encontrado"



def test_obtener_maestros_excluye_desactivados(db):
    maestro = crear_maestro(
        db,
        MaestroCrear(
            nombre="Carlos",
            apellido="Perez",
            email="carlos.inactivo@test.com",
            password="12345678",
        ),
    )

    desactivado, error = desactivar_maestro(db, maestro.id)

    assert error is None
    assert desactivado is not None

    maestros = obtener_maestros(db)

    assert all(m.activo for m in maestros)
    assert all(m.id != maestro.id for m in maestros)