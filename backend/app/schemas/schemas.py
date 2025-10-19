from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.models import UserRole


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole
    language: str = "en"
    date_of_birth: datetime
    weight: float = Field(gt=0, description="Weight in kg")
    height: float = Field(gt=0, description="Height in cm")
    desired_weight: Optional[float] = Field(None, gt=0, description="Target weight goal in kg")
    phone: Optional[str] = None
    personal_trainer_id: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @validator('language')
    def validate_language(cls, v):
        if v not in ['en', 'pt']:
            raise ValueError('Language must be either "en" or "pt"')
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    weight: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    desired_weight: Optional[float] = Field(None, gt=0)
    phone: Optional[str] = None

    @validator('language')
    def validate_language(cls, v):
        if v is not None and v not in ['en', 'pt']:
            raise ValueError('Language must be either "en" or "pt"')
        return v


class UserResponse(UserBase):
    id: str
    created_at: datetime
    bmi: Optional[float] = None
    age: Optional[int] = None
    personal_trainer_name: Optional[str] = None

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Exercise Schemas
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    muscle_group: str
    equipment: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    muscle_group: Optional[str] = None
    equipment: Optional[str] = None


class ExerciseResponse(ExerciseBase):
    id: str
    image_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Workout Plan Schemas
class PlanExerciseBase(BaseModel):
    exercise_id: str
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    rest_time: int = Field(ge=0, description="Rest time in seconds")
    weight: Optional[float] = Field(None, ge=0, description="Weight in kg")
    order: int = Field(ge=0)


class PlanExerciseCreate(PlanExerciseBase):
    pass


class PlanExerciseResponse(PlanExerciseBase):
    id: str
    workout_plan_id: str
    exercise: Optional[ExerciseResponse] = None

    class Config:
        from_attributes = True


class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = False


class WorkoutPlanCreate(WorkoutPlanBase):
    exercises: List[PlanExerciseCreate] = []


class WorkoutPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WorkoutPlanResponse(WorkoutPlanBase):
    id: str
    user_id: str
    created_at: datetime
    plan_exercises: List[PlanExerciseResponse] = []

    class Config:
        from_attributes = True


# Workout Session Schemas
class ExerciseLogBase(BaseModel):
    exercise_id: str
    sets_completed: int = Field(gt=0)
    reps_completed: int = Field(gt=0)
    weight_used: Optional[float] = Field(None, ge=0)
    rest_time_actual: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class ExerciseLogCreate(ExerciseLogBase):
    pass


class ExerciseLogResponse(ExerciseLogBase):
    id: str
    session_id: str
    completed_at: datetime
    exercise: Optional[ExerciseResponse] = None

    class Config:
        from_attributes = True


class WorkoutSessionBase(BaseModel):
    workout_plan_id: Optional[str] = None
    notes: Optional[str] = None


class WorkoutSessionCreate(WorkoutSessionBase):
    pass


class WorkoutSessionUpdate(BaseModel):
    notes: Optional[str] = None
    end_time: Optional[datetime] = None


class WorkoutSessionResponse(WorkoutSessionBase):
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    exercise_logs: List[ExerciseLogResponse] = []

    class Config:
        from_attributes = True


# Cardio Session Schemas
class CardioSessionBase(BaseModel):
    activity_type: str
    location: Optional[str] = None
    duration: int = Field(gt=0, description="Duration in minutes")
    distance: Optional[float] = Field(None, ge=0, description="Distance in km")
    calories_burned: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class CardioSessionCreate(CardioSessionBase):
    start_time: Optional[datetime] = None


class CardioSessionUpdate(BaseModel):
    activity_type: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[int] = Field(None, gt=0)
    distance: Optional[float] = Field(None, ge=0)
    calories_burned: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class CardioSessionResponse(CardioSessionBase):
    id: str
    user_id: str
    start_time: datetime

    class Config:
        from_attributes = True


# Health Metrics
class HealthMetrics(BaseModel):
    current_weight: float
    desired_weight: Optional[float] = None
    weight_difference: Optional[float] = None  # kg to gain/lose
    current_bmi: float
    bmi_category: str
    target_bmi: Optional[float] = None
    healthy_weight_range: dict  # {"min": float, "max": float}
    estimated_weeks: Optional[int] = None  # weeks to reach goal
    estimated_date: Optional[str] = None  # estimated achievement date
    weekly_change_needed: Optional[float] = None  # kg per week
    daily_calorie_adjustment: Optional[int] = None  # calorie deficit/surplus
    recommendation: str
    health_status: str  # "healthy", "underweight", "overweight", "obese"


# Dashboard Stats
class DashboardStats(BaseModel):
    total_workouts: int
    total_cardio_sessions: int
    current_bmi: Optional[float] = None
    active_streak: int
    total_exercises: int


# Assigned Exercise Schemas
class AssignedExerciseBase(BaseModel):
    exercise_id: str
    client_id: str
    notes: Optional[str] = None


class AssignedExerciseCreate(AssignedExerciseBase):
    pass


class AssignedExerciseResponse(AssignedExerciseBase):
    id: str
    personal_trainer_id: str
    assigned_at: datetime
    exercise: Optional[ExerciseResponse] = None

    class Config:
        from_attributes = True
