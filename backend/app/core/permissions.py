"""
Role-based access control utilities
"""
from fastapi import HTTPException, status, Depends
from app.models.models import User, UserRole
from app.core.security import get_current_user


async def require_personal_trainer(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is a personal trainer"""
    if current_user.role != UserRole.PERSONAL_TRAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires a Personal Trainer account"
        )
    return current_user


async def require_client(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is a client"""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires a Client account"
        )
    return current_user


def check_client_belongs_to_trainer(client: User, trainer: User):
    """Verify that a client belongs to the specified trainer"""
    if client.personal_trainer_id != trainer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This client is not assigned to you"
        )
    return True
