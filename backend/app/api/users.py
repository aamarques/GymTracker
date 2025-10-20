from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import UserResponse, UserUpdate, DashboardStats, HealthMetrics, ClientListResponse
from app.core.security import get_current_user
from app.core.permissions import require_personal_trainer
from app.api.auth import calculate_bmi, calculate_age
from datetime import datetime, timedelta

router = APIRouter(prefix="/users", tags=["Users"])


# Health recommendation translations
TRANSLATIONS = {
    "en": {
        "in_healthy_range": "Your BMI is {bmi:.1f}, which is in the healthy range.",
        "below_healthy_range": "Your BMI is {bmi:.1f}, which is below the healthy range.",
        "above_healthy_range": "Your BMI is {bmi:.1f}, which is above the healthy range.",
        "significantly_above": "Your BMI is {bmi:.1f}, which is significantly above the healthy range.",
        "set_goal": "Set a desired weight goal to get a personalized timeline and recommendations.",
        "consider_target": "Consider setting a target weight between {min}kg and {max}kg.",
        "consult_professional": "Consult with a healthcare professional for personalized advice.",
        "consult_before_loss": "Please consult with a healthcare professional before starting any weight loss program.",
        "gain_recommendation": "To reach your goal of {target}kg, you need to gain {diff:.1f}kg. At a healthy rate of {rate}kg per week, this will take approximately {weeks} weeks. Aim for a calorie surplus of ~{cal} calories per day through increased food intake and strength training.",
        "loss_recommendation": "To reach your goal of {target}kg, you need to lose {diff:.1f}kg. At a healthy rate of {rate}kg per week, this will take approximately {weeks} weeks. Aim for a calorie deficit of ~{cal} calories per day through diet and exercise.",
        "at_target": "You're at your target weight! Focus on maintaining through balanced diet and regular exercise."
    },
    "pt": {
        "in_healthy_range": "Seu IMC é {bmi:.1f}, que está na faixa saudável.",
        "below_healthy_range": "Seu IMC é {bmi:.1f}, que está abaixo da faixa saudável.",
        "above_healthy_range": "Seu IMC é {bmi:.1f}, que está acima da faixa saudável.",
        "significantly_above": "Seu IMC é {bmi:.1f}, que está significativamente acima da faixa saudável.",
        "set_goal": "Defina um objetivo de peso desejado para obter um cronograma e recomendações personalizadas.",
        "consider_target": "Considere definir um peso alvo entre {min}kg e {max}kg.",
        "consult_professional": "Consulte um profissional de saúde para aconselhamento personalizado.",
        "consult_before_loss": "Por favor, consulte um profissional de saúde antes de iniciar qualquer programa de perda de peso.",
        "gain_recommendation": "Para atingir seu objetivo de {target}kg, você precisa ganhar {diff:.1f}kg. A uma taxa saudável de {rate}kg por semana, isso levará aproximadamente {weeks} semanas. Procure um superávit calórico de ~{cal} calorias por dia através de maior ingestão alimentar e treino de força.",
        "loss_recommendation": "Para atingir seu objetivo de {target}kg, você precisa perder {diff:.1f}kg. A uma taxa saudável de {rate}kg por semana, isso levará aproximadamente {weeks} semanas. Procure um déficit calórico de ~{cal} calorias por dia através de dieta e exercício.",
        "at_target": "Você está no seu peso alvo! Concentre-se em manter através de dieta equilibrada e exercício regular."
    }
}


