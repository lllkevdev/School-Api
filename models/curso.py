from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


if TYPE_CHECKING:
    from models.evaluacion import Evaluacion
    from models.inscripcion import Inscripcion
    from models.usuario import Usuario


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    docente_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )

    nombre_materia: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    division: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    anio_lectivo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    cantidad_periodos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    docente: Mapped["Usuario"] = relationship(
        back_populates="cursos"
    )

    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        back_populates="curso",
    )

    evaluaciones: Mapped[list["Evaluacion"]] = relationship(
        back_populates="curso",
    )