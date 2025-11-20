# Gym Workout Tracker - API Documentation

## Base URL
- Local: `http://localhost:8000`
- API Prefix: `/api`

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Register User
**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe",
  "date_of_birth": "1990-01-15T00:00:00",
  "weight": 75.5,
  "height": 180.0,
  "phone": "+1234567890"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "date_of_birth": "1990-01-15T00:00:00",
  "weight": 75.5,
  "height": 180.0,
  "phone": "+1234567890",
  "created_at": "2025-10-12T20:00:00Z",
  "bmi": 23.3,
  "age": 35
}
```

**Validation Rules:**
- `email`: Valid email format, unique
- `password`: Minimum 8 characters
- `name`: Required
- `date_of_birth`: ISO 8601 datetime format
- `weight`: Positive float (kg)
- `height`: Positive float (cm)
- `phone`: Optional

---

### Login User
**POST** `/api/auth/login`

Login with email and password to receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Missing fields

---

### Get Current User
**GET** `/api/auth/me`

Get authenticated user's information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "date_of_birth": "1990-01-15T00:00:00",
  "weight": 75.5,
  "height": 180.0,
  "phone": "+1234567890",
  "created_at": "2025-10-12T20:00:00Z",
  "bmi": 23.3,
  "age": 35
}
```

---

## User Profile

### Get User Profile
**GET** `/api/users/profile`

Get current user's profile with detailed information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "date_of_birth": "1990-01-15T00:00:00",
  "weight": 75.5,
  "height": 180.0,
  "phone": "+1234567890",
  "created_at": "2025-10-12T20:00:00Z",
  "bmi": 23.3,
  "age": 35
}
```

---

### Update User Profile
**PUT** `/api/users/profile`

Update user profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "John Updated",
  "weight": 77.0,
  "height": 181.0,
  "phone": "+9876543210"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Updated",
  "weight": 77.0,
  "height": 181.0,
  "phone": "+9876543210",
  "bmi": 23.5,
  "age": 35
}
```

---

### Get Dashboard Statistics
**GET** `/api/users/dashboard`

Get dashboard statistics for the current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "total_workouts": 25,
  "total_cardio_sessions": 10,
  "current_bmi": 23.3,
  "current_weight": 75.5,
  "workout_streak": 5,
  "last_workout": "2025-10-11T18:30:00Z",
  "total_exercises": 15,
  "total_workout_plans": 3
}
```

---

## Exercises

### List All Exercises
**GET** `/api/exercises`

Get list of all exercises.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `muscle_group` (optional): Filter by muscle group (chest, back, legs, shoulders, arms, core, full_body)
- `search` (optional): Search by name or description

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-string",
    "name": "Bench Press",
    "description": "Compound chest exercise",
    "muscle_group": "chest",
    "equipment": "barbell",
    "image_url": "/uploads/exercises/bench-press.jpg",
    "user_id": "uuid-string",
    "created_at": "2025-10-12T20:00:00Z"
  }
]
```

---

### Create Exercise
**POST** `/api/exercises`

Create a new exercise with optional image upload.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `name`: string (required)
- `description`: string (required)
- `muscle_group`: string (required) - one of: chest, back, legs, shoulders, arms, core, full_body
- `equipment`: string (optional)
- `image`: file (optional) - PNG, JPG, JPEG, GIF (max 5MB)

**Response:** `201 Created`
```json
{
  "id": "uuid-string",
  "name": "Bench Press",
  "description": "Compound chest exercise",
  "muscle_group": "chest",
  "equipment": "barbell",
  "image_url": "/uploads/exercises/bench-press.jpg",
  "user_id": "uuid-string",
  "created_at": "2025-10-12T20:00:00Z"
}
```

---

### Get Exercise Details
**GET** `/api/exercises/{exercise_id}`

Get detailed information about a specific exercise.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid-string",
  "name": "Bench Press",
  "description": "Compound chest exercise",
  "muscle_group": "chest",
  "equipment": "barbell",
  "image_url": "/uploads/exercises/bench-press.jpg",
  "user_id": "uuid-string",
  "created_at": "2025-10-12T20:00:00Z"
}
```

---

### Update Exercise
**PUT** `/api/exercises/{exercise_id}`

Update an existing exercise.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:** (same as Create Exercise)

**Response:** `200 OK`

---

### Delete Exercise
**DELETE** `/api/exercises/{exercise_id}`

Delete an exercise (only if created by current user).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `204 No Content`

---

## Workout Plans

### List Workout Plans
**GET** `/api/workout-plans`

Get all workout plans for the current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-string",
    "name": "Push Day",
    "description": "Chest, shoulders, triceps workout",
    "user_id": "uuid-string",
    "created_at": "2025-10-12T20:00:00Z",
    "exercises": [
      {
        "exercise_id": "uuid-string",
        "exercise_name": "Bench Press",
        "sets": 4,
        "reps": 8,
        "weight": 80.0,
        "rest_time": 120,
        "order": 1
      }
    ]
  }
]
```

