# 🚀 GymTracker - Installation Guide

Complete guide to install GymTracker on a new computer.

---

## 📋 System Requirements

### Minimum Requirements
- **OS:** Linux, macOS, or Windows (with WSL2)
- **RAM:** 2GB minimum, 4GB recommended
- **Disk Space:** 2GB free space
- **Network:** Internet connection for initial setup

### Software Requirements
- **Docker** OR **Podman** (container runtime)
- **Git** (optional, for cloning repository)

---

## 🔧 Step 1: Install Prerequisites

### Option A: Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Docker
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, avoids using sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect

# OR Install Podman (alternative to Docker)
sudo apt install -y podman
```

### Option B: Windows (WSL2)

**Install WSL2 first:**
```powershell
# Run in PowerShell as Administrator
wsl --install
```

**Then install Podman in WSL2:**
```bash
# Inside WSL2 terminal
sudo apt update
sudo apt install -y podman

# Configure podman (recommended for WSL2)
mkdir -p ~/.config/containers
cat > ~/.config/containers/containers.conf <<EOF
[network]
firewall_driver = "iptables"
EOF
```

### Option C: macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop
brew install --cask docker

# OR Install Podman
brew install podman
podman machine init
podman machine start
```

### Verify Installation

```bash
# Check Docker
docker --version
docker-compose --version

# OR Check Podman
podman --version
```

---

## 📥 Step 2: Download GymTracker

### Option A: Using Git (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/GymTracker.git

# Navigate to directory
cd GymTracker
```

### Option B: Download ZIP

1. Download the ZIP file from GitHub
2. Extract to desired location
3. Open terminal in the extracted folder

```bash
# Example
cd /path/to/GymTracker
```

---

## ⚙️ Step 3: Configuration (Optional but Recommended)

### Create Environment File

```bash
# Copy example environment file
cp backend/.env.example backend/.env
```

### Edit Configuration (Optional)

Open `backend/.env` and customize:

```bash
# Edit with your preferred editor
nano backend/.env
# or
vim backend/.env
# or
code backend/.env  # VS Code
```

**Key settings to change for production:**

```env
# Security - CHANGE THIS!
SECRET_KEY=your-super-secret-key-change-me-in-production

# Database
POSTGRES_PASSWORD=your-strong-password-here

# Email (optional - for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

> **Note:** For development/testing, the default values work fine. Change them for production use.

---

## 🚀 Step 4: Start the Application

### Using Podman (Recommended for WSL2/Linux)

```bash
# Start containers
./start-containers.sh
```

### Using Docker Compose

```bash
# For WSL2 (disable BuildKit)
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# Start containers
docker-compose up -d
```

### What This Does

The startup script will:
1. ✅ Build the backend container (Python + FastAPI)
2. ✅ Start PostgreSQL database
3. ✅ Run database migrations
4. ✅ Start Nginx reverse proxy
5. ✅ Expose the application

**First time setup takes 2-5 minutes** (downloading images and building).

---

## 🌐 Step 5: Access the Application

### Open Your Browser

**For Podman (default):**
- Main App: **http://localhost:8080**
- API Docs: **http://localhost:8080/docs**

**For Docker Compose:**
- Main App: **http://localhost**
- API Docs: **http://localhost/docs**

### Create Your First Account

1. Click **"Register"**
2. Fill in your details:
   - **Role:** Select "Personal Trainer" or "Client"
   - **Email:** Your email address
   - **Username:** Choose a username
   - **Password:** At least 8 characters
   - Fill in other required fields
3. Click **"Register"**
4. Login with your credentials

---

## 📚 Step 6: Load Exercise Library (Optional)

### Import Sample Exercises

```bash
# Import English exercises
./import-exercises.sh exercises_template.csv

# OR Import Portuguese exercises
./import-exercises-pt.sh Imports/exercicios.csv
```

### Import Your Own Exercises

See **[Exercise Import Guide](IMPORT_EXERCISES_GUIDE.md)** for detailed instructions.

---

## ✅ Verify Installation

### Check All Services Running

**Podman:**
```bash
podman ps
```

**Docker:**
```bash
docker-compose ps
```

You should see 3 containers:
- `gym_postgres` - Database
- `gym_backend` - API Server
- `gym_nginx` - Web Server

### Check Application Health

```bash
# Check backend health
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### View Logs

**Podman:**
```bash
podman logs gym_backend
podman logs gym_postgres
podman logs gym_nginx
```

**Docker:**
```bash
docker-compose logs backend
docker-compose logs db
docker-compose logs nginx
```

---

## 🛠️ Common Commands

### Start/Stop/Restart

**Podman:**
```bash
# Stop
podman stop gym_nginx gym_backend gym_postgres

