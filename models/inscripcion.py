from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


if TYPE_CHECKING:
    from models.alumno import Alumno
    from models.curso import Curso


class Inscripcion(Base):
    __tablename__ = "inscripciones"

    __table_args__ = (
        UniqueConstraint(
            "alumno_id",
            "curso_id",
            name="uq_inscripcion_alumno_curso",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    alumno_id: Mapped[int] = mapped_column(
        ForeignKey("alumnos.id"),
        nullable=False,
    )

    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id"),
        nullable=False,
    )

    alumno: Mapped["Alumno"] = relationship(
        back_populates="inscripciones",
    )

    curso: Mapped["Curso"] = relationship(
        back_populates="inscripciones",
    )