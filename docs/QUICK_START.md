# Gym Workout Tracker - Quick Start Guide

Get up and running in 5 minutes!

## For WSL2 Users (Recommended)

### 1. Start the Application

```bash
cd /mnt/c/Users/Alexandre/WSL_HOME/Gym
bash start-containers.sh
```

### 2. Access the Application

Open your browser:
- **Main App**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8000/health

### 3. Register Your Account

1. Go to http://localhost:8080
2. Click "Register"
3. Fill in your details:
   - Email
   - Password (min 8 characters)
   - Name
   - Date of Birth (format: YYYY-MM-DDTHH:MM:SS)
   - Weight (kg)
   - Height (cm)
4. Click "Register"

### 4. Start Using the App

**Add Exercises:**
1. Go to "Exercises" tab
2. Click "Add Exercise"
3. Fill in exercise details
4. Upload an image (optional)

**Create Workout Plan:**
1. Go to "Workout Plans" tab
2. Click "Create Plan"
3. Add exercises from your library
4. Set sets, reps, and rest times

**Start Workout:**
1. Go to "Active Workout" tab
2. Select a workout plan (or freestyle)
3. Click "Start Workout"
4. Log exercises as you complete them
5. Click "End Workout" when done

**Track Cardio:**
1. Go to "Cardio" tab
2. Click "Log Cardio"
3. Enter activity details
4. Save

---

## For Docker Users

### 1. Start with Docker Compose

```bash
cd Gym
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker-compose up -d
```

### 2. Access the Application

- **Main App**: http://localhost
- **API Docs**: http://localhost/docs

### 3. Follow steps 3-4 from above

---

## Container Management

### Check Status

```bash
# Podman
podman ps

# Docker
docker-compose ps
```

### View Logs

```bash
# Podman
podman logs -f gym_backend
podman logs -f gym_postgres

# Docker
docker-compose logs -f backend
docker-compose logs -f db
```

### Stop Containers

```bash
# Podman
podman stop gym_nginx gym_backend gym_postgres

# Docker
docker-compose down
```

### Restart Containers

```bash
# Podman
podman restart gym_backend

# Docker
docker-compose restart backend
```

---

## Common Issues

### "Cannot register"
- Check backend logs: `podman logs gym_backend`
- Verify database is running: `podman ps | grep postgres`
- Check API health: `curl http://localhost:8000/health`

### "nftables error"
- Use the Podman script: `bash start-containers.sh`
- Or disable BuildKit for Docker (see above)

### "Port already in use"
- Stop existing containers first
- Check what's using the port: `sudo lsof -i :8080`

### "Database connection failed"
- Restart PostgreSQL: `podman restart gym_postgres`
- Check logs: `podman logs gym_postgres`

---

## Quick Commands Cheat Sheet

```bash
# Start everything
bash start-containers.sh

# Stop everything
podman stop gym_nginx gym_backend gym_postgres
podman rm gym_nginx gym_backend gym_postgres

# View all logs
podman logs gym_backend
podman logs gym_postgres
podman logs gym_nginx

# Access database
podman exec -it gym_postgres psql -U gymuser -d gymtracker

# Rebuild backend after code changes
podman stop gym_backend && podman rm gym_backend
podman build -t localhost/gym_backend:latest backend/
bash start-containers.sh

# Check container stats
podman stats

# List volumes
podman volume ls
```

---

## Next Steps

Once you're up and running:

1. **Read the full documentation**:
   - [README.md](../README.md) - Complete overview
   - [API.md](API.md) - API documentation
   - [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Explore the API**:
   - Visit http://localhost:8080/docs
   - Try out the interactive API documentation

3. **Customize your experience**:
   - Update your profile with accurate metrics
   - Create your exercise library
   - Build workout plans that match your goals

4. **Track your progress**:
   - Log workouts regularly
   - Monitor your dashboard statistics
   - Track weight and BMI changes over time

---

## Getting Help

- Check the [Troubleshooting section](../README.md#troubleshooting) in README
- Review [Common Issues](#common-issues) above
- Check container logs for error details
- Ensure all services are running: `podman ps`

Happy training!
