"""agregar maestro a materias

Revision ID: 673e2e72a793
Revises: ff23908a2cb2
Create Date: 2026-09-21 21:21:54.292693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '673e2e72a793'
down_revision: Union[str, Sequence[str], None] = 'ff23908a2cb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "materias",
        sa.Column(
            "maestro_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_materias_maestro_id",
        "materias",
        "usuarios",
        ["maestro_id"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_materias_maestro_id",
        "materias",
        type_="foreignkey"
    )

    op.drop_column(
        "materias",
        "maestro_id"
    )