"""
Add desired_weight column to users table
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS desired_weight FLOAT",
        "ALTER TABLE users DROP COLUMN IF EXISTS desired_weight"
    )
]
