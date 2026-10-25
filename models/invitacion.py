from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


if TYPE_CHECKING:
    from models.alumno import Alumno
    from models.curso import Curso
    from models.usuario import Usuario


class Invitacion(Base):
    __tablename__ = "invitaciones"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    alumno_id: Mapped[int] = mapped_column(
        ForeignKey("alumnos.id"),
        nullable=False,
        index=True,
    )

    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id"),
        nullable=False,
        index=True,
    )

    docente_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    expira_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    aceptada_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revocada_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    creada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default= lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    alumno: Mapped["Alumno"] = relationship(
        back_populates="invitaciones",
    )

    curso: Mapped["Curso"] = relationship(
        back_populates="invitaciones",
    )

    docente: Mapped["Usuario"] = relationship(
        back_populates="invitaciones",
    )

    @property
    def revocada(self) -> bool:
        return self.revocada_en is not None