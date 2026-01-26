"""
Convert sets, reps, and rest_time fields from numeric to text
This allows flexible input like 'Max', 'Min', '70Kcal', '5'', '10-12', etc.
"""

from yoyo import step

__depends__ = {'0005_add_login_attempts_and_indexes'}

steps = [
    # Convert plan_exercises columns to text
    step(
        """
        ALTER TABLE plan_exercises
        ALTER COLUMN sets TYPE VARCHAR USING sets::VARCHAR,
        ALTER COLUMN reps TYPE VARCHAR USING reps::VARCHAR,
        ALTER COLUMN rest_time TYPE VARCHAR USING rest_time::VARCHAR
        """,
        """
        ALTER TABLE plan_exercises
        ALTER COLUMN sets TYPE INTEGER USING sets::INTEGER,
        ALTER COLUMN reps TYPE INTEGER USING reps::INTEGER,
        ALTER COLUMN rest_time TYPE INTEGER USING rest_time::INTEGER
        """
    ),

    # Convert exercise_logs columns to text
    step(
        """
        ALTER TABLE exercise_logs
        ALTER COLUMN sets_completed TYPE VARCHAR USING sets_completed::VARCHAR,
        ALTER COLUMN reps_completed TYPE VARCHAR USING reps_completed::VARCHAR,
        ALTER COLUMN rest_time_actual TYPE VARCHAR USING COALESCE(rest_time_actual::VARCHAR, NULL)
        """,
        """
        ALTER TABLE exercise_logs
        ALTER COLUMN sets_completed TYPE INTEGER USING sets_completed::INTEGER,
        ALTER COLUMN reps_completed TYPE INTEGER USING reps_completed::INTEGER,
        ALTER COLUMN rest_time_actual TYPE INTEGER USING rest_time_actual::INTEGER
        """
    )
]
