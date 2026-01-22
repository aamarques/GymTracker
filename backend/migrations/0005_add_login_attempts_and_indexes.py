"""
Add login attempts tracking table and performance indexes for security and optimization
"""

from yoyo import step

__depends__ = {'0004_add_metrics_and_weight_history'}

steps = [
    # Create login_attempts table
    step(
        """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id VARCHAR(255) PRIMARY KEY,
            identifier VARCHAR(255) NOT NULL,
            ip_address VARCHAR(255),
            success BOOLEAN DEFAULT FALSE,
            attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        DROP TABLE IF EXISTS login_attempts;
        """
    ),

    # Create indexes for login_attempts
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_login_attempts_identifier ON login_attempts(identifier);
        """,
        """
        DROP INDEX IF EXISTS ix_login_attempts_identifier;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_login_attempts_attempted_at ON login_attempts(attempted_at);
        """,
        """
        DROP INDEX IF EXISTS ix_login_attempts_attempted_at;
        """
    ),

    # Add performance indexes to workout_sessions
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_workout_sessions_user_id ON workout_sessions(user_id);
        """,
        """
        DROP INDEX IF EXISTS ix_workout_sessions_user_id;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_workout_sessions_start_time ON workout_sessions(start_time);
        """,
        """
        DROP INDEX IF EXISTS ix_workout_sessions_start_time;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_workout_sessions_end_time ON workout_sessions(end_time);
        """,
        """
        DROP INDEX IF EXISTS ix_workout_sessions_end_time;
        """
    ),

    # Add indexes to exercise_logs
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_exercise_logs_session_id ON exercise_logs(session_id);
        """,
        """
        DROP INDEX IF EXISTS ix_exercise_logs_session_id;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_exercise_logs_exercise_id ON exercise_logs(exercise_id);
        """,
        """
        DROP INDEX IF EXISTS ix_exercise_logs_exercise_id;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_exercise_logs_completed_at ON exercise_logs(completed_at);
        """,
        """
        DROP INDEX IF EXISTS ix_exercise_logs_completed_at;
        """
    ),

    # Add indexes to cardio_sessions
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_cardio_sessions_user_id ON cardio_sessions(user_id);
        """,
        """
        DROP INDEX IF EXISTS ix_cardio_sessions_user_id;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_cardio_sessions_activity_type ON cardio_sessions(activity_type);
        """,
        """
        DROP INDEX IF EXISTS ix_cardio_sessions_activity_type;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_cardio_sessions_start_time ON cardio_sessions(start_time);
        """,
        """
        DROP INDEX IF EXISTS ix_cardio_sessions_start_time;
        """
    ),

    # Add indexes to workout_plans
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_workout_plans_user_id ON workout_plans(user_id);
        """,
        """
        DROP INDEX IF EXISTS ix_workout_plans_user_id;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_workout_plans_is_active ON workout_plans(is_active);
        """,
        """
        DROP INDEX IF EXISTS ix_workout_plans_is_active;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_workout_plans_created_at ON workout_plans(created_at);
        """,
        """
        DROP INDEX IF EXISTS ix_workout_plans_created_at;
        """
    ),

    # Add indexes to assigned_exercises
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_assigned_exercises_exercise_id ON assigned_exercises(exercise_id);
        """,
        """
        DROP INDEX IF EXISTS ix_assigned_exercises_exercise_id;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_assigned_exercises_client_id ON assigned_exercises(client_id);
        """,
        """
        DROP INDEX IF EXISTS ix_assigned_exercises_client_id;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_assigned_exercises_personal_trainer_id ON assigned_exercises(personal_trainer_id);
        """,
        """
        DROP INDEX IF EXISTS ix_assigned_exercises_personal_trainer_id;
        """
    ),

    step(
        """
        CREATE INDEX IF NOT EXISTS ix_assigned_exercises_assigned_at ON assigned_exercises(assigned_at);
        """,
        """
        DROP INDEX IF EXISTS ix_assigned_exercises_assigned_at;
        """
    ),
]
