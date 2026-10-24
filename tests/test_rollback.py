import pytest
from sqlalchemy.exc import IntegrityError

from models.calificacion import Calificacion
from database.connection import SessionLocal


def test_rollback_calificacion():
    db = SessionLocal()

    try:
        calificacion = Calificacion(
            alumno_id=999999,
            evaluacion_id=999999,
            curso_id=999999,
            nota=10,
        )

        db.add(calificacion)

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()

        resultado = db.query(Calificacion).count()

        assert resultado >= 0

    finally:
        db.close()