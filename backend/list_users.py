#!/usr/bin/env python3
"""
Script to list all users in the database
Usage: python list_users.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import User, UserRole
from sqlalchemy import func


def list_all_users():
    """List all users with their details"""
    db = SessionLocal()

    try:
        users = db.query(User).order_by(User.created_at.desc()).all()

        if not users:
            print("No users found in database.")
            return

        # Count by role
        pt_count = db.query(User).filter(User.role == UserRole.PERSONAL_TRAINER).count()
        client_count = db.query(User).filter(User.role == UserRole.CLIENT).count()

        print("=" * 100)
        print(f"USERS IN DATABASE - Total: {len(users)} (Personal Trainers: {pt_count}, Clients: {client_count})")
        print("=" * 100)
        print()

        for idx, user in enumerate(users, 1):
            print(f"{idx}. {user.name}")
            print(f"   Email:        {user.email}")
            print(f"   Username:     {user.username}")
            print(f"   Role:         {user.role}")
            print(f"   Language:     {user.language}")
            print(f"   Created:      {user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A'}")

            if user.role == UserRole.CLIENT:
                print(f"   Weight:       {user.weight} kg")
                print(f"   Height:       {user.height} cm")
                print(f"   BMI:          {round(user.weight / ((user.height/100) ** 2), 1) if user.weight and user.height else 'N/A'}")
                if user.desired_weight:
                    print(f"   Goal Weight:  {user.desired_weight} kg")
                if user.personal_trainer_id:
                    trainer = db.query(User).filter(User.id == user.personal_trainer_id).first()
                    if trainer:
                        print(f"   Trainer:      {trainer.name} ({trainer.email})")

            if user.role == UserRole.PERSONAL_TRAINER:
                client_count = len(user.clients)
                print(f"   Clients:      {client_count}")
                if client_count > 0:
                    print(f"   Client List:")
                    for client in user.clients:
                        print(f"      - {client.name} ({client.email})")

            print(f"   ID:           {user.id}")
            print()

        print("=" * 100)
        print(f"Total Users: {len(users)}")
        print("=" * 100)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print()
    list_all_users()
