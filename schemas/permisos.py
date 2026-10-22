from enum import Enum


class Permiso(str, Enum):
    # Alumnos
    CREAR_ALUMNO = "crear_alumno"
    VER_ALUMNOS = "ver_alumnos"
    VER_ALUMNO = "ver_alumno"
    MODIFICAR_ALUMNO = "modificar_alumno"
    ELIMINAR_ALUMNO = "eliminar_alumno"

    # Cursos
    CREAR_CURSO = "crear_curso"
    VER_CURSOS = "ver_cursos"
    VER_CURSO = "ver_curso"
    MODIFICAR_CURSO = "modificar_curso"
    ELIMINAR_CURSO = "eliminar_curso"

    # Evaluaciones
    CREAR_EVALUACION = "crear_evaluacion"
    VER_EVALUACIONES = "ver_evaluaciones"
    MODIFICAR_EVALUACION = "modificar_evaluacion"
    ELIMINAR_EVALUACION = "eliminar_evaluacion"

    # Inscripciones
    CREAR_INSCRIPCION = "crear_inscripcion"
    VER_INSCRIPCIONES = "ver_inscripciones"
    ELIMINAR_INSCRIPCION = "eliminar_inscripcion"

    # Calificaciones
    CREAR_CALIFICACION = "crear_calificacion"
    VER_CALIFICACIONES = "ver_calificaciones"
    MODIFICAR_CALIFICACION = "modificar_calificacion"
    ELIMINAR_CALIFICACION = "eliminar_calificacion"
    EXPORTAR_CALIFICACIONES = "exportar_calificaciones"

    # Invitaciones
    CREAR_INVITACION = "crear_invitacion"
    VER_INVITACIONES = "ver_invitaciones"
    REVOCAR_INVITACION = "revocar_invitacion"

    # Perfil académico
    VER_PERFIL_ACADEMICO = "ver_perfil_academico"
    MODIFICAR_PERFIL_ACADEMICO = "modificar_perfil_academico"

    # Usuarios
    VER_MI_PERFIL = "ver_mi_perfil"
    MODIFICAR_MI_PERFIL = "modificar_mi_perfil"