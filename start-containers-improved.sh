#!/bin/bash

# Improved Gym Tracker container startup script
# Handles Podman/Docker automatically with better error handling

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo "Starting Gym Tracker"
echo "=================================================="
echo ""

# Function to check if running as root
is_root() {
    [ "$(id -u)" -eq 0 ]
}

# Detect container runtime
detect_runtime() {
    if command -v podman &> /dev/null; then
        echo "podman"
    elif command -v docker &> /dev/null; then
        echo "docker"
    else
        echo "none"
    fi
}

RUNTIME=$(detect_runtime)

if [ "$RUNTIME" = "none" ]; then
    echo -e "${RED}❌ Error: Neither Podman nor Docker is installed${NC}"
    echo ""
    echo "Please install one of them:"
    echo "  - Ubuntu/Debian: sudo apt install podman"
    echo "  - or: sudo apt install docker.io docker-compose"
    exit 1
fi

echo "✓ Detected runtime: $RUNTIME"

# Check for permission issues with podman
if [ "$RUNTIME" = "podman" ] && ! is_root; then
    echo "Checking Podman configuration..."

    # Test podman
    if ! podman info &>/dev/null; then
        echo -e "${YELLOW}⚠️  Podman rootless mode issue detected${NC}"
        echo ""
        echo "Quick fixes:"
        echo "1. Run with sudo: sudo bash $0"
        echo "2. Or configure user namespaces:"
        echo "   sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 \$(whoami)"
        echo "   podman system reset --force"
        echo ""
        read -p "Try with sudo now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            exec sudo bash "$0"
        else
            exit 1
        fi
    fi
fi

echo "✓ Runtime configured correctly"
echo ""

# Use docker-compose if using docker
if [ "$RUNTIME" = "docker" ]; then
    echo "Using Docker Compose..."

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ docker-compose not found${NC}"
        echo "Install with: sudo apt install docker-compose"
        exit 1
    fi

    # Check if docker service is running
    if ! docker info &>/dev/null; then
        if is_root; then
            systemctl start docker
        else
            echo -e "${YELLOW}⚠️  Docker daemon not running${NC}"
            echo "Start with: sudo systemctl start docker"
            exit 1
        fi
    fi

    export DOCKER_BUILDKIT=0
    export COMPOSE_DOCKER_CLI_BUILD=0

    cd "$SCRIPT_DIR"
    docker-compose up -d

    echo ""
    echo -e "${GREEN}✓ All containers started!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  - Main App:     http://localhost"
    echo "  - API Docs:     http://localhost/docs"
    echo "  - Health Check: http://localhost/health"
    echo ""
    echo "Useful commands:"
    echo "  - View logs:  docker-compose logs -f"
    echo "  - Stop:       docker-compose down"
    echo "  - Restart:    docker-compose restart"

    exit 0
fi

# Continue with Podman
echo "Using Podman..."
echo ""

# Remove SELinux flags if not on SELinux system
SELINUX_FLAG=""
if command -v getenforce &>/dev/null && [ "$(getenforce)" = "Enforcing" ]; then
    SELINUX_FLAG=",Z"
fi

# Create network
echo "Creating network..."
$RUNTIME network create gym_network 2>/dev/null || true

# Create volumes
echo "Creating volumes..."
$RUNTIME volume create gym_postgres_data 2>/dev/null || true
$RUNTIME volume create gym_backend_uploads 2>/dev/null || true

# Stop and remove existing containers
echo "Cleaning up old containers..."
$RUNTIME stop gym_postgres gym_backend gym_nginx 2>/dev/null || true
$RUNTIME rm gym_postgres gym_backend gym_nginx 2>/dev/null || true

# Build backend image if needed
echo "Building backend image..."
cd "$SCRIPT_DIR/backend"
$RUNTIME build -t localhost/gym_backend:latest . 2>&1 | grep -v "WARN" || true

# Start PostgreSQL
echo ""
echo "Starting PostgreSQL..."
$RUNTIME run -d \
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

# Wait for PostgreSQL
echo "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if $RUNTIME exec gym_postgres pg_isready -U gymuser >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ PostgreSQL failed to start${NC}"
        echo "Check logs: $RUNTIME logs gym_postgres"
        exit 1
    fi
    sleep 1
done

# Start Backend
echo ""
echo "Starting Backend..."
$RUNTIME run -d \
  --name gym_backend \
  --network gym_network \
  -e DATABASE_URL="postgresql://gymuser:gympass123@gym_postgres:5432/gymtracker" \
  -e SECRET_KEY="your-secret-key-change-this-in-production" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  -v "$SCRIPT_DIR/backend:/app:ro${SELINUX_FLAG}" \
  -v gym_backend_uploads:/app/uploads \
  localhost/gym_backend:latest

# Wait a bit for backend to start
sleep 2

# Start Nginx
echo "Starting Nginx..."
$RUNTIME run -d \
  --name gym_nginx \
  --network gym_network \
  -p 8080:80 \
  -v "$SCRIPT_DIR/nginx/nginx.conf:/etc/nginx/nginx.conf:ro${SELINUX_FLAG}" \
  -v "$SCRIPT_DIR/frontend:/usr/share/nginx/html:ro${SELINUX_FLAG}" \
  -v gym_backend_uploads:/usr/share/nginx/html/uploads:ro \
  docker.io/library/nginx:alpine

echo ""
echo "=================================================="
echo -e "${GREEN}✓ All containers started successfully!${NC}"
echo "=================================================="
echo ""
echo "Access the application at:"
echo "  - Main App:     http://localhost:8080"
echo "  - API Docs:     http://localhost:8080/docs"
echo "  - Health Check: http://localhost:8080/health"
echo ""
echo "Useful commands:"
echo "  - View logs:  $RUNTIME logs -f gym_backend"
echo "  - Stop all:   $RUNTIME stop gym_nginx gym_backend gym_postgres"
echo "  - Restart:    $RUNTIME restart gym_backend"
echo ""
