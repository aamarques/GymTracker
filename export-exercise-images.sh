#!/bin/bash

# Export exercise images from database
# Usage: ./export-exercise-images.sh [output_directory]

OUTPUT_DIR="${1:-exported_exercise_images}"

echo "=================================================="
echo "Export Exercise Images"
echo "=================================================="
echo ""
echo "Output directory: $OUTPUT_DIR"
echo ""

# Run export script inside backend container
docker exec gym_backend python export_exercise_images.py --output-dir "/app/$OUTPUT_DIR"

# Copy from container to host
if [ $? -eq 0 ]; then
    echo ""
    echo "📦 Copying images from container to host..."
    docker cp gym_backend:/app/$OUTPUT_DIR .

    if [ $? -eq 0 ]; then
        echo "✅ Images copied successfully to: $(pwd)/$OUTPUT_DIR"
    else
        echo "❌ Failed to copy images from container"
        exit 1
    fi
fi
