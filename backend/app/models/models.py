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
    username = Column(String, unique=True, index=True, nullable=False)
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
    exercise_logs = relationship("ExerciseLog", back_populates="exercise", passive_deletes=True)
    assigned_exercises = relationship("AssignedExercise", back_populates="exercise", cascade="all, delete-orphan")

    @property
    def image_url(self):
        """Return the image URL path for frontend"""
        return self.image_path if self.image_path else None


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
    sets = Column(String, nullable=False)  # Changed to String to allow values like "Max", "3-4", etc.
    reps = Column(String, nullable=False)  # Changed to String to allow values like "10-12", "Max", etc.
    rest_time = Column(String, nullable=False)  # Changed to String to allow values like "60", "90s", "5'", etc.
    weight = Column(Float, nullable=True)  # kg
    equipment_number = Column(String, nullable=True)  # Equipment to use (e.g., "Machine 5", "Bench 3")
    notes = Column(Text, nullable=True)  # PT instructions/observations for the client
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
    sets_completed = Column(String, nullable=False)  # Changed to String to allow values like "Max", "3-4", etc.
    reps_completed = Column(String, nullable=False)  # Changed to String to allow values like "10-12", "Max", etc.
    weight_used = Column(Float, nullable=True)  # kg
    rest_time_actual = Column(String, nullable=True)  # Changed to String to allow values like "60", "90s", "5'", etc.
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


class WeightHistory(Base):
    """
    Tracks weight changes over time for each user
    This allows calculating time between weight changes and tracking progress
    """
    __tablename__ = "weight_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    weight = Column(Float, nullable=False)  # kg
    previous_weight = Column(Float, nullable=True)  # kg - previous weight for calculating difference
    days_since_last_change = Column(Integer, nullable=True)  # days since last weight update
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class ClientMetrics(Base):
    """
    Stores aggregated metrics for clients that Personal Trainers can track
    These metrics persist even if the client resets their workout count
    """
    __tablename__ = "client_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    personal_trainer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Workout metrics (cumulative, never reset)
    total_workouts_completed = Column(Integer, default=0)  # Total workouts ever completed
    total_cardio_sessions = Column(Integer, default=0)  # Total cardio sessions ever completed
    total_training_hours = Column(Float, default=0.0)  # Total hours of training
    total_training_days = Column(Integer, default=0)  # Unique days with training activity

    # Series and reps tracking
    total_sets_completed = Column(Integer, default=0)
    total_reps_completed = Column(Integer, default=0)

    # Weight tracking
    initial_weight = Column(Float, nullable=True)  # kg - weight when client started
    current_weight = Column(Float, nullable=True)  # kg - current weight
    lowest_weight = Column(Float, nullable=True)  # kg - lowest recorded weight
    highest_weight = Column(Float, nullable=True)  # kg - highest recorded weight
    total_weight_changes = Column(Integer, default=0)  # Number of times weight was updated
    average_days_between_weight_changes = Column(Float, nullable=True)  # Average days between weight updates

    # Client resets (when client zeros their workout count)
    times_workouts_reset = Column(Integer, default=0)
    last_reset_date = Column(DateTime(timezone=True), nullable=True)
    workouts_before_last_reset = Column(Integer, default=0)

    # Consistency metrics
    consistency_percentage = Column(Float, nullable=True)  # % of days with activity since start
    average_workout_duration_minutes = Column(Float, nullable=True)

    # Timestamps
    client_since = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    client = relationship("User", foreign_keys=[client_id])
    personal_trainer = relationship("User", foreign_keys=[personal_trainer_id])


class PasswordResetToken(Base):
    """
    Stores password reset tokens for users who forgot their password
    Tokens expire after a set time period
    """
    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class LoginAttempt(Base):
    """
    Tracks failed login attempts for rate limiting and security monitoring
    """
    __tablename__ = "login_attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = Column(String, nullable=False, index=True)  # Email or username attempted
    ip_address = Column(String, nullable=True)
    success = Column(Boolean, default=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Null if user not found

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
