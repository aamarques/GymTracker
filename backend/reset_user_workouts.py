#!/usr/bin/env python3
"""
Script to reset workout count for one or more users
Usage:
    python reset_user_workouts.py                    # Interactive mode
    python reset_user_workouts.py --all              # Reset all users
    python reset_user_workouts.py --email user@example.com
    python reset_user_workouts.py --username john_doe
"""

import sys
import os
import argparse

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import User
from app.services.metrics_service import reset_client_workouts


def reset_workouts_for_user(db, user):
    """Reset workouts for a specific user"""
    try:
        result = reset_client_workouts(db, user.id)
        print(f"✓ Reset workouts for: {user.name} ({user.email})")
        print(f"  - Workouts archived: {result.get('workouts_archived', 0)}")
        print(f"  - Reset count: {result.get('reset_count', 0)}")
        return True
    except Exception as e:
        print(f"✗ Error resetting workouts for {user.email}: {str(e)}")
        return False


def reset_all_users(db):
    """Reset workouts for all users"""
    users = db.query(User).all()

    if not users:
        print("No users found in database.")
        return

    print(f"Found {len(users)} users.\n")

    success_count = 0
    for user in users:
        if reset_workouts_for_user(db, user):
            success_count += 1
        print()

    print(f"\n✅ Successfully reset workouts for {success_count}/{len(users)} users!")


def reset_by_email(db, email):
    """Reset workouts for user by email"""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        print(f"❌ User not found with email: {email}")
        return False

    return reset_workouts_for_user(db, user)


def reset_by_username(db, username):
    """Reset workouts for user by username"""
    user = db.query(User).filter(User.username == username).first()

    if not user:
        print(f"❌ User not found with username: {username}")
        return False

    return reset_workouts_for_user(db, user)


def interactive_mode(db):
    """Interactive mode to select users"""
    users = db.query(User).all()

    if not users:
        print("No users found in database.")
        return

    print("\n" + "=" * 80)
    print("AVAILABLE USERS:")
    print("=" * 80)

    for idx, user in enumerate(users, 1):
        print(f"{idx}. {user.name} ({user.email}) - Username: {user.username} - Role: {user.role}")

    print("\n" + "=" * 80)
    print("Enter user numbers separated by commas (e.g., 1,3,5)")
    print("Or type 'all' to reset all users")
    print("=" * 80)

    choice = input("\nYour choice: ").strip().lower()

    if choice == 'all':
        confirm = input("\n⚠️  Are you sure you want to reset ALL users? (yes/no): ").lower().strip()
        if confirm == 'yes':
            reset_all_users(db)
        else:
            print("❌ Operation cancelled.")
        return

    try:
        indices = [int(x.strip()) for x in choice.split(',')]
        selected_users = [users[i-1] for i in indices if 1 <= i <= len(users)]

        if not selected_users:
            print("❌ No valid users selected.")
            return

        print(f"\nYou selected {len(selected_users)} user(s):")
        for user in selected_users:
            print(f"  - {user.name} ({user.email})")

        confirm = input("\nProceed? (yes/no): ").lower().strip()

        if confirm == 'yes':
            success_count = 0
            for user in selected_users:
                if reset_workouts_for_user(db, user):
                    success_count += 1
                print()

            print(f"\n✅ Successfully reset workouts for {success_count}/{len(selected_users)} users!")
        else:
            print("❌ Operation cancelled.")

    except (ValueError, IndexError) as e:
        print(f"❌ Invalid input: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Reset workout count for users')
    parser.add_argument('--all', action='store_true', help='Reset all users')
    parser.add_argument('--email', type=str, help='Reset user by email')
    parser.add_argument('--username', type=str, help='Reset user by username')

    args = parser.parse_args()

    db = SessionLocal()

    try:
        print("=" * 80)
        print("RESET WORKOUT COUNT SCRIPT")
        print("=" * 80)
        print("⚠️  This will reset workout counts but preserve metrics for trainers")
        print("=" * 80)
        print()

        if args.all:
            confirm = input("⚠️  Reset ALL users? (yes/no): ").lower().strip()
            if confirm == 'yes':
                reset_all_users(db)
            else:
                print("❌ Operation cancelled.")

        elif args.email:
            confirm = input(f"Reset workouts for {args.email}? (yes/no): ").lower().strip()
            if confirm == 'yes':
                if reset_by_email(db, args.email):
                    print("\n✅ Operation completed successfully!")
            else:
                print("❌ Operation cancelled.")

        elif args.username:
            confirm = input(f"Reset workouts for username '{args.username}'? (yes/no): ").lower().strip()
            if confirm == 'yes':
                if reset_by_username(db, args.username):
                    print("\n✅ Operation completed successfully!")
            else:
                print("❌ Operation cancelled.")

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
