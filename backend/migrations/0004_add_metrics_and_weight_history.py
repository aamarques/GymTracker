"""
Add client metrics and weight history tables for tracking client progress
"""

from yoyo import step

__depends__ = {'0003_add_username_field'}

steps = [
    # Create weight_history table
    step(
        """
        CREATE TABLE IF NOT EXISTS weight_history (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            weight FLOAT NOT NULL,
            previous_weight FLOAT,
            days_since_last_change INTEGER,
            recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            CONSTRAINT weight_positive CHECK (weight > 0)
        );
        """,
        """
        DROP TABLE IF EXISTS weight_history;
        """
    ),

    # Create index on user_id for weight_history
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_weight_history_user_id ON weight_history(user_id);
        """,
        """
        DROP INDEX IF EXISTS ix_weight_history_user_id;
        """
    ),

    # Create index on recorded_at for weight_history
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_weight_history_recorded_at ON weight_history(recorded_at DESC);
        """,
        """
        DROP INDEX IF EXISTS ix_weight_history_recorded_at;
        """
    ),

    # Create client_metrics table
    step(
        """
        CREATE TABLE IF NOT EXISTS client_metrics (
            id VARCHAR(255) PRIMARY KEY,
            client_id VARCHAR(255) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            personal_trainer_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,

            -- Workout metrics
            total_workouts_completed INTEGER DEFAULT 0,
            total_cardio_sessions INTEGER DEFAULT 0,
            total_training_hours FLOAT DEFAULT 0.0,
            total_training_days INTEGER DEFAULT 0,

            -- Series and reps tracking
            total_sets_completed INTEGER DEFAULT 0,
            total_reps_completed INTEGER DEFAULT 0,

            -- Weight tracking
            initial_weight FLOAT,
            current_weight FLOAT,
            lowest_weight FLOAT,
            highest_weight FLOAT,
            total_weight_changes INTEGER DEFAULT 0,
            average_days_between_weight_changes FLOAT,

            -- Client resets
            times_workouts_reset INTEGER DEFAULT 0,
            last_reset_date TIMESTAMP WITH TIME ZONE,
            workouts_before_last_reset INTEGER DEFAULT 0,

            -- Consistency metrics
            consistency_percentage FLOAT,
            average_workout_duration_minutes FLOAT,

            -- Timestamps
            client_since TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_activity_date TIMESTAMP WITH TIME ZONE,
            last_updated TIMESTAMP WITH TIME ZONE,

            CONSTRAINT positive_metrics CHECK (
                total_workouts_completed >= 0 AND
                total_cardio_sessions >= 0 AND
                total_training_hours >= 0 AND
                total_training_days >= 0 AND
                total_sets_completed >= 0 AND
                total_reps_completed >= 0 AND
                times_workouts_reset >= 0
            )
        );
        """,
        """
        DROP TABLE IF EXISTS client_metrics;
        """
    ),

    # Create index on client_id for client_metrics
    step(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ix_client_metrics_client_id ON client_metrics(client_id);
        """,
        """
        DROP INDEX IF EXISTS ix_client_metrics_client_id;
        """
    ),

    # Create index on personal_trainer_id for client_metrics
    step(
        """
        CREATE INDEX IF NOT EXISTS ix_client_metrics_pt_id ON client_metrics(personal_trainer_id);
        """,
        """
        DROP INDEX IF EXISTS ix_client_metrics_pt_id;
        """
    ),

    # Populate initial weight history for existing users
    step(
        """
        INSERT INTO weight_history (id, user_id, weight, previous_weight, days_since_last_change, recorded_at)
        SELECT
            CONCAT(id, '-initial') as id,
            id as user_id,
            weight,
            NULL as previous_weight,
            NULL as days_since_last_change,
            created_at as recorded_at
        FROM users
        WHERE NOT EXISTS (
            SELECT 1 FROM weight_history WHERE weight_history.user_id = users.id
        );
        """,
        ""
    ),

    # Create initial metrics for existing clients
    step(
        """
        INSERT INTO client_metrics (
            id,
            client_id,
            personal_trainer_id,
            initial_weight,
            current_weight,
            lowest_weight,
            highest_weight,
            total_workouts_completed,
            total_cardio_sessions,
            client_since
        )
        SELECT
            CONCAT(u.id, '-metrics') as id,
            u.id as client_id,
            u.personal_trainer_id,
            u.weight as initial_weight,
            u.weight as current_weight,
            u.weight as lowest_weight,
            u.weight as highest_weight,
            COALESCE((
                SELECT COUNT(*)
                FROM workout_sessions ws
                WHERE ws.user_id = u.id AND ws.end_time IS NOT NULL
            ), 0) as total_workouts_completed,
            COALESCE((
                SELECT COUNT(*)
                FROM cardio_sessions cs
                WHERE cs.user_id = u.id
            ), 0) as total_cardio_sessions,
            u.created_at as client_since
        FROM users u
        WHERE u.role = 'client'
        AND NOT EXISTS (
            SELECT 1 FROM client_metrics WHERE client_metrics.client_id = u.id
        );
        """,
        ""
    )
]
