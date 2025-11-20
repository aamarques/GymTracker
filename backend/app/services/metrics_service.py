"""
Service for managing client metrics and tracking progress
This service automatically updates metrics when workouts are completed or weight is changed
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.models import (
    ClientMetrics, WeightHistory, User, WorkoutSession,
    CardioSession, ExerciseLog
)
from typing import Optional


def get_or_create_client_metrics(db: Session, client_id: str, personal_trainer_id: Optional[str] = None) -> ClientMetrics:
    """
    Get existing metrics or create new ones for a client
    """
    metrics = db.query(ClientMetrics).filter(ClientMetrics.client_id == client_id).first()

    if not metrics:
        # Get client to get initial weight
        client = db.query(User).filter(User.id == client_id).first()

        metrics = ClientMetrics(
            client_id=client_id,
            personal_trainer_id=personal_trainer_id or client.personal_trainer_id,
            initial_weight=client.weight if client else None,
            current_weight=client.weight if client else None,
            lowest_weight=client.weight if client else None,
            highest_weight=client.weight if client else None
        )
        db.add(metrics)
        db.commit()
        db.refresh(metrics)

    return metrics


def update_metrics_after_workout(db: Session, workout_session_id: str) -> None:
    """
    Update client metrics after a workout session is completed
    Called when a workout session is marked as complete (end_time is set)
    """
    session = db.query(WorkoutSession).filter(WorkoutSession.id == workout_session_id).first()

    if not session or not session.end_time:
        return

    # Get or create metrics
    metrics = get_or_create_client_metrics(db, session.user_id)

    # Calculate workout duration
    duration_seconds = (session.end_time - session.start_time).total_seconds()
    duration_hours = duration_seconds / 3600

    # Update workout counts
    metrics.total_workouts_completed += 1
    if metrics.total_training_hours is None:
        metrics.total_training_hours = 0.0
    metrics.total_training_hours += duration_hours
    metrics.last_activity_date = session.end_time

    # Calculate average workout duration
    metrics.average_workout_duration_minutes = (metrics.total_training_hours * 60) / metrics.total_workouts_completed

    # Count sets and reps from exercise logs
    exercise_logs = db.query(ExerciseLog).filter(ExerciseLog.session_id == workout_session_id).all()
    for log in exercise_logs:
        if metrics.total_sets_completed is None:
            metrics.total_sets_completed = 0
        if metrics.total_reps_completed is None:
            metrics.total_reps_completed = 0
        metrics.total_sets_completed += log.sets_completed
        metrics.total_reps_completed += log.reps_completed

    # Update unique training days
    update_training_days(db, metrics, session.user_id)

    # Update consistency percentage
    update_consistency_percentage(db, metrics)

    db.commit()


def update_metrics_after_cardio(db: Session, cardio_session_id: str) -> None:
    """
    Update client metrics after a cardio session is completed
    """
    from app.models.models import CardioSession

    cardio = db.query(CardioSession).filter(CardioSession.id == cardio_session_id).first()

    if not cardio:
        return

    # Get or create metrics
    metrics = get_or_create_client_metrics(db, cardio.user_id)

    # Update cardio counts
    metrics.total_cardio_sessions += 1
    metrics.last_activity_date = cardio.start_time

    # Add cardio duration to total training hours
    cardio_hours = cardio.duration / 60.0
    if metrics.total_training_hours is None:
        metrics.total_training_hours = 0.0
    metrics.total_training_hours += cardio_hours

    # Update unique training days
    update_training_days(db, metrics, cardio.user_id)

    # Update consistency percentage
    update_consistency_percentage(db, metrics)

    db.commit()


def update_training_days(db: Session, metrics: ClientMetrics, user_id: str) -> None:
    """
    Calculate total unique days with training activity
    """
    # Get all unique dates with workout sessions
    workout_dates = db.query(
        func.date(WorkoutSession.start_time).label('date')
    ).filter(
        WorkoutSession.user_id == user_id,
        WorkoutSession.end_time.isnot(None)
    ).distinct().all()

    # Get all unique dates with cardio sessions
    cardio_dates = db.query(
        func.date(CardioSession.start_time).label('date')
    ).filter(
        CardioSession.user_id == user_id
    ).distinct().all()

    # Combine and count unique dates
    all_dates = set([d.date for d in workout_dates] + [d.date for d in cardio_dates])
    metrics.total_training_days = len(all_dates)


def update_consistency_percentage(db: Session, metrics: ClientMetrics) -> None:
    """
    Calculate consistency as percentage of days with activity since client started
    """
    if not metrics.client_since:
        return

    days_since_start = (datetime.now() - metrics.client_since).days

    if days_since_start > 0:
        metrics.consistency_percentage = (metrics.total_training_days / days_since_start) * 100
    else:
        metrics.consistency_percentage = 0.0


def track_weight_change(db: Session, user_id: str, new_weight: float, notes: Optional[str] = None) -> WeightHistory:
    """
    Record a weight change in history and update client metrics
    Called when user updates their weight in profile
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    # Get last weight record
    last_record = db.query(WeightHistory).filter(
        WeightHistory.user_id == user_id
    ).order_by(WeightHistory.recorded_at.desc()).first()

    # Calculate days since last change
    days_since_last = None
    if last_record:
        days_since_last = (datetime.now() - last_record.recorded_at).days

    # Create new weight history record
    weight_history = WeightHistory(
        user_id=user_id,
        weight=new_weight,
        previous_weight=last_record.weight if last_record else None,
        days_since_last_change=days_since_last,
        notes=notes
    )
    db.add(weight_history)

    # Update client metrics
    metrics = get_or_create_client_metrics(db, user_id)
    metrics.current_weight = new_weight
    if metrics.total_weight_changes is None:
        metrics.total_weight_changes = 0
    metrics.total_weight_changes += 1

    # Update lowest/highest weight
    if metrics.lowest_weight is None or new_weight < metrics.lowest_weight:
        metrics.lowest_weight = new_weight
    if metrics.highest_weight is None or new_weight > metrics.highest_weight:
        metrics.highest_weight = new_weight

    # Calculate average days between weight changes
    all_records = db.query(WeightHistory).filter(
        WeightHistory.user_id == user_id,
        WeightHistory.days_since_last_change.isnot(None)
    ).all()

    if all_records:
        total_days = sum([r.days_since_last_change for r in all_records if r.days_since_last_change])
        metrics.average_days_between_weight_changes = total_days / len(all_records)

    db.commit()
    db.refresh(weight_history)

    return weight_history


