"""
Add user roles, language preference, client-trainer relationships, and assigned exercises table
This migration transforms the app from single-user to multi-tenant (Personal Trainers + Clients)
"""

from yoyo import step

__depends__ = {'0001_add_desired_weight'}

steps = [
    # Add role column to users table
    step(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                CREATE TYPE userrole AS ENUM ('personal_trainer', 'client');
            END IF;
        END$$;
        """,
        "DROP TYPE IF EXISTS userrole;"
    ),

    step(
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS role userrole;

        UPDATE users SET role = 'client'::userrole WHERE role IS NULL;

        ALTER TABLE users
        ALTER COLUMN role SET DEFAULT 'client'::userrole,
        ALTER COLUMN role SET NOT NULL;
        """,
        "ALTER TABLE users DROP COLUMN IF EXISTS role;"
    ),

    # Add language column
    step(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(2) NOT NULL DEFAULT 'en'",
        "ALTER TABLE users DROP COLUMN IF EXISTS language"
    ),

    # Add personal_trainer_id for client-trainer relationship
    step(
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS personal_trainer_id VARCHAR
        REFERENCES users(id) ON DELETE SET NULL;

        CREATE INDEX IF NOT EXISTS idx_users_personal_trainer
        ON users(personal_trainer_id);
        """,
        """
        DROP INDEX IF EXISTS idx_users_personal_trainer;
        ALTER TABLE users DROP COLUMN IF EXISTS personal_trainer_id;
        """
    ),

    # Update exercises table: created_by should be NOT NULL and reference users
    step(
        """
        ALTER TABLE exercises
        DROP CONSTRAINT IF EXISTS exercises_created_by_fkey;

        ALTER TABLE exercises
        ALTER COLUMN created_by SET NOT NULL;

        ALTER TABLE exercises
        ADD CONSTRAINT exercises_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE;
        """,
        """
        ALTER TABLE exercises
        DROP CONSTRAINT IF EXISTS exercises_created_by_fkey;

        ALTER TABLE exercises
        ALTER COLUMN created_by DROP NOT NULL;
        """
    ),

    # Create assigned_exercises table
    step(
        """
        CREATE TABLE IF NOT EXISTS assigned_exercises (
            id VARCHAR PRIMARY KEY,
            exercise_id VARCHAR NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
            client_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            personal_trainer_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            notes TEXT,
            UNIQUE(exercise_id, client_id)
        );

        CREATE INDEX IF NOT EXISTS idx_assigned_exercises_client
        ON assigned_exercises(client_id);

        CREATE INDEX IF NOT EXISTS idx_assigned_exercises_trainer
        ON assigned_exercises(personal_trainer_id);
        """,
        """
        DROP INDEX IF EXISTS idx_assigned_exercises_trainer;
        DROP INDEX IF EXISTS idx_assigned_exercises_client;
        DROP TABLE IF EXISTS assigned_exercises;
        """
    )
]