def get_translation(lang: str, key: str, **kwargs) -> str:
    """Get translated text for a given key and language"""
    if lang not in TRANSLATIONS:
        lang = "en"
    template = TRANSLATIONS[lang].get(key, TRANSLATIONS["en"][key])
    return template.format(**kwargs)


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
    from app.services.metrics_service import track_weight_change

    # Check if username is being updated and if it's already taken
    if user_update.username is not None and user_update.username != current_user.username:
        existing_username = db.query(User).filter(
            User.username == user_update.username,
            User.id != current_user.id
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.language is not None:
        current_user.language = user_update.language

    # Track weight change if updated
    weight_changed = False
    if user_update.weight is not None and user_update.weight != current_user.weight:
        weight_changed = True
        old_weight = current_user.weight
        current_user.weight = user_update.weight

    if user_update.height is not None:
        current_user.height = user_update.height
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.desired_weight is not None:
        current_user.desired_weight = user_update.desired_weight

    db.commit()
    db.refresh(current_user)

    # Track weight change in history and update metrics
    if weight_changed:
        track_weight_change(db, current_user.id, current_user.weight)

    response = UserResponse.from_orm(current_user)
    response.bmi = calculate_bmi(current_user.weight, current_user.height)
    response.age = calculate_age(current_user.date_of_birth)
    if current_user.personal_trainer:
        response.personal_trainer_name = current_user.personal_trainer.name
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

            # Generate recommendation using user's language
            lang = current_user.language if current_user.language in ["en", "pt"] else "en"

            if weight_difference > 0:
                recommendation = get_translation(
                    lang, "gain_recommendation",
                    target=current_user.desired_weight,
                    diff=abs(weight_difference),
                    rate=safe_weekly_change,
                    weeks=estimated_weeks,
                    cal=abs(daily_calorie_adjustment)
                )
            elif weight_difference < 0:
                recommendation = get_translation(
                    lang, "loss_recommendation",
                    target=current_user.desired_weight,
                    diff=abs(weight_difference),
                    rate=safe_weekly_change,
                    weeks=estimated_weeks,
                    cal=abs(daily_calorie_adjustment)
                )
            else:
                recommendation = get_translation(lang, "at_target")
        else:
            lang = current_user.language if current_user.language in ["en", "pt"] else "en"
            recommendation = get_translation(lang, "at_target")
    else:
        # No goal weight set - use user's language
        lang = current_user.language if current_user.language in ["en", "pt"] else "en"

        if health_status == "healthy":
            bmi_msg = get_translation(lang, "in_healthy_range", bmi=current_bmi)
            goal_msg = get_translation(lang, "set_goal")
            recommendation = f"{bmi_msg} {goal_msg}"
        elif health_status == "underweight":
            bmi_msg = get_translation(lang, "below_healthy_range", bmi=current_bmi)
            target_msg = get_translation(lang, "consider_target",
                                       min=healthy_weight_range['min'],
                                       max=healthy_weight_range['max'])
            consult_msg = get_translation(lang, "consult_professional")
            recommendation = f"{bmi_msg} {target_msg} {consult_msg}"
        elif health_status == "overweight":
            bmi_msg = get_translation(lang, "above_healthy_range", bmi=current_bmi)
            target_msg = get_translation(lang, "consider_target",
                                       min=healthy_weight_range['min'],
                                       max=healthy_weight_range['max'])
            goal_msg = get_translation(lang, "set_goal")
            recommendation = f"{bmi_msg} {target_msg} {goal_msg}"
        else:  # obese
            bmi_msg = get_translation(lang, "significantly_above", bmi=current_bmi)
            target_msg = get_translation(lang, "consider_target",
                                       min=healthy_weight_range['min'],
                                       max=healthy_weight_range['max'])
            consult_msg = get_translation(lang, "consult_before_loss")
            recommendation = f"{bmi_msg} {target_msg} {consult_msg}"

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


# ===== Client Management Endpoints (Personal Trainers) =====

@router.get("/clients", response_model=List[ClientListResponse])
async def get_my_clients(
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """Get all clients assigned to the current Personal Trainer"""
    clients = db.query(User).filter(
        User.personal_trainer_id == current_user.id,
        User.role == UserRole.CLIENT
    ).all()

    return clients


@router.get("/clients/{client_id}", response_model=UserResponse)
async def get_client_detail(
    client_id: str,
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific client"""
    from app.core.permissions import check_client_belongs_to_trainer

    client = db.query(User).filter(User.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    check_client_belongs_to_trainer(client, current_user)

    response = UserResponse.from_orm(client)
    response.bmi = calculate_bmi(client.weight, client.height)
    response.age = calculate_age(client.date_of_birth)
    response.personal_trainer_name = current_user.name

    return response


@router.get("/available-clients", response_model=List[ClientListResponse])
async def get_available_clients(
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """Get all clients without a personal trainer"""
    available_clients = db.query(User).filter(
        User.role == UserRole.CLIENT,
        User.personal_trainer_id.is_(None)
    ).all()

    return available_clients


@router.post("/clients/{client_id}/assign")
async def assign_client_to_trainer(
    client_id: str,
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """Assign a client to the current personal trainer"""
    client = db.query(User).filter(
        User.id == client_id,
        User.role == UserRole.CLIENT
    ).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    if client.personal_trainer_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client already has a personal trainer"
        )

    client.personal_trainer_id = current_user.id
    db.commit()

    return {"message": "Client assigned successfully"}


@router.delete("/clients/{client_id}/unassign")
async def unassign_client_from_trainer(
    client_id: str,
    current_user: User = Depends(require_personal_trainer),
    db: Session = Depends(get_db)
):
    """Remove a client from the current personal trainer"""
    from app.core.permissions import check_client_belongs_to_trainer

    client = db.query(User).filter(User.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    check_client_belongs_to_trainer(client, current_user)

    client.personal_trainer_id = None
    db.commit()

    return {"message": "Client unassigned successfully"}
