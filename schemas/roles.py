from enum import Enum

class Rol(str, Enum):
    ADMIN = "admin"
    ALUMNO = "alumno"