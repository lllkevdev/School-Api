"""agregar cascade de inscripciones a calificaciones

Revision ID: 44407db584bf
Revises: 924015851034
Create Date: 2026-10-01 12:19:42.881932

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "44407db584bf"
down_revision: Union[str, Sequence[str], None] = "924015851034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_foreign_key(
        "fk_calificaciones_inscripcion",
        "calificaciones",
        "inscripciones",
        ["alumno_id", "materia_id"],
        ["alumno_id", "materia_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_calificaciones_inscripcion",
        "calificaciones",
        type_="foreignkey",
    )
