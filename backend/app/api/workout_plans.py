from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import User, WorkoutPlan, PlanExercise, Exercise, UserRole, AssignedExercise
from app.schemas.schemas import (
    WorkoutPlanCreate,
    WorkoutPlanResponse,
    WorkoutPlanUpdate,
    PlanExerciseCreate
)
from app.core.security import get_current_user

router = APIRouter(prefix="/workout-plans", tags=["Workout Plans"])


@router.post("", response_model=WorkoutPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_plan(
    plan_data: WorkoutPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workout plan"""
    # Determine the user_id for the workout plan
    target_user_id = current_user.id

    # If client_id is provided and user is a PT, create plan for that client
    if plan_data.client_id and current_user.role == UserRole.PERSONAL_TRAINER:
        # Verify the client belongs to this PT
        client = db.query(User).filter(
            User.id == plan_data.client_id,
            User.personal_trainer_id == current_user.id
        ).first()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This client is not assigned to you"
            )

        target_user_id = plan_data.client_id

    # Create workout plan
    new_plan = WorkoutPlan(
        user_id=target_user_id,
        name=plan_data.name,
        description=plan_data.description,
        is_active=plan_data.is_active
    )
    db.add(new_plan)
    db.flush()  # Get the ID without committing

    # Add exercises to plan
    for exercise_data in plan_data.exercises:
        # Verify exercise exists
        exercise = db.query(Exercise).filter(Exercise.id == exercise_data.exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise {exercise_data.exercise_id} not found"
            )

        # SECURITY: Verify user has permission to use this exercise
        if current_user.role == UserRole.PERSONAL_TRAINER:
            # PT can only use exercises they created
            if exercise.created_by != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You don't have permission to use exercise {exercise_data.exercise_id}"
                )
        else:
            # CLIENT can only use exercises assigned to them
            is_assigned = db.query(AssignedExercise).filter(
                AssignedExercise.exercise_id == exercise_data.exercise_id,
                AssignedExercise.client_id == current_user.id
            ).first()
            if not is_assigned:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Exercise {exercise_data.exercise_id} has not been assigned to you"
                )

        plan_exercise = PlanExercise(
            workout_plan_id=new_plan.id,
            exercise_id=exercise_data.exercise_id,
            sets=exercise_data.sets,
            reps=exercise_data.reps,
            rest_time=exercise_data.rest_time,
            weight=exercise_data.weight,
            order=exercise_data.order
        )
        db.add(plan_exercise)

    db.commit()
    db.refresh(new_plan)

    return new_plan


@router.get("", response_model=List[WorkoutPlanResponse])
async def get_workout_plans(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workout plans for current user"""
    plans = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return plans


@router.get("/{plan_id}", response_model=WorkoutPlanResponse)
async def get_workout_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific workout plan"""
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )

    return plan


@router.put("/{plan_id}", response_model=WorkoutPlanResponse)
async def update_workout_plan(
    plan_id: str,
    plan_update: WorkoutPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update workout plan"""
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )

    if plan_update.name is not None:
        plan.name = plan_update.name
    if plan_update.description is not None:
        plan.description = plan_update.description
    if plan_update.is_active is not None:
        plan.is_active = plan_update.is_active

    db.commit()
    db.refresh(plan)

    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete workout plan"""
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )

    db.delete(plan)
    db.commit()

    return None


@router.post("/{plan_id}/exercises", response_model=WorkoutPlanResponse)
async def add_exercise_to_plan(
    plan_id: str,
    exercise_data: PlanExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an exercise to workout plan"""
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )

    # Verify exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == exercise_data.exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # SECURITY: Verify user has permission to use this exercise
    if current_user.role == UserRole.PERSONAL_TRAINER:
        # PT can only use exercises they created
        if exercise.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to use exercise {exercise_data.exercise_id}"
            )
    else:
        # CLIENT can only use exercises assigned to them
        is_assigned = db.query(AssignedExercise).filter(
            AssignedExercise.exercise_id == exercise_data.exercise_id,
            AssignedExercise.client_id == current_user.id
        ).first()
        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Exercise {exercise_data.exercise_id} has not been assigned to you"
            )

    plan_exercise = PlanExercise(
        workout_plan_id=plan_id,
        exercise_id=exercise_data.exercise_id,
        sets=exercise_data.sets,
        reps=exercise_data.reps,
        rest_time=exercise_data.rest_time,
        weight=exercise_data.weight,
        order=exercise_data.order
    )

    db.add(plan_exercise)
    db.commit()
    db.refresh(plan)

    return plan


@router.delete("/{plan_id}/exercises/{plan_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_exercise_from_plan(
    plan_id: str,
    plan_exercise_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an exercise from workout plan"""
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout plan not found"
        )

    plan_exercise = db.query(PlanExercise).filter(
        PlanExercise.id == plan_exercise_id,
        PlanExercise.workout_plan_id == plan_id
    ).first()

    if not plan_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found in plan"
        )

    db.delete(plan_exercise)
    db.commit()

    return None
