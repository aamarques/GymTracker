# Gym Workout Tracker

**Version 0.1.2** - Enhanced Role-Based Workflow & Client Management

A full-stack web application for Personal Trainers and Clients to manage workouts, exercises, and progress tracking with multi-tenant architecture, internationalization support, and streamlined role-based workflows.

## Features

### 🆕 Enhanced Role-Based System (V0.1.2)
- **Personal Trainer Role:**
  - Create and manage exercise library
  - Add/remove clients from roster
  - Create custom workout plans for each client
  - Define exercises, sets, reps, weight, and rest time per workout
  - Mark workout plans as active for client's default
  - Dedicated tabs: Dashboard, Exercises, My Clients, Profile
- **Client Role:**
  - Self-registration with username and email
  - View assigned workout plans from Personal Trainer
  - Start workout sessions directly from "Treino Ativo" (Active Workout)
  - Real-time workout timer and exercise logging
  - Track cardio sessions
  - Health metrics analysis with BMI and weight goal tracking
  - Dedicated tabs: Dashboard, Active Workout, Cardio, Profile

### 🌍 Internationalization (V0.1.0)
- Support for English and Portuguese languages
- User-selectable language preference
- 180+ translated UI strings
- Real-time language switching

### User Management
- Secure user registration and authentication with JWT tokens
- Role-based access control (Personal Trainer / Client)
- Password hashing with bcrypt
- Profile management with BMI and age calculation
- Health metrics tracking with personalized recommendations

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

**Using Podman (default WSL2 configuration):**
- **Application**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/health

**Using Docker Compose (with privileged port access):**
- **Application**: http://localhost
- **API Documentation**: http://localhost/docs
- **Backend API**: http://localhost:8000

> **Note**: Podman uses port 8080 to avoid privileged port binding issues on WSL2. See [WSL2 + Podman Setup Guide](docs/WSL2_PODMAN_SETUP.md) for details.

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

### WSL2 + Podman Issues

If you encounter issues running with Podman on WSL2, see the **[WSL2 + Podman Setup Guide](docs/WSL2_PODMAN_SETUP.md)** for complete configuration instructions.

**Common WSL2/Podman errors:**

1. **nftables/netavark Error**
   ```
   Error: netavark: nftables error: nft did not return successfully
   ```
   **Fix**: Configure netavark to use iptables instead of nftables
   ```bash
   # Add to ~/.config/containers/containers.conf
   [network]
   firewall_driver = "iptables"
   ```

2. **Privileged Port Binding Error**
   ```
   Error: rootlessport cannot expose privileged port 80
   ```
   **Fix**: Use port 8080 instead (already configured in docker-compose.yml)

   See the [WSL2 + Podman Setup Guide](docs/WSL2_PODMAN_SETUP.md) for detailed solutions.

### WSL2 nftables/netavark Error (Legacy Docker)
If you encounter "nftables error: nft did not return successfully" with Docker Compose in WSL2:
```bash
# Solution 1: Use Podman instead (recommended)
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
- **[WSL2 + Podman Setup](docs/WSL2_PODMAN_SETUP.md)** - WSL2/Podman configuration guide
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

## Version History

### Version 0.1.2 (January 2025) - Current
**Enhanced Role-Based Workflow & Client Management:**

**🔐 Authentication & User Management:**
- ✅ Added username field to user model with unique constraint
- ✅ Login with username OR email support
- ✅ Automatic username generation for existing users (migration)
- ✅ Username editing in user profile
- ✅ Role-based registration fields (health fields only for clients)
- ✅ Removed PT ID from client registration (PTs now assign clients)

**👥 Client Management (Personal Trainers):**
- ✅ "Add Client" functionality - PTs can add/remove clients
- ✅ Client roster management in "My Clients" tab
- ✅ Create workout plans directly for specific clients
- ✅ View client details (BMI, weight, height)
- ✅ Workout plans assigned to clients (not PTs)

**🏋️ Workout Management:**
- ✅ Workout plan creation with active/inactive toggle
- ✅ Active workout plans marked as default for clients
- ✅ Fixed workout plan deletion (JSON error resolved)
- ✅ Automatic workout session start from plan selection
- ✅ Real-time workout timer and exercise logging
- ✅ Clients see their assigned plans in "Treino Ativo" (Active Workout)

**📊 Role-Based UI:**
- ✅ Personal Trainers see: Dashboard, Exercises, My Clients, Profile
- ✅ Clients see: Dashboard (with health metrics), Active Workout, Cardio, Profile
- ✅ Hidden "Treinos" tab (replaced by client-specific workflow)
- ✅ Health metrics and BMI only for clients
- ✅ Exercise library only accessible to Personal Trainers

**🌍 Internationalization:**
- ✅ Added translations for client management buttons
- ✅ Translated "Add Client", "Create Workout", "Remove" buttons
- ✅ Updated Portuguese translations for new features
- ✅ Better placeholder and label translations

**🎨 UX Improvements:**
- ✅ Improved checkbox formatting for "Set as Active Plan"
- ✅ Clear workflow: PT → My Clients → Create Workout → Client sees in Active Workout
- ✅ Registration form auto-clears after successful signup
- ✅ Conditional field visibility based on user role
- ✅ Better error messages and user feedback

### Version 0.1.1 (October 2025)
**Bug Fixes & UX Improvements:**
- ✅ Fixed nginx configuration for Docker container networking
- ✅ Fixed database enum type mismatch (role field)
- ✅ Fixed SQLAlchemy enum handling for user roles
- ✅ Improved empty state messages for Exercises, Workout Plans, and Clients
- ✅ Added role-specific empty state guidance
- ✅ Added glassmorphism styling for empty states
- ✅ Added multilingual support for empty state messages

### Version 0.1.0 (October 2025)
**Multi-Tenant Release:**
- ✅ Multi-tenant system (Personal Trainers & Clients)
- ✅ Client-Trainer relationships
- ✅ Exercise assignment system
- ✅ Internationalization (English & Portuguese)
- ✅ Role-based access control
- ✅ Language preferences in user profile

### Version 0.0.1 (Initial Release)
- Basic workout tracking
- Exercise library
- Workout plans
- Cardio tracking
- Dashboard statistics

## Future Enhancements

See [docs/FUTURE_IMPROVEMENTS.md](docs/FUTURE_IMPROVEMENTS.md) for detailed roadmap.

**Planned for V0.2.0 (Q1 2026):**
- Client invitation system via email
- Workout plan templates for PTs
- Progress tracking and analytics
- In-app messaging between PT and clients
- Additional languages (Spanish, French, German)
- Exercise video uploads
- Client progress photos

**Future Versions:**
- Mobile application (React Native / Flutter)
- Nutrition tracking
- Payment & subscription management
- Group training and classes
- Gamification and achievements
- AI-powered features (form analysis, workout suggestions)
