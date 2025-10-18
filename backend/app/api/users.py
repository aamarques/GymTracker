from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, UserUpdate, DashboardStats, HealthMetrics
from app.core.security import get_current_user
from app.api.auth import calculate_bmi, calculate_age
from datetime import datetime, timedelta

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    response = UserResponse.from_orm(current_user)
    response.bmi = calculate_bmi(current_user.weight, current_user.height)
    response.age = calculate_age(current_user.date_of_birth)
    return response


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.weight is not None:
        current_user.weight = user_update.weight
    if user_update.height is not None:
        current_user.height = user_update.height
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.desired_weight is not None:
        current_user.desired_weight = user_update.desired_weight

    db.commit()
    db.refresh(current_user)

    response = UserResponse.from_orm(current_user)
    response.bmi = calculate_bmi(current_user.weight, current_user.height)
    response.age = calculate_age(current_user.date_of_birth)
    return response


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for current user"""
    from app.models.models import WorkoutSession, CardioSession, Exercise

    # Total workouts
    total_workouts = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == current_user.id,
        WorkoutSession.end_time.isnot(None)
    ).count()

    # Total cardio sessions
    total_cardio = db.query(CardioSession).filter(
        CardioSession.user_id == current_user.id
    ).count()

    # Calculate BMI
    current_bmi = calculate_bmi(current_user.weight, current_user.height)

    # Calculate active streak (consecutive days with workouts)
    today = datetime.now().date()
    active_streak = 0
    check_date = today

    while True:
        has_workout = db.query(WorkoutSession).filter(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.start_time >= check_date,
            WorkoutSession.start_time < check_date + timedelta(days=1),
            WorkoutSession.end_time.isnot(None)
        ).first() is not None

        has_cardio = db.query(CardioSession).filter(
            CardioSession.user_id == current_user.id,
            CardioSession.start_time >= check_date,
            CardioSession.start_time < check_date + timedelta(days=1)
        ).first() is not None

        if has_workout or has_cardio:
            active_streak += 1
            check_date -= timedelta(days=1)
        else:
            break

        # Limit to prevent infinite loop
        if active_streak > 365:
            break

    # Total exercises in library
    total_exercises = db.query(Exercise).count()

    return DashboardStats(
        total_workouts=total_workouts,
        total_cardio_sessions=total_cardio,
        current_bmi=current_bmi,
        active_streak=active_streak,
        total_exercises=total_exercises
    )


@router.get("/health-metrics", response_model=HealthMetrics)
async def get_health_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive health metrics analysis including weight goal timeline"""
    import math

    # Calculate current BMI
    height_m = current_user.height / 100  # Convert cm to meters
    current_bmi = current_user.weight / (height_m ** 2)

    # Determine BMI category
    if current_bmi < 18.5:
        bmi_category = "Underweight"
        health_status = "underweight"
    elif 18.5 <= current_bmi < 25:
        bmi_category = "Normal weight"
        health_status = "healthy"
    elif 25 <= current_bmi < 30:
        bmi_category = "Overweight"
        health_status = "overweight"
    else:
        bmi_category = "Obese"
        health_status = "obese"

    # Calculate healthy weight range (BMI 18.5-24.9)
    healthy_min = 18.5 * (height_m ** 2)
    healthy_max = 24.9 * (height_m ** 2)
    healthy_weight_range = {
        "min": round(healthy_min, 1),
        "max": round(healthy_max, 1)
    }

    # Calculate weight goal metrics if desired_weight is set
    weight_difference = None
    target_bmi = None
    estimated_weeks = None
    estimated_date = None
    weekly_change_needed = None
    daily_calorie_adjustment = None
    recommendation = ""

    if current_user.desired_weight:
        weight_difference = current_user.desired_weight - current_user.weight
        target_bmi = current_user.desired_weight / (height_m ** 2)

        # Safe weight loss/gain rate: 0.5-1 kg per week
        # We'll use 0.5 kg/week for conservative estimate
        safe_weekly_change = 0.5

        if abs(weight_difference) > 0.1:  # If difference is significant
            estimated_weeks = math.ceil(abs(weight_difference) / safe_weekly_change)
            estimated_date = (datetime.now() + timedelta(weeks=estimated_weeks)).strftime("%Y-%m-%d")
            weekly_change_needed = round(weight_difference / estimated_weeks, 2) if estimated_weeks > 0 else 0

            # 1 kg fat = approximately 7700 calories
            # Calculate daily calorie adjustment needed
            total_calories = abs(weight_difference) * 7700
            days_needed = estimated_weeks * 7
            daily_calorie_adjustment = round(total_calories / days_needed) if days_needed > 0 else 0

            # Make it negative for weight loss, positive for weight gain
            if weight_difference < 0:
                daily_calorie_adjustment = -daily_calorie_adjustment

            # Generate recommendation
            if weight_difference > 0:
                recommendation = (
                    f"To reach your goal of {current_user.desired_weight}kg, you need to gain "
                    f"{abs(weight_difference):.1f}kg. At a healthy rate of {safe_weekly_change}kg per week, "
                    f"this will take approximately {estimated_weeks} weeks. "
                    f"Aim for a calorie surplus of ~{abs(daily_calorie_adjustment)} calories per day through "
                    f"increased food intake and strength training."
                )
            elif weight_difference < 0:
                recommendation = (
                    f"To reach your goal of {current_user.desired_weight}kg, you need to lose "
                    f"{abs(weight_difference):.1f}kg. At a healthy rate of {safe_weekly_change}kg per week, "
                    f"this will take approximately {estimated_weeks} weeks. "
                    f"Aim for a calorie deficit of ~{abs(daily_calorie_adjustment)} calories per day through "
                    f"diet and exercise."
                )
            else:
                recommendation = "You're at your target weight! Focus on maintaining through balanced diet and regular exercise."
        else:
            recommendation = "You're at your target weight! Focus on maintaining through balanced diet and regular exercise."
    else:
        # No goal weight set
        if health_status == "healthy":
            recommendation = (
                f"Your BMI is {current_bmi:.1f}, which is in the healthy range. "
                f"Set a desired weight goal to get a personalized timeline and recommendations."
            )
        elif health_status == "underweight":
            recommendation = (
                f"Your BMI is {current_bmi:.1f}, which is below the healthy range. "
                f"Consider setting a target weight between {healthy_weight_range['min']}kg and {healthy_weight_range['max']}kg. "
                f"Consult with a healthcare professional for personalized advice."
            )
        elif health_status == "overweight":
            recommendation = (
                f"Your BMI is {current_bmi:.1f}, which is above the healthy range. "
                f"Consider setting a target weight between {healthy_weight_range['min']}kg and {healthy_weight_range['max']}kg. "
                f"Set a desired weight goal to get a personalized timeline."
            )
        else:  # obese
            recommendation = (
                f"Your BMI is {current_bmi:.1f}, which is significantly above the healthy range. "
                f"Consider setting a target weight between {healthy_weight_range['min']}kg and {healthy_weight_range['max']}kg. "
                f"Please consult with a healthcare professional before starting any weight loss program."
            )

    return HealthMetrics(
        current_weight=current_user.weight,
        desired_weight=current_user.desired_weight,
        weight_difference=round(weight_difference, 1) if weight_difference else None,
        current_bmi=round(current_bmi, 1),
        bmi_category=bmi_category,
        target_bmi=round(target_bmi, 1) if target_bmi else None,
        healthy_weight_range=healthy_weight_range,
        estimated_weeks=estimated_weeks,
        estimated_date=estimated_date,
        weekly_change_needed=weekly_change_needed,
        daily_calorie_adjustment=daily_calorie_adjustment,
        recommendation=recommendation,
        health_status=health_status
    )
