"""convertir rol de usuario a enum

Revision ID: ff23908a2cb2
Revises: 6596ec8a486e
Create Date: 2026-09-17 20:03:19.518311

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff23908a2cb2'
down_revision: Union[str, Sequence[str], None] = '6596ec8a486e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    rol_enum = sa.Enum(
        "admin",
        "maestro",
        "alumno",
        name="rol"
    )

    rol_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "usuarios",
        "rol",
        existing_type=sa.String(length=20),
        type_=rol_enum,
        existing_nullable=False,
        postgresql_using="rol::rol"
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "usuarios",
        "rol",
        existing_type=sa.Enum(
            "admin",
            "maestro",
            "alumno",
            name="rol"
        ),
        type_=sa.String(length=20),
        existing_nullable=False,
        postgresql_using="rol::text"
    )

    sa.Enum(
        "admin",
        "maestro",
        "alumno",
        name="rol"
    ).drop(op.get_bind(), checkfirst=True)