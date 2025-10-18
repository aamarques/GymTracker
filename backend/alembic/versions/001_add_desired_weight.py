"""Add desired_weight field to users

Revision ID: 001_add_desired_weight
Revises:
Create Date: 2025-10-12 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_desired_weight'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add desired_weight column to users table
    op.add_column('users', sa.Column('desired_weight', sa.Float(), nullable=True))


def downgrade():
    # Remove desired_weight column from users table
    op.drop_column('users', 'desired_weight')
