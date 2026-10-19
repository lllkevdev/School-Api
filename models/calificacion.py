from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


if TYPE_CHECKING:
    from models.alumno import Alumno
    from models.evaluacion import Evaluacion


class Calificacion(Base):
    __tablename__ = "calificaciones"

    __table_args__ = (
        CheckConstraint(
            "nota >= 1 AND nota <= 10",
            name="ck_calificaciones_nota",
        ),
        UniqueConstraint(
            "alumno_id",
            "evaluacion_id",
            name="uq_calificacion_alumno_evaluacion",
        ),
        ForeignKeyConstraint(
            ["alumno_id", "curso_id"],
            ["inscripciones.alumno_id", "inscripciones.curso_id"],
            name="fk_calificacion_inscripcion",
        ),
        ForeignKeyConstraint(
            ["evaluacion_id", "curso_id"],
            ["evaluaciones.id", "evaluaciones.curso_id"],
            name="fk_calificacion_evaluacion_curso",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    alumno_id: Mapped[int] = mapped_column(
        ForeignKey("alumnos.id"),
        nullable=False,
    )

    evaluacion_id: Mapped[int] = mapped_column(
        ForeignKey("evaluaciones.id"),
        nullable=False,
    )

    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id"),
        nullable=False,
    )

    nota: Mapped[float] = mapped_column(nullable=False)

    alumno: Mapped["Alumno"] = relationship(
        back_populates="calificaciones",
        foreign_keys=[alumno_id],
    )

    evaluacion: Mapped["Evaluacion"] = relationship(
        back_populates="calificaciones",
        foreign_keys=[evaluacion_id],
    )