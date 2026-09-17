from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


if TYPE_CHECKING:
    from models.alumno import Alumno
    from models.materia import Materia


class Calificacion(Base):
    __tablename__ = "calificaciones"

    __table_args__ = (
        CheckConstraint(
            "nota >= 1 AND nota <= 10",
            name="ck_calificaciones_nota"
        ),
        CheckConstraint(
            "periodo >= 1 AND periodo <= 3",
            name="ck_calificaciones_periodo"
        )
    )



    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    alumno_id: Mapped[int] = mapped_column(
        ForeignKey("alumnos.id"),
        nullable=False
    )

    materia_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id"),
        nullable=False
    )

    nota: Mapped[float] = mapped_column(nullable=False)
    periodo: Mapped[int] = mapped_column(nullable=False)

    alumno: Mapped["Alumno"] = relationship(
        back_populates="calificaciones"
    )

    materia: Mapped["Materia"] = relationship(
        back_populates="calificaciones"
    )