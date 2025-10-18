"""
Database migration runner using yoyo-migrations
Automatically applies pending migrations on application startup
"""

import os
from yoyo import read_migrations, get_backend
from app.core.config import settings


def run_migrations():
    """
    Run pending database migrations
    This is called automatically when the application starts
    """
    try:
        # Get database URL from settings
        db_url = settings.DATABASE_URL

        # Convert SQLAlchemy URL format to yoyo format if needed
        # SQLAlchemy: postgresql://user:pass@host:port/db
        # Yoyo: postgresql://user:pass@host:port/db (same format, but need to ensure compatibility)
        if db_url.startswith('postgresql://'):
            # Yoyo prefers 'postgres://' over 'postgresql://'
            db_url = db_url.replace('postgresql://', 'postgres://', 1)

        # Get the migrations directory
        migrations_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'migrations'
        )

        # Initialize yoyo backend
        backend = get_backend(db_url)

        # Read migrations from directory
        migrations = read_migrations(migrations_dir)

        # Apply pending migrations
        if migrations:
            print(f"Found {len(migrations)} migration(s)")
            with backend.lock():
                backend.apply_migrations(backend.to_apply(migrations))
                print("✓ All migrations applied successfully")
        else:
            print("No migrations found")

    except Exception as e:
        print(f"⚠ Migration error: {e}")
        print("Application will continue, but database schema may be outdated")
        # Don't crash the app if migrations fail - let it start anyway


def rollback_migration(steps=1):
    """
    Rollback the last N migrations
    This is a utility function for development/debugging
    """
    try:
        db_url = settings.DATABASE_URL
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgres://', 1)

        migrations_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'migrations'
        )

        backend = get_backend(db_url)
        migrations = read_migrations(migrations_dir)

        with backend.lock():
            to_rollback = backend.to_rollback(migrations)[:steps]
            backend.rollback_migrations(to_rollback)
            print(f"✓ Rolled back {len(to_rollback)} migration(s)")

    except Exception as e:
        print(f"⚠ Rollback error: {e}")
