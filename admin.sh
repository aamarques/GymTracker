#!/bin/bash
# Admin Menu Wrapper - Executes admin scripts inside the container

# Change to the directory where docker-compose.yml is located
cd "$(dirname "$0")"

# Check if container is running
if ! docker ps | grep -q "gym_backend.*Up"; then
    echo "❌ Error: Backend container is not running!"
    echo ""
    echo "Start the containers first:"
    echo "  docker-compose up -d"
    echo "  or: docker-compose -f docker-compose-simple.yml up -d"
    exit 1
fi

# Run admin.py inside the container
docker exec -it gym_backend python admin.py
