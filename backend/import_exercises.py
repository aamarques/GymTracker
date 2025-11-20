#!/usr/bin/env python3
"""
Import exercises from CSV file with images

CSV Format:
name,muscle_group,equipment,description,image_path

Example:
Bench Press,Chest,Barbell,Classic chest exercise,images/bench_press.jpg
Squat,Legs,Barbell,Compound leg exercise,images/squat.jpg

Usage:
    python import_exercises.py exercises.csv
    python import_exercises.py exercises.csv --user-id UUID
"""

import sys
import os
import csv
import shutil
import uuid
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import Exercise, User


VALID_MUSCLE_GROUPS = ['Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps', 'Legs', 'Glutes', 'Abs', 'Cardio']
UPLOAD_DIR = Path('/app/uploads')


def import_exercises_from_csv(csv_file, user_id=None):
    """
    Import exercises from CSV file

    Args:
        csv_file: Path to CSV file
        user_id: User ID to assign exercises to (optional, uses first PT if not provided)
    """
    db = SessionLocal()

    try:
        # Get user (Personal Trainer)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                print(f"❌ User with ID {user_id} not found!")
                return
        else:
            # Get first Personal Trainer
            user = db.query(User).filter(User.role == 'personal_trainer').first()
            if not user:
                print("❌ No Personal Trainer found in database!")
                print("Please create a PT user first or specify --user-id")
                return

        print(f"📋 Importing exercises for user: {user.name} ({user.email})")
        print()

        # Create upload directory if it doesn't exist
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Read CSV
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate headers
            required_fields = ['name', 'muscle_group']
            if not all(field in reader.fieldnames for field in required_fields):
                print(f"❌ CSV must have at least these columns: {', '.join(required_fields)}")
                print(f"Found columns: {', '.join(reader.fieldnames)}")
                return

            imported = 0
            skipped = 0
            errors = 0

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (line 1 is header)
                try:
                    name = row['name'].strip()
                    muscle_group = row['muscle_group'].strip()

                    if not name:
                        print(f"⚠️  Row {row_num}: Skipping empty name")
                        skipped += 1
                        continue

                    # Validate muscle group
                    if muscle_group not in VALID_MUSCLE_GROUPS:
                        print(f"⚠️  Row {row_num}: Invalid muscle group '{muscle_group}' for '{name}'")
                        print(f"    Valid groups: {', '.join(VALID_MUSCLE_GROUPS)}")
                        print(f"    Using 'Chest' as default")
                        muscle_group = 'Chest'

                    # Check if exercise already exists for this user
                    existing = db.query(Exercise).filter(
                        Exercise.name == name,
                        Exercise.created_by == user.id
                    ).first()

                    if existing:
                        print(f"⏭️  Row {row_num}: '{name}' already exists, skipping")
                        skipped += 1
                        continue

                    # Handle image
                    image_filename = None
                    if 'image_path' in row and row['image_path']:
                        image_path = row['image_path'].strip()
                        if image_path and os.path.exists(image_path):
                            # Copy image to uploads directory
                            ext = os.path.splitext(image_path)[1]
                            image_filename = f"{uuid.uuid4()}{ext}"
                            dest_path = UPLOAD_DIR / image_filename
                            shutil.copy2(image_path, dest_path)
                            print(f"   📷 Image uploaded: {image_filename}")
                        elif image_path:
                            print(f"   ⚠️  Image not found: {image_path}")

                    # Create exercise
                    exercise = Exercise(
                        name=name,
                        muscle_group=muscle_group,
                        equipment=row.get('equipment', '').strip() or None,
                        description=row.get('description', '').strip() or None,
                        image_path=f"/uploads/{image_filename}" if image_filename else None,
                        created_by=user.id
                    )

                    db.add(exercise)
                    db.commit()

                    print(f"✅ Row {row_num}: Created '{name}' ({muscle_group})")
                    imported += 1

                except Exception as e:
                    db.rollback()
                    print(f"❌ Row {row_num}: Error - {str(e)}")
                    errors += 1

        print()
        print("=" * 60)
        print(f"✅ Import completed!")
        print(f"   Imported: {imported}")
        print(f"   Skipped:  {skipped}")
        print(f"   Errors:   {errors}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"❌ Fatal error: {str(e)}")
        raise
    finally:
        db.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Import exercises from CSV')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--user-id', help='User ID to assign exercises to (optional)')

    args = parser.parse_args()

    print("=" * 60)
    print("IMPORT EXERCISES FROM CSV")
    print("=" * 60)
    print()

    import_exercises_from_csv(args.csv_file, args.user_id)


if __name__ == "__main__":
    main()
