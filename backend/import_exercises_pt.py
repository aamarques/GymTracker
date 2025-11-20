#!/usr/bin/env python3
"""
Import exercises from Portuguese CSV with column-pair format

CSV Format:
- Columns are organized in pairs: (Exercise Name, Muscle Group)
- Exercise names can appear in any row under their respective column
- Muscle groups are in Portuguese and will be mapped to English

Usage:
    python import_exercises_pt.py path/to/exercicios.csv
    python import_exercises_pt.py path/to/exercicios.csv --user-id UUID
"""

import sys
import os
import csv
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import Exercise, User


# Map Portuguese muscle group names to English
MUSCLE_GROUP_MAP = {
    'Peito': 'Chest',
    'Pernas': 'Legs',
    'Ombros': 'Shoulders',
    'Costas': 'Back',
    'Triceps': 'Triceps',
    'Biceps': 'Biceps',
    'Core': 'Abs',
    'Cardio': 'Cardio',
    'Trapézio': 'Back',  # Trapezius is part of back
    'Glúteos': 'Glutes',
}


def parse_column_pairs(csv_file):
    """
    Parse CSV with column-pair format into list of exercises

    Returns:
        List of tuples: [(name, muscle_group_en), ...]
    """
    exercises = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        # Parse column pairs
        column_pairs = []
        for i in range(0, len(headers), 2):
            if i + 1 < len(headers):
                muscle_group_pt = headers[i + 1].strip()
                muscle_group_en = MUSCLE_GROUP_MAP.get(muscle_group_pt)
                if muscle_group_en:
                    column_pairs.append((i, muscle_group_en))

        print(f"📊 Found {len(column_pairs)} muscle group columns:")
        for col_idx, muscle_group in column_pairs:
            muscle_group_pt = headers[col_idx + 1]
            print(f"   - Column {col_idx}: {muscle_group_pt} → {muscle_group}")
        print()

        # Read all rows and extract exercises
        for row_num, row in enumerate(reader, start=2):
            for col_idx, muscle_group in column_pairs:
                if col_idx < len(row):
                    exercise_name = row[col_idx].strip()
                    if exercise_name and exercise_name not in ['', ' ']:
                        exercises.append((exercise_name, muscle_group, row_num))

    return exercises


def import_exercises_from_csv(csv_file, user_id=None):
    """
    Import exercises from Portuguese CSV file

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

        # Parse CSV
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return

        exercises = parse_column_pairs(csv_file)

        print(f"📝 Found {len(exercises)} total exercises in CSV")
        print()

        imported = 0
        skipped = 0
        errors = 0

        for name, muscle_group, row_num in exercises:
            try:
                # Check if exercise already exists for this user
                existing = db.query(Exercise).filter(
                    Exercise.name == name,
                    Exercise.created_by == user.id
                ).first()

                if existing:
                    print(f"⏭️  '{name}' ({muscle_group}) already exists, skipping")
                    skipped += 1
                    continue

                # Create exercise
                exercise = Exercise(
                    name=name,
                    muscle_group=muscle_group,
                    equipment=None,
                    description=None,
                    image_path=None,
                    created_by=user.id
                )

                db.add(exercise)
                db.commit()

                print(f"✅ Created '{name}' ({muscle_group})")
                imported += 1

            except Exception as e:
                db.rollback()
                print(f"❌ Error importing '{name}': {str(e)}")
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

    parser = argparse.ArgumentParser(description='Import exercises from Portuguese CSV')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--user-id', help='User ID to assign exercises to (optional)')

    args = parser.parse_args()

    print("=" * 60)
    print("IMPORT EXERCISES FROM PORTUGUESE CSV")
    print("=" * 60)
    print()

    import_exercises_from_csv(args.csv_file, args.user_id)


if __name__ == "__main__":
    main()
