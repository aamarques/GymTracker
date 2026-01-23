# Changelog

All notable changes to the Gym Workout Tracker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-01-20

### Added
- **Comprehensive Client Metrics System**
  - Automatic tracking of all workout and cardio activities
  - Cumulative metrics that persist even when clients reset their workout count
  - Weight history tracking with min/max values and time intervals
  - Consistency percentage calculation based on active training days
  - Total sets and reps tracking across all workouts
  - Detailed progress analysis with 30-day workout trends
  - Client ability to reset workout count while preserving PT visibility

- **Personal Trainer Dashboard Enhancements**
  - View metrics for all clients in one place
  - Dashboard summary with aggregate statistics
  - Most active and most consistent client highlights
  - Individual client detailed metrics and progress
  - Client weight history tracking and analysis

- **New API Endpoints**
  - `GET /api/metrics/my-metrics` - Client metrics overview
  - `GET /api/metrics/my-progress` - Client progress analysis
  - `GET /api/metrics/weight-history` - Client weight history
  - `POST /api/metrics/workouts/reset` - Reset workout count
  - `GET /api/metrics/clients` - PT view all clients
  - `GET /api/metrics/clients/{id}` - PT view client details
  - `GET /api/metrics/clients/{id}/progress` - PT view client progress
  - `GET /api/metrics/clients/{id}/weight-history` - PT view client weight history
  - `GET /api/metrics/dashboard-summary` - PT dashboard summary

### Changed
- Weight updates now automatically tracked in weight history table
- Workout sessions automatically update client metrics
- Cardio sessions automatically update client metrics
- Enhanced client-trainer relationship tracking

### Database
- Added `client_metrics` table for comprehensive client tracking
- Added `weight_history` table for weight change tracking
- Migration for existing users to initialize metrics

---

## [0.1.1] - 2025-10-19

### Fixed
- Fixed nginx configuration for Docker container networking
- Fixed database enum type mismatch (role field)
- Fixed SQLAlchemy enum handling for user roles

### Changed
- Improved empty state messages for Exercises, Workout Plans, and Clients
- Added role-specific empty state guidance
- Added glassmorphism styling for empty states
- Enhanced multilingual support for empty state messages

---

## [0.1.0] - 2025-10-15

### Added
- Comprehensive documentation suite
  - Quick Start Guide for new users
  - Complete API documentation with examples
  - Development guide with setup instructions
  - Deployment guide for production environments
  - Documentation index for easy navigation
- Podman support for WSL2 environments
- `start-containers.sh` script for easy Podman deployment
- Container management commands in troubleshooting section

### Changed
- **BREAKING**: Replaced `passlib[bcrypt]` with `bcrypt==4.1.2` for improved compatibility
  - Direct bcrypt implementation for password hashing
  - Fixes password hashing errors in some environments
  - Automatic 72-byte password truncation for bcrypt compatibility
- Updated README with WSL2/Podman instructions
- Enhanced troubleshooting section with container-specific commands
- Improved error handling in authentication endpoints

### Fixed
- WSL2 nftables/netavark networking issue with Docker Compose
- Bcrypt "password cannot be longer than 72 bytes" error
- Database configuration mismatch in start scripts
- Container naming conflicts in multi-environment setups
- Security.py password hashing compatibility issues

### Security
- Updated to bcrypt 4.1.2 with improved security
- Fixed password truncation to meet bcrypt requirements
- Enhanced JWT token security documentation

## [0.0.1] - 2025-10-10

### Added
- Initial release
- User authentication with JWT tokens
- User registration and profile management
- Exercise library with image uploads
- Workout plan creation and management
- Active workout session tracking with real-time timer
- Cardio activity logging
- Dashboard with statistics
- BMI and age calculation
- PostgreSQL database with SQLAlchemy ORM
- FastAPI backend with automatic API documentation
- Vanilla JavaScript frontend with responsive design
- Docker Compose orchestration
- Nginx reverse proxy with security headers
- Rate limiting on API endpoints
- File upload handling for exercise images
- Database migrations with Alembic

