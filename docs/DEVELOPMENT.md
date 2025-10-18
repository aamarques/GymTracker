# Gym Workout Tracker - Development Guide

This guide covers setting up a local development environment, coding standards, testing, and contributing to the project.

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Database Management](#database-management)
6. [Testing](#testing)
7. [Coding Standards](#coding-standards)
8. [Git Workflow](#git-workflow)
9. [Common Development Tasks](#common-development-tasks)

---

## Development Environment Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (optional, for frontend tooling)
- **Docker/Podman**
- **PostgreSQL 15** (or use Docker)
- **Git**
- **Code Editor** (VS Code recommended)

### Option 1: Local Python Development

#### 1. Clone Repository

```bash
git clone <repository-url>
cd Gym
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

#### 3. Database Setup

```bash
# Start PostgreSQL with Docker
docker run -d \
  --name gym_postgres_dev \
  -e POSTGRES_USER=gymuser \
  -e POSTGRES_PASSWORD=gympass123 \
  -e POSTGRES_DB=gymtracker \
  -p 5432:5432 \
  postgres:15-alpine

# OR use local PostgreSQL
createdb gymtracker
```

#### 4. Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Update .env for development
nano .env
```

```bash
DATABASE_URL=postgresql://gymuser:gympass123@localhost:5432/gymtracker
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
```

#### 5. Database Migration

```bash
cd backend

# Run migrations
alembic upgrade head

# Create initial migration (if needed)
alembic revision --autogenerate -m "Initial migration"
```

#### 6. Start Development Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- http://localhost:8000
- http://localhost:8000/docs (API documentation)

#### 7. Frontend Development

```bash
# Serve frontend with Python
cd frontend
python3 -m http.server 8080

# OR use a simple Node.js server
npx http-server -p 8080
```

Frontend will be available at http://localhost:8080

### Option 2: Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access backend container
docker-compose exec backend bash

# Access database
docker-compose exec db psql -U gymuser -d gymtracker
```

### Option 3: VSCode Dev Containers

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "Gym Tracker Dev",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "backend",
  "workspaceFolder": "/app",
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ],
  "settings": {
    "python.pythonPath": "/usr/local/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
  }
}
```

---

## Project Structure

```
Gym/
├── backend/
│   ├── app/
│   │   ├── api/                    # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── users.py           # User management
│   │   │   ├── exercises.py       # Exercise CRUD
│   │   │   ├── workout_plans.py   # Workout plan management
│   │   │   ├── workout_sessions.py # Active workout sessions
│   │   │   └── cardio.py          # Cardio tracking
│   │   ├── core/                   # Core application config
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Settings and configuration
│   │   │   └── security.py        # Authentication & security
│   │   ├── db/                     # Database configuration
│   │   │   ├── __init__.py
│   │   │   └── database.py        # SQLAlchemy setup
│   │   ├── models/                 # Database models
│   │   │   ├── __init__.py
│   │   │   └── models.py          # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   └── schemas.py         # Request/response models
│   │   ├── services/               # Business logic layer
│   │   │   ├── __init__.py
│   │   │   └── file_service.py    # File upload handling
│   │   └── main.py                 # FastAPI application entry
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/                      # Test suite
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_exercises.py
│   │   └── test_workouts.py
│   ├── uploads/                    # Uploaded files (gitignored)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── alembic.ini
├── frontend/
│   ├── css/
│   │   └── style.css              # Application styles
│   ├── js/
│   │   └── app.js                 # Application logic
│   ├── assets/                     # Images, fonts, etc.
│   └── index.html                  # Main HTML file
├── nginx/
│   └── nginx.conf                  # Nginx configuration
├── docs/                           # Documentation
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
├── .github/                        # GitHub Actions CI/CD
│   └── workflows/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Backend Development

### FastAPI Application Structure

**main.py** - Application entry point:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, exercises, workout_plans, workout_sessions, cardio
from app.core.config import settings

app = FastAPI(
    title="Gym Workout Tracker API",
    description="API for tracking gym workouts and exercises",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(exercises.router, prefix="/api", tags=["Exercises"])
app.include_router(workout_plans.router, prefix="/api", tags=["Workout Plans"])
app.include_router(workout_sessions.router, prefix="/api", tags=["Workout Sessions"])
app.include_router(cardio.router, prefix="/api", tags=["Cardio"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Adding New Endpoints

#### 1. Create Schema (schemas.py)

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    muscle_group: str
    equipment: Optional[str] = None

class ExerciseResponse(ExerciseCreate):
    id: str
    user_id: str
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

#### 2. Create Model (models.py)

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    muscle_group = Column(String(50))
    equipment = Column(String(100))
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="exercises")
```

#### 3. Create API Route (exercises.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Exercise
from app.schemas.schemas import ExerciseCreate, ExerciseResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/exercises")

@router.post("/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise: ExerciseCreate,
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new exercise"""
    new_exercise = Exercise(
        user_id=current_user.id,
        **exercise.dict()
    )

    # Handle image upload
    if image:
        image_url = await save_exercise_image(image)
        new_exercise.image_url = image_url

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return new_exercise

@router.get("/", response_model=list[ExerciseResponse])
async def list_exercises(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    muscle_group: Optional[str] = None
):
    """List all exercises"""
    query = db.query(Exercise)

    if muscle_group:
        query = query.filter(Exercise.muscle_group == muscle_group)

    return query.all()
```

### Database Migrations

#### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add exercise table"

# Create empty migration
alembic revision -m "Custom migration"
```

#### Edit Migration File

```python
# alembic/versions/xxx_add_exercise_table.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'exercises',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('muscle_group', sa.String(50)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

def downgrade():
    op.drop_table('exercises')
```

#### Apply Migration

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

---

## Frontend Development

### JavaScript Architecture

**app.js** structure:

```javascript
// Global state
const state = {
    token: localStorage.getItem('token'),
    user: null,
    currentView: 'dashboard'
};

// API client
const api = {
    baseURL: 'http://localhost:8000/api',

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (state.token) {
            headers['Authorization'] = `Bearer ${state.token}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        return response.json();
    },

    auth: {
        login: (credentials) => api.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        }),
        register: (userData) => api.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        })
    },

    exercises: {
        list: () => api.request('/exercises'),
        create: (data) => api.request('/exercises', {
            method: 'POST',
            body: JSON.stringify(data)
        })
    }
};

// UI controllers
const ui = {
    showView(viewName) {
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.style.display = 'none';
        });

        // Show requested view
        document.getElementById(`${viewName}-view`).style.display = 'block';
        state.currentView = viewName;
    },

    showError(message) {
        const alert = document.getElementById('alert-container');
        alert.innerHTML = `<div class="alert error">${message}</div>`;
        setTimeout(() => alert.innerHTML = '', 5000);
    },

    showSuccess(message) {
        const alert = document.getElementById('alert-container');
        alert.innerHTML = `<div class="alert success">${message}</div>`;
        setTimeout(() => alert.innerHTML = '', 3000);
    }
};

// Event handlers
async function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        const response = await api.auth.login({
            email: formData.get('email'),
            password: formData.get('password')
        });

        state.token = response.access_token;
        localStorage.setItem('token', response.access_token);

        ui.showView('dashboard');
        loadDashboard();
    } catch (error) {
        ui.showError('Login failed: ' + error.message);
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (state.token) {
        loadDashboard();
    } else {
        ui.showView('login');
    }
});
```

### Adding New Features

#### 1. Create HTML View

```html
<div id="feature-view" class="view" style="display: none;">
    <h2>New Feature</h2>
    <form id="feature-form">
        <input type="text" name="name" required>
        <button type="submit">Submit</button>
    </form>
    <div id="feature-list"></div>
</div>
```

#### 2. Add API Methods

```javascript
api.features = {
    list: () => api.request('/features'),
    create: (data) => api.request('/features', {
        method: 'POST',
        body: JSON.stringify(data)
    })
};
```

#### 3. Create Event Handlers

```javascript
async function handleFeatureSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        await api.features.create({
            name: formData.get('name')
        });
        ui.showSuccess('Feature created!');
        loadFeatures();
    } catch (error) {
        ui.showError(error.message);
    }
}

document.getElementById('feature-form')
    .addEventListener('submit', handleFeatureSubmit);
```

---

## Database Management

### Common SQL Queries

```sql
-- View all users
SELECT * FROM users;

-- View user's exercises
SELECT e.* FROM exercises e
JOIN users u ON e.user_id = u.id
WHERE u.email = 'user@example.com';

-- View workout statistics
SELECT
    u.name,
    COUNT(DISTINCT ws.id) as total_workouts,
    COUNT(DISTINCT e.id) as total_exercises
FROM users u
LEFT JOIN workout_sessions ws ON u.id = ws.user_id
LEFT JOIN exercises e ON u.id = e.user_id
GROUP BY u.id, u.name;

-- Delete user and all related data (cascade should handle this)
DELETE FROM users WHERE email = 'user@example.com';
```

### Database Console Access

```bash
# Docker Compose
docker-compose exec db psql -U gymuser -d gymtracker

# Podman
podman exec -it gym_postgres psql -U gymuser -d gymtracker

# Common psql commands
\dt              # List tables
\d table_name    # Describe table
\q               # Quit
```

### Seed Data for Development

Create `backend/seed.py`:

```python
from app.db.database import engine, SessionLocal
from app.models.models import User, Exercise
from app.core.security import get_password_hash
import uuid

def seed_database():
    db = SessionLocal()

    # Create test user
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        name="Test User",
        weight=75.0,
        height=180.0,
        date_of_birth=datetime(1990, 1, 1)
    )
    db.add(user)

    # Create exercises
    exercises = [
        Exercise(
            id=uuid.uuid4(),
            user_id=user.id,
            name="Bench Press",
            description="Compound chest exercise",
            muscle_group="chest",
            equipment="barbell"
        ),
        # Add more exercises...
    ]
    db.add_all(exercises)

    db.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
```

Run: `python backend/seed.py`

---

## Testing

### Backend Testing with Pytest

**Install test dependencies:**

```bash
pip install pytest pytest-asyncio httpx pytest-cov
```

**Create `backend/tests/conftest.py`:**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "postgresql://gymuser:gympass123@localhost:5432/gymtracker_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

**Create test file `backend/tests/test_auth.py`:**

```python
def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
        "name": "New User",
        "date_of_birth": "1990-01-01T00:00:00",
        "weight": 75.0,
        "height": 180.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_login_user(client, db):
    # First register
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test",
        "date_of_birth": "1990-01-01T00:00:00",
        "weight": 75.0,
        "height": 180.0
    })

    # Then login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
```

**Run tests:**

```bash
# Run all tests
pytest backend/tests/

# Run with coverage
pytest --cov=app backend/tests/

# Run specific test file
pytest backend/tests/test_auth.py

# Run with verbose output
pytest -v backend/tests/
```

---

## Coding Standards

### Python Style Guide

Follow PEP 8 with these tools:

```bash
# Install linting tools
pip install black isort flake8 mypy

# Format code
black backend/app/
isort backend/app/

# Check style
flake8 backend/app/

# Type checking
mypy backend/app/
```

**Pre-commit hooks** (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### JavaScript Style Guide

Use ESLint and Prettier:

```bash
# Install
npm install --save-dev eslint prettier

# Create .eslintrc.json
{
  "extends": "eslint:recommended",
  "env": {
    "browser": true,
    "es2021": true
  },
  "rules": {
    "indent": ["error", 2],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
```

---

## Git Workflow

### Branch Strategy

```
main (production)
  ├── develop (staging)
  │   ├── feature/user-authentication
  │   ├── feature/workout-tracking
  │   └── bugfix/login-issue
```

### Commit Messages

Follow Conventional Commits:

```
feat: add workout timer feature
fix: resolve authentication token expiry
docs: update API documentation
test: add unit tests for exercises
refactor: simplify database queries
chore: update dependencies
```

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes and commit
3. Push branch and create PR
4. Request review
5. Address feedback
6. Merge to `develop`

---

## Common Development Tasks

### Reset Database

```bash
# Drop and recreate
alembic downgrade base
alembic upgrade head
python seed.py
```

### Clear Uploaded Files

```bash
rm -rf backend/uploads/*
mkdir -p backend/uploads/exercises
```

### Update Dependencies

```bash
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

### Debug API Issues

```bash
# Enable debug logging
DEBUG=True uvicorn app.main:app --reload --log-level debug

# Use pdb for debugging
import pdb; pdb.set_trace()
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
