#!/usr/bin/env python3
"""
Script to reset all user passwords to 'password123'
Usage: python reset_passwords.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash


def reset_all_passwords():
    """Reset all user passwords to 'password123'"""
    db = SessionLocal()

    try:
        # New password
        new_password = "password123"
        hashed_password = get_password_hash(new_password)

        # Get all users
        users = db.query(User).all()

        if not users:
            print("No users found in database.")
            return

        print(f"Found {len(users)} users. Resetting passwords...")

        # Update all users
        updated_count = 0
        for user in users:
            user.hashed_password = hashed_password
            updated_count += 1
            print(f"✓ Updated password for: {user.email} (username: {user.username})")

        # Commit changes
        db.commit()

        print(f"\n✅ Successfully reset passwords for {updated_count} users!")
        print(f"All users can now login with password: {new_password}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("PASSWORD RESET SCRIPT")
    print("=" * 60)
    print("This will reset ALL user passwords to: password123")
    print("=" * 60)
    print()

    # Confirm action
    response = input("Are you sure you want to continue? (yes/no): ").lower().strip()

    if response == "yes":
        reset_all_passwords()
    else:
        print("\n❌ Operation cancelled.")
