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

# Run import script inside backend container
if [ -n "$USER_ID" ]; then
    podman exec gym_backend python import_exercises_pt.py "/app/$CSV_FILE" --user-id "$USER_ID"
else
    podman exec gym_backend python import_exercises_pt.py "/app/$CSV_FILE"
fi