---

### Create Workout Plan
**POST** `/api/workout-plans`

Create a new workout plan with exercises.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Push Day",
  "description": "Chest, shoulders, triceps workout",
  "exercises": [
    {
      "exercise_id": "uuid-string",
      "sets": 4,
      "reps": 8,
      "weight": 80.0,
      "rest_time": 120,
      "order": 1
    },
    {
      "exercise_id": "uuid-string-2",
      "sets": 3,
      "reps": 12,
      "weight": 15.0,
      "rest_time": 90,
      "order": 2
    }
  ]
}
```

**Response:** `201 Created`

---

### Get Workout Plan
**GET** `/api/workout-plans/{plan_id}`

Get detailed information about a workout plan.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`

---

### Update Workout Plan
**PUT** `/api/workout-plans/{plan_id}`

Update a workout plan.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:** (same as Create Workout Plan)

**Response:** `200 OK`

---

### Delete Workout Plan
**DELETE** `/api/workout-plans/{plan_id}`

Delete a workout plan.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `204 No Content`

---

## Workout Sessions

### List Workout Sessions
**GET** `/api/workout-sessions`

Get all workout sessions for the current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional): Number of sessions to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-string",
    "user_id": "uuid-string",
    "workout_plan_id": "uuid-string",
    "start_time": "2025-10-12T18:00:00Z",
    "end_time": "2025-10-12T19:30:00Z",
    "duration": 5400,
    "notes": "Great workout, felt strong",
    "exercises": [
      {
        "exercise_id": "uuid-string",
        "exercise_name": "Bench Press",
        "sets_completed": 4,
        "reps_completed": [8, 8, 7, 6],
        "weight_used": 80.0
      }
    ]
  }
]
```

---

### Start Workout Session
**POST** `/api/workout-sessions`

Start a new workout session.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "workout_plan_id": "uuid-string",
  "notes": "Optional notes"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid-string",
  "user_id": "uuid-string",
  "workout_plan_id": "uuid-string",
  "start_time": "2025-10-12T18:00:00Z",
  "end_time": null,
  "duration": null,
  "notes": "Optional notes",
  "status": "active"
}
```

---

### Get Active Workout Session
**GET** `/api/workout-sessions/active`

Get the currently active workout session.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK` or `404 Not Found`

---

### End Workout Session
**POST** `/api/workout-sessions/{session_id}/end`

End an active workout session.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "notes": "Updated notes"
}
```

**Response:** `200 OK`

---

### Log Exercise in Session
**POST** `/api/workout-sessions/{session_id}/exercises`

Log an exercise performed during a workout session.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "exercise_id": "uuid-string",
  "sets_completed": 4,
  "reps_completed": [8, 8, 7, 6],
  "weight_used": 80.0,
  "notes": "Felt good"
}
```

**Response:** `201 Created`

---

## Cardio Sessions

### List Cardio Sessions
**GET** `/api/cardio`

Get all cardio sessions for the current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-string",
    "user_id": "uuid-string",
    "activity_type": "running",
    "duration": 3600,
    "distance": 10.0,
    "calories": 600,
    "location": "Park",
    "notes": "Morning run",
    "date": "2025-10-12T07:00:00Z",
    "created_at": "2025-10-12T08:00:00Z"
  }
]
```

---

### Log Cardio Session
**POST** `/api/cardio`

Log a new cardio session.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "activity_type": "running",
  "duration": 3600,
  "distance": 10.0,
  "calories": 600,
  "location": "Park",
  "notes": "Morning run",
  "date": "2025-10-12T07:00:00Z"
}
```

**Activity Types:**
- `running`
- `cycling`
- `swimming`
- `walking`
- `rowing`
- `elliptical`
- `other`

**Response:** `201 Created`

---

### Get Cardio Session
**GET** `/api/cardio/{cardio_id}`

Get details of a specific cardio session.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`

---

### Update Cardio Session
**PUT** `/api/cardio/{cardio_id}`

Update a cardio session.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:** (same as Log Cardio Session)

**Response:** `200 OK`

---

### Delete Cardio Session
**DELETE** `/api/cardio/{cardio_id}`

