"""crear usuarios

Revision ID: 6596ec8a486e
Revises: ffdba5543a54
Create Date: 2026-09-17 18:53:01.727212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6596ec8a486e'
down_revision: Union[str, Sequence[str], None] = 'ffdba5543a54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('rol', sa.String(length=20), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_usuarios_email'),
        'usuarios',
        ['email'],
        unique=True
    )

    op.create_index(
        op.f('ix_usuarios_id'),
        'usuarios',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_usuarios_id'),
        table_name='usuarios'
    )

    op.drop_index(
        op.f('ix_usuarios_email'),
        table_name='usuarios'
    )

    op.drop_table('usuarios')