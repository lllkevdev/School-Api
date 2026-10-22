from fastapi import Depends, HTTPException

from core.dependencies import get_usuario_actual
from schemas.permisos import Permiso
from schemas.roles import Rol


PERMISOS_POR_ROL: dict[Rol, set[Permiso]] = {
    Rol.ADMIN: {
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
        Permiso.VER_PERFIL_ACADEMICO,
        Permiso.VER_MI_PERFIL,
        Permiso.MODIFICAR_MI_PERFIL,
    },
}


def tiene_permiso(rol: Rol, permiso: Permiso) -> bool:
    return permiso in PERMISOS_POR_ROL.get(rol, set())


def requiere_permiso(permiso: Permiso):
    def verificar(usuario=Depends(get_usuario_actual)):
        if not tiene_permiso(usuario.rol, permiso):
            raise HTTPException(
                status_code=403,
                detail="No tiene permiso para realizar esta acción",
            )

        return usuario

    return verificar