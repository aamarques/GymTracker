"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status


class TestRegistration:
    """Test user registration"""

    def test_register_client_success(self, client, test_user_data):
        """Test successful client registration"""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["role"] == "client"
        assert "hashed_password" not in data

    def test_register_pt_success(self, client, test_pt_data):
        """Test successful Personal Trainer registration"""
        response = client.post("/api/auth/register", json=test_pt_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["role"] == "personal_trainer"

    def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email fails"""
        # Register first user
        client.post("/api/auth/register", json=test_user_data)

        # Try to register with same email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "differentuser"
        response = client.post("/api/auth/register", json=duplicate_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email already registered" in response.json()["detail"].lower()

    def test_register_duplicate_username(self, client, test_user_data):
        """Test registration with duplicate username fails"""
        # Register first user
        client.post("/api/auth/register", json=test_user_data)

        # Try to register with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/api/auth/register", json=duplicate_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username already taken" in response.json()["detail"].lower()

    def test_register_weak_password(self, client, test_user_data):
        """Test registration with weak password fails"""
        weak_password_data = test_user_data.copy()
        weak_password_data["password"] = "short"

        response = client.post("/api/auth/register", json=weak_password_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "at least 8 characters" in response.json()["detail"].lower()


class TestLogin:
    """Test user login"""

    def test_login_with_email_success(self, client, test_user_data):
        """Test successful login with email"""
        # Register user
        client.post("/api/auth/register", json=test_user_data)

        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_username_success(self, client, test_user_data):
        """Test successful login with username"""
        # Register user
        client.post("/api/auth/register", json=test_user_data)

        # Login with username
        login_data = {
            "email": test_user_data["username"],  # API accepts username in email field
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client, test_user_data):
        """Test login with wrong password fails"""
        # Register user
        client.post("/api/auth/register", json=test_user_data)

        # Login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLoginAttemptLockout:
    """Test login attempt tracking and lockout"""

    def test_login_lockout_after_max_attempts(self, client, test_user_data):
        """Test account locks after maximum failed attempts"""
        # Register user
        client.post("/api/auth/register", json=test_user_data)

        # Make 5 failed login attempts
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }

        for i in range(5):
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # 6th attempt should be locked
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "locked" in response.json()["detail"].lower()

    def test_successful_login_after_failed_attempts(self, client, test_user_data):
        """Test successful login works even after some failed attempts"""
        # Register user
        client.post("/api/auth/register", json=test_user_data)

        # Make 3 failed login attempts
        wrong_login = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        for _ in range(3):
            client.post("/api/auth/login", json=wrong_login)

        # Correct login should still work
        correct_login = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=correct_login)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()


class TestAuthenticatedEndpoints:
    """Test endpoints requiring authentication"""

    def test_get_current_user_success(self, client, test_user_data):
        """Test getting current user info with valid token"""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]

    def test_get_current_user_without_token(self, client):
        """Test getting current user without token fails"""
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token fails"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPasswordChange:
    """Test password change functionality"""

    def test_change_password_success(self, client, test_user_data):
        """Test successful password change"""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]

        # Change password
        new_password = "newpassword123"
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": new_password,
            "confirm_new_password": new_password
        }
        response = client.post(
            "/api/auth/change-password",
            json=change_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify can login with new password
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": new_password
        })
        assert login_response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_current(self, client, test_user_data):
        """Test password change with wrong current password fails"""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]

        # Try to change with wrong current password
        change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123"
        }
        response = client.post(
            "/api/auth/change-password",
            json=change_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorrect" in response.json()["detail"].lower()


class TestPasswordReset:
    """Test password reset functionality"""

    def test_forgot_password_existing_user(self, client, test_user_data):
        """Test password reset request for existing user"""
        # Register user
        client.post("/api/auth/register", json=test_user_data)

        # Request password reset
        response = client.post("/api/auth/forgot-password", json={
            "email": test_user_data["email"]
        })

        assert response.status_code == status.HTTP_200_OK
        # Should always return success message (security)
        assert "reset" in response.json()["message"].lower()

    def test_forgot_password_nonexistent_user(self, client):
        """Test password reset for nonexistent user returns same message"""
        response = client.post("/api/auth/forgot-password", json={
            "email": "nonexistent@example.com"
        })

        assert response.status_code == status.HTTP_200_OK
        # Should return same message to prevent user enumeration
        assert "reset" in response.json()["message"].lower()
