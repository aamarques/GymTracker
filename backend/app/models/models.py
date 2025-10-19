from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum


class UserRole(str, enum.Enum):
    PERSONAL_TRAINER = "personal_trainer"
    CLIENT = "client"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserRole.CLIENT)
    language = Column(String, nullable=False, default="en")  # en or pt
    date_of_birth = Column(DateTime, nullable=False)
    weight = Column(Float, nullable=False)  # kg
    height = Column(Float, nullable=False)  # cm
    desired_weight = Column(Float, nullable=True)  # kg - target weight goal
    phone = Column(String, nullable=True)
    personal_trainer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    personal_trainer = relationship("User", remote_side=[id], foreign_keys=[personal_trainer_id], backref="clients")
    workout_plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")
    workout_sessions = relationship("WorkoutSession", back_populates="user", cascade="all, delete-orphan")
    cardio_sessions = relationship("CardioSession", back_populates="user", cascade="all, delete-orphan")
    created_exercises = relationship("Exercise", back_populates="creator", cascade="all, delete-orphan")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    muscle_group = Column(String, nullable=False)
    equipment = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="created_exercises")
    plan_exercises = relationship("PlanExercise", back_populates="exercise", cascade="all, delete-orphan")
    exercise_logs = relationship("ExerciseLog", back_populates="exercise")
    assigned_exercises = relationship("AssignedExercise", back_populates="exercise", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="workout_plans")
    plan_exercises = relationship("PlanExercise", back_populates="workout_plan", cascade="all, delete-orphan", order_by="PlanExercise.order")
    workout_sessions = relationship("WorkoutSession", back_populates="workout_plan")


class PlanExercise(Base):
    __tablename__ = "plan_exercises"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workout_plan_id = Column(String, ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(String, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    rest_time = Column(Integer, nullable=False)  # seconds
    weight = Column(Float, nullable=True)  # kg
    order = Column(Integer, nullable=False, default=0)

    # Relationships
    workout_plan = relationship("WorkoutPlan", back_populates="plan_exercises")
    exercise = relationship("Exercise", back_populates="plan_exercises")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workout_plan_id = Column(String, ForeignKey("workout_plans.id", ondelete="SET NULL"), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="workout_sessions")
    workout_plan = relationship("WorkoutPlan", back_populates="workout_sessions")
    exercise_logs = relationship("ExerciseLog", back_populates="session", cascade="all, delete-orphan")


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(String, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    sets_completed = Column(Integer, nullable=False)
    reps_completed = Column(Integer, nullable=False)
    weight_used = Column(Float, nullable=True)  # kg
    rest_time_actual = Column(Integer, nullable=True)  # seconds
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("WorkoutSession", back_populates="exercise_logs")
    exercise = relationship("Exercise", back_populates="exercise_logs")


class CardioSession(Base):
    __tablename__ = "cardio_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String, nullable=False)  # running, cycling, swimming, etc.
    location = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)  # minutes
    distance = Column(Float, nullable=True)  # km
    calories_burned = Column(Integer, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="cardio_sessions")


class AssignedExercise(Base):
    """
    Junction table for Personal Trainers assigning exercises to their clients
    A PT can assign exercises from the library to specific clients
    """
    __tablename__ = "assigned_exercises"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exercise_id = Column(String, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    personal_trainer_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)  # PT can add notes for the client

    # Relationships
    exercise = relationship("Exercise", back_populates="assigned_exercises")
    client = relationship("User", foreign_keys=[client_id])
    personal_trainer = relationship("User", foreign_keys=[personal_trainer_id])
