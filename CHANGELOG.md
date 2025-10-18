# Changelog

All notable changes to the Gym Workout Tracker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-12

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

## [1.0.0] - 2025-10-10

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

### Version 1.1.0 Notes

This release focuses on improving developer experience and deployment flexibility, particularly for WSL2 users. The major change is the switch from passlib to direct bcrypt implementation, which resolves compatibility issues across different environments.

**Important for Existing Deployments:**
- If upgrading from 1.0.0, rebuild your backend container to get the new bcrypt dependency
- Existing password hashes remain compatible with the new implementation
- WSL2 users should switch to the Podman deployment script for better reliability

**Migration Steps:**
1. Stop existing containers
2. Rebuild backend: `podman build -t localhost/gym_backend:latest backend/`
3. Start with new script: `bash start-containers.sh`

### Version 1.0.0 Notes

Initial stable release with full feature set for personal gym workout tracking. Includes complete authentication system, exercise management, workout planning, and activity tracking.

---

## Upgrade Guide

### From 1.0.0 to 1.1.0

#### For Docker Compose Users

```bash
# Stop containers
docker-compose down

# Pull latest changes
git pull origin main

# Rebuild with new dependencies
docker-compose up -d --build
```

#### For Podman Users (New in 1.1.0)

```bash
# Stop existing containers
podman stop gym_nginx gym_backend gym_postgres
podman rm gym_nginx gym_backend gym_postgres

# Rebuild backend
podman build -t localhost/gym_backend:latest backend/

# Start with new script
bash start-containers.sh
```

#### Database Migration

No database schema changes in 1.1.0, but run migrations to be safe:

```bash
# Docker Compose
docker-compose exec backend alembic upgrade head

# Podman
podman exec gym_backend alembic upgrade head
```

---

## Deprecation Notices

### Version 1.1.0
- **Deprecated**: Using `passlib[bcrypt]` - Will be removed in 2.0.0
  - **Replacement**: Direct `bcrypt` library (already implemented)
  - **Action Required**: Update requirements.txt if maintaining custom fork

---

## Known Issues

### Version 1.1.0
- Docker Compose on WSL2 may encounter nftables errors
  - **Workaround**: Use Podman with `start-containers.sh`
  - **Workaround**: Disable BuildKit: `export DOCKER_BUILDKIT=0`
- Hot reload in development may not detect some file changes
  - **Workaround**: Manually restart container
- Large image uploads (>5MB) may timeout
  - **Workaround**: Adjust `client_max_body_size` in nginx.conf

### Version 1.0.0
- Bcrypt password hashing errors in some environments
  - **Status**: Fixed in 1.1.0

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
