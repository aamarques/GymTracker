"""
Pytest configuration and fixtures for testing
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
        "role": "client",
        "language": "en",
        "date_of_birth": "1990-01-01T00:00:00",
        "weight": 75.0,
        "height": 180.0,
        "phone": "+1234567890"
    }


@pytest.fixture
def test_pt_data():
    """Sample Personal Trainer data for testing"""
    return {
        "username": "testpt",
        "email": "pt@example.com",
        "password": "ptpassword123",
        "name": "Test PT",
        "role": "personal_trainer",
        "language": "en",
        "date_of_birth": "1985-01-01T00:00:00",
        "weight": 80.0,
        "height": 185.0,
        "phone": "+1234567891"
    }
