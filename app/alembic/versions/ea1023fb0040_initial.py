
"""initial

Revision ID: ea1023fb0040
Revises: 994e7a606d3d
Create Date: 2026-08-29 10:30:49.643115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'ea1023fb0040'
down_revision: Union[str, Sequence[str], None] = '994e7a606d3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

   
    # Add created_at to appointment.
    # First allow NULL because existing rows have no value.
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('created_at', sa.DateTime(), nullable=True)
        )

    # Populate existing appointment rows.
    op.execute(
        "UPDATE appointment "
        "SET created_at = CURRENT_TIMESTAMP "
        "WHERE created_at IS NULL"
    )

    # Now make the column NOT NULL.
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            existing_type=sa.DateTime(),
            nullable=False
        )

    # Add created_at to appointment_owner.
    # Again, allow NULL temporarily because existing rows have no value.
    with op.batch_alter_table('appointment_owner', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('created_at', sa.DateTime(), nullable=True)
        )

    # Populate existing appointment_owner rows.
    op.execute(
        "UPDATE appointment_owner "
        "SET created_at = CURRENT_TIMESTAMP "
        "WHERE created_at IS NULL"
    )

    # Now make the column NOT NULL.
    with op.batch_alter_table('appointment_owner', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            existing_type=sa.DateTime(),
            nullable=False
        )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove created_at from appointment_owner
    with op.batch_alter_table('appointment_owner', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # Remove created_at from appointment
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_column('created_at')

   