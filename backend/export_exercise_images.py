#!/usr/bin/env python3
"""
Export all exercise images to a folder
Images will be renamed with format: {exercise_name}_{original_filename}
"""

import sys
import os
import shutil
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.models import Exercise


def sanitize_filename(name):
    """Convert exercise name to valid filename"""
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()


def export_exercise_images(export_dir='exported_exercise_images'):
    """Export all exercise images to specified directory"""
    db = SessionLocal()

    try:
        # Create export directory
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)

        print("=" * 60)
        print("EXPORT EXERCISE IMAGES")
        print("=" * 60)
        print()
        print(f"📁 Export directory: {export_path.absolute()}")
        print()

        # Get all exercises with images
        exercises = db.query(Exercise).filter(Exercise.image_path.isnot(None)).all()

        if not exercises:
            print("⚠️  No exercises with images found")
            return

        print(f"📊 Found {len(exercises)} exercises with images")
        print()

        exported = 0
        skipped = 0
        errors = 0

        for exercise in exercises:
            try:
                # Source path (in container)
                source_path = Path('/app') / exercise.image_path.lstrip('/')

                if not source_path.exists():
                    print(f"⚠️  Image not found: {exercise.name} - {source_path}")
                    skipped += 1
                    continue

                # Get file extension
                ext = source_path.suffix

                # Create new filename
                safe_name = sanitize_filename(exercise.name)
                new_filename = f"{safe_name}_{exercise.muscle_group}{ext}"
                dest_path = export_path / new_filename

                # Handle duplicate filenames
                counter = 1
                while dest_path.exists():
                    new_filename = f"{safe_name}_{exercise.muscle_group}_{counter}{ext}"
                    dest_path = export_path / new_filename
                    counter += 1

                # Copy image
                shutil.copy2(source_path, dest_path)
                print(f"✅ Exported: {exercise.name} ({exercise.muscle_group})")
                print(f"   → {new_filename}")
                exported += 1

            except Exception as e:
                print(f"❌ Error exporting {exercise.name}: {str(e)}")
                errors += 1

        print()
        print("=" * 60)
        print(f"✅ Export completed!")
        print(f"   Exported: {exported}")
        print(f"   Skipped:  {skipped}")
        print(f"   Errors:   {errors}")
        print(f"   Location: {export_path.absolute()}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Export exercise images')
    parser.add_argument(
        '--output-dir',
        default='exported_exercise_images',
        help='Output directory for exported images (default: exported_exercise_images)'
    )

    args = parser.parse_args()

    print()
    export_exercise_images(args.output_dir)
    print()
