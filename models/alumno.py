from typing import TYPE_CHECKING

from sqlalchemy import String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


if TYPE_CHECKING:
    from models.calificacion import Calificacion


class Alumno(Base):
    __tablename__ = "alumnos"


    __table_args__ = (
        CheckConstraint(
            "edad > 0 AND edad < 100",
            name="ck_alumnos_edad"
        ),
    )


    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    apellido: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    edad: Mapped[int] = mapped_column(nullable=False)

    calificaciones: Mapped[list["Calificacion"]] = relationship(
        back_populates="alumno"
    )