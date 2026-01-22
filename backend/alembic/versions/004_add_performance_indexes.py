"""Add performance indexes

Revision ID: 004
Revises: 003
Create Date: 2026-01-22

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes to workout_sessions
    op.create_index('ix_workout_sessions_user_id', 'workout_sessions', ['user_id'])
    op.create_index('ix_workout_sessions_start_time', 'workout_sessions', ['start_time'])
    op.create_index('ix_workout_sessions_end_time', 'workout_sessions', ['end_time'])

    # Add indexes to exercise_logs
    op.create_index('ix_exercise_logs_session_id', 'exercise_logs', ['session_id'])
    op.create_index('ix_exercise_logs_exercise_id', 'exercise_logs', ['exercise_id'])
    op.create_index('ix_exercise_logs_completed_at', 'exercise_logs', ['completed_at'])

    # Add indexes to cardio_sessions
    op.create_index('ix_cardio_sessions_user_id', 'cardio_sessions', ['user_id'])
    op.create_index('ix_cardio_sessions_activity_type', 'cardio_sessions', ['activity_type'])
    op.create_index('ix_cardio_sessions_start_time', 'cardio_sessions', ['start_time'])

    # Add indexes to workout_plans
    op.create_index('ix_workout_plans_user_id', 'workout_plans', ['user_id'])
    op.create_index('ix_workout_plans_is_active', 'workout_plans', ['is_active'])
    op.create_index('ix_workout_plans_created_at', 'workout_plans', ['created_at'])

    # Add indexes to assigned_exercises
    op.create_index('ix_assigned_exercises_exercise_id', 'assigned_exercises', ['exercise_id'])
    op.create_index('ix_assigned_exercises_client_id', 'assigned_exercises', ['client_id'])
    op.create_index('ix_assigned_exercises_personal_trainer_id', 'assigned_exercises', ['personal_trainer_id'])
    op.create_index('ix_assigned_exercises_assigned_at', 'assigned_exercises', ['assigned_at'])

    # Add indexes to weight_history
    op.create_index('ix_weight_history_user_id', 'weight_history', ['user_id'])
    op.create_index('ix_weight_history_recorded_at', 'weight_history', ['recorded_at'])

    # Add indexes to client_metrics
    op.create_index('ix_client_metrics_personal_trainer_id', 'client_metrics', ['personal_trainer_id'])
    # client_id already has unique constraint which creates index


def downgrade():
    # Drop client_metrics indexes
    op.drop_index('ix_client_metrics_personal_trainer_id', table_name='client_metrics')

    # Drop weight_history indexes
    op.drop_index('ix_weight_history_recorded_at', table_name='weight_history')
    op.drop_index('ix_weight_history_user_id', table_name='weight_history')

    # Drop assigned_exercises indexes
    op.drop_index('ix_assigned_exercises_assigned_at', table_name='assigned_exercises')
    op.drop_index('ix_assigned_exercises_personal_trainer_id', table_name='assigned_exercises')
    op.drop_index('ix_assigned_exercises_client_id', table_name='assigned_exercises')
    op.drop_index('ix_assigned_exercises_exercise_id', table_name='assigned_exercises')

    # Drop workout_plans indexes
    op.drop_index('ix_workout_plans_created_at', table_name='workout_plans')
    op.drop_index('ix_workout_plans_is_active', table_name='workout_plans')
    op.drop_index('ix_workout_plans_user_id', table_name='workout_plans')

    # Drop cardio_sessions indexes
    op.drop_index('ix_cardio_sessions_start_time', table_name='cardio_sessions')
    op.drop_index('ix_cardio_sessions_activity_type', table_name='cardio_sessions')
    op.drop_index('ix_cardio_sessions_user_id', table_name='cardio_sessions')

    # Drop exercise_logs indexes
    op.drop_index('ix_exercise_logs_completed_at', table_name='exercise_logs')
    op.drop_index('ix_exercise_logs_exercise_id', table_name='exercise_logs')
    op.drop_index('ix_exercise_logs_session_id', table_name='exercise_logs')

    # Drop workout_sessions indexes
    op.drop_index('ix_workout_sessions_end_time', table_name='workout_sessions')
    op.drop_index('ix_workout_sessions_start_time', table_name='workout_sessions')
    op.drop_index('ix_workout_sessions_user_id', table_name='workout_sessions')
