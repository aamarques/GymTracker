from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from pathlib import Path
from app.db.database import get_db
from app.models.models import User, Exercise
from app.schemas.schemas import ExerciseCreate, ExerciseResponse, ExerciseUpdate
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/exercises", tags=["Exercises"])


def save_exercise_image(file: UploadFile) -> str:
    """Save uploaded exercise image and return path"""
    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, "exercises", unique_filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        buffer.write(content)

    return f"/uploads/exercises/{unique_filename}"


@router.post("", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    name: str = Form(...),
    muscle_group: str = Form(...),
    description: Optional[str] = Form(None),
    equipment: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new exercise"""
    image_path = None
    if image:
        image_path = save_exercise_image(image)

    new_exercise = Exercise(
        name=name,
        description=description,
        muscle_group=muscle_group,
        equipment=equipment,
        image_path=image_path,
        created_by=current_user.id
    )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return new_exercise


@router.get("", response_model=List[ExerciseResponse])
async def get_exercises(
    skip: int = 0,
    limit: int = 100,
    muscle_group: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all exercises with optional filtering"""
    query = db.query(Exercise)

    if muscle_group:
        query = query.filter(Exercise.muscle_group.ilike(f"%{muscle_group}%"))

    if search:
        query = query.filter(Exercise.name.ilike(f"%{search}%"))

    exercises = query.offset(skip).limit(limit).all()
    return exercises


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific exercise by ID"""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    return exercise


@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: str,
    name: Optional[str] = Form(None),
    muscle_group: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    equipment: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update exercise"""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    if name is not None:
        exercise.name = name
    if muscle_group is not None:
        exercise.muscle_group = muscle_group
    if description is not None:
        exercise.description = description
    if equipment is not None:
        exercise.equipment = equipment
    if image:
        # Delete old image if exists
        if exercise.image_path:
            old_path = os.path.join("/app", exercise.image_path.lstrip("/"))
            if os.path.exists(old_path):
                os.remove(old_path)
        exercise.image_path = save_exercise_image(image)

    db.commit()
    db.refresh(exercise)

    return exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
    exercise_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete exercise"""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # Delete image file if exists
    if exercise.image_path:
        file_path = os.path.join("/app", exercise.image_path.lstrip("/"))
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(exercise)
    db.commit()

    return None
