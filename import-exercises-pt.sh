#!/bin/bash

# Import exercises from Portuguese CSV file
# Usage: ./import-exercises-pt.sh [csv_file] [user_id]

CSV_FILE="${1:-Imports/exercicios.csv}"
USER_ID="${2}"

echo "=================================================="
echo "Import Portuguese Exercises"
echo "=================================================="
echo ""
echo "CSV File: $CSV_FILE"
if [ -n "$USER_ID" ]; then
    echo "User ID: $USER_ID"
else
    echo "User ID: (will use first Personal Trainer)"
fi
echo ""

if [ ! -f "$CSV_FILE" ]; then
    echo "❌ Error: CSV file not found: $CSV_FILE"
    exit 1
fi

# Get just the filename
CSV_FILENAME=$(basename "$CSV_FILE")

# Copy CSV to container
echo "📋 Copying CSV to container..."
podman cp "$CSV_FILE" gym_backend:/tmp/"$CSV_FILENAME"

# Run import script inside backend container
echo ""
if [ -n "$USER_ID" ]; then
    podman exec gym_backend python import_exercises_pt.py "/tmp/$CSV_FILENAME" --user-id "$USER_ID"
else
    podman exec gym_backend python import_exercises_pt.py "/tmp/$CSV_FILENAME"
fi

# Cleanup
podman exec gym_backend rm /tmp/"$CSV_FILENAME"
