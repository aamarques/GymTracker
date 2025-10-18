# Health Metrics & Weight Goals Feature

## Overview

The Gym Workout Tracker now includes a comprehensive health metrics analysis feature that helps users set weight goals and receive personalized recommendations on how to achieve them.

## What's New

### 1. Desired Weight Field
Users can now set a target weight goal in their profile.

**API Endpoint:** `PUT /api/users/profile`

**Request:**
```json
{
  "desired_weight": 75.0
}
```

### 2. Health Metrics Analysis
Get comprehensive health analysis including BMI, weight goals, timeline, and recommendations.

**API Endpoint:** `GET /api/users/health-metrics`

**Response includes:**
- Current BMI and category (Underweight/Normal/Overweight/Obese)
- Target BMI (if goal set)
- Healthy weight range for your height
- Estimated weeks to reach goal
- Estimated achievement date
- Weekly weight change needed
- Daily calorie adjustment needed
- Personalized recommendations

## Features

### BMI Calculation & Categories

The system automatically calculates your BMI and categorizes it:

| BMI Range | Category | Health Status |
|-----------|----------|---------------|
| < 18.5 | Underweight | `underweight` |
| 18.5 - 24.9 | Normal weight | `healthy` |
| 25.0 - 29.9 | Overweight | `overweight` |
| ≥ 30.0 | Obese | `obese` |

### Healthy Weight Range

Based on your height, the system calculates your healthy weight range (BMI 18.5-24.9):

**Example:** For someone 180cm tall:
- Minimum healthy weight: 60.0 kg
- Maximum healthy weight: 80.7 kg

### Weight Goal Timeline

When you set a desired weight, the system calculates:

#### Safe Weight Change Rate
- **0.5 kg per week** (conservative and sustainable)
- Based on scientific recommendations for healthy weight loss/gain

#### Timeline Calculation
```
Estimated Weeks = |Weight Difference| / 0.5 kg per week
Estimated Date = Current Date + Estimated Weeks
```

**Example:**
- Current weight: 77 kg
- Desired weight: 75 kg
- Weight difference: -2 kg
- Estimated weeks: 4 weeks
- Estimated date: ~1 month from now

### Calorie Recommendations

The system calculates daily calorie adjustments needed:

#### Formula
```
1 kg of fat ≈ 7,700 calories

Total calories needed = Weight Difference × 7,700
Days needed = Estimated Weeks × 7
Daily adjustment = Total Calories / Days Needed
```

**For Weight Loss:**
- Negative calorie adjustment (deficit)
- Example: -550 calories/day for 2kg loss in 4 weeks

**For Weight Gain:**
- Positive calorie adjustment (surplus)
- Example: +550 calories/day for 2kg gain in 4 weeks

### Personalized Recommendations

The system provides context-aware recommendations based on:

1. **Current health status** (BMI category)
2. **Weight goal** (if set)
3. **Weight difference** (amount to lose/gain)

#### Example Recommendations

**Scenario 1: Weight Loss Goal**
```
"To reach your goal of 75.0kg, you need to lose 2.0kg.
At a healthy rate of 0.5kg per week, this will take approximately 4 weeks.
Aim for a calorie deficit of ~550 calories per day through diet and exercise."
```

**Scenario 2: Weight Gain Goal**
```
"To reach your goal of 80.0kg, you need to gain 3.0kg.
At a healthy rate of 0.5kg per week, this will take approximately 6 weeks.
Aim for a calorie surplus of ~550 calories per day through
increased food intake and strength training."
```

**Scenario 3: No Goal Set (Healthy BMI)**
```
"Your BMI is 23.1, which is in the healthy range.
Set a desired weight goal to get a personalized timeline and recommendations."
```

**Scenario 4: No Goal Set (Overweight)**
```
"Your BMI is 27.5, which is above the healthy range.
Consider setting a target weight between 60.2kg and 80.7kg.
Set a desired weight goal to get a personalized timeline."
```

## API Usage

### Set Your Weight Goal

**Request:**
```bash
curl -X PUT http://localhost:8000/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"desired_weight": 75.0}'
```

### Get Health Metrics

**Request:**
```bash
curl http://localhost:8000/api/users/health-metrics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "current_weight": 77.0,
  "desired_weight": 75.0,
  "weight_difference": -2.0,
  "current_bmi": 23.7,
  "bmi_category": "Normal weight",
  "target_bmi": 23.1,
  "healthy_weight_range": {
    "min": 60.0,
    "max": 80.7
  },
  "estimated_weeks": 4,
  "estimated_date": "2025-11-09",
  "weekly_change_needed": -0.5,
  "daily_calorie_adjustment": -550,
  "recommendation": "To reach your goal of 75.0kg...",
  "health_status": "healthy"
}
```

## Database Changes

### New Column in Users Table

```sql
ALTER TABLE users ADD COLUMN desired_weight FLOAT NULL;
```

