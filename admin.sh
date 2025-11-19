#!/bin/bash
# Admin Menu Wrapper - Executes admin scripts inside the container

# Change to the directory where docker-compose.yml is located
cd "$(dirname "$0")"

# Check if container is running
if ! podman-compose ps | grep -q "backend.*Up"; then
    echo "❌ Error: Backend container is not running!"
    echo ""
    echo "Start the containers first:"
    echo "  docker-compose up -d"
    exit 1
fi

# Run admin.py inside the container
podman-compose exec backend python admin.py
