from schemas.roles import Rol


def get_usuario_actual():
    return {
        "rol": Rol.ADMIN
    }
