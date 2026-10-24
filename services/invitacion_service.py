import secrets
import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.security import hash_password
from models.alumno import Alumno
from models.curso import Curso
from models.invitacion import Invitacion
from models.usuario import Usuario
from schemas.invitacion import InvitacionCrear, InvitacionAceptar
from schemas.roles import Rol


INVITACION_TTL_HORAS = 48


def _generar_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


def crear_invitacion(
    db: Session,
    datos: InvitacionCrear,
    docente: Usuario,
) -> tuple[Invitacion | None, str | None, str | None]:
    alumno = db.scalar(
        select(Alumno).where(Alumno.id == datos.alumno_id)
    )
    if alumno is None:
        return None, "alumno_inexistente", None

    curso = db.scalar(
        select(Curso).where(
            Curso.id == datos.curso_id,
            Curso.docente_id == docente.id,
        )
    )
    if curso is None:
        return None, "curso_inexistente", None

    if not curso.activo:
        return None, "curso_inactivo", None

    token, token_hash = _generar_token()
    expira_en = datetime.now(timezone.utc) + timedelta(hours=INVITACION_TTL_HORAS)

    invitacion = Invitacion(
        alumno_id=alumno.id,
        curso_id=curso.id,
        docente_id=docente.id,
        email=str(datos.email).lower(),
        token_hash=token_hash,
        expira_en=expira_en,
    )

    try:
        db.add(invitacion)
        db.commit()
        db.refresh(invitacion)
    except IntegrityError:
        db.rollback()
        raise

    return invitacion, None, token


def listar_invitaciones(
    db: Session,
    docente: Usuario,
) -> list[Invitacion]:
    invitaciones = db.scalars(
        select(Invitacion).where(Invitacion.docente_id == docente.id)
    ).all()
    return list(invitaciones)


def revocar_invitacion(
    db: Session,
    invitacion_id: int,
    docente: Usuario,
) -> tuple[bool, str | None]:
    invitacion = db.scalar(
        select(Invitacion).where(
            Invitacion.id == invitacion_id,
            Invitacion.docente_id == docente.id,
        )
    )
    if invitacion is None:
        return False, "invitacion_inexistente"

    if invitacion.aceptada_en is not None:
        return False, "invitacion_usada"

    if invitacion.revocada_en is not None:
        return False, "invitacion_revocada"

    invitacion.revocada_en = datetime.now(timezone.utc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    return True, None


def aceptar_invitacion(
    db: Session,
    datos: InvitacionAceptar,
) -> tuple[Usuario | None, str | None]:
    token_hash = hashlib.sha256(datos.token.encode()).hexdigest()
    invitacion = db.scalar(
        select(Invitacion).where(Invitacion.token_hash == token_hash)
    )
    if invitacion is None:
        return None, "invitacion_invalida"

    if invitacion.revocada_en is not None:
        return None, "invitacion_revocada"

    if invitacion.aceptada_en is not None:
        return None, "invitacion_usada"

    ahora = datetime.now(timezone.utc)
    expira = invitacion.expira_en
    if expira.tzinfo is None:
        expira = expira.replace(tzinfo=timezone.utc)
    if ahora > expira:
        return None, "invitacion_expirada"

    usuario_existente = db.scalar(
        select(Usuario).where(Usuario.email == invitacion.email)
    )
    if usuario_existente is not None:
        if usuario_existente.alumno_id == invitacion.alumno_id and usuario_existente.activo:
            invitacion.aceptada_en = ahora
            db.commit()
            return usuario_existente, None
        return None, "conflicto"

    usuario = Usuario(
        nombre="",
        apellido="",
        email=invitacion.email,
        password_hash=hash_password(datos.password),
        rol=Rol.ALUMNO,
        alumno_id=invitacion.alumno_id,
        activo=True,
    )
    try:
        db.add(usuario)
        db.flush()
        invitacion.aceptada_en = ahora
        db.commit()
        db.refresh(usuario)
    except IntegrityError:
        db.rollback()
        raise

    return usuario, None
