# Testing Guide

## Running Tests

### Quick Start

```bash
# Install test dependencies
cd backend
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestLogin

# Run specific test
pytest tests/test_auth.py::TestLogin::test_login_with_email_success
```

### Inside Docker Container

```bash
# Using Podman
podman exec -it gym_backend pytest

# Using Docker Compose
docker-compose exec backend pytest
```

## Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── test_auth.py             # Authentication tests
├── test_exercises.py        # Exercise CRUD tests (to be added)
├── test_workout_sessions.py # Workout session tests (to be added)
└── test_metrics.py          # Metrics calculation tests (to be added)
```

## Test Coverage

### Current Coverage

**Authentication (test_auth.py):**
- ✅ User registration (client and PT)
- ✅ Duplicate email/username validation
- ✅ Password strength validation
- ✅ Login with email
- ✅ Login with username
- ✅ Invalid credentials
- ✅ Login attempt lockout (5 attempts)
- ✅ Authenticated endpoint access
- ✅ Password change
- ✅ Password reset request

### Planned Coverage

**Exercises:**
- Exercise creation with image upload
- Exercise CRUD operations
- Role-based access (PT vs Client)
- Bulk import from CSV

**Workout Sessions:**
- Start/stop workout
- Exercise logging
- Duration calculation
- History retrieval

**Metrics:**
- Client metrics calculation
- Weight history tracking
- Progress analysis
- PT dashboard aggregation

## Test Database

Tests use an in-memory SQLite database that is created fresh for each test. This ensures:
- Fast test execution
- No contamination between tests
- No need to clean up test data

## Writing New Tests

### Example Test

```python
def test_my_feature(client, test_user_data):
    """Test description"""
    # Arrange: Set up test data
    response = client.post("/api/auth/register", json=test_user_data)
    token = response.json()["access_token"]

    # Act: Perform the action
    response = client.get(
        "/api/my-endpoint",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Assert: Verify the result
    assert response.status_code == 200
    assert response.json()["expected_field"] == "expected_value"
```

### Available Fixtures

- `client`: FastAPI TestClient instance
- `db_session`: Database session for direct queries
- `test_user_data`: Sample client user data
- `test_pt_data`: Sample Personal Trainer data

### Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

1. **Test Independence:** Each test should be independent and not rely on other tests
2. **Clear Naming:** Test names should describe what they test
3. **Arrange-Act-Assert:** Follow the AAA pattern
4. **One Assertion Per Test:** Ideally, test one thing at a time
5. **Use Fixtures:** Reuse common setup code with fixtures
6. **Mock External Services:** Don't make real API calls or send real emails

## Troubleshooting

### Import Errors

If you get import errors, make sure you're in the backend directory:
```bash
cd backend
pytest
```

### Database Errors

If tests fail with database errors, check that SQLAlchemy models are properly defined and migrations are up to date.

### Fixture Not Found

Make sure `conftest.py` is in the `tests/` directory and pytest can find it.

## Next Steps

1. Add more test files for other endpoints
2. Increase test coverage to 80%+
3. Add integration tests
4. Set up CI/CD pipeline
5. Add performance tests
