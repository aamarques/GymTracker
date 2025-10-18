# Gym Workout Tracker - Deployment Guide

This guide covers deploying the Gym Workout Tracker application to production environments.

## Table of Contents
1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Podman Deployment](#podman-deployment)
5. [Production Best Practices](#production-best-practices)
6. [SSL/HTTPS Setup](#sslhttps-setup)
7. [Database Backups](#database-backups)
8. [Monitoring & Logging](#monitoring--logging)
9. [Scaling](#scaling)

---

## Pre-deployment Checklist

Before deploying to production, ensure you have:

- [ ] Domain name configured with DNS pointing to your server
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Strong passwords generated for all services
- [ ] Secure secret key generated for JWT tokens
- [ ] Firewall rules configured
- [ ] Backup strategy planned
- [ ] Monitoring solution ready
- [ ] Log aggregation configured

---

## Environment Configuration

### 1. Generate Secure Credentials

```bash
# Generate a secure SECRET_KEY (32 bytes hex)
openssl rand -hex 32

# Generate a secure database password
openssl rand -base64 32
```

### 2. Create Production .env File

```bash
cp .env.example .env.production
```

Edit `.env.production`:

```bash
# Database Configuration
POSTGRES_USER=gymuser
POSTGRES_PASSWORD=<strong-password-here>
POSTGRES_DB=gymtracker
DATABASE_URL=postgresql://gymuser:<strong-password>@db:5432/gymtracker

# JWT Configuration
SECRET_KEY=<generated-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# File Upload Configuration
MAX_UPLOAD_SIZE=5242880
UPLOAD_DIR=/app/uploads

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Docker Deployment

### Option 1: Docker Compose (Standard)

#### 1. Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin
```

#### 2. Deploy Application

```bash
# Clone repository
git clone <your-repo-url>
cd Gym

# Copy and configure environment
cp .env.example .env
# Edit .env with production values

# Build and start services
docker-compose -f docker-compose.yml up -d --build

# Check status
docker-compose ps
docker-compose logs -f
```

#### 3. Configure Nginx for Production

Update `nginx/nginx.conf` for production:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        client_max_body_size 5M;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend:8000/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Auth endpoints with stricter rate limiting
        location /api/auth/ {
            limit_req zone=auth_limit burst=3 nodelay;
            proxy_pass http://backend:8000/api/auth/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://backend:8000/health;
            access_log off;
        }

        # API Docs
        location /docs {
            proxy_pass http://backend:8000/docs;
        }

        # Uploaded files
        location /uploads/ {
            alias /usr/share/nginx/html/uploads/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

---

## Podman Deployment

### For WSL2 or Rootless Environments

#### 1. Install Podman

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y podman

# Verify installation
podman --version
```

#### 2. Deploy with Podman Script

The provided `start-containers.sh` script is optimized for Podman:

```bash
# Make script executable
chmod +x start-containers.sh

# Edit script for production (if needed)
nano start-containers.sh

# Start containers
./start-containers.sh
```

#### 3. Create Systemd Services (Optional)

For automatic startup on boot:

**Create `/etc/systemd/system/gym-postgres.service`:**
```ini
[Unit]
Description=Gym Tracker PostgreSQL
After=network.target

[Service]
Type=forking
User=youruser
ExecStart=/usr/bin/podman start gym_postgres
ExecStop=/usr/bin/podman stop gym_postgres
Restart=always

[Install]
WantedBy=multi-user.target
```

**Create similar services for backend and nginx:**
```bash
sudo cp gym-postgres.service gym-backend.service
sudo cp gym-postgres.service gym-nginx.service

# Edit descriptions and container names
sudo nano gym-backend.service
sudo nano gym-nginx.service

# Enable services
sudo systemctl daemon-reload
sudo systemctl enable gym-postgres gym-backend gym-nginx
sudo systemctl start gym-postgres gym-backend gym-nginx
```

---

## Production Best Practices

### 1. Database Configuration

**Optimize PostgreSQL for Production:**

Create `postgresql.conf` overrides:
```ini
# Performance
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB

# Connection pooling
max_connections = 100

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'mod'
log_duration = on
```

### 2. Backend Optimization

**Update Dockerfile for production:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /app/uploads/exercises

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Use Gunicorn for production
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

Add Gunicorn to `requirements.txt`:
```
gunicorn==21.2.0
```

### 3. Environment Variables Security

Never commit `.env` files. Use Docker secrets or environment variable management:

```bash
# Create secrets
echo "your-secret-key" | docker secret create jwt_secret -
echo "db-password" | docker secret create db_password -

# Use in docker-compose.yml
services:
  backend:
    secrets:
      - jwt_secret
      - db_password
    environment:
      SECRET_KEY_FILE: /run/secrets/jwt_secret
      DB_PASSWORD_FILE: /run/secrets/db_password
```

---

## SSL/HTTPS Setup

### Option 1: Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

### Option 2: Manual SSL Certificate

```bash
# Place certificates in nginx/ssl/
mkdir -p nginx/ssl
cp /path/to/fullchain.pem nginx/ssl/
cp /path/to/privkey.pem nginx/ssl/

# Update docker-compose.yml to mount certificates
volumes:
  - ./nginx/ssl:/etc/nginx/ssl:ro
```

---

## Database Backups

### Automated Backup Script

Create `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/gym-tracker"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/gym_backup_$TIMESTAMP.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Docker Compose
docker-compose exec -T db pg_dump -U gymuser gymtracker > $BACKUP_FILE

# OR Podman
# podman exec gym_postgres pg_dump -U gymuser gymtracker > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Delete backups older than 30 days
find $BACKUP_DIR -type f -name "*.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### Cron Job for Daily Backups

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/gym-backup.log 2>&1
```

### Restore from Backup

```bash
# Decompress backup
gunzip gym_backup_20251012_020000.sql.gz

# Docker Compose
cat gym_backup_20251012_020000.sql | docker-compose exec -T db psql -U gymuser -d gymtracker

# OR Podman
cat gym_backup_20251012_020000.sql | podman exec -i gym_postgres psql -U gymuser -d gymtracker
```

---

## Monitoring & Logging

### 1. Application Logs

**View logs:**
```bash
# Docker Compose
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f db

# Podman
podman logs -f gym_backend
podman logs -f gym_postgres
```

### 2. Log Aggregation

Configure log rotation in `/etc/logrotate.d/gym-tracker`:

```
/var/log/gym-tracker/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker-compose restart nginx
    endscript
}
```

### 3. Health Monitoring

Create `healthcheck.sh`:

```bash
#!/bin/bash

# Check API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "API is healthy"
else
    echo "API is down! Restarting..."
    docker-compose restart backend
    # Send alert email/notification
fi
```

Add to crontab for every 5 minutes:
```bash
*/5 * * * * /path/to/healthcheck.sh
```

### 4. Prometheus & Grafana (Advanced)

Install monitoring stack:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus_data:
  grafana_data:
```

---

## Scaling

### Horizontal Scaling

**Scale backend workers:**

```bash
# Docker Compose
docker-compose up -d --scale backend=3

# Update nginx upstream
upstream backend {
    server backend:8000;
    server backend:8001;
    server backend:8002;
}
```

### Load Balancer Setup

Use Nginx as load balancer:

```nginx
upstream backend_servers {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

location /api/ {
    proxy_pass http://backend_servers;
}
```

### Database Replication

Set up PostgreSQL read replicas for scaling reads:

```yaml
services:
  db-primary:
    image: postgres:15-alpine
    environment:
      - POSTGRES_REPLICATION_MODE=master

  db-replica:
    image: postgres:15-alpine
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_SERVICE_HOST=db-primary
```

---

## Performance Optimization

### 1. Enable Redis Caching

Add Redis to `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

### 2. CDN Integration

Use CDN for static assets:
- Upload images to AWS S3, Cloudflare, or similar
- Update frontend to use CDN URLs
- Configure CORS headers

### 3. Database Connection Pooling

Update backend to use connection pooling:

```python
# backend/app/db/database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# Ubuntu/Debian with ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2ban Setup

```bash
# Install fail2ban
sudo apt install fail2ban

# Configure jail
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 3600
```

### 3. Regular Updates

```bash
# Schedule automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## Troubleshooting Production Issues

### High CPU Usage
```bash
# Check container stats
docker stats

# Identify slow queries
docker-compose exec db psql -U gymuser -d gymtracker -c \
  "SELECT pid, now() - query_start as duration, query
   FROM pg_stat_activity
   WHERE state = 'active'
   ORDER BY duration DESC;"
```

### Out of Memory
```bash
# Check memory usage
docker-compose exec backend ps aux --sort=-%mem | head

# Increase container limits in docker-compose.yml
services:
  backend:
    mem_limit: 1g
    mem_reservation: 512m
```

### Database Connection Pool Exhausted
```bash
# Check active connections
docker-compose exec db psql -U gymuser -d gymtracker -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Increase max_connections in postgresql.conf
```

---

## Post-Deployment Checklist

- [ ] Application accessible via HTTPS
- [ ] SSL certificate valid
- [ ] All endpoints working correctly
- [ ] Database backups automated
- [ ] Monitoring alerts configured
- [ ] Log rotation working
- [ ] Firewall rules active
- [ ] Health checks passing
- [ ] Rate limiting tested
- [ ] Performance acceptable
- [ ] Security scan completed
- [ ] Documentation updated

---

## Support

For deployment issues:
1. Check application logs
2. Review this deployment guide
3. Consult the troubleshooting section
4. Check system resources (CPU, memory, disk)
5. Verify network connectivity and DNS