### Security Features
- JWT token-based authentication
- Bcrypt password hashing
- Input validation with Pydantic
- SQL injection prevention via ORM
- CORS protection
- Secure file upload handling
- Security headers (X-Frame-Options, CSP, etc.)

---

## Version History

### [Unreleased]
Features and fixes in development:
- Push notifications for rest timers
- Progressive Web App (PWA) features
- Social features and workout sharing
- Advanced analytics and progress charts
- Integration with fitness wearables
- Nutrition tracking
- Exercise video tutorials
- Workout templates library
- Personal records tracking
- Export workout data to CSV/PDF

---

## Release Notes

### Version 0.1.2 Notes

This release introduces a comprehensive metrics and progress tracking system that enables Personal Trainers to monitor their clients' progress in detail. Key highlights:

**For Personal Trainers:**
- Track all client activities automatically
- View aggregate statistics across all clients
- Monitor individual client progress and consistency
- Access detailed weight history for each client

**For Clients:**
- View personal workout statistics and trends
- Track weight changes over time
- Analyze progress with trend data
- Reset workout count while preserving data for trainer

**Database Changes:**
- New `client_metrics` table tracks cumulative client data
- New `weight_history` table records all weight changes
- Automatic migrations handle existing users

### Version 0.1.1 Notes

Bug fixes and UX improvements focusing on role-based empty states and database compatibility.

### Version 0.1.0 Notes

Major release introducing multi-tenant system with Personal Trainer and Client roles, internationalization (English & Portuguese), and role-based workflows.

---

## Upgrade Guide

### From 0.1.1 to 0.1.2

#### Database Migration (Required)

Version 0.1.2 adds new tables for metrics tracking:

```bash
# Docker Compose
docker-compose exec backend alembic upgrade head

# Podman
podman exec gym_backend alembic upgrade head
```

#### For Docker Compose Users

```bash
# Stop containers
docker-compose down

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

#### For Podman Users

```bash
# Stop existing containers
podman stop gym_nginx gym_backend gym_postgres
podman rm gym_nginx gym_backend gym_postgres

# Rebuild backend
podman build -t localhost/gym_backend:latest backend/

# Start with script
bash start-containers.sh
```

**Important Notes:**
- Existing users will have metrics automatically initialized
- Weight history will begin tracking from first weight update after upgrade
- No data loss - all existing workouts and data are preserved

### From 0.1.0 to 0.1.1

```bash
# Standard upgrade, no database changes
docker-compose up -d --build
```

### From 0.0.1 to 0.1.0

```bash
# Database migration required for role-based system
docker-compose exec backend alembic upgrade head
docker-compose up -d --build
```

---

## Deprecation Notices

### Version 0.1.2
- None

---

## Known Issues

### Version 0.1.2
- Docker Compose on WSL2 may encounter nftables errors
  - **Workaround**: Use Podman with `start-containers.sh`
  - **Workaround**: Disable BuildKit: `export DOCKER_BUILDKIT=0`
- Hot reload in development may not detect some file changes
  - **Workaround**: Manually restart container
- Large image uploads (>5MB) may timeout
  - **Workaround**: Adjust `client_max_body_size` in nginx.conf

### Version 0.1.1
- None (bug fix release)

### Version 0.1.0
- Enum type mismatches in database
  - **Status**: Fixed in 0.1.1

---

## Contributors

- Alexandre - Initial development and maintenance
- Claude AI - Documentation assistance and code review

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

For issues and questions:
- Check the [Troubleshooting](README.md#troubleshooting) section
- Review the [Documentation](docs/INDEX.md)
- Check [Known Issues](#known-issues) above
- Report bugs via GitHub Issues

---

## Acknowledgments

- FastAPI team for the excellent web framework
- PostgreSQL community for the robust database
- Docker and Podman projects for containerization
- All open-source contributors whose libraries made this possible
