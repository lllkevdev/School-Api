from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from schemas.roles import Rol


if TYPE_CHECKING:
    from models.alumno import Alumno
    from models.curso import Curso
    from models.invitacion import Invitacion


class Usuario(Base):
    __tablename__ = "usuarios"

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
        default="",
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )

    telefono: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    rol: Mapped[Rol] = mapped_column(
        Enum(
            Rol,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    cursos: Mapped[list["Curso"]] = relationship(
        back_populates="docente",
    )

    alumno_id: Mapped[int | None] = mapped_column(
        ForeignKey("alumnos.id"),
        nullable=True,
        unique=True,
    )

    alumno: Mapped["Alumno | None"] = relationship()

    invitaciones: Mapped[list["Invitacion"]] = relationship(
        back_populates="docente",
    )