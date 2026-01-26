"""
Add equipment_number and notes fields to plan_exercises
- equipment_number: Which equipment to use (e.g., "Machine 5", "Bench 3")
- notes: PT instructions/observations for the client
"""

from yoyo import step

__depends__ = {'0006_convert_numeric_to_text'}

steps = [
    # Add equipment_number column
    step(
        """
        ALTER TABLE plan_exercises
        ADD COLUMN IF NOT EXISTS equipment_number VARCHAR,
        ADD COLUMN IF NOT EXISTS notes TEXT
        """,
        """
        ALTER TABLE plan_exercises
        DROP COLUMN IF EXISTS equipment_number,
        DROP COLUMN IF EXISTS notes
        """
    )
]
