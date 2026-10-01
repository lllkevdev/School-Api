from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.inscripcion import Inscripcion

if TYPE_CHECKING:
    from models.calificacion import Calificacion
    from models.usuario import Usuario


class Materia(Base):
    __tablename__ = "materias"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    calificaciones: Mapped[list["Calificacion"]] = relationship(
        back_populates="materia"
    )


    maestro_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=True
    )

    maestro: Mapped["Usuario"] = relationship(
        back_populates="materias"
    )

    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        back_populates="materia"
    )