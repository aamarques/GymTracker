#!/bin/bash

# Start Gym Tracker containers with Podman
# This script works around the netavark/nftables issue in WSL2

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Gym Tracker containers..."

# Create network
podman network create gym_network 2>/dev/null || true

# Create volumes
podman volume create gym_postgres_data 2>/dev/null || true
podman volume create gym_backend_uploads 2>/dev/null || true

# Start PostgreSQL
echo "Starting PostgreSQL..."
podman run -d \
  --name gym_postgres \
  --network gym_network \
  -e POSTGRES_USER=gymuser \
  -e POSTGRES_PASSWORD=gympass123 \
  -e POSTGRES_DB=gymtracker \
  -p 5432:5432 \
  -v gym_postgres_data:/var/lib/postgresql/data \
  --health-cmd "pg_isready -U gymuser" \
  --health-interval 10s \
  --health-timeout 5s \
  --health-retries 5 \
  docker.io/library/postgres:15-alpine

# Wait for PostgreSQL to be healthy
echo "Waiting for PostgreSQL to be ready..."
until podman exec gym_postgres pg_isready -U gymuser >/dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Start Backend
echo "Starting Backend..."
podman run -d \
  --name gym_backend \
  --network gym_network \
  -e DATABASE_URL="postgresql://gymuser:gympass123@gym_postgres:5432/gymtracker" \
  -e SECRET_KEY="your-secret-key-change-this-in-production" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  -v "$SCRIPT_DIR/backend:/app:Z" \
  -v gym_backend_uploads:/app/uploads \
  localhost/gym_backend:latest

# Start Nginx
echo "Starting Nginx..."
podman run -d \
  --name gym_nginx \
  --network gym_network \
  -p 8080:80 \
  -v "$SCRIPT_DIR/nginx/nginx.conf:/etc/nginx/nginx.conf:ro,Z" \
  -v "$SCRIPT_DIR/frontend:/usr/share/nginx/html:ro,Z" \
  -v gym_backend_uploads:/usr/share/nginx/html/uploads:ro \
  docker.io/library/nginx:alpine

echo ""
echo "✓ All containers started!"
echo ""
echo "Access the application at:"
echo "  - Main App:    http://localhost:8080"
echo "  - API Docs:    http://localhost:8080/docs"
echo "  - Health Check: http://localhost:8080/health"
echo ""
echo "To view logs: podman logs -f <container_name>"
echo "To stop: podman stop gym_nginx gym_backend gym_postgres"
