"""add password reset tokens table

Revision ID: 002
Revises: 001
Create Date: 2025-01-20
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create index on token for fast lookups
    op.create_index('ix_password_reset_tokens_token', 'password_reset_tokens', ['token'], unique=True)


def downgrade():
    # Drop index
    op.drop_index('ix_password_reset_tokens_token', table_name='password_reset_tokens')

    # Drop table
    op.drop_table('password_reset_tokens')
