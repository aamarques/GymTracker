# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack Gym Workout Tracker web application built with FastAPI (backend), PostgreSQL (database), vanilla JavaScript (frontend), and containerized with Docker.

## Architecture

### Backend (FastAPI)
- **Location**: `backend/app/`
- **Framework**: FastAPI with Python 3.11
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **API Docs**: Available at http://localhost/docs

### Frontend
- **Location**: `frontend/`
- **Tech**: Vanilla HTML5, CSS3, JavaScript (no frameworks)
- **Design**: Responsive, mobile-first design
- **Features**: Real-time workout timer, image uploads, interactive UI

### Infrastructure
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy with rate limiting and security headers
- **PostgreSQL**: Database container with persistent volumes

## Build and Run Commands

### Start the application
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f
docker-compose logs backend
docker-compose logs db
```

### Stop the application
```bash
docker-compose down
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Access containers
```bash
docker-compose exec backend bash
docker-compose exec db psql -U gymuser -d gymtracker
```

### Database operations
```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

## Development Workflow

1. **Backend changes**: Edit files in `backend/app/`, hot reload is enabled
2. **Frontend changes**: Edit files in `frontend/`, refresh browser
3. **Database changes**: Create migrations with Alembic
4. **Nginx changes**: Edit `nginx/nginx.conf`, restart nginx container

## Testing

Access the application at:
- **Main App**: http://localhost
- **API Docs**: http://localhost/docs
- **Health Check**: http://localhost/health

## Key Features

### Role-Based System (v0.1.2)
- **Personal Trainers**: Manage exercise library, clients, and workout plans
- **Clients**: Track workouts, cardio, and progress

### Core Features
- User registration and JWT authentication (username OR email login)
- Multi-language support (English & Portuguese)
- Exercise library with image uploads
- Workout plan creation and management (with active/inactive status)
- Active workout sessions with real-time timer
- Cardio session tracking
- Comprehensive metrics and progress tracking
- Weight history tracking with analytics
- Dashboard with statistics and trends
- Profile management with BMI calculation and desired weight goals

## Security Features

- JWT token authentication
- Bcrypt password hashing
- Rate limiting on API endpoints
- CORS protection
- Input validation with Pydantic
- SQL injection prevention via ORM
- Secure file upload handling
