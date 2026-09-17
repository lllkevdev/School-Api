"""agregar checks a calificaciones

Revision ID: b8253f2d882e
Revises: 605e5c5357a5
Create Date: 2026-09-16 00:05:13.090099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8253f2d882e'
down_revision: Union[str, Sequence[str], None] = '605e5c5357a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_calificaciones_nota",
        "calificaciones",
        "nota >= 1 AND nota <= 10"
    )

    op.create_check_constraint(
        "ck_calificaciones_periodo",
        "calificaciones",
        "periodo >= 1 AND periodo <= 3"
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_calificaciones_periodo",
        "calificaciones",
        type_="check"
    )

    op.drop_constraint(
        "ck_calificaciones_nota",
        "calificaciones",
        type_="check"
    )