def reset_client_workouts(db: Session, client_id: str) -> dict:
    """
    Reset client's workout count while preserving metrics for PT
    This allows clients to "start fresh" while PT can still see historical data
    """
    metrics = get_or_create_client_metrics(db, client_id)

    # Store current workout count before reset
    current_workouts = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == client_id,
        WorkoutSession.end_time.isnot(None)
    ).count()

    # Update reset tracking in metrics (PT can still see this)
    if metrics.times_workouts_reset is None:
        metrics.times_workouts_reset = 0
    metrics.times_workouts_reset += 1
    metrics.last_reset_date = datetime.now()
    metrics.workouts_before_last_reset = current_workouts

    db.commit()

    # Note: We don't actually delete workout sessions, just track that client "reset"
    # The dashboard can be modified to show workouts since last reset

    return {
        "message": "Workout count reset successfully",
        "workouts_archived": current_workouts,
        "reset_count": metrics.times_workouts_reset,
        "metrics_preserved": True
    }


def calculate_client_progress(db: Session, client_id: str) -> dict:
    """
    Calculate comprehensive progress metrics for a client
    """
    metrics = db.query(ClientMetrics).filter(ClientMetrics.client_id == client_id).first()

    if not metrics:
        return None

    # Calculate weight change since start
    weight_change = None
    weight_change_percentage = None
    if metrics.initial_weight and metrics.current_weight:
        weight_change = metrics.current_weight - metrics.initial_weight
        weight_change_percentage = (weight_change / metrics.initial_weight) * 100

    # Get recent workout trend (last 30 days vs previous 30 days)
    today = datetime.now()
    last_30_days = today - timedelta(days=30)
    previous_60_to_30_days = today - timedelta(days=60)

    recent_workouts = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == client_id,
        WorkoutSession.start_time >= last_30_days,
        WorkoutSession.end_time.isnot(None)
    ).count()

    previous_workouts = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == client_id,
        WorkoutSession.start_time >= previous_60_to_30_days,
        WorkoutSession.start_time < last_30_days,
        WorkoutSession.end_time.isnot(None)
    ).count()

    trend = "stable"
    if recent_workouts > previous_workouts:
        trend = "improving"
    elif recent_workouts < previous_workouts:
        trend = "declining"

    return {
        "total_workouts": metrics.total_workouts_completed,
        "total_training_hours": round(metrics.total_training_hours, 2),
        "total_training_days": metrics.total_training_days,
        "consistency_percentage": round(metrics.consistency_percentage, 1) if metrics.consistency_percentage else 0,
        "average_workout_duration": round(metrics.average_workout_duration_minutes, 1) if metrics.average_workout_duration_minutes else 0,
        "weight_change_kg": round(weight_change, 2) if weight_change else None,
        "weight_change_percentage": round(weight_change_percentage, 1) if weight_change_percentage else None,
        "recent_workout_trend": trend,
        "recent_workouts_30_days": recent_workouts,
        "previous_workouts_30_days": previous_workouts,
        "total_sets": metrics.total_sets_completed,
        "total_reps": metrics.total_reps_completed,
        "times_reset": metrics.times_workouts_reset,
        "days_since_start": (datetime.now() - metrics.client_since).days if metrics.client_since else 0
    }
