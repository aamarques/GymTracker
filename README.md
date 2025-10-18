# Gym Workout Tracker

A full-stack web application for tracking gym workouts, exercises, and cardio sessions with real-time workout timers and comprehensive progress tracking.

## Features

### User Management
- Secure user registration and authentication with JWT tokens
- Password hashing with bcrypt
- Profile management with BMI and age calculation
- Health metrics tracking

### Exercise Library
- Create and manage exercises with images
- Upload exercise images (PNG, JPG, JPEG, GIF)
- Filter by muscle group
- Search functionality
- Collapsible exercise descriptions

### Workout Planning
- Create custom workout plans
- Add multiple exercises to plans
- Define sets, reps, weight, and rest time
- Save and reuse workout plans

### Active Workout Sessions
- Start/stop workout functionality
- Real-time workout timer (hours:minutes:seconds)
- Log exercises during session
- Track actual performance vs. planned
- Session notes and history

### Cardio Tracking
- Log cardio activities (running, cycling, swimming, etc.)
- Track duration, distance, calories, and location
- View cardio history

### Dashboard
- Quick stats overview
- Total workouts completed
- Current BMI
- Active workout streak
- Total cardio sessions

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - ORM for database operations
- **JWT** - Secure authentication with python-jose
- **Bcrypt** - Password hashing with passlib
- **Pydantic** - Data validation
- **Docker** - Containerization

### Frontend
- **HTML5/CSS3/JavaScript** - Vanilla, no frameworks
- **Responsive Design** - Mobile-first approach
- **Real-time Updates** - Interactive UI with live timers

### Infrastructure
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy with security headers
- **PostgreSQL** - Database container
- **Redis** (optional) - Caching layer

## Security Features

- JWT token-based authentication with expiration
- Bcrypt password hashing with salt
- Input validation and sanitization
- SQL injection prevention via ORM
- CORS protection
- Rate limiting on API endpoints
- Secure file upload handling
- HTTPS/SSL ready configuration
- Security headers (X-Frame-Options, CSP, etc.)

## Quick Start

### Prerequisites
- Docker/Podman installed (Podman recommended for WSL2)
- Git (optional)

### Installation

1. **Clone or download the repository**
```bash
git clone <repository-url>
cd Gym
```

2. **Create environment file**
```bash
cp .env.example .env
```

3. **Configure environment variables** (optional)
Edit `.env` file and update:
- `SECRET_KEY` - Change to a secure random string for production
- `POSTGRES_PASSWORD` - Set a strong database password
- Database credentials if needed

4. **Start the application**

**Option A: Using Podman (Recommended for WSL2)**
```bash
bash start-containers.sh
```

**Option B: Using Docker Compose**
```bash
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker-compose up -d
```

5. **Access the application**
Open your browser and navigate to:
- **Application**: http://localhost:8080 (Podman) or http://localhost (Docker Compose)
- **API Documentation**: http://localhost:8080/docs (Podman) or http://localhost/docs (Docker Compose)
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/health

### First Time Setup

1. **Register a new user**
   - Navigate to http://localhost
   - Click "Register"
   - Fill in your details (all fields required except phone)
   - Password must be at least 8 characters

2. **Add exercises to the library**
   - Go to "Exercises" tab
   - Click "Add Exercise"
   - Upload exercise images for better visualization

3. **Create a workout plan**
   - Go to "Workout Plans" tab
   - Click "Create Plan"
   - Add exercises and configure sets/reps

4. **Start your first workout**
   - Go to "Active Workout" tab
   - Click "Start Workout"
   - Log exercises as you complete them
   - Click "End Workout" when done

## Development

### Project Structure
```
Gym/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration and security
│   │   ├── db/           # Database configuration
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI application
│   ├── uploads/          # Uploaded files
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── css/
│   │   └── style.css    # Application styles
│   ├── js/
│   │   └── app.js       # Application logic
│   └── index.html       # Main HTML file
├── nginx/
│   └── nginx.conf       # Nginx configuration
├── docker-compose.yml
├── .env.example
└── README.md
```

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

#### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/dashboard` - Get dashboard statistics

#### Exercises
- `GET /api/exercises` - List all exercises
- `POST /api/exercises` - Create exercise (with image upload)
- `GET /api/exercises/{id}` - Get exercise details
- `PUT /api/exercises/{id}` - Update exercise
- `DELETE /api/exercises/{id}` - Delete exercise

