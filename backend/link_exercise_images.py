#!/usr/bin/env python3
"""
Link existing exercise images to exercises in database

Matches images named like: "Exercise Name_MuscleGroup.jpg"
to exercises with matching name and muscle group
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import Exercise


# Map English muscle groups to match image filenames
MUSCLE_GROUP_MAP = {
    'chest': 'Chest',
    'legs': 'Legs',
    'shoulders': 'Shoulders',
    'back': 'Back',
    'triceps': 'Triceps',
    'biceps': 'Biceps',
    'abs': 'Abs',  # Fixed: Images use 'Abs' not 'Core'
    'cardio': 'Cardio',
    'glutes': 'Glutes',
}


def normalize_name(name):
    """Normalize exercise name for comparison"""
    # Replace / with _ for filename matching
    return name.replace('/', '_').replace(' ', ' ')


def link_images():
    """Link images to exercises based on filename pattern"""
    db = SessionLocal()

    # Get images directory
    uploads_dir = Path('/app/uploads/exercises')

    if not uploads_dir.exists():
        print(f"❌ Uploads directory not found: {uploads_dir}")
        return

    # Get all image files
    image_files = list(uploads_dir.glob('*.jpg'))
    print(f"📁 Found {len(image_files)} images in {uploads_dir}")
    print()

    # Get all exercises without images
    exercises = db.query(Exercise).filter(Exercise.image_path == None).all()
    print(f"📊 Found {len(exercises)} exercises without images")
    print()

    linked_count = 0
    not_found_count = 0

    for exercise in exercises:
        # Try to match image filename
        # Pattern: {ExerciseName}_{MuscleGroup}.jpg
        normalized_name = normalize_name(exercise.name)
        muscle_group_name = MUSCLE_GROUP_MAP.get(exercise.muscle_group.lower(), exercise.muscle_group)

        # Try exact match
        expected_filename = f"{normalized_name}_{muscle_group_name}.jpg"
        image_path = uploads_dir / expected_filename

        if image_path.exists():
            # Update exercise with image path
            exercise.image_path = f"/uploads/exercises/{expected_filename}"
            linked_count += 1
            print(f"✅ Linked '{exercise.name}' ({exercise.muscle_group}) -> {expected_filename}")
        else:
            not_found_count += 1
            print(f"⚠️  No image found for '{exercise.name}' ({exercise.muscle_group})")
            print(f"   Expected: {expected_filename}")

    # Commit changes
    db.commit()

    print()
    print("=" * 60)
    print(f"✅ Linking completed!")
    print(f"   Linked:    {linked_count}")
    print(f"   Not found: {not_found_count}")
    print("=" * 60)

    db.close()


if __name__ == '__main__':
    try:
        link_images()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