# Start
./start-containers.sh

# Restart single service
podman restart gym_backend
```

**Docker Compose:**
```bash
# Stop
docker-compose down

# Start
docker-compose up -d

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build
```

### View Logs

```bash
# Podman
podman logs -f gym_backend

# Docker
docker-compose logs -f backend
```

### Access Database

```bash
# Podman
podman exec -it gym_postgres psql -U gymuser -d gymtracker

# Docker
docker-compose exec db psql -U gymuser -d gymtracker
```

---

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `port is already allocated`

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :8080
sudo lsof -i :80

# Stop the conflicting service or change ports in docker-compose.yml
```

### Containers Won't Start

**Solution:**
```bash
# Podman
podman stop gym_nginx gym_backend gym_postgres
podman rm gym_nginx gym_backend gym_postgres
podman volume prune
./start-containers.sh

# Docker
docker-compose down -v
docker-compose up -d --build
```

### Database Connection Error

**Solution:**
```bash
# Check database is healthy
podman logs gym_postgres
# or
docker-compose logs db

# Restart database
podman restart gym_postgres
# or
docker-compose restart db
```

### Permission Denied (Linux)

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then try again
```

### Podman "cannot clone: Permission denied"

**Error:**
```
cannot clone: Permission denied
Error: cannot re-exec process
```

**Solution 1: Configure User Namespaces (Recommended)**
```bash
# Add user namespace configuration
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $(whoami)

# Enable user namespaces
echo "user.max_user_namespaces=15000" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Reset podman
podman system reset --force

# Try again
./start-containers.sh
```

**Solution 2: Use Improved Script (Auto-detects issues)**
```bash
# Use the improved startup script
./start-containers-improved.sh

# This script will:
# - Auto-detect Podman/Docker
# - Handle permission issues
# - Offer to run with sudo if needed
# - Build images automatically
```

**Solution 3: Run with Sudo (Quick Fix)**
```bash
sudo bash start-containers.sh
```

**Solution 4: Switch to Docker**
```bash
# Install Docker instead
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER

# Log out and back in, then:
docker-compose up -d
```

### WSL2 Network Issues

See **[WSL2 + Podman Setup Guide](docs/WSL2_PODMAN_SETUP.md)** for detailed WSL2 troubleshooting.

---

## 📦 What Gets Installed?

### Containers
- **PostgreSQL 15** - Database
- **Python 3.11** - Backend runtime
- **FastAPI** - Web framework
- **Nginx** - Reverse proxy

### Directories Created
- `backend/uploads/` - Uploaded images
- PostgreSQL data volume - Database storage

### Ports Used
- `8080` (Podman) or `80` (Docker) - Web interface
- `8000` - Backend API (internal)
- `5432` - PostgreSQL (internal)

---

## 🔒 Security Notes

### For Production Deployment

1. **Change SECRET_KEY** in `.env`
2. **Set strong POSTGRES_PASSWORD**
3. **Enable HTTPS** (configure SSL certificates)
4. **Use firewall** to restrict access
5. **Regular backups** of database
6. **Update regularly** for security patches

### Backup Database

```bash
# Podman
podman exec gym_postgres pg_dump -U gymuser gymtracker > backup_$(date +%Y%m%d).sql

# Docker
docker-compose exec db pg_dump -U gymuser gymtracker > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# Podman
podman exec -i gym_postgres psql -U gymuser gymtracker < backup_20250101.sql

# Docker
docker-compose exec -T db psql -U gymuser gymtracker < backup_20250101.sql
```

---

## 📖 Next Steps

1. ✅ **Read the [User Guide](docs/QUICK_START.md)**
2. ✅ **Import exercises** - [Import Guide](IMPORT_EXERCISES_GUIDE.md)
3. ✅ **Admin scripts** - [Admin Guide](ADMIN_GUIDE.md)
4. ✅ **API documentation** - http://localhost:8080/docs

---

## 🆘 Getting Help

- **Documentation:** [docs/INDEX.md](docs/INDEX.md)
- **Troubleshooting:** See sections above
- **API Reference:** http://localhost:8080/docs
- **Issues:** Check application logs

---

## 📝 Summary

**Minimum Installation Steps:**

```bash
# 1. Install Docker or Podman
sudo apt install podman

# 2. Download GymTracker
git clone <repository-url>
cd GymTracker

# 3. Start application
./start-containers.sh

# 4. Open browser
# http://localhost:8080

# Done! 🎉
```

**Total Time:** 5-10 minutes (including downloads)

---

**Enjoy your GymTracker installation!** 💪
