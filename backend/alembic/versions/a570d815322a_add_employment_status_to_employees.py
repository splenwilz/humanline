"""add_employment_status_to_employees

Revision ID: a570d815322a
Revises: d6dfdaad75c4
Create Date: 2025-10-11 23:34:26.499314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a570d815322a'
down_revision: Union[str, Sequence[str], None] = 'd6dfdaad75c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add employment_status column to employees table
    op.add_column('employees', sa.Column('employment_status', sa.String(length=50), nullable=True, default='ACTIVE'))
    
    # Update existing records to have ACTIVE status
    op.execute("UPDATE employees SET employment_status = 'ACTIVE' WHERE employment_status IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove employment_status column from employees table
    op.drop_column('employees', 'employment_status')
