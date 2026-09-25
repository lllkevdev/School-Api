from enum import Enum


class Permiso(str, Enum):
    CREAR_ALUMNO = "crear_alumno"
    MODIFICAR_ALUMNO = "modificar_alumno"
    ELIMINAR_ALUMNO = "eliminar_alumno"

    CREAR_MATERIA = "crear_materia"
    MODIFICAR_MATERIA = "modificar_materia"
    ELIMINAR_MATERIA = "eliminar_materia"

    CREAR_CALIFICACION = "crear_calificacion"
    MODIFICAR_CALIFICACION = "modificar_calificacion"
    ELIMINAR_CALIFICACION = "eliminar_calificacion"

    VER_CALIFICACION = "ver_calificacion"
    VER_TODAS_CALIFICACIONES = "ver_todas_calificaciones"
    VER_ALUMNOS = "ver_alumnos"
    VER_MATERIAS = "ver_materias"