from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.models import User, WorkoutSession, ExerciseLog, Exercise, WorkoutPlan
from app.schemas.schemas import (
    WorkoutSessionCreate,
    WorkoutSessionResponse,
    WorkoutSessionUpdate,
    ExerciseLogCreate,
    ExerciseLogResponse
)
from app.core.security import get_current_user

router = APIRouter(prefix="/workout-sessions", tags=["Workout Sessions"])


@router.post("", response_model=WorkoutSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_workout_session(
    session_data: WorkoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new workout session"""
    # Verify workout plan exists if provided
    if session_data.workout_plan_id:
        plan = db.query(WorkoutPlan).filter(
            WorkoutPlan.id == session_data.workout_plan_id,
            WorkoutPlan.user_id == current_user.id
        ).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout plan not found"
            )

    new_session = WorkoutSession(
        user_id=current_user.id,
        workout_plan_id=session_data.workout_plan_id,
        notes=session_data.notes
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.get("", response_model=List[WorkoutSessionResponse])
async def get_workout_sessions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workout sessions for current user"""
    query = db.query(WorkoutSession).filter(WorkoutSession.user_id == current_user.id)

    if active_only:
        query = query.filter(WorkoutSession.end_time.is_(None))

    sessions = query.order_by(WorkoutSession.start_time.desc()).offset(skip).limit(limit).all()

    return sessions


@router.get("/active", response_model=Optional[WorkoutSessionResponse])
async def get_active_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current active workout session"""
    session = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == current_user.id,
        WorkoutSession.end_time.is_(None)
    ).order_by(WorkoutSession.start_time.desc()).first()

    return session


@router.get("/{session_id}", response_model=WorkoutSessionResponse)
async def get_workout_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific workout session"""
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )

    return session


@router.put("/{session_id}", response_model=WorkoutSessionResponse)
async def update_workout_session(
    session_id: str,
    session_update: WorkoutSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update workout session (e.g., end session)"""
    from app.services.metrics_service import update_metrics_after_workout

    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )

    # Track if workout is being ended
    workout_ended = False
    if session_update.end_time is not None and session.end_time is None:
        workout_ended = True

    if session_update.notes is not None:
        session.notes = session_update.notes
    if session_update.end_time is not None:
        session.end_time = session_update.end_time

    db.commit()
    db.refresh(session)

    # Update metrics if workout was ended
    if workout_ended:
        update_metrics_after_workout(db, session_id)

    return session


@router.post("/{session_id}/end", response_model=WorkoutSessionResponse)
async def end_workout_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End workout session"""
    from app.services.metrics_service import update_metrics_after_workout

    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )

    if session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already ended"
        )

    session.end_time = datetime.now()
    db.commit()
    db.refresh(session)

    # Update metrics after workout completion
    update_metrics_after_workout(db, session_id)

    return session


@router.post("/{session_id}/exercises", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED)
async def log_exercise(
    session_id: str,
    exercise_log: ExerciseLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log an exercise during workout session"""
    # Verify session exists and belongs to user
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )

    # Verify exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == exercise_log.exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    new_log = ExerciseLog(
        session_id=session_id,
        exercise_id=exercise_log.exercise_id,
        sets_completed=exercise_log.sets_completed,
        reps_completed=exercise_log.reps_completed,
        weight_used=exercise_log.weight_used,
        rest_time_actual=exercise_log.rest_time_actual,
        notes=exercise_log.notes
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete workout session"""
    session = db.query(WorkoutSession).filter(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )

    db.delete(session)
    db.commit()

    return None
