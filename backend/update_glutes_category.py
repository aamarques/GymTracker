#!/usr/bin/env python3
"""
Update exercises that should be in Glutes category instead of Legs
This updates exercises that were imported before the Glutes category was added
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import Exercise

# List of exercise names that should be Glutes, not Legs
GLUTES_EXERCISES = [
    'Ponte de Glúteos',
    'Box Steps',
    'Bulgarian Split Squat',
    'Standing Cable Abduction',
    'Hip Thrust',
    'Kick Back polia',
    'Lateral Band Walk',
    'Lunge (Glt. Inf.)',
    'Peso Morto (Glt. Inf.)',
    'Ponte de Gluteo Unilateral',
]


def update_glutes_category():
    """Update exercises from Legs to Glutes category"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("UPDATE GLUTES CATEGORY")
        print("=" * 60)
        print()

        updated = 0
        not_found = 0

        for exercise_name in GLUTES_EXERCISES:
            exercise = db.query(Exercise).filter(
                Exercise.name == exercise_name,
                Exercise.muscle_group == 'Legs'
            ).first()

            if exercise:
                exercise.muscle_group = 'Glutes'
                db.commit()
                print(f"✅ Updated '{exercise_name}': Legs → Glutes")
                updated += 1
            else:
                # Check if it already exists as Glutes or doesn't exist
                exists_as_glutes = db.query(Exercise).filter(
                    Exercise.name == exercise_name,
                    Exercise.muscle_group == 'Glutes'
                ).first()

                if exists_as_glutes:
                    print(f"⏭️  '{exercise_name}' already set to Glutes")
                else:
                    print(f"⚠️  '{exercise_name}' not found in database")
                not_found += 1

        print()
        print("=" * 60)
        print(f"✅ Update completed!")
        print(f"   Updated:   {updated}")
        print(f"   Skipped:   {not_found}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print()
    update_glutes_category()
    print()
