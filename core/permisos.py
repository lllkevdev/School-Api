from schemas.roles import Rol
from schemas.permisos import Permiso
from core.dependencies import get_usuario_actual

from fastapi import HTTPException, Depends


PERMISOS_POR_ROL: dict[Rol, set[Permiso]] = {

    Rol.ADMIN: {
        Permiso.CREAR_ALUMNO,
        Permiso.MODIFICAR_ALUMNO,
        Permiso.ELIMINAR_ALUMNO,

        Permiso.CREAR_MATERIA,
        Permiso.MODIFICAR_MATERIA,
        Permiso.ELIMINAR_MATERIA,

        Permiso.CREAR_CALIFICACION,
        Permiso.MODIFICAR_CALIFICACION,
        Permiso.ELIMINAR_CALIFICACION,

        Permiso.VER_CALIFICACION,
        Permiso.VER_TODAS_CALIFICACIONES,
        Permiso.VER_ALUMNOS,
        Permiso.VER_MATERIAS
    },

    Rol.MAESTRO: {
        Permiso.CREAR_CALIFICACION,
        Permiso.MODIFICAR_CALIFICACION,
        Permiso.ELIMINAR_CALIFICACION,
        Permiso.VER_CALIFICACION,
        Permiso.VER_ALUMNOS,
        Permiso.VER_MATERIAS
    },

    Rol.ALUMNO: {
        Permiso.VER_CALIFICACION,
        Permiso.VER_MATERIAS
    },
}

def tiene_permiso(rol, permiso):
    return permiso in PERMISOS_POR_ROL[rol]


def requiere_permiso(permiso):

    def verificar(usuario=Depends(get_usuario_actual)):
        tiene = tiene_permiso(usuario["rol"], permiso)

        if not tiene:
            raise HTTPException(
                status_code=403,
                detail="No tiene permiso para realizar esta acción"
            )

        return tiene

    return verificar