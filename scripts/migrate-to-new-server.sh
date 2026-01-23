#!/bin/bash

# ============================================================
# GymTracker - Migration to New Server Script
# ============================================================
# This script helps migrate GymTracker from one server to another
#
# Usage:
#   ./migrate-to-new-server.sh backup    # On OLD server
#   ./migrate-to-new-server.sh restore   # On NEW server
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BACKUP_DIR="gymtracker_migration_$(date +%Y%m%d_%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================
# BACKUP FUNCTION - Run on OLD server
# ============================================================
backup_database() {
    echo "============================================================"
    echo "BACKUP - Creating Migration Package"
    echo "============================================================"
    echo ""

    # Check if container is running
    if ! podman ps | grep -q gym_backend && ! podman ps | grep -q gym_backend; then
        echo -e "${RED}❌ Error: Backend container is not running!${NC}"
        echo ""
        echo "Start containers first:"
        echo "  docker-compose up -d"
        echo "  or: podman-compose up -d"
        exit 1
    fi

    # Detect runtime
    if command -v podman &> /dev/null && podman ps | grep -q gym_backend; then
        RUNTIME="podman"
    else
        RUNTIME="docker"
    fi

    echo "Using runtime: $RUNTIME"
    echo ""

    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    cd "$BACKUP_DIR"

    # 1. Backup database
    echo "📦 Step 1/4: Backing up database..."
    $RUNTIME exec gym_postgres pg_dump -U gymuser gymtracker > database.sql
    gzip database.sql
    echo -e "${GREEN}✅ Database backup: database.sql.gz ($(du -h database.sql.gz | cut -f1))${NC}"

    # 2. Export exercise images
    echo ""
    echo "🖼️  Step 2/4: Exporting exercise images..."
    cd "$SCRIPT_DIR"
    if [ -f "export-exercise-images.sh" ]; then
        ./export-exercise-images.sh exported_exercise_images
        mv exported_exercise_images "$BACKUP_DIR/"
        IMG_COUNT=$(ls -1 "$BACKUP_DIR/exported_exercise_images" 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ Exported $IMG_COUNT exercise images${NC}"
    else
        echo -e "${YELLOW}⚠️  export-exercise-images.sh not found, skipping images${NC}"
    fi

    # 3. Copy configuration files
    echo ""
    echo "⚙️  Step 3/4: Copying configuration files..."
    cd "$SCRIPT_DIR"
    cp docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
    cp docker-compose-simple.yml "$BACKUP_DIR/" 2>/dev/null || true
    cp -r backend/.env "$BACKUP_DIR/env_backup" 2>/dev/null || true
    echo -e "${GREEN}✅ Configuration files copied${NC}"

    # 4. Create migration info
    echo ""
    echo "📋 Step 4/4: Creating migration info..."
    cat > "$BACKUP_DIR/MIGRATION_INFO.txt" <<EOF
GymTracker Migration Package
Created: $(date)
Runtime: $RUNTIME

Database: database.sql.gz
Images: exported_exercise_images/
Config: docker-compose files

Instructions:
1. Copy this entire folder to new server
2. Run: ./migrate-to-new-server.sh restore

EOF
    echo -e "${GREEN}✅ Migration info created${NC}"

    # Create archive
    echo ""
    echo "📦 Creating archive..."
    cd "$SCRIPT_DIR"
    tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"

    echo ""
    echo "============================================================"
    echo -e "${GREEN}✅ BACKUP COMPLETE!${NC}"
    echo "============================================================"
    echo ""
    echo "Migration package: ${BACKUP_DIR}.tar.gz"
    echo "Size: $(du -h ${BACKUP_DIR}.tar.gz | cut -f1)"
    echo ""
    echo "Transfer to new server:"
    echo "  scp ${BACKUP_DIR}.tar.gz user@newserver:/tmp/"
    echo ""
    echo "Then on new server:"
    echo "  cd /opt/GymTracker"
    echo "  tar -xzf /tmp/${BACKUP_DIR}.tar.gz"
    echo "  cd ${BACKUP_DIR}"
    echo "  ../migrate-to-new-server.sh restore"
    echo ""
}

# ============================================================
# RESTORE FUNCTION - Run on NEW server
# ============================================================
restore_database() {
    echo "============================================================"
    echo "RESTORE - Migrating to New Server"
    echo "============================================================"
    echo ""

    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ This script must be run with sudo${NC}"
        echo "Run: sudo ./migrate-to-new-server.sh restore"
        exit 1
    fi

    # Find backup files
    if [ ! -f "database.sql.gz" ] && [ ! -f "database.sql" ]; then
        echo -e "${RED}❌ Error: database backup not found!${NC}"
        echo ""
        echo "Make sure you're in the migration backup directory"
        exit 1
    fi

    # Detect docker-compose file
    COMPOSE_FILE="docker-compose-simple.yml"
    if [ ! -f "$COMPOSE_FILE" ]; then
        COMPOSE_FILE="docker-compose.yml"
    fi

    echo "Using compose file: $COMPOSE_FILE"
    echo ""

    # Step 1: Stop everything
    echo "🛑 Step 1/8: Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true
    docker stop gym_postgres gym_backend gym_nginx 2>/dev/null || true
    docker rm gym_postgres gym_backend gym_nginx 2>/dev/null || true

    # Step 2: Remove volumes
    echo ""
    echo "🗑️  Step 2/8: Removing old volumes..."
    docker volume rm gymtracker_postgres_data 2>/dev/null || true
    docker volume rm gymtracker_backend_uploads 2>/dev/null || true
    REMOVED=$(docker volume ls -q | grep gym | wc -l)
    if [ $REMOVED -gt 0 ]; then
        docker volume rm $(docker volume ls -q | grep gym) 2>/dev/null || true
    fi

    # Step 3: Clean data directories
    echo ""
    echo "🧹 Step 3/8: Cleaning data directories..."
    rm -rf /opt/GymTracker/data/postgres
    rm -rf /opt/GymTracker/data/uploads
    mkdir -p /opt/GymTracker/data/postgres
    mkdir -p /opt/GymTracker/data/uploads
    chmod -R 777 /opt/GymTracker/data

    # Step 4: Start PostgreSQL only
    echo ""
    echo "🐘 Step 4/8: Starting PostgreSQL (temporary)..."
    docker run -d \
      --name gym_postgres_temp \
      -e POSTGRES_USER=gymuser \
      -e POSTGRES_PASSWORD=gympass123 \
      -e POSTGRES_DB=gymtracker \
      -v /opt/GymTracker/data/postgres:/var/lib/postgresql/data \
      -p 5432:5432 \
      postgres:15-alpine

    # Step 5: Wait for PostgreSQL
    echo ""
    echo "⏳ Step 5/8: Waiting for PostgreSQL to initialize..."
    sleep 10
    for i in {1..30}; do
        if podman exec gym_postgres_temp pg_isready -U gymuser &>/dev/null; then
            echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ PostgreSQL failed to start${NC}"
            docker logs gym_postgres_temp
            exit 1
        fi
        sleep 1
    done

    # Step 6: Restore database
    echo ""
    echo "💾 Step 6/8: Restoring database..."
    if [ -f "database.sql.gz" ]; then
        gunzip -c database.sql.gz | podman exec -i gym_postgres_temp psql -U gymuser gymtracker
    elif [ -f "database.sql" ]; then
        podman exec -i gym_postgres_temp psql -U gymuser gymtracker < database.sql
    fi

    # Verify restore
    EXERCISE_COUNT=$(podman exec gym_postgres_temp psql -U gymuser gymtracker -t -c "SELECT COUNT(*) FROM exercises;" 2>/dev/null | xargs)
    USER_COUNT=$(podman exec gym_postgres_temp psql -U gymuser gymtracker -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs)

    echo -e "${GREEN}✅ Database restored:${NC}"
    echo "   - Users: $USER_COUNT"
    echo "   - Exercises: $EXERCISE_COUNT"

    # Step 7: Restore images
    echo ""
    echo "🖼️  Step 7/8: Restoring exercise images..."
    if [ -d "exported_exercise_images" ]; then
        mkdir -p /opt/GymTracker/data/uploads/exercises
        cp -r exported_exercise_images/* /opt/GymTracker/data/uploads/exercises/
        chmod -R 777 /opt/GymTracker/data/uploads
        IMG_COUNT=$(ls -1 /opt/GymTracker/data/uploads/exercises 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ Restored $IMG_COUNT exercise images${NC}"
    else
        echo -e "${YELLOW}⚠️  No images found, skipping${NC}"
    fi

    # Step 8: Stop temp container and start with docker-compose
    echo ""
    echo "🚀 Step 8/8: Starting full application..."
    docker stop gym_postgres_temp
    docker rm gym_postgres_temp

    # Copy compose file to /opt/GymTracker if needed
    if [ ! -f "/opt/GymTracker/$COMPOSE_FILE" ]; then
        cp "$COMPOSE_FILE" /opt/GymTracker/
    fi

    cd /opt/GymTracker
    docker-compose -f "$COMPOSE_FILE" up -d

    # Wait for services
    echo ""
    echo "⏳ Waiting for services to start..."
    sleep 10

    # Verify
    echo ""
    echo "🔍 Verifying installation..."
    podman ps --filter "name=gym_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    echo "============================================================"
    echo -e "${GREEN}✅ MIGRATION COMPLETE!${NC}"
    echo "============================================================"
    echo ""
    echo "Application is running at:"
    echo "  - Main App:  http://$(hostname -I | awk '{print $1}')"
    echo "  - API Docs:  http://$(hostname -I | awk '{print $1}')/docs"
    echo "  - Health:    http://$(hostname -I | awk '{print $1}')/health"
    echo ""
    echo "Database restored with:"
    echo "  - $USER_COUNT users"
    echo "  - $EXERCISE_COUNT exercises"
    echo "  - $IMG_COUNT images"
    echo ""
    echo "To verify:"
    echo "  podman ps"
    echo "  curl http://localhost/health"
    echo ""
}

# ============================================================
# MAIN
# ============================================================

case "$1" in
    backup)
        backup_database
        ;;
    restore)
        restore_database
        ;;
    *)
        echo "Usage: $0 {backup|restore}"
        echo ""
        echo "On OLD server (create backup):"
        echo "  ./migrate-to-new-server.sh backup"
        echo ""
        echo "On NEW server (restore backup):"
        echo "  sudo ./migrate-to-new-server.sh restore"
        echo ""
        exit 1
        ;;
esac
