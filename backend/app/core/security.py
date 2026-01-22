from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Bcrypt has a maximum password length of 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """Decode JWT token and return user_id"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def validate_password_strength(password: str) -> bool:
    """Validate password meets minimum requirements"""
    if len(password) < 8:
        return False
    return True


def check_login_attempts(db, identifier: str) -> tuple[bool, int]:
    """
    Check if user has exceeded maximum login attempts
    Returns: (is_locked, attempts_remaining)
    """
    from app.models.models import LoginAttempt
    from datetime import datetime, timedelta, timezone

    lockout_window = datetime.now(timezone.utc) - timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)

    # Count failed attempts within lockout window
    failed_attempts = db.query(LoginAttempt).filter(
        LoginAttempt.identifier == identifier,
        LoginAttempt.success == False,
        LoginAttempt.attempted_at >= lockout_window
    ).count()

    is_locked = failed_attempts >= settings.MAX_LOGIN_ATTEMPTS
    attempts_remaining = max(0, settings.MAX_LOGIN_ATTEMPTS - failed_attempts)

    return is_locked, attempts_remaining


def record_login_attempt(db, identifier: str, success: bool, user_id: str = None, ip_address: str = None) -> None:
    """Record a login attempt for security tracking"""
    from app.models.models import LoginAttempt

    attempt = LoginAttempt(
        identifier=identifier,
        success=success,
        user_id=user_id,
        ip_address=ip_address
    )

    db.add(attempt)
    db.commit()
