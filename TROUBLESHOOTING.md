# Troubleshooting Guide

## Login Returns HTML Instead of JSON

### Symptoms

When trying to login, you get an error like:
```
Unexpected token '<', "<html> <h"... is not valid JSON
```

The browser console shows the API is returning HTML error pages instead of JSON responses.

### Root Cause

This happens when **nginx loses connection to the backend container**.

#### Why This Happens

Podman/Docker containers communicate via an internal network. When a container starts, it gets assigned an IP address on this network. Nginx is configured to forward API requests to the backend container's IP address.

**The Problem:**
- When the backend container restarts (for any reason), it gets a **new IP address**
- Nginx is still trying to connect to the **old IP address**
- Since that IP is no longer valid, nginx returns a 502/504 error page (HTML)
- The frontend expects JSON, causing the parsing error

#### Common Triggers

The backend container restarts when:
1. You manually restart it: `podman restart gym_backend`
2. Code changes trigger hot-reload (if watching files)
3. The backend crashes or is stopped
4. System reboots
5. Running `podman-compose restart`

### Quick Fix (Temporary Solution)

Restart the nginx container to force it to reconnect:

```bash
podman restart gym_nginx
```

**Verification:**
```bash
# Test the health endpoint
curl http://localhost:8080/health

# Should return:
{"status":"healthy"}
```

### When To Apply This Fix

You need to restart nginx **whenever**:
- Backend container is restarted
- You see "Host is unreachable" in nginx logs
- Login/API calls return HTML instead of JSON
- API requests return 502 Bad Gateway or 504 Gateway Timeout

### Checking Nginx Logs

To see if this is the issue:

```bash
podman logs gym_nginx --tail 20
```

Look for errors like:
```
connect() failed (113: Host is unreachable) while connecting to upstream
```

### Permanent Solution Options

To fix this permanently, you have several options:

#### Option 1: Use Container Names (Recommended)

Modify `nginx/nginx.conf` to use the container name instead of IP:

**Current (uses IP):**
```nginx
upstream backend {
    server 10.89.2.3:8000;
}
```

**Better (uses container name):**
```nginx
upstream backend {
    server gym_backend:8000;
}
```

This works because Docker/Podman provides DNS resolution for container names within the same network.

**Steps:**
1. Edit `nginx/nginx.conf`
2. Change `server 10.89.2.3:8000;` to `server gym_backend:8000;`
3. Restart nginx: `podman restart gym_nginx`

#### Option 2: Use Docker Compose Depends On

Ensure nginx restarts when backend restarts by adding proper dependency management in `docker-compose.yml`.

**Current:**
```yaml
nginx:
  depends_on:
    - backend
```

**Better:**
```yaml
nginx:
  depends_on:
    backend:
      condition: service_healthy
  restart: unless-stopped
```

This requires adding a healthcheck to the backend service.

#### Option 3: Use Health Checks with Automatic Restart

Add a health check to nginx that monitors backend connectivity and restarts if it fails:

```yaml
nginx:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://gym_backend:8000/health"]
    interval: 30s
    timeout: 3s
    retries: 3
    start_period: 40s
  restart: unless-stopped
```

### Prevention Checklist

To minimize this issue:

1. **After any backend restart**, always restart nginx:
   ```bash
   podman restart gym_backend
   podman restart gym_nginx  # Don't forget this!
   ```

2. **After code changes** that trigger backend reload:
   ```bash
   podman restart gym_nginx
   ```

3. **After system reboot**, verify all containers are communicating:
   ```bash
   podman ps  # Check all containers are running
   curl http://localhost:8080/health  # Test connectivity
   ```

4. **Use container names** instead of IPs (see Option 1 above)

### Related Issues

This same issue can affect:
- File uploads returning errors
- Exercise images not loading
- Any API endpoint returning HTML instead of JSON

**Solution is always the same:** Restart nginx to reconnect to backend.

### Quick Reference

```bash
# Problem: API returns HTML instead of JSON
# Solution:
podman restart gym_nginx

# Verify it worked:
curl http://localhost:8080/health

# Should return JSON:
{"status":"healthy"}
```

### Container Communication Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP :8080
       ▼
┌─────────────┐
│    Nginx    │ (Reverse Proxy)
└──────┬──────┘
       │ HTTP :8000
       │ (via container network)
       ▼
┌─────────────┐
│   Backend   │ (FastAPI)
└──────┬──────┘
       │ PostgreSQL
       ▼
┌─────────────┐
│  Database   │
└─────────────┘
```

When backend restarts, it gets a new IP on the container network, breaking the connection from nginx.
