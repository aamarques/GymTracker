#!/bin/bash
# Import exercises from CSV - Wrapper script

if ! docker ps | grep -q gym_backend; then
    echo "❌ Error: gym_backend container is not running!"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: ./import-exercises.sh exercises.csv [--user-id UUID]"
    echo ""
    echo "Example:"
    echo "  ./import-exercises.sh my_exercises.csv"
    echo "  ./import-exercises.sh my_exercises.csv --user-id abc-123-def"
    exit 1
fi

# Get the CSV file path
CSV_FILE="$1"
shift  # Remove first argument

# Check if file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ File not found: $CSV_FILE"
    exit 1
fi

# Get just the filename
CSV_FILENAME=$(basename "$CSV_FILE")

# Copy CSV to container
echo "📋 Copying CSV to container..."
docker cp "$CSV_FILE" gym_backend:/tmp/"$CSV_FILENAME"

# Run import script
echo ""
docker exec -it gym_backend python import_exercises.py /tmp/"$CSV_FILENAME" "$@"

# Cleanup
docker exec gym_backend rm /tmp/"$CSV_FILENAME"
