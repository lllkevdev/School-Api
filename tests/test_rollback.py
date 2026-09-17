import pytest
from sqlalchemy.exc import IntegrityError

from models.calificacion import Calificacion
from database.connection import SessionLocal


def test_rollback_calificacion():
    db = SessionLocal()

    try:
        calificacion = Calificacion(
            alumno_id=999999,
            materia_id=999999,
            nota=10,
            periodo=1
        )

        db.add(calificacion)

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()

        # Comprobamos que la sesión sigue funcionando
        resultado = db.query(Calificacion).count()

        assert resultado >= 0

    finally:
        db.close()