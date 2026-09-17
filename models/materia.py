from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


if TYPE_CHECKING:
    from models.calificacion import Calificacion


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