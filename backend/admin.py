#!/usr/bin/env python3
"""
Admin Menu - Gym Tracker
Central script for all admin operations

Usage: python admin.py
"""

import sys
import os
import subprocess


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def show_menu():
    """Display the main admin menu"""
    clear_screen()
    print("=" * 80)
    print("GYM TRACKER - ADMIN MENU")
    print("=" * 80)
    print()
    print("1. List All Users")
    print("2. Reset All Passwords (to 'password123')")
    print("3. Reset User Workouts")
    print("4. Delete User")
    print()
    print("0. Exit")
    print()
    print("=" * 80)


def run_script(script_name, args=[]):
    """Run a Python script with optional arguments"""
    try:
        cmd = [sys.executable, script_name] + args
        subprocess.run(cmd)
    except Exception as e:
        print(f"\n❌ Error running script: {str(e)}")

    input("\n\nPress Enter to continue...")


def main():
    while True:
        show_menu()

        choice = input("Enter your choice: ").strip()

        if choice == '0':
            print("\n👋 Goodbye!\n")
            break

        elif choice == '1':
            # List users
            run_script('list_users.py')

        elif choice == '2':
            # Reset passwords
            run_script('reset_passwords.py')

        elif choice == '3':
            # Reset workouts - submenu
            clear_screen()
            print("=" * 80)
            print("RESET USER WORKOUTS")
            print("=" * 80)
            print()
            print("1. Interactive mode (choose from list)")
            print("2. By email")
            print("3. By username")
            print("4. Reset ALL users")
            print("0. Back to main menu")
            print()
            print("=" * 80)

            sub_choice = input("\nEnter your choice: ").strip()

            if sub_choice == '1':
                run_script('reset_user_workouts.py')
            elif sub_choice == '2':
                email = input("Enter email: ").strip()
                run_script('reset_user_workouts.py', ['--email', email])
            elif sub_choice == '3':
                username = input("Enter username: ").strip()
                run_script('reset_user_workouts.py', ['--username', username])
            elif sub_choice == '4':
                run_script('reset_user_workouts.py', ['--all'])

        elif choice == '4':
            # Delete user - submenu
            clear_screen()
            print("=" * 80)
            print("DELETE USER")
            print("=" * 80)
            print("⚠️  WARNING: This action CANNOT be undone!")
            print("=" * 80)
            print()
            print("1. Interactive mode (choose from list)")
            print("2. By email")
            print("3. By username")
            print("4. By ID")
            print("0. Back to main menu")
            print()
            print("=" * 80)

            sub_choice = input("\nEnter your choice: ").strip()

            if sub_choice == '1':
                run_script('delete_user.py')
            elif sub_choice == '2':
                email = input("Enter email: ").strip()
                run_script('delete_user.py', ['--email', email])
            elif sub_choice == '3':
                username = input("Enter username: ").strip()
                run_script('delete_user.py', ['--username', username])
            elif sub_choice == '4':
                user_id = input("Enter user ID: ").strip()
                run_script('delete_user.py', ['--id', user_id])

        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!\n")
        sys.exit(0)
