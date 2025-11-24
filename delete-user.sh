#!/bin/bash
# Delete user - Wrapper script

if ! docker ps | grep -q gym_backend; then
    echo "❌ Error: gym_backend container is not running!"
    exit 1
fi

docker exec -it gym_backend python delete_user.py "$@"
