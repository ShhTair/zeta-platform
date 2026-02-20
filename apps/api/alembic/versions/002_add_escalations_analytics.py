"""add escalations and analytics tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create escalations table
    op.create_table(
        'escalations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('user_telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('user_name', sa.String(), nullable=True),
        sa.Column('product_sku', sa.String(), nullable=True),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('conversation', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_escalations_id', 'escalations', ['id'])
    op.create_index('ix_escalations_user_telegram_id', 'escalations', ['user_telegram_id'])

    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analytics_events_id', 'analytics_events', ['id'])
    op.create_index('ix_analytics_events_event_type', 'analytics_events', ['event_type'])
    op.create_index('ix_analytics_events_created_at', 'analytics_events', ['created_at'])


def downgrade():
    op.drop_index('ix_analytics_events_created_at', table_name='analytics_events')
    op.drop_index('ix_analytics_events_event_type', table_name='analytics_events')
    op.drop_index('ix_analytics_events_id', table_name='analytics_events')
    op.drop_table('analytics_events')
    
    op.drop_index('ix_escalations_user_telegram_id', table_name='escalations')
    op.drop_index('ix_escalations_id', table_name='escalations')
    op.drop_table('escalations')
