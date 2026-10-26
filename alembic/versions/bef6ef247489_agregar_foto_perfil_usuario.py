"""agregar foto perfil usuario

Revision ID: bef6ef247489
Revises: 72335e404ca2
Create Date: 2026-10-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bef6ef247489"
down_revision: Union[str, Sequence[str], None] = "72335e404ca2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "usuarios",
        sa.Column(
            "foto_perfil",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("usuarios", "foto_perfil")
