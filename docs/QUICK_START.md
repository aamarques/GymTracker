# Quick Start Guide

## Launch the Application

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Access Points

- **Main App**: http://localhost
- **API Docs**: http://localhost/docs
- **Health Check**: http://localhost/health

## First Time Setup

1. Open http://localhost
2. Click "Register" and create an account
3. Login with your credentials
4. You're ready to go!

## Common Tasks

### Add an Exercise
1. Go to "Exercises" tab
2. Click "Add Exercise"
3. Upload an image (optional)
4. Fill in details
5. Click "Add Exercise"

### Create a Workout Plan
1. Go to "Workout Plans" tab
2. Click "Create Plan"
3. Name your plan
4. (Add exercises via API or future UI enhancement)
5. Click "Create Plan"

### Start a Workout
1. Go to "Active Workout" tab
2. Click "Start Workout"
3. Select exercise and log sets/reps/weight
4. Click "Log Exercise" after each set
5. Click "End Workout" when done

### Log Cardio
1. Go to "Cardio" tab
2. Click "Log Cardio"
3. Select activity type
4. Enter duration, distance, calories
5. Click "Log Session"

### Update Profile
1. Go to "Profile" tab
2. Update your weight, height, phone
3. Click "Update Profile"
4. BMI recalculates automatically

## Troubleshooting

**Can't access the app?**
- Make sure Docker is running
- Check if ports 80 and 5432 are available
- Run `docker-compose ps` to see container status

**Backend errors?**
- Check logs: `docker-compose logs backend`
- Restart: `docker-compose restart backend`

**Database issues?**
- Check logs: `docker-compose logs db`
- Restart: `docker-compose restart db`

**Need to reset everything?**
```bash
docker-compose down -v
docker-compose up -d
```

## Development

**Hot reload is enabled!**
- Backend: Edit files in `backend/app/`, changes apply automatically
- Frontend: Edit files in `frontend/`, refresh browser

**Access containers:**
```bash
# Backend
docker-compose exec backend bash

# Database
docker-compose exec db psql -U gymuser -d gymtracker
```

## Production Deployment

1. Update `.env` with secure values:
   ```bash
   SECRET_KEY=<generate with: openssl rand -hex 32>
   POSTGRES_PASSWORD=<strong password>
   DEBUG=False
   ```

2. Configure HTTPS in `nginx/nginx.conf`

3. Set up backups for PostgreSQL

4. Deploy!

## Need Help?

- Check README.md for detailed documentation
- View API docs at http://localhost/docs
- Check PROJECT_SUMMARY.md for technical details
