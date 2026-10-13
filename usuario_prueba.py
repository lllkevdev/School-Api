from database.connection import SessionLocal

from models.alumno import Alumno
from models.materia import Materia
from models.calificacion import Calificacion
from models.inscripcion import Inscripcion
from models.usuario import Usuario

from schemas.usuario import UsuarioCrear
from schemas.roles import Rol

from services.usuario_service import crear_usuario


db = SessionLocal()

usuario = UsuarioCrear(
    nombre="Kevin",
    email="kevin@test.com",
    password="12345678",
    rol=Rol.ADMIN,
)

crear_usuario(db, usuario)

db.close()

print("Usuario creado correctamente")