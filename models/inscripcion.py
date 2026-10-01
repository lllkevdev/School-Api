from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base



if TYPE_CHECKING:
    from models.alumno import Alumno
    from models.materia import Materia




class Inscripcion(Base):
    __tablename__ = "inscripciones"

    __table_args__ = (
        UniqueConstraint(
            "alumno_id",
            "materia_id",
            name="uq_inscripcion_alumno_materia",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    alumno_id: Mapped[int] = mapped_column(
        ForeignKey("alumnos.id"),
        nullable=False,
    )

    materia_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id"),
        nullable=False,
    )

    alumno: Mapped["Alumno"] = relationship(
        back_populates="inscripciones"
    )

    materia: Mapped["Materia"] = relationship(
        back_populates="inscripciones"
    )