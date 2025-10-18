# Database Migrations Guide

## Migration System: Yoyo-Migrations

This project uses **yoyo-migrations** for database schema management. Migrations are automatically applied when the application starts.

## Why Yoyo?

✅ **Automatic**: Runs on app startup - no manual commands needed
✅ **Simple**: Pure Python, no complex configuration
✅ **Safe**: Transactional with rollback support
✅ **Container-friendly**: Perfect for Docker/Podman environments

## How It Works

When you start the backend container:
1. Application initializes database tables
2. **Migrations run automatically**
3. Only pending migrations are applied
4. Already-applied migrations are skipped

You'll see this in the logs:
```
Running database migrations...
Found 1 migration(s)
✓ All migrations applied successfully
Application ready!
```

## Creating a New Migration

### Step 1: Create Migration File

Create a new file in `backend/migrations/` with this naming pattern:
```
XXXX_description.py
```

Examples:
- `0001_add_desired_weight.py`
- `0002_add_user_avatar.py`
- `0003_create_notifications_table.py`

### Step 2: Write the Migration

```python
"""
Brief description of what this migration does
"""

from yoyo import step

# Dependencies (if any)
__depends__ = {'0001_add_desired_weight'}  # Optional: only if this depends on another migration

steps = [
    step(
        # Forward migration (what to do)
        "ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)",

        # Backward migration (how to undo)
        "ALTER TABLE users DROP COLUMN avatar_url"
    )
]
```

### Step 3: Restart the App

That's it! Just restart the backend and the migration runs automatically:

```bash
# Podman
podman restart gym_backend

# Docker Compose
docker-compose restart backend
```

## Migration Examples

### Adding a Column

```python
from yoyo import step

__depends__ = {}

steps = [
    step(
        "ALTER TABLE users ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE",
        "ALTER TABLE users DROP COLUMN phone_verified"
    )
]
```

### Creating a Table

```python
from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE notifications (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        "DROP TABLE notifications"
    )
]
```

### Multiple Changes in One Migration

```python
from yoyo import step

__depends__ = {}

steps = [
    step(
        "ALTER TABLE users ADD COLUMN last_login TIMESTAMP",
        "ALTER TABLE users DROP COLUMN last_login"
    ),
    step(
        "CREATE INDEX idx_user_email ON users(email)",
        "DROP INDEX idx_user_email"
    ),
    step(
        "ALTER TABLE workouts ADD COLUMN difficulty VARCHAR(20)",
        "ALTER TABLE workouts DROP COLUMN difficulty"
    )
]
```

### Using Python Functions (Advanced)

For complex logic, you can use Python functions:

```python
from yoyo import step

__depends__ = {}

def apply_migration(conn):
    cursor = conn.cursor()

    # Get all users
    cursor.execute("SELECT id, weight, height FROM users WHERE weight > 0 AND height > 0")
    users = cursor.fetchall()

    # Calculate and update BMI for each user
    for user_id, weight, height in users:
        bmi = weight / ((height / 100) ** 2)
        cursor.execute("UPDATE users SET bmi = %s WHERE id = %s", (bmi, user_id))

def rollback_migration(conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET bmi = NULL")

steps = [
    step(apply_migration, rollback_migration)
]
```

## Checking Migration Status

You can check which migrations have been applied:

```bash
# From inside the backend container
podman exec gym_backend python3 -c "
from app.db.migrations import run_migrations
from yoyo import read_migrations, get_backend
from app.core.config import settings

db_url = settings.DATABASE_URL.replace('postgresql://', 'postgres://', 1)
backend = get_backend(db_url)
migrations = read_migrations('/app/migrations')

print('Applied migrations:')
for m in backend.to_apply(migrations):
    print(f'  - {m.id}')
"
```

## Rolling Back Migrations

⚠️ **Use with caution!** Only for development/debugging.

```python
# Create a rollback script: backend/rollback.py
from app.db.migrations import rollback_migration

# Rollback the last migration
rollback_migration(steps=1)

# Rollback the last 3 migrations
rollback_migration(steps=3)
```

Run it:
```bash
podman exec gym_backend python3 rollback.py
```

## Best Practices

### ✅ DO:
- **Use descriptive names**: `0002_add_user_avatar.py` not `0002_update.py`
- **Keep migrations small**: One logical change per migration
- **Test rollbacks**: Ensure your rollback works before deploying
- **Use `IF NOT EXISTS`**: Makes migrations idempotent (safe to run multiple times)
- **Commit migrations**: Include migration files in git

### ❌ DON'T:
- **Modify existing migrations**: Once applied, never change them
- **Delete applied migrations**: Can break the migration chain
- **Use migrations for data**: Keep data changes separate from schema
- **Rollback in production**: Only rollback in development

## Migration File Structure

```
backend/
├── migrations/
│   ├── 0001_add_desired_weight.py      ✅ Applied
│   ├── 0002_add_user_avatar.py         ⏳ Pending
│   └── 0003_create_notifications.py    ⏳ Pending
└── app/
    └── db/
        └── migrations.py                # Auto-runner
```

## Troubleshooting

### "Migration failed" error

Check the backend logs:
```bash
podman logs gym_backend | grep -A 10 "Migration error"
```

Common issues:
1. **Syntax error in SQL**: Check your SQL syntax
2. **Column already exists**: Use `IF NOT EXISTS`
3. **Foreign key constraint**: Ensure referenced table/column exists

### Migration runs multiple times

This shouldn't happen - yoyo tracks which migrations have been applied. If it does:
```bash
# Check the yoyo tracking table
podman exec gym_postgres psql -U gymuser -d gymtracker -c "SELECT * FROM _yoyo_migration"
```

### Need to skip a migration

Don't skip migrations! Instead:
1. Fix the migration file
2. If already applied, create a new migration to fix it

## Comparing to Alembic

| Feature | Yoyo | Alembic |
|---------|------|---------|
| Auto-run on startup | ✅ | ❌ |
| Configuration needed | ❌ | ✅ (alembic.ini) |
| Manual commands | ❌ | ✅ (alembic upgrade) |
| ORM integration | ❌ | ✅ |
| Learning curve | Low | Medium-High |
| Best for | Simple schemas, containers | Complex schemas, SQLAlchemy |

## Future Migrations

When you need to make database changes:

1. **Create migration file** in `backend/migrations/`
2. **Write forward and backward steps**
3. **Commit to git**
4. **Deploy** (migrations run automatically)

That's it! No manual intervention needed.

---

## Quick Reference

```bash
# Create new migration
touch backend/migrations/0002_my_change.py

# Restart to apply
podman restart gym_backend

# Check logs
podman logs gym_backend | grep migration

# Check database
podman exec gym_postgres psql -U gymuser -d gymtracker -c "\d table_name"
```

**Happy migrating! 🚀**
