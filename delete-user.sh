#!/bin/bash
# Delete user - Wrapper script

if ! podman ps | grep -q gym_backend; then
    echo "❌ Error: gym_backend container is not running!"
    exit 1
fi

podman exec -it gym_backend python delete_user.py "$@"
