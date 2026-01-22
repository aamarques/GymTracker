"""Add login attempts tracking

Revision ID: 003
Revises: 002
Create Date: 2026-01-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create login_attempts table
    op.create_table(
        'login_attempts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('identifier', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True, default=False),
        sa.Column('attempted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('ix_login_attempts_identifier', 'login_attempts', ['identifier'])
    op.create_index('ix_login_attempts_attempted_at', 'login_attempts', ['attempted_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_login_attempts_attempted_at', table_name='login_attempts')
    op.drop_index('ix_login_attempts_identifier', table_name='login_attempts')

    # Drop table
    op.drop_table('login_attempts')
