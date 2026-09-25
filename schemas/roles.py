from enum import Enum


class Rol(str, Enum):
    ADMIN = "admin"
    MAESTRO = "maestro"
    ALUMNO = "alumno"