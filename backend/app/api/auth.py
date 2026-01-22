from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import (
    UserCreate,
    UserResponse,
    Token,
    LoginRequest,
    ChangePasswordRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    validate_password_strength,
    get_current_user,
    check_login_attempts,
    record_login_attempt
)
from app.core.config import settings
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)"""
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)


def calculate_age(date_of_birth: datetime) -> int:
    """Calculate age from date of birth"""
    today = datetime.now()
    age = today.year - date_of_birth.year
    if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
        age -= 1
    return age


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        role=user_data.role,  # Allow user to choose role
        language=user_data.language,
        date_of_birth=user_data.date_of_birth,
        weight=user_data.weight,
        height=user_data.height,
        phone=user_data.phone,
        personal_trainer_id=user_data.personal_trainer_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Add calculated fields
    response = UserResponse.from_orm(new_user)
    response.bmi = calculate_bmi(new_user.weight, new_user.height)
    response.age = calculate_age(new_user.date_of_birth)

    return response


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    # Check if account is locked due to failed attempts
    is_locked, attempts_remaining = check_login_attempts(db, login_data.email)

    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked due to too many failed login attempts. Please try again in {settings.LOGIN_LOCKOUT_MINUTES} minutes."
        )

    # Check if login identifier is email or username
    user = db.query(User).filter(
        (User.email == login_data.email) | (User.username == login_data.email)
    ).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        # Record failed attempt
        record_login_attempt(db, login_data.email, success=False, user_id=user.id if user else None)

        # Calculate remaining attempts for better UX
        new_attempts_remaining = attempts_remaining - 1
        detail_msg = "Incorrect username/email or password"
        if new_attempts_remaining > 0:
            detail_msg += f". {new_attempts_remaining} attempts remaining."
        else:
            detail_msg += f". Account locked for {settings.LOGIN_LOCKOUT_MINUTES} minutes."

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Record successful login
    record_login_attempt(db, login_data.email, success=True, user_id=user.id)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token endpoint"""
    # Check if account is locked due to failed attempts
    is_locked, attempts_remaining = check_login_attempts(db, form_data.username)

    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked due to too many failed login attempts. Please try again in {settings.LOGIN_LOCKOUT_MINUTES} minutes."
        )

    # Check if login identifier is email or username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        # Record failed attempt
        record_login_attempt(db, form_data.username, success=False, user_id=user.id if user else None)

        # Calculate remaining attempts for better UX
        new_attempts_remaining = attempts_remaining - 1
        detail_msg = "Incorrect username/email or password"
        if new_attempts_remaining > 0:
            detail_msg += f". {new_attempts_remaining} attempts remaining."
        else:
            detail_msg += f". Account locked for {settings.LOGIN_LOCKOUT_MINUTES} minutes."

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Record successful login
    record_login_attempt(db, form_data.username, success=True, user_id=user.id)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    response = UserResponse.from_orm(current_user)
    response.bmi = calculate_bmi(current_user.weight, current_user.height)
    response.age = calculate_age(current_user.date_of_birth)
    return response


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    if not validate_password_strength(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )

    # Check if new password is different from current
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset (generates token and sends email)"""
    from app.models.models import PasswordResetToken
    from app.services.email_service import send_password_reset_email
    import secrets

    # Find user by email or username
    user = db.query(User).filter(
        (User.email == request_data.email) | (User.username == request_data.email)
    ).first()

    # Always return success message to prevent user enumeration
    success_message = "If an account with that email/username exists, a password reset link has been sent."

    if not user:
        return {
            "message": success_message,
            "reset_token": None
        }

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)

    # Expire old tokens for this user
    old_tokens = db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).all()
    for token in old_tokens:
        token.used = True

    # Create new reset token (expires in 1 hour)
    from datetime import datetime, timedelta, timezone
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    new_token = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at
    )

    db.add(new_token)
    db.commit()

    # Send password reset email
    try:
        send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            user_name=user.name
        )
    except Exception as e:
        # Log error but don't reveal it to user (security)
        print(f"Error sending password reset email: {str(e)}")
        # Still return success to prevent user enumeration

    # Return success (email sent or not, don't reveal)
    return {
        "message": success_message,
        "reset_token": reset_token if settings.DEBUG else None  # Only in DEBUG mode
    }


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password using token"""
    from app.models.models import PasswordResetToken
    from datetime import datetime, timezone

    # Find token
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token,
        PasswordResetToken.used == False
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check if token is expired
    if token_record.expires_at < datetime.now(timezone.utc):
        token_record.used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )

    # Get user
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Validate new password strength
    if not validate_password_strength(reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)

    # Mark token as used
    token_record.used = True

    db.commit()

    return {"message": "Password has been reset successfully"}
