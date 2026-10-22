from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.inscripcion import Inscripcion
from models.invitacion import Invitacion


if TYPE_CHECKING:
    from models.calificacion import Calificacion


class Alumno(Base):
    __tablename__ = "alumnos"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    apellido: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    documento_identidad: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    fecha_nacimiento: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    calificaciones: Mapped[list["Calificacion"]] = relationship(
        back_populates="alumno",
    )

    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        back_populates="alumno",
    )

    invitaciones: Mapped[list["Invitacion"]] = relationship(
        back_populates="alumno",
    )