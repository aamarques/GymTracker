from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.models.models import User, CardioSession
from app.schemas.schemas import (
    CardioSessionCreate,
    CardioSessionResponse,
    CardioSessionUpdate
)
from app.core.security import get_current_user

router = APIRouter(prefix="/cardio", tags=["Cardio"])


@router.post("", response_model=CardioSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_cardio_session(
    cardio_data: CardioSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a new cardio session"""
    new_cardio = CardioSession(
        user_id=current_user.id,
        activity_type=cardio_data.activity_type,
        location=cardio_data.location,
        duration=cardio_data.duration,
        distance=cardio_data.distance,
        calories_burned=cardio_data.calories_burned,
        start_time=cardio_data.start_time or datetime.now(),
        notes=cardio_data.notes
    )

    db.add(new_cardio)
    db.commit()
    db.refresh(new_cardio)

    return new_cardio


@router.get("", response_model=List[CardioSessionResponse])
async def get_cardio_sessions(
    skip: int = 0,
    limit: int = 100,
    activity_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all cardio sessions for current user"""
    query = db.query(CardioSession).filter(CardioSession.user_id == current_user.id)

    if activity_type:
        query = query.filter(CardioSession.activity_type.ilike(f"%{activity_type}%"))

    sessions = query.order_by(CardioSession.start_time.desc()).offset(skip).limit(limit).all()

    return sessions


@router.get("/{session_id}", response_model=CardioSessionResponse)
async def get_cardio_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific cardio session"""
    session = db.query(CardioSession).filter(
        CardioSession.id == session_id,
        CardioSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio session not found"
        )

    return session


@router.put("/{session_id}", response_model=CardioSessionResponse)
async def update_cardio_session(
    session_id: str,
    cardio_update: CardioSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cardio session"""
    session = db.query(CardioSession).filter(
        CardioSession.id == session_id,
        CardioSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio session not found"
        )

    if cardio_update.activity_type is not None:
        session.activity_type = cardio_update.activity_type
    if cardio_update.location is not None:
        session.location = cardio_update.location
    if cardio_update.duration is not None:
        session.duration = cardio_update.duration
    if cardio_update.distance is not None:
        session.distance = cardio_update.distance
    if cardio_update.calories_burned is not None:
        session.calories_burned = cardio_update.calories_burned
    if cardio_update.notes is not None:
        session.notes = cardio_update.notes

    db.commit()
    db.refresh(session)

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cardio_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete cardio session"""
    session = db.query(CardioSession).filter(
        CardioSession.id == session_id,
        CardioSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio session not found"
        )

    db.delete(session)
    db.commit()

    return None
