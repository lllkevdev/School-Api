from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from models.alumno import Alumno
from models.curso import Curso
from models.inscripcion import Inscripcion
from models.invitacion import Invitacion
from services.alumno_service import desactivar_alumno


def crear_alumno_inscripto(db, usuario_maestro, activo=True):
    alumno = Alumno(
        nombre="Juan",
        apellido="Pérez",
        documento_identidad="TEST-12345",
        fecha_nacimiento=date(2010, 5, 10),
        activo=activo,
    )

    curso = Curso(
        docente_id=usuario_maestro.id,
        nombre_materia="Matemática",
        division="1A",
        anio_lectivo=2026,
        cantidad_periodos=3,
        activo=True,
    )

    db.add_all([alumno, curso])
    db.commit()

    db.refresh(alumno)
    db.refresh(curso)

    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        curso_id=curso.id,
    )

    db.add(inscripcion)
    db.commit()

    return alumno, curso


def test_desactivar_alumno_inexistente(db, usuario_maestro):
    alumno, error = desactivar_alumno(
        db,
        alumno_id=99999,
        usuario=usuario_maestro,
    )

    assert alumno is None
    assert error == "alumno_inexistente"


def test_desactivar_alumno_sin_curso_del_docente(
    db,
    usuario_maestro,
):
    alumno = Alumno(
        nombre="Ana",
        apellido="López",
        documento_identidad="TEST-67890",
        fecha_nacimiento=date(2011, 3, 15),
        activo=True,
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    resultado, error = desactivar_alumno(
        db,
        alumno_id=alumno.id,
        usuario=usuario_maestro,
    )

    assert resultado is None
    assert error == "permiso"
    assert alumno.activo is True


def test_desactivar_alumno_ya_inactivo(db, usuario_maestro):
    alumno, _ = crear_alumno_inscripto(
        db,
        usuario_maestro,
        activo=False,
    )

    resultado, error = desactivar_alumno(
        db,
        alumno_id=alumno.id,
        usuario=usuario_maestro,
    )

    assert resultado is None
    assert error == "alumno_inactivo"
    assert alumno.activo is False


def test_desactivar_alumno_exitosamente_sin_borrar_relaciones(
    db,
    usuario_maestro,
):
    alumno, curso = crear_alumno_inscripto(
        db,
        usuario_maestro,
        activo=True,
    )

    invitacion = Invitacion(
        alumno_id=alumno.id,
        curso_id=curso.id,
        docente_id=usuario_maestro.id,
        email="juan@example.com",
        token_hash="hash-test-12345",
        expira_en=datetime.now(timezone.utc) + timedelta(days=1),
        creada_en=datetime.now(timezone.utc),
    )

    db.add(invitacion)
    db.commit()
    db.refresh(invitacion)

    resultado, error = desactivar_alumno(
        db,
        alumno_id=alumno.id,
        usuario=usuario_maestro,
    )

    assert error is None
    assert resultado is not None
    assert resultado.id == alumno.id
    assert resultado.activo is False

    inscripcion_existente = db.scalar(
        select(Inscripcion).where(
            Inscripcion.alumno_id == alumno.id,
            Inscripcion.curso_id == curso.id,
        )
    )

    invitacion_existente = db.scalar(
        select(Invitacion).where(
            Invitacion.id == invitacion.id,
        )
    )

    assert inscripcion_existente is not None
    assert invitacion_existente is not None
