"""agregar check de edad a alumnos

Revision ID: ffdba5543a54
Revises: b8253f2d882e
Create Date: 2026-09-17 15:05:47.722107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffdba5543a54'
down_revision: Union[str, Sequence[str], None] = 'b8253f2d882e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_alumnos_edad",
        "alumnos",
        "edad > 0 AND edad < 100"
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_alumnos_edad",
        "alumnos",
        type_="check"
    )