Delete a cardio session.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `204 No Content`

---

## Metrics & Progress Tracking

### Get My Metrics (Client)
**GET** `/api/metrics/my-metrics`

Get current user's comprehensive metrics.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid-string",
  "client_id": "uuid-string",
  "personal_trainer_id": "uuid-string",
  "total_workouts_completed": 25,
  "total_cardio_sessions": 10,
  "total_training_hours": 42.5,
  "total_training_days": 30,
  "total_sets_completed": 375,
  "total_reps_completed": 4500,
  "initial_weight": 85.0,
  "current_weight": 80.5,
  "lowest_weight": 79.8,
  "highest_weight": 85.5,
  "total_weight_changes": 8,
  "average_days_between_weight_changes": 7.5,
  "times_workouts_reset": 1,
  "last_reset_date": "2025-01-15T10:30:00Z",
  "workouts_before_last_reset": 15,
  "consistency_percentage": 75.5,
  "average_workout_duration_minutes": 65.2,
  "client_since": "2024-10-01T00:00:00Z",
  "last_activity_date": "2025-01-20T18:00:00Z"
}
```

---

### Get My Progress (Client)
**GET** `/api/metrics/my-progress`

Get detailed progress analysis for current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "total_workouts": 25,
  "total_training_hours": 42.5,
  "total_training_days": 30,
  "consistency_percentage": 75.5,
  "average_workout_duration": 65.2,
  "weight_change_kg": -4.5,
  "weight_change_percentage": -5.3,
  "recent_workout_trend": "improving",
  "recent_workouts_30_days": 12,
  "previous_workouts_30_days": 8,
  "total_sets": 375,
  "total_reps": 4500,
  "times_reset": 1,
  "days_since_start": 112
}
```

---

### Get Weight History (Client)
**GET** `/api/metrics/weight-history`

Get weight history for current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 50)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-string",
    "user_id": "uuid-string",
    "weight": 80.5,
    "previous_weight": 81.2,
    "days_since_last_change": 7,
    "recorded_at": "2025-01-20T10:00:00Z",
    "notes": null
  }
]
```

---

### Reset Workout Count (Client)
**POST** `/api/metrics/workouts/reset`

Allow a client to reset their workout count. Metrics are preserved for the Personal Trainer.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "message": "Workout count reset successfully",
  "workouts_archived": 25,
  "reset_count": 2,
  "metrics_preserved": true
}
```

---

### Get All Clients Metrics (Personal Trainer)
**GET** `/api/metrics/clients`

Get metrics for all clients of the current Personal Trainer.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK` - Array of ClientMetricsResponse objects

---

### Get Client Metrics Detail (Personal Trainer)
**GET** `/api/metrics/clients/{client_id}`

Get detailed metrics for a specific client.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid-string",
  "client_id": "uuid-string",
  "client_name": "João Silva",
  "client_email": "joao@email.com",
  "personal_trainer_id": "uuid-string",
  "total_workouts_completed": 25,
  "total_cardio_sessions": 10,
  "weight_history": [
    {
      "id": "uuid-string",
      "weight": 80.5,
      "previous_weight": 81.2,
      "days_since_last_change": 7,
      "recorded_at": "2025-01-20T10:00:00Z"
    }
  ]
}
```

---

### Get Client Progress (Personal Trainer)
**GET** `/api/metrics/clients/{client_id}/progress`

Get detailed progress analysis for a specific client.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK` - Progress object with client details

---

### Get Client Weight History (Personal Trainer)
**GET** `/api/metrics/clients/{client_id}/weight-history`

Get weight history for a specific client.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 50)

**Response:** `200 OK` - Array of WeightHistoryResponse objects

---

### Get Dashboard Summary (Personal Trainer)
**GET** `/api/metrics/dashboard-summary`

Get summary statistics for Personal Trainer dashboard.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "total_clients": 15,
  "total_workouts_all_clients": 450,
  "total_training_hours_all_clients": 675.5,
  "average_client_consistency": 68.5,
  "most_active_client": {
    "name": "João Silva",
    "workouts": 45
  },
  "most_consistent_client": {
    "name": "Maria Santos",
    "consistency": 85.5
  }
}
```

---

## Health Check

### API Health Check
**GET** `/health`

Check if the API is running.

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **Authentication endpoints**: 5 requests per minute
- **Read endpoints**: 100 requests per minute
- **Write endpoints**: 30 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1697123456
```

---

## Interactive API Documentation

For interactive API testing and exploration, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Try-it-out functionality
- Schema documentation
- Example requests/responses
- Authentication testing
