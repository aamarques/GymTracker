#!/bin/bash
# List all users - Wrapper script

if ! docker ps | grep -q gym_backend; then
    echo "❌ Error: gym_backend container is not running!"
    exit 1
fi

docker exec -it gym_backend python list_users.py