#### Workout Plans
- `GET /api/workout-plans` - List user's workout plans
- `POST /api/workout-plans` - Create workout plan
- `GET /api/workout-plans/{id}` - Get plan details
- `PUT /api/workout-plans/{id}` - Update plan
- `DELETE /api/workout-plans/{id}` - Delete plan

#### Workout Sessions
- `GET /api/workout-sessions` - List workout sessions
- `POST /api/workout-sessions` - Start workout session
- `GET /api/workout-sessions/active` - Get active session
- `POST /api/workout-sessions/{id}/end` - End workout session
- `POST /api/workout-sessions/{id}/exercises` - Log exercise

#### Cardio
- `GET /api/cardio` - List cardio sessions
- `POST /api/cardio` - Log cardio session
- `GET /api/cardio/{id}` - Get cardio session details
- `PUT /api/cardio/{id}` - Update cardio session
- `DELETE /api/cardio/{id}` - Delete cardio session

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest backend/tests/
```

### Database Migrations

```bash
# Access backend container
docker-compose exec backend bash

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Deployment

### Production Checklist

1. **Update environment variables**
   - Generate a strong `SECRET_KEY`
   - Set strong database password
   - Update `ALLOWED_HOSTS`
   - Set `DEBUG=False`

2. **Enable HTTPS**
   - Configure SSL certificates in Nginx
   - Update nginx.conf with SSL settings
   - Force HTTPS redirect

3. **Database Backup**
   - Set up automated PostgreSQL backups
   - Configure backup retention policy

4. **Monitoring**
   - Set up application monitoring
   - Configure log aggregation
   - Enable health checks

5. **Rate Limiting**
   - Review and adjust rate limits in nginx.conf
   - Consider adding Redis for distributed rate limiting

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Troubleshooting

### WSL2 nftables/netavark Error
If you encounter "nftables error: nft did not return successfully" with Docker Compose in WSL2:
```bash
# Solution 1: Use Podman instead
bash start-containers.sh

# Solution 2: Disable BuildKit for Docker
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker-compose up -d
```

### Database Connection Issues
```bash
# Docker Compose
docker-compose logs db
docker-compose restart db

# Podman
podman logs gym_postgres
podman restart gym_postgres
```

### Backend Not Starting
```bash
# Docker Compose
docker-compose logs backend
docker-compose up -d --build backend

# Podman
podman logs gym_backend
podman stop gym_backend && podman rm gym_backend
bash start-containers.sh
```

### Bcrypt Password Hashing Error
If you see "ValueError: password cannot be longer than 72 bytes":
- This is fixed in the current version using `bcrypt==4.1.2` directly
- Rebuild the backend container to apply the fix

### File Upload Issues
```bash
# Docker Compose
docker-compose exec backend ls -la /app/uploads
docker-compose exec backend mkdir -p /app/uploads/exercises

# Podman
podman exec gym_backend ls -la /app/uploads
podman exec gym_backend mkdir -p /app/uploads/exercises
```

### Port Already in Use
```bash
# Docker Compose
docker-compose down

# Podman
podman stop gym_nginx gym_backend gym_postgres
podman rm gym_nginx gym_backend gym_postgres

# Check what's using the port
sudo lsof -i :80
sudo lsof -i :8080
sudo lsof -i :5432
```

### Container Management Commands
```bash
# Docker Compose
docker-compose ps              # List containers
docker-compose logs -f         # Follow all logs
docker-compose down -v         # Stop and remove volumes
docker-compose restart         # Restart all services

# Podman
podman ps -a                   # List all containers
podman logs -f gym_backend     # Follow backend logs
podman volume ls               # List volumes
podman stop gym_nginx gym_backend gym_postgres  # Stop all
```

## Documentation

### Quick Links
- **[Quick Start Guide](docs/QUICK_START.md)** - Get running in 5 minutes
- **[API Documentation](docs/API.md)** - Complete API reference
- **[Development Guide](docs/DEVELOPMENT.md)** - Developer setup and workflow
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment
- **[Documentation Index](docs/INDEX.md)** - Complete documentation map

### Interactive API Documentation
Once the application is running, visit http://localhost:8000/docs for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review the API documentation at http://localhost/docs
- Check application logs: `docker-compose logs -f`

## Future Enhancements

- Progressive Web App (PWA) features
- Push notifications for rest timers
- Social features and workout sharing
- Advanced analytics and progress charts
- Integration with fitness wearables
- Nutrition tracking
- Exercise video tutorials
- Workout templates library
- Personal records tracking
- Export workout data to CSV/PDF
