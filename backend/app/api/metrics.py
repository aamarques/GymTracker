"""
API endpoints for client metrics and progress tracking
Personal Trainers can view comprehensive metrics about their clients
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import User, ClientMetrics, WeightHistory, UserRole
from app.schemas.schemas import (
    ClientMetricsResponse,
    ClientMetricsDetailedResponse,
    WeightHistoryResponse
)
from app.core.security import get_current_user
from app.core.permissions import require_personal_trainer, check_client_belongs_to_trainer
from app.services.metrics_service import (
    get_or_create_client_metrics,
    reset_client_workouts,
    calculate_client_progress
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.post("/workouts/reset")
async def reset_my_workouts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allow a client to reset their workout count
    Metrics are preserved for the Personal Trainer
    """
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can reset their workout count"
        )

    result = reset_client_workouts(db, current_user.id)
    return result


@router.get("/my-metrics", response_model=ClientMetricsResponse)
async def get_my_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's metrics (for clients to see their own progress)
    """
    metrics = get_or_create_client_metrics(db, current_user.id)
    return metrics


@router.get("/my-progress")
async def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed progress analysis for current user
    """
    progress = calculate_client_progress(db, current_user.id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics found"
        )

    return progress


@router.get("/weight-history", response_model=List[WeightHistoryResponse])
async def get_my_weight_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weight history for current user
    """
    history = db.query(WeightHistory).filter(
        WeightHistory.user_id == current_user.id
    ).order_by(WeightHistory.recorded_at.desc()).limit(limit).all()

    return history


# ===== Personal Trainer Endpoints =====

@router.get("/clients", response_model=List[ClientMetricsResponse])
async def get_all_clients_metrics(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """
    Get metrics for all clients of the current Personal Trainer
    Supports pagination via skip and limit parameters
    """
    metrics = db.query(ClientMetrics).filter(
        ClientMetrics.personal_trainer_id == current_user.id
    ).offset(skip).limit(limit).all()

    return metrics


@router.get("/clients/{client_id}", response_model=ClientMetricsDetailedResponse)
async def get_client_metrics_detail(
    client_id: str,
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """
    Get detailed metrics for a specific client
    """
    client = db.query(User).filter(User.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    check_client_belongs_to_trainer(client, current_user)

    metrics = db.query(ClientMetrics).filter(
        ClientMetrics.client_id == client_id
    ).first()

    if not metrics:
        # Create metrics if they don't exist
        metrics = get_or_create_client_metrics(db, client_id, current_user.id)

    # Get weight history
    weight_history = db.query(WeightHistory).filter(
        WeightHistory.user_id == client_id
    ).order_by(WeightHistory.recorded_at.desc()).limit(20).all()

    # Create response with additional client details
    response = ClientMetricsDetailedResponse(
        **metrics.__dict__,
        client_name=client.name,
        client_email=client.email,
        weight_history=weight_history
    )

    return response


@router.get("/clients/{client_id}/progress")
async def get_client_progress(
    client_id: str,
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """
    Get detailed progress analysis for a specific client
    """
    client = db.query(User).filter(User.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    check_client_belongs_to_trainer(client, current_user)

    progress = calculate_client_progress(db, client_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics found for this client"
        )

    # Add client info to response
    progress["client_name"] = client.name
    progress["client_email"] = client.email

    return progress


@router.get("/clients/{client_id}/weight-history", response_model=List[WeightHistoryResponse])
async def get_client_weight_history(
    client_id: str,
    limit: int = 50,
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """
    Get weight history for a specific client
    """
    client = db.query(User).filter(User.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    check_client_belongs_to_trainer(client, current_user)

    history = db.query(WeightHistory).filter(
        WeightHistory.user_id == client_id
    ).order_by(WeightHistory.recorded_at.desc()).limit(limit).all()

    return history


@router.get("/dashboard-summary")
async def get_trainer_dashboard_summary(
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for Personal Trainer dashboard
    Shows aggregate data across all clients
    """
    from sqlalchemy import func

    # Get all metrics for this trainer's clients
    all_metrics = db.query(ClientMetrics).filter(
        ClientMetrics.personal_trainer_id == current_user.id
    ).all()

    if not all_metrics:
        return {
            "total_clients": 0,
            "total_workouts_all_clients": 0,
            "total_training_hours_all_clients": 0,
            "average_client_consistency": 0,
            "most_active_client": None,
            "most_consistent_client": None
        }

    # Calculate aggregates
    total_clients = len(all_metrics)
    total_workouts = sum([m.total_workouts_completed for m in all_metrics])
    total_hours = sum([m.total_training_hours for m in all_metrics])
    avg_consistency = sum([m.consistency_percentage or 0 for m in all_metrics]) / total_clients if total_clients > 0 else 0

    # Find most active client (by workouts)
    most_active = max(all_metrics, key=lambda m: m.total_workouts_completed)
    most_active_client = db.query(User).filter(User.id == most_active.client_id).first()

    # Find most consistent client (by consistency percentage)
    most_consistent = max(all_metrics, key=lambda m: m.consistency_percentage or 0)
    most_consistent_client = db.query(User).filter(User.id == most_consistent.client_id).first()

    return {
        "total_clients": total_clients,
        "total_workouts_all_clients": total_workouts,
        "total_training_hours_all_clients": round(total_hours, 2),
        "average_client_consistency": round(avg_consistency, 1),
        "most_active_client": {
            "name": most_active_client.name,
            "workouts": most_active.total_workouts_completed
        } if most_active_client else None,
        "most_consistent_client": {
            "name": most_consistent_client.name,
            "consistency": round(most_consistent.consistency_percentage, 1)
        } if most_consistent_client else None
    }
