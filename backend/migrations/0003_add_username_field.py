"""
Add username field to users table
"""

from yoyo import step

__depends__ = {'0002_add_roles_and_multi_tenant'}

steps = [
    step(
        """
        ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(255);
        """,
        """
        ALTER TABLE users DROP COLUMN IF EXISTS username;
        """
    ),
    step(
        """
        UPDATE users
        SET username = SPLIT_PART(email, '@', 1) || '_' || SUBSTRING(id FROM 1 FOR 8)
        WHERE username IS NULL;
        """,
        ""
    ),
    step(
        """
        ALTER TABLE users ALTER COLUMN username SET NOT NULL;
        """,
        ""
    ),
    step(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username);
        """,
        """
        DROP INDEX IF EXISTS ix_users_username;
        """
    )
]
