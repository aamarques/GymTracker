from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import init_db
from app.db.migrations import run_migrations
from app.api import auth, users, exercises, workout_plans, workout_sessions, cardio
from app.core.config import settings
import os

app = FastAPI(
    title="Gym Workout Tracker API",
    description="API for tracking gym workouts, exercises, and cardio sessions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving images
uploads_dir = os.path.join(settings.UPLOAD_DIR, "exercises")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(exercises.router, prefix="/api")
app.include_router(workout_plans.router, prefix="/api")
app.include_router(workout_sessions.router, prefix="/api")
app.include_router(cardio.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and run migrations on startup"""
    init_db()
    print("Running database migrations...")
    run_migrations()
    print("Application ready!")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Gym Workout Tracker API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
