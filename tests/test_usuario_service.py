from services.usuario_service import crear_usuario, buscar_usuario_por_email
from schemas.usuario import UsuarioCrear
from security.password import verify_password

from models.alumno import Alumno
from models.usuario import Usuario
from schemas.roles import Rol
from models.calificacion import Calificacion
from models.materia import Materia

from app.main import app
from core.dependencies import get_usuario_actual

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
        password_hash="hash",
        rol=Rol.ALUMNO,
        alumno_id=alumno.id
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    def usuario_alumno_override():
        return {
            "id": usuario.id,
            "rol": Rol.ALUMNO,
            "alumno_id": usuario.alumno_id
        }

    app.dependency_overrides[get_usuario_actual] = usuario_alumno_override

    response = client.get(f"/calificaciones/{calificacion.id}")

    app.dependency_overrides.pop(get_usuario_actual, None)

    assert response.status_code == 200
    assert response.json()["id"] == calificacion.id





def test_alumno_no_puede_ver_calificacion_de_otro_alumno(client, db):
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

    db.add_all([alumno_1, alumno_2])
    db.commit()
    db.refresh(alumno_1)
    db.refresh(alumno_2)

    materia = Materia(nombre="Matematica")
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
        password_hash="hash",
        rol=Rol.ALUMNO,
        alumno_id=alumno_2.id
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    def usuario_alumno_override():
        return {
            "id": usuario.id,
            "rol": Rol.ALUMNO,
            "alumno_id": usuario.alumno_id
        }

    app.dependency_overrides[get_usuario_actual] = usuario_alumno_override

    response = client.get(f"/calificaciones/{calificacion.id}")

    print(response.status_code)
    print(response.json())
    
    app.dependency_overrides.pop(get_usuario_actual, None)

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