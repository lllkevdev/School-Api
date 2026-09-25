import pytest
from fastapi import HTTPException

from core.permisos import (
    Rol,
    Permiso,
    tiene_permiso,
    requiere_permiso,
)


@pytest.mark.parametrize(
    "rol, permiso, esperado",
    [
        # =========================
        # ADMIN
        # =========================

        (Rol.ADMIN, Permiso.CREAR_ALUMNO, True),
        (Rol.ADMIN, Permiso.MODIFICAR_ALUMNO, True),
        (Rol.ADMIN, Permiso.ELIMINAR_ALUMNO, True),

        (Rol.ADMIN, Permiso.CREAR_MATERIA, True),
        (Rol.ADMIN, Permiso.MODIFICAR_MATERIA, True),
        (Rol.ADMIN, Permiso.ELIMINAR_MATERIA, True),

        (Rol.ADMIN, Permiso.CREAR_CALIFICACION, True),
        (Rol.ADMIN, Permiso.MODIFICAR_CALIFICACION, True),
        (Rol.ADMIN, Permiso.ELIMINAR_CALIFICACION, True),

        (Rol.ADMIN, Permiso.VER_CALIFICACION, True),
        (Rol.ADMIN, Permiso.VER_TODAS_CALIFICACIONES, True),
        (Rol.ADMIN, Permiso.VER_ALUMNOS, True),
        (Rol.ADMIN, Permiso.VER_MATERIAS, True),

        # =========================
        # MAESTRO
        # =========================

        (Rol.MAESTRO, Permiso.CREAR_ALUMNO, False),
        (Rol.MAESTRO, Permiso.MODIFICAR_ALUMNO, False),
        (Rol.MAESTRO, Permiso.ELIMINAR_ALUMNO, False),

        (Rol.MAESTRO, Permiso.CREAR_MATERIA, False),
        (Rol.MAESTRO, Permiso.MODIFICAR_MATERIA, False),
        (Rol.MAESTRO, Permiso.ELIMINAR_MATERIA, False),

        (Rol.MAESTRO, Permiso.CREAR_CALIFICACION, True),
        (Rol.MAESTRO, Permiso.MODIFICAR_CALIFICACION, True),
        (Rol.MAESTRO, Permiso.ELIMINAR_CALIFICACION, True),

        (Rol.MAESTRO, Permiso.VER_CALIFICACION, True),
        (Rol.MAESTRO, Permiso.VER_TODAS_CALIFICACIONES, False),
        (Rol.MAESTRO, Permiso.VER_ALUMNOS, True),
        (Rol.MAESTRO, Permiso.VER_MATERIAS, True),

        # =========================
        # ALUMNO
        # =========================

        (Rol.ALUMNO, Permiso.CREAR_ALUMNO, False),
        (Rol.ALUMNO, Permiso.MODIFICAR_ALUMNO, False),
        (Rol.ALUMNO, Permiso.ELIMINAR_ALUMNO, False),

        (Rol.ALUMNO, Permiso.CREAR_MATERIA, False),
        (Rol.ALUMNO, Permiso.MODIFICAR_MATERIA, False),
        (Rol.ALUMNO, Permiso.ELIMINAR_MATERIA, False),

        (Rol.ALUMNO, Permiso.CREAR_CALIFICACION, False),
        (Rol.ALUMNO, Permiso.MODIFICAR_CALIFICACION, False),
        (Rol.ALUMNO, Permiso.ELIMINAR_CALIFICACION, False),

        (Rol.ALUMNO, Permiso.VER_CALIFICACION, True),
        (Rol.ALUMNO, Permiso.VER_TODAS_CALIFICACIONES, False),
        (Rol.ALUMNO, Permiso.VER_ALUMNOS, False),
        (Rol.ALUMNO, Permiso.VER_MATERIAS, True),
    ],
)
def test_tiene_permiso(rol, permiso, esperado):
    assert tiene_permiso(rol, permiso) == esperado


def test_tiene_permiso_rol_invalido():
    with pytest.raises(KeyError):
        tiene_permiso(
            "OTRO_ROL",
            Permiso.CREAR_ALUMNO
        )


def test_requiere_permiso_con_permiso():
    usuario = {
        "rol": Rol.MAESTRO
    }

    verificar = requiere_permiso(
        Permiso.CREAR_CALIFICACION
    )

    assert verificar(usuario) is True


def test_requiere_permiso_sin_permiso():
    usuario = {
        "rol": Rol.MAESTRO
    }

    verificar = requiere_permiso(
        Permiso.ELIMINAR_ALUMNO
    )

    with pytest.raises(HTTPException) as excepcion:
        verificar(usuario)

    assert excepcion.value.status_code == 403
    assert excepcion.value.detail == (
        "No tiene permiso para realizar esta acción"
    )
