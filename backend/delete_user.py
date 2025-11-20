#!/usr/bin/env python3
"""
Script to delete one or more users from the database
Usage:
    python delete_user.py                           # Interactive mode
    python delete_user.py --email user@example.com
    python delete_user.py --username john_doe
    python delete_user.py --id uuid-string
"""

import sys
import os
import argparse

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import User


def delete_user(db, user):
    """Delete a specific user"""
    try:
        user_info = f"{user.name} ({user.email}) - Username: {user.username}"

        # Show what will be deleted
        print(f"\n⚠️  DELETING USER: {user_info}")
        print("⚠️  This will also delete:")
        print("    - All workout plans")
        print("    - All workout sessions")
        print("    - All exercise logs")
        print("    - All cardio sessions")
        print("    - All created exercises")
        print("    - All client metrics")
        print("    - All weight history")

        if user.role == "personal_trainer":
            client_count = len(user.clients)
            print(f"    - This trainer has {client_count} client(s) (clients will not be deleted)")

        confirm = input("\n⚠️  Are you ABSOLUTELY sure? Type 'DELETE' to confirm: ").strip()

        if confirm != 'DELETE':
            print("❌ Deletion cancelled.")
            return False

        # Delete user (cascade will handle related records)
        db.delete(user)
        db.commit()

        print(f"✅ Successfully deleted user: {user_info}")
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting user: {str(e)}")
        return False


def delete_by_email(db, email):
    """Delete user by email"""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        print(f"❌ User not found with email: {email}")
        return False

    return delete_user(db, user)


def delete_by_username(db, username):
    """Delete user by username"""
    user = db.query(User).filter(User.username == username).first()

    if not user:
        print(f"❌ User not found with username: {username}")
        return False

    return delete_user(db, user)


def delete_by_id(db, user_id):
    """Delete user by ID"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        print(f"❌ User not found with ID: {user_id}")
        return False

    return delete_user(db, user)


def interactive_mode(db):
    """Interactive mode to select users for deletion"""
    users = db.query(User).all()

    if not users:
        print("No users found in database.")
        return

    print("\n" + "=" * 80)
    print("AVAILABLE USERS:")
    print("=" * 80)

    for idx, user in enumerate(users, 1):
        client_info = ""
        if user.role == "personal_trainer":
            client_count = len(user.clients)
            client_info = f" - {client_count} client(s)"

        print(f"{idx}. {user.name} ({user.email})")
        print(f"    Username: {user.username} | Role: {user.role}{client_info}")

    print("\n" + "=" * 80)
    print("Enter user numbers separated by commas (e.g., 1,3,5)")
    print("⚠️  WARNING: This action cannot be undone!")
    print("=" * 80)

    choice = input("\nYour choice (or 'cancel' to abort): ").strip().lower()

    if choice == 'cancel':
        print("❌ Operation cancelled.")
        return

    try:
        indices = [int(x.strip()) for x in choice.split(',')]
        selected_users = [users[i-1] for i in indices if 1 <= i <= len(users)]

        if not selected_users:
            print("❌ No valid users selected.")
            return

        print(f"\n⚠️  You selected {len(selected_users)} user(s) for deletion:")
        for user in selected_users:
            print(f"  - {user.name} ({user.email})")

        confirm = input(f"\n⚠️  Type 'DELETE ALL' to confirm deletion of {len(selected_users)} user(s): ").strip()

        if confirm == 'DELETE ALL':
            success_count = 0
            for user in selected_users:
                print(f"\nProcessing: {user.email}")
                # Delete without additional confirmation since we already confirmed
                try:
                    db.delete(user)
                    db.commit()
                    print(f"✅ Deleted: {user.name} ({user.email})")
                    success_count += 1
                except Exception as e:
                    db.rollback()
                    print(f"❌ Error deleting {user.email}: {str(e)}")

            print(f"\n✅ Successfully deleted {success_count}/{len(selected_users)} users!")
        else:
            print("❌ Operation cancelled.")

    except (ValueError, IndexError) as e:
        print(f"❌ Invalid input: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Delete users from database')
    parser.add_argument('--email', type=str, help='Delete user by email')
    parser.add_argument('--username', type=str, help='Delete user by username')
    parser.add_argument('--id', type=str, help='Delete user by ID')

    args = parser.parse_args()

    db = SessionLocal()

    try:
        print("=" * 80)
        print("DELETE USER SCRIPT")
        print("=" * 80)
        print("⚠️  WARNING: This action CANNOT be undone!")
        print("⚠️  All user data will be permanently deleted!")
        print("=" * 80)
        print()

        if args.email:
            delete_by_email(db, args.email)

        elif args.username:
            delete_by_username(db, args.username)

        elif args.id:
            delete_by_id(db, args.id)

        else:
            # Interactive mode
            interactive_mode(db)

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
