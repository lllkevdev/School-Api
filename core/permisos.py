# -*- coding: utf-8 -*-
from fastapi import Depends, HTTPException

from core.dependencies import get_usuario_actual
from models.usuario import Usuario
from schemas.permisos import Permiso
from schemas.roles import Rol


PERMISOS_POR_ROL: dict[Rol, set[Permiso]] = {
    Rol.ADMIN: {
        # Materias (compatibilidad legacy)
        Permiso.CREAR_MATERIA,
        Permiso.VER_MATERIAS,
        Permiso.VER_MATERIA,
        Permiso.MODIFICAR_MATERIA,
        Permiso.ELIMINAR_MATERIA,

        # Alumnos y perfiles académicos
        Permiso.CREAR_ALUMNO,
        Permiso.VER_ALUMNOS,
        Permiso.VER_ALUMNO,
        Permiso.MODIFICAR_ALUMNO,
        Permiso.ELIMINAR_ALUMNO,
        Permiso.VER_PERFIL_ACADEMICO,
        Permiso.MODIFICAR_PERFIL_ACADEMICO,

        # Cursos
        Permiso.CREAR_CURSO,
        Permiso.VER_CURSOS,
        Permiso.VER_CURSO,
        Permiso.MODIFICAR_CURSO,
        Permiso.ELIMINAR_CURSO,

        # Evaluaciones
        Permiso.CREAR_EVALUACION,
        Permiso.VER_EVALUACIONES,
        Permiso.MODIFICAR_EVALUACION,
        Permiso.ELIMINAR_EVALUACION,

        # Inscripciones
        Permiso.CREAR_INSCRIPCION,
        Permiso.VER_INSCRIPCIONES,
        Permiso.ELIMINAR_INSCRIPCION,

        # Calificaciones
        Permiso.CREAR_CALIFICACION,
        Permiso.VER_CALIFICACIONES,
        Permiso.VER_CALIFICACION,
        Permiso.VER_TODAS_CALIFICACIONES,
        Permiso.MODIFICAR_CALIFICACION,
        Permiso.ELIMINAR_CALIFICACION,
        Permiso.EXPORTAR_CALIFICACIONES,

        # Invitaciones
        Permiso.CREAR_INVITACION,
        Permiso.VER_INVITACIONES,
        Permiso.REVOCAR_INVITACION,

        # Perfil propio
        Permiso.VER_MI_PERFIL,
        Permiso.MODIFICAR_MI_PERFIL,
    },

    Rol.ALUMNO: {
        Permiso.VER_MATERIAS,
        Permiso.VER_MATERIA,
        Permiso.VER_PERFIL_ACADEMICO,
        Permiso.VER_MI_PERFIL,
        Permiso.MODIFICAR_MI_PERFIL,
        Permiso.VER_CALIFICACION,
    },
}


def tiene_permiso(rol: Rol, permiso: Permiso) -> bool:
    if rol not in PERMISOS_POR_ROL:
        raise KeyError(rol)
    return permiso in PERMISOS_POR_ROL[rol]


def requiere_permiso(permiso: Permiso):
    def verificar(
        usuario: Usuario = Depends(get_usuario_actual),
    ) -> Usuario:
        if not tiene_permiso(usuario.rol, permiso):
            raise HTTPException(
                status_code=403,
                detail="No tiene permiso para realizar esta acción",
            )

        return usuario

    return verificar