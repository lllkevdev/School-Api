from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.usuario import Usuario
from schemas.perfil import PerfilActualizar


def actualizar_perfil(
    db: Session,
    usuario: Usuario,
    datos: PerfilActualizar,
) -> tuple[Usuario | None, str | None]:
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        return None, "sin_cambios"

    for campo, valor in cambios.items():
        if isinstance(valor, str):
            valor = valor.strip()

        if campo == "telefono" and valor == "":
            valor = None

        setattr(usuario, campo, valor)

    try:
        db.commit()
        db.refresh(usuario)
        return usuario, None
    except IntegrityError:
        db.rollback()
        raise
