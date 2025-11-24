# 🚀 GymTracker - Migration Guide

Complete guide to migrate GymTracker from one server to another.

---

## 📋 Overview

This migration script handles:
- ✅ Database backup and restore
- ✅ Exercise images export/import
- ✅ Configuration files
- ✅ Automatic cleanup and setup
- ✅ Works with Docker and Podman

---

## 🎯 Quick Migration (2 Commands!)

### **On OLD Server:**
```bash
cd ~/Gym/GymTracker  # or wherever GymTracker is
./migrate-to-new-server.sh backup
```

### **On NEW Server:**
```bash
# Transfer the backup file
scp old-server:~/Gym/GymTracker/gymtracker_migration_*.tar.gz /tmp/

# Extract and restore
cd /opt/GymTracker
tar -xzf /tmp/gymtracker_migration_*.tar.gz
cd gymtracker_migration_*
sudo ../migrate-to-new-server.sh restore
```

**Done! 🎉**

---

## 📖 Detailed Steps

### **Step 1: Backup on OLD Server**

```bash
# Navigate to GymTracker directory
cd ~/Gym/GymTracker

# Run backup
./migrate-to-new-server.sh backup

# This creates:
#   gymtracker_migration_YYYYMMDD_HHMMSS.tar.gz
```

**What gets backed up:**
- 💾 Complete database dump (compressed)
- 🖼️ All exercise images
- ⚙️ Configuration files
- 📋 Migration info

**Output:**
```
✅ BACKUP COMPLETE!
Migration package: gymtracker_migration_20250120_143022.tar.gz
Size: 2.1M
```

---

### **Step 2: Transfer to NEW Server**

```bash
# Method 1: SCP
scp gymtracker_migration_*.tar.gz user@newserver:/tmp/

# Method 2: USB/Network drive
# Just copy the .tar.gz file

# Method 3: Download and upload
# Download from old server, upload to new server
```

---

### **Step 3: Restore on NEW Server**

```bash
# Navigate to GymTracker installation directory
cd /opt/GymTracker

# Extract backup
tar -xzf /tmp/gymtracker_migration_*.tar.gz

# Enter backup directory
cd gymtracker_migration_*

# Run restore (needs sudo)
sudo ../migrate-to-new-server.sh restore
```

**The script automatically:**
1. ✅ Stops existing containers
2. ✅ Removes old volumes and data
3. ✅ Starts PostgreSQL alone
4. ✅ Restores database
5. ✅ Restores images
6. ✅ Starts full application

**Output:**
```
✅ MIGRATION COMPLETE!

Application is running at:
  - Main App:  http://192.168.1.100
  - API Docs:  http://192.168.1.100/docs

Database restored with:
  - 4 users
  - 101 exercises
  - 101 images
```

---

## 🔧 Advanced Usage

### **Backup Only Database (No Images)**

```bash
# Manual database backup
docker exec gym_postgres pg_dump -U gymuser gymtracker | gzip > backup.sql.gz

# Or with Podman
podman exec gym_postgres pg_dump -U gymuser gymtracker | gzip > backup.sql.gz
```

### **Restore to Different Location**

```bash
# Edit paths in the script or docker-compose file
# Then run restore
sudo ./migrate-to-new-server.sh restore
```

### **Verify Migration**

```bash
# Check containers
docker ps

# Check database
docker exec gym_postgres psql -U gymuser gymtracker -c "SELECT COUNT(*) FROM exercises;"

# Test API
curl http://localhost/health
curl http://localhost/api/exercises

# Check images
ls -la /opt/GymTracker/data/uploads/exercises/
```

---

## 🐛 Troubleshooting

### **Error: Container already running**

```bash
# Stop all containers first
docker-compose down
docker stop gym_postgres gym_backend gym_nginx
docker rm gym_postgres gym_backend gym_nginx

# Try restore again
sudo ./migrate-to-new-server.sh restore
```

### **Error: Volume already exists**

```bash
# Remove volumes manually
docker volume rm gymtracker_postgres_data
docker volume rm gymtracker_backend_uploads

# Or remove all gym volumes
docker volume rm $(docker volume ls -q | grep gym)

# Try restore again
sudo ./migrate-to-new-server.sh restore
```

### **Error: Permission denied**

```bash
# Run with sudo
sudo ./migrate-to-new-server.sh restore

# Or fix permissions
sudo chmod +x migrate-to-new-server.sh
```

### **Database restore shows errors**

This is normal if you're restoring to a fresh installation. The script handles it automatically by:
1. Starting PostgreSQL in isolation
2. Restoring to empty database
3. Then starting backend (which sees tables already exist)

---

## 📊 What Gets Migrated

| Item | Included | Location |
|------|----------|----------|
| **Database** | ✅ Yes | `database.sql.gz` |
| **Exercise images** | ✅ Yes | `exported_exercise_images/` |
| **User data** | ✅ Yes | In database |
| **Workout plans** | ✅ Yes | In database |
| **Metrics/history** | ✅ Yes | In database |
| **Configuration** | ✅ Yes | `.env` and compose files |
| **Backend code** | ❌ No | Use git clone |
| **Frontend code** | ❌ No | Use git clone |

---

## 🔒 Security Notes

### **Backup Contains:**
- ✅ Database with user passwords (hashed with bcrypt)
- ✅ Email addresses and personal data
- ✅ Workout history and metrics

### **Protect Your Backup:**
```bash
# Encrypt backup
gpg -c gymtracker_migration_*.tar.gz

# Transfer encrypted
scp gymtracker_migration_*.tar.gz.gpg user@newserver:/tmp/

# Decrypt on new server
gpg -d gymtracker_migration_*.tar.gz.gpg > backup.tar.gz
```

### **After Migration:**
1. Change `SECRET_KEY` in `/opt/GymTracker/backend/.env`
2. Change database password
3. Delete backup files from `/tmp/`

---

## ⏱️ Migration Time

| Server Size | Backup | Transfer | Restore | Total |
|-------------|--------|----------|---------|-------|
| Small (< 10 users) | 1 min | 2 min | 3 min | ~6 min |
| Medium (< 100 users) | 2 min | 5 min | 5 min | ~12 min |
| Large (> 100 users) | 5 min | 10 min | 8 min | ~23 min |

---

## 📝 Example Session

```bash
# === OLD SERVER ===
cd ~/Gym/GymTracker
./migrate-to-new-server.sh backup
# Output: gymtracker_migration_20250120_143022.tar.gz (2.1M)

scp gymtracker_migration_*.tar.gz admin@newserver:/tmp/

# === NEW SERVER ===
cd /opt/GymTracker
tar -xzf /tmp/gymtracker_migration_20250120_143022.tar.gz
cd gymtracker_migration_20250120_143022
sudo ../migrate-to-new-server.sh restore

# Verify
curl http://localhost/health
# {"status":"healthy"}

docker ps
# gym_postgres   Up 2 minutes
# gym_backend    Up 2 minutes
# gym_nginx      Up 2 minutes
```

---

## 🎉 Success!

Your GymTracker is now running on the new server with:
- ✅ All users and data
- ✅ All exercises and images
- ✅ Complete workout history
- ✅ All metrics and progress

Access at: **http://your-new-server-ip**

---

## 📞 Support

If you encounter issues:
1. Check container logs: `docker logs gym_backend`
2. Verify database: `docker exec gym_postgres psql -U gymuser gymtracker -c "\dt"`
3. Check this guide's troubleshooting section

---

**Happy migrating! 🚀**
