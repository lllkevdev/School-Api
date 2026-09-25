from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base

from typing import TYPE_CHECKING

from schemas.roles import Rol

if TYPE_CHECKING:
    from models.materia import Materia
    from models.alumno import Alumno





class Usuario(Base):
    __tablename__ = "usuarios"



    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )



    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )



    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )



    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )



    rol: Mapped[Rol] = mapped_column(
        Enum(
            Rol,
            values_callable=lambda enum: [item.value for item in enum]
        ),
        nullable=False
    )



    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )



    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )



    materias: Mapped[list["Materia"]] = relationship(
        back_populates="maestro"
    )



    alumno_id: Mapped[int | None] = mapped_column(
        ForeignKey("alumnos.id"),
        nullable=True,
        unique=True
    )

    alumno: Mapped["Alumno | None"] = relationship()