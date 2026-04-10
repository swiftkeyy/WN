"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-09 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('language_code', sa.String(length=16), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)

    op.create_table(
        'prompt_templates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=128), nullable=False),
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_prompt_templates_category', 'prompt_templates', ['category'], unique=False)
    op.create_index('ix_prompt_templates_is_active', 'prompt_templates', ['is_active'], unique=False)
    op.create_index('ix_prompt_templates_key', 'prompt_templates', ['key'], unique=True)

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_type', sa.String(length=64), nullable=False),
        sa.Column('input_text', sa.Text(), nullable=True),
        sa.Column('input_file_path', sa.String(length=1024), nullable=True),
        sa.Column('output_file_path', sa.String(length=1024), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_tasks_status', 'tasks', ['status'], unique=False)
    op.create_index('ix_tasks_task_type', 'tasks', ['task_type'], unique=False)
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'], unique=False)

    op.create_table(
        'user_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=128), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_history_action_type', 'user_history', ['action_type'], unique=False)
    op.create_index('ix_user_history_user_id', 'user_history', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_history_user_id', table_name='user_history')
    op.drop_index('ix_user_history_action_type', table_name='user_history')
    op.drop_table('user_history')
    op.drop_index('ix_tasks_user_id', table_name='tasks')
    op.drop_index('ix_tasks_task_type', table_name='tasks')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_table('tasks')
    op.drop_index('ix_prompt_templates_key', table_name='prompt_templates')
    op.drop_index('ix_prompt_templates_is_active', table_name='prompt_templates')
    op.drop_index('ix_prompt_templates_category', table_name='prompt_templates')
    op.drop_table('prompt_templates')
    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_table('users')
