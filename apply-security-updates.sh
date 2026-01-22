#!/bin/bash
#
# Apply Security and Performance Updates
# Run this script after pulling the latest code changes
#

set -e  # Exit on error

echo "============================================================"
echo "🔐 GYMTRACKER - Security & Performance Updates"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're using Podman or Docker
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    echo "✅ Using Podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker-compose"
    echo "✅ Using Docker"
else
    echo -e "${RED}❌ Neither Podman nor Docker found. Please install one of them.${NC}"
    exit 1
fi

echo ""
echo "============================================================"
echo "Step 1: Generate Secure SECRET_KEY"
echo "============================================================"
echo ""

# Check if SECRET_KEY is set in .env
if [ -f "backend/.env" ]; then
    CURRENT_KEY=$(grep "^SECRET_KEY=" backend/.env | cut -d'=' -f2)
    if [ "$CURRENT_KEY" == "your-secret-key-change-this-in-production" ]; then
        echo -e "${YELLOW}⚠️  WARNING: Default SECRET_KEY detected!${NC}"
        echo ""
        echo "Generating a secure SECRET_KEY..."
        NEW_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
        echo ""
        echo -e "${GREEN}Generated KEY:${NC} $NEW_KEY"
        echo ""
        read -p "Apply this key to backend/.env? (y/N) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Update .env file
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" backend/.env
            else
                # Linux
                sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" backend/.env
            fi
            echo -e "${GREEN}✅ SECRET_KEY updated in backend/.env${NC}"
        else
            echo -e "${YELLOW}⚠️  Skipped. Please update SECRET_KEY manually.${NC}"
        fi
    else
        echo -e "${GREEN}✅ Custom SECRET_KEY already set${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  backend/.env not found. Creating from .env.example...${NC}"
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        NEW_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" backend/.env
        else
            sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" backend/.env
        fi
        echo -e "${GREEN}✅ Created backend/.env with secure SECRET_KEY${NC}"
    else
        echo -e "${RED}❌ backend/.env.example not found!${NC}"
        exit 1
    fi
fi

echo ""
echo "============================================================"
echo "Step 2: Rebuild Backend Container"
echo "============================================================"
echo ""

echo "Stopping backend container..."
if [ "$CONTAINER_CMD" == "podman" ]; then
    $CONTAINER_CMD stop gym_backend || true
    $CONTAINER_CMD rm gym_backend || true
    echo "Building new backend image..."
    $CONTAINER_CMD build -t localhost/gym_backend:latest backend/
else
    $COMPOSE_CMD down backend || true
    echo "Building new backend image..."
    $COMPOSE_CMD build backend
fi

echo -e "${GREEN}✅ Backend container rebuilt${NC}"

echo ""
echo "============================================================"
echo "Step 3: Start Containers"
echo "============================================================"
echo ""

if [ "$CONTAINER_CMD" == "podman" ]; then
    bash start-containers.sh
else
    $COMPOSE_CMD up -d
fi

echo ""
echo "Waiting for database to be ready..."
sleep 5

echo ""
echo "============================================================"
echo "Step 4: Apply Database Migrations"
echo "============================================================"
echo ""

echo "Applying migrations..."
if [ "$CONTAINER_CMD" == "podman" ]; then
    $CONTAINER_CMD exec gym_backend alembic upgrade head
else
    $COMPOSE_CMD exec backend alembic upgrade head
fi

echo -e "${GREEN}✅ Database migrations applied${NC}"

echo ""
echo "============================================================"
echo "Step 5: Verify Installation"
echo "============================================================"
echo ""

echo "Checking backend logs for errors..."
if [ "$CONTAINER_CMD" == "podman" ]; then
    $CONTAINER_CMD logs gym_backend | tail -n 20
else
    $COMPOSE_CMD logs backend | tail -n 20
fi

echo ""
echo "Testing health endpoint..."
sleep 2
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo "Check logs: ${CONTAINER_CMD} logs gym_backend"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ Security Updates Applied Successfully!"
echo "============================================================"
echo ""
echo "What was updated:"
echo "  ✅ SECRET_KEY validation added"
echo "  ✅ Login attempt tracking enabled"
echo "  ✅ Account lockout protection (5 attempts, 15 min)"
echo "  ✅ Database indexes for performance"
echo "  ✅ Pagination on all list endpoints"
echo ""
echo "Application URLs:"
echo "  🌐 Frontend:  http://localhost:8080"
echo "  📡 Backend:   http://localhost:8000"
echo "  📖 API Docs:  http://localhost:8000/docs"
echo ""
echo "Next steps:"
echo "  1. Test login functionality"
echo "  2. Verify login lockout (5 failed attempts)"
echo "  3. Review SECURITY_IMPROVEMENTS.md for details"
echo ""
echo "For more info: cat SECURITY_IMPROVEMENTS.md"
echo "============================================================"