**Migration file:** `backend/alembic/versions/001_add_desired_weight.py`

To apply the migration:
```bash
# If using Podman
podman exec gym_backend alembic upgrade head

# If using Docker Compose
docker-compose exec backend alembic upgrade head
```

## Implementation Details

### Backend Files Modified

1. **`backend/app/models/models.py`**
   - Added `desired_weight` column to User model

2. **`backend/app/schemas/schemas.py`**
   - Added `desired_weight` to `UserBase` schema
   - Added `desired_weight` to `UserUpdate` schema
   - Created new `HealthMetrics` schema

3. **`backend/app/api/users.py`**
   - Added health metrics calculation logic
   - Created `/api/users/health-metrics` endpoint
   - Updated profile update to handle `desired_weight`

### Calculation Logic

The health metrics endpoint (`users.py:112-238`) implements:

1. **BMI Calculation:** `weight / (height_m²)`
2. **BMI Categorization:** Based on WHO standards
3. **Healthy Weight Range:** Using BMI 18.5-24.9 boundaries
4. **Timeline Estimation:** Safe 0.5 kg/week rate
5. **Calorie Calculation:** 7,700 calories per kg of fat
6. **Recommendation Generation:** Context-aware messaging

## Use Cases

### 1. Weight Loss Journey
**User Story:** Sarah wants to lose 5kg

```
Current: 70kg, Height: 165cm
Desired: 65kg
Timeline: 10 weeks (~2.5 months)
Daily deficit: -550 calories
Recommendation: Calorie deficit through diet + exercise
```

### 2. Muscle Gain
**User Story:** Mike wants to gain 3kg of muscle

```
Current: 75kg, Height: 180cm
Desired: 78kg
Timeline: 6 weeks
Daily surplus: +550 calories
Recommendation: Calorie surplus + strength training
```

### 3. Maintenance
**User Story:** Lisa is at healthy weight

```
Current: 60kg, Height: 165cm
BMI: 22.0 (healthy)
Recommendation: Maintain through balanced diet
```

## Scientific Basis

### Safe Weight Change Rates
- **Weight Loss:** 0.5-1 kg per week (we use 0.5 kg for safety)
- **Weight Gain:** 0.25-0.5 kg per week
- Source: CDC, WHO guidelines

### Calorie Calculations
- **1 kg fat ≈ 7,700 calories**
- **Daily deficit/surplus:** Spread evenly over timeline
- Accounts for both fat loss/gain scenarios

### BMI Standards
- Based on WHO (World Health Organization) classifications
- Widely accepted medical standard
- Accounts for height-to-weight ratio

## Limitations & Disclaimers

⚠️ **Important Notes:**

1. **BMI limitations:**
   - Doesn't distinguish muscle vs. fat
   - Less accurate for athletes with high muscle mass
   - May not apply to all ethnicities

2. **Individual variation:**
   - Actual results may vary based on metabolism
   - Activity level affects calorie needs
   - Consult healthcare professional for personalized advice

3. **Medical conditions:**
   - Always consult doctor before starting weight loss/gain program
   - Certain conditions may require different approaches

## Future Enhancements

Potential improvements:

- [ ] Body fat percentage tracking
- [ ] Muscle mass vs fat mass analysis
- [ ] Integration with workout calorie burn
- [ ] Weekly weight tracking and progress charts
- [ ] Adaptive recommendations based on actual progress
- [ ] Macronutrient (protein/carbs/fat) recommendations
- [ ] Activity level consideration in calorie calculations
- [ ] Age and gender-specific BMR calculations

## Testing

### Manual Testing

1. **Set a weight goal:**
```bash
curl -X PUT http://localhost:8000/api/users/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"desired_weight": 75.0}'
```

2. **Get health metrics:**
```bash
curl http://localhost:8000/api/users/health-metrics \
  -H "Authorization: Bearer $TOKEN" | jq
```

3. **Verify calculations:**
   - Check BMI matches manual calculation
   - Verify timeline is realistic (weeks = kg difference / 0.5)
   - Confirm calorie adjustment is reasonable

### Test Scenarios

| Current | Goal | Expected Weeks | Expected Daily Cal |
|---------|------|----------------|-------------------|
| 77 kg | 75 kg | 4 weeks | -550 cal |
| 70 kg | 75 kg | 10 weeks | +550 cal |
| 80 kg | 75 kg | 10 weeks | -550 cal |
| 75 kg | 75 kg | 0 | 0 |

## Support

For questions or issues:
- Check the [API Documentation](API.md)
- Review the [Development Guide](DEVELOPMENT.md)
- Test the endpoint at http://localhost:8000/docs

## Changelog

**Version 1.2.0** - 2025-10-12
- Added `desired_weight` field to User model
- Created health metrics analysis endpoint
- Implemented timeline and calorie calculations
- Added personalized recommendations
- Created comprehensive documentation

---

**Happy training and healthy goal setting! 🎯💪**
