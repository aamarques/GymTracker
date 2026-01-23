#!/bin/bash

# Start Gym Tracker with Docker Compose
# Simple wrapper script

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=================================================="
echo "Starting Gym Tracker with Docker"
echo "=================================================="
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo ""
    echo "Install with:"
    echo "  sudo apt update"
    echo "  sudo apt install -y docker.io docker-compose"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed${NC}"
    echo ""
    echo "Install with:"
    echo "  sudo apt install -y docker-compose"
    exit 1
fi

# Check if docker daemon is running
if ! docker info &>/dev/null; then
    echo -e "${YELLOW}⚠️  Docker daemon is not running${NC}"
    echo ""

    # Try to start it
    if [ "$EUID" -eq 0 ]; then
        echo "Starting Docker daemon..."
        systemctl start docker
    else
        echo "Start with:"
        echo "  sudo systemctl start docker"
        echo ""
        echo "Or run this script with sudo:"
        echo "  sudo bash $0"
        exit 1
    fi
fi

# Check if user is in docker group
if ! docker ps &>/dev/null && [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Permission denied${NC}"
    echo ""
    echo "You can either:"
    echo "1. Run with sudo: sudo docker-compose up -d"
    echo "2. Add yourself to docker group:"
    echo "   sudo usermod -aG docker $USER"
    echo "   then log out and back in"
    echo ""
    read -p "Run with sudo now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        USE_SUDO="sudo"
    else
        exit 1
    fi
else
    USE_SUDO=""
fi

echo "✓ Docker is ready"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Disable BuildKit for better compatibility
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

echo "Starting containers..."
echo ""

# Start containers
$USE_SUDO docker-compose up -d

# Wait a moment for containers to initialize
sleep 3

# Check status
echo ""
echo "Checking container status..."
$USE_SUDO docker-compose ps

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Gym Tracker is running!${NC}"
echo "=================================================="
echo ""
echo "Access the application at:"
echo "  - Main App:     http://localhost"
echo "  - API Docs:     http://localhost/docs"
echo "  - Health Check: http://localhost/health"
echo ""
echo "Useful commands:"
echo "  - View logs:    docker-compose logs -f"
echo "  - Stop:         docker-compose down"
echo "  - Restart:      docker-compose restart"
echo "  - Rebuild:      docker-compose up -d --build"
echo ""
