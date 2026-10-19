from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


if TYPE_CHECKING:
    from models.calificacion import Calificacion
    from models.curso import Curso


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    __table_args__ = (
        CheckConstraint(
            "periodo >= 1",
            name="ck_evaluaciones_periodo_positivo",
        ),
        UniqueConstraint(
            "id",
            "curso_id",
            name="uq_evaluacion_id_curso",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id"),
        nullable=False,
        index=True,
    )

    titulo: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    periodo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    curso: Mapped["Curso"] = relationship(
        back_populates="evaluaciones",
    )

    calificaciones: Mapped[list["Calificacion"]] = relationship(
        back_populates="evaluacion",
        foreign_keys="Calificacion.evaluacion_id",
    )