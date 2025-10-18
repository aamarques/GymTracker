#!/bin/bash

echo "==============================================="
echo "  Gym Workout Tracker - Startup Script"
echo "==============================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "Starting Gym Workout Tracker..."
echo ""

# Build and start containers
docker-compose up -d --build

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check container status
echo ""
echo "Container Status:"
docker-compose ps

echo ""
echo "==============================================="
echo "  Application is running!"
echo "==============================================="
echo ""
echo "Access the application at:"
echo "  - Main App: http://localhost"
echo "  - API Docs: http://localhost/docs"
echo "  - Health Check: http://localhost/health"
echo ""
echo "View logs with: docker-compose logs -f"
echo "Stop with: docker-compose down"
echo ""
