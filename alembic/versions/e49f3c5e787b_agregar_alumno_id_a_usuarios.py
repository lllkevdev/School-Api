"""agregar alumno_id a usuarios

Revision ID: e49f3c5e787b
Revises: 673e2e72a793
Create Date: 2026-09-22 19:47:21.249323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e49f3c5e787b'
down_revision: Union[str, Sequence[str], None] = '673e2e72a793'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'usuarios',
        sa.Column('alumno_id', sa.Integer(), nullable=True)
    )

    op.create_unique_constraint(
        'uq_usuarios_alumno_id',
        'usuarios',
        ['alumno_id']
    )

    op.create_foreign_key(
        'fk_usuarios_alumno_id',
        'usuarios',
        'alumnos',
        ['alumno_id'],
        ['id']
    )



def downgrade() -> None:
    op.drop_constraint(
        'fk_usuarios_alumno_id',
        'usuarios',
        type_='foreignkey'
    )

    op.drop_constraint(
        'uq_usuarios_alumno_id',
        'usuarios',
        type_='unique'
    )  