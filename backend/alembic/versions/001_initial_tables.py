"""initial tables

Revision ID: 001
Revises: 
Create Date: 2026-05-30 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('profile_picture', sa.String(length=500), nullable=True),
        sa.Column('google_access_token_encrypted', sa.Text(), nullable=True),
        sa.Column('google_refresh_token_encrypted', sa.Text(), nullable=True),
        sa.Column('google_token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_scan_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('platform_name', sa.String(length=100), nullable=False),
        sa.Column('platform_domain', sa.String(length=100), nullable=False),
        sa.Column('platform_category', sa.String(length=50), nullable=False),
        sa.Column('account_email', sa.String(length=255), nullable=True),
        sa.Column('email_count', sa.Integer(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('is_confirmed', sa.Boolean(), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_user_id'), 'accounts', ['user_id'], unique=False)

    # 3. Create requests table
    # We will create the requeststatus enum type in postgres first
    request_status_enum = postgresql.ENUM('pending', 'sent', 'acknowledged', 'completed', 'rejected', 'expired', name='requeststatus')
    request_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'requests',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('account_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'sent', 'acknowledged', 'completed', 'rejected', 'expired', name='requeststatus'), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('response_received_at', sa.DateTime(), nullable=True),
        sa.Column('email_subject', sa.String(length=500), nullable=True),
        sa.Column('email_body', sa.Text(), nullable=True),
        sa.Column('platform_dpo_email', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requests_account_id'), 'requests', ['account_id'], unique=False)
    op.create_index(op.f('ix_requests_user_id'), 'requests', ['user_id'], unique=False)
    op.create_index(op.f('ix_requests_status'), 'requests', ['status'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_requests_status'), table_name='requests')
    op.drop_index(op.f('ix_requests_user_id'), table_name='requests')
    op.drop_index(op.f('ix_requests_account_id'), table_name='requests')
    op.drop_table('requests')
    
    # Drop enum type
    request_status_enum = postgresql.ENUM('pending', 'sent', 'acknowledged', 'completed', 'rejected', 'expired', name='requeststatus')
    request_status_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index(op.f('ix_accounts_user_id'), table_name='accounts')
    op.drop_table('accounts')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
