# WSL2 + Podman Configuration Guide

This guide documents the configuration changes required to run the Gym Tracker application with Podman on Windows Subsystem for Linux 2 (WSL2).

## Table of Contents
1. [Overview](#overview)
2. [Issues Encountered](#issues-encountered)
3. [Configuration Changes](#configuration-changes)
4. [Verification](#verification)
5. [Alternative Solutions](#alternative-solutions)
6. [Troubleshooting](#troubleshooting)

---

## Overview

When running containerized applications with Podman on WSL2, you may encounter networking and permission issues that don't occur on standard Linux installations. This guide addresses two main issues:

1. **Netavark nftables error**: Podman's network backend (netavark) using nftables firewall driver incompatible with WSL2
2. **Privileged port binding**: Rootless Podman cannot bind to ports below 1024

---

## Issues Encountered

### Issue 1: Netavark nftables Error

**Error Message:**
```
Error: unable to start container: netavark: nftables error:
nft did not return successfully while applying ruleset
```

**Root Cause:**
- Podman's netavark network backend defaults to using the `nftables` firewall driver
- WSL2 kernel has limited/incompatible nftables support
- Causes container networking to fail during startup

### Issue 2: Privileged Port Binding

**Error Message:**
```
Error response from daemon: rootlessport cannot expose privileged port 80,
you can add 'net.ipv4.ip_unprivileged_port_start=80' to /etc/sysctl.conf
(currently 1024), or choose a larger port number (>= 1024):
listen tcp 0.0.0.0:80: bind: permission denied
```

**Root Cause:**
- Linux restricts binding to ports < 1024 to root user only
- Podman running in rootless mode cannot bind to port 80
- Requires either system configuration changes or using higher port numbers

---

## Configuration Changes

### Change 1: Configure Netavark to Use iptables

**File Modified:** `~/.config/containers/containers.conf`

**Location:** `/home/aamarques/.config/containers/containers.conf`

**Change:**
```toml
[network]
network_backend = "netavark"
firewall_driver = "iptables"  # Added this line
pasta_options = ["--dns-forward", "8.8.8.8"]

[engine]
network_cmd_options = []
```

**Explanation:**
- Added `firewall_driver = "iptables"` to force netavark to use iptables instead of nftables
- iptables is fully supported by WSL2 kernel
- This configuration is user-specific and doesn't require root access

**Effect:**
- Containers can now create network namespaces successfully
- Network rules are applied using iptables
- Resolves the netavark nftables startup error

---

### Change 2: Modify Nginx Port Mapping

**File Modified:** `docker-compose.yml`

**Location:** `/home/aamarques/Gym/GymTracker/docker-compose.yml`

**Change:**
```yaml
nginx:
  image: docker.io/library/nginx:alpine
  container_name: gym_nginx
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./frontend:/usr/share/nginx/html:ro
    - backend_uploads:/usr/share/nginx/html/uploads:ro
  ports:
    - "8080:80"  # Changed from "80:80" to "8080:80"
  depends_on:
    - backend
  networks:
    - gym_network
```

**Explanation:**
- Changed host port from `80` to `8080`
- Container still uses port 80 internally (right side of mapping)
- Host binds to port 8080 (left side of mapping)
- Port 8080 is above the 1024 threshold, allowing rootless binding

**Effect:**
- Application accessible via `http://localhost:8080` instead of `http://localhost`
- No system configuration changes required
- Rootless Podman can bind successfully

---

## Verification

### Check Container Status

```bash
# View all running containers
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Expected Output:**
```
NAMES         STATUS                    PORTS
gym_postgres  Up X minutes (healthy)    0.0.0.0:5432->5432/tcp
gym_backend   Up X minutes              0.0.0.0:8000->8000/tcp
gym_nginx     Up X minutes              0.0.0.0:8080->80/tcp
```

### Verify Network Configuration

```bash
# Check Podman network backend
podman info --format json | grep -A5 networkBackend

# Verify containers.conf settings
cat ~/.config/containers/containers.conf
```

### Test Application Access

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test API docs
curl -I http://localhost:8080/docs

# Test frontend
curl -I http://localhost:8080/
```

---

## Access Points

After the configuration changes, access the application at:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8080 | Main web application |
| **API Docs** | http://localhost:8080/docs | Interactive API documentation |
| **Health Check** | http://localhost:8080/health | Backend health status |
| **Backend API** | http://localhost:8000 | Direct backend access (optional) |
| **PostgreSQL** | localhost:5432 | Database (for DB clients) |

---

## Alternative Solutions

### Alternative 1: Enable Privileged Port Binding (Requires Root)

If you prefer to use port 80, you can configure the system to allow unprivileged port binding:

```bash
# Check current unprivileged port start
sysctl net.ipv4.ip_unprivileged_port_start

# Temporarily allow port 80
sudo sysctl net.ipv4.ip_unprivileged_port_start=80

# Make permanent (add to /etc/sysctl.conf)
echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

**Pros:**
- Can use standard port 80
- No need to specify port in URLs

**Cons:**
- Requires root/sudo access
- Security consideration: allows any user to bind privileged ports
- WSL2 specific: may need to be reapplied after WSL restart

### Alternative 2: Use Docker Desktop Instead

Docker Desktop for WSL2 handles these issues automatically:

```bash
# If Docker Desktop is installed, use docker-compose directly
docker-compose up -d
```

**Pros:**
- No configuration changes needed
- Better WSL2 integration
- Handles privileged ports automatically

**Cons:**
- Requires Docker Desktop installation
- Additional resource overhead
- Proprietary software

### Alternative 3: Use CNI Network Backend

Instead of netavark, you can use the older CNI network backend:

```toml
# In ~/.config/containers/containers.conf
[network]
network_backend = "cni"
```

**Pros:**
- May work without firewall_driver configuration
- Stable and well-tested

**Cons:**
- CNI is deprecated in favor of netavark
- Future Podman versions may not support CNI

---

## Troubleshooting

### Containers Still Failing to Start

1. **Verify Podman socket is running:**
   ```bash
   systemctl --user status podman.socket
   systemctl --user start podman.socket
   ```

2. **Check for conflicting containers:**
   ```bash
   podman ps -a
   podman rm -f gym_postgres gym_backend gym_nginx
   ```

3. **Rebuild without cache:**
   ```bash
   docker compose down -v
   docker compose up -d --build --force-recreate
   ```

### Network Issues After Configuration

1. **Reset Podman networks:**
   ```bash
   podman network prune -f
   podman network ls
   ```

2. **Check iptables rules:**
   ```bash
   sudo iptables -L -n
   sudo iptables -t nat -L -n
   ```

3. **Verify DNS resolution:**
   ```bash
   podman exec gym_backend ping -c 2 google.com
   ```

### Port Already in Use

If port 8080 is already in use:

```bash
# Check what's using the port
sudo netstat -tulpn | grep 8080
# OR
sudo lsof -i :8080

# Choose a different port in docker-compose.yml
# For example, use 8081:80 instead of 8080:80
```

### WSL2 Kernel Issues

If issues persist, update WSL2 kernel:

```bash
# From PowerShell (Windows)
wsl --update
wsl --shutdown
wsl

# Check kernel version
uname -r
```

Required minimum kernel version: 5.10.x or higher for best compatibility

---

## Starting the Application

After configuration, use standard Docker Compose commands:

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild and start
docker compose up -d --build
```

---

## Summary of Benefits

With these configuration changes:

✅ Containers start successfully on WSL2 with Podman
✅ No nftables compatibility issues
✅ No need for root/sudo privileges
✅ Rootless Podman security benefits maintained
✅ Simple port mapping solution
✅ Easy to revert if needed

---

## Configuration Files Reference

### Complete ~/.config/containers/containers.conf

```toml
[network]
network_backend = "netavark"
firewall_driver = "iptables"
pasta_options = ["--dns-forward", "8.8.8.8"]

[engine]
network_cmd_options = []
```

### Modified docker-compose.yml (nginx service only)

```yaml
nginx:
  image: docker.io/library/nginx:alpine
  container_name: gym_nginx
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./frontend:/usr/share/nginx/html:ro
    - backend_uploads:/usr/share/nginx/html/uploads:ro
  ports:
    - "8080:80"  # Modified for rootless Podman
  depends_on:
    - backend
  networks:
    - gym_network
```

---

## Additional Resources

- [Podman Documentation](https://docs.podman.io/)
- [Podman Rootless Mode](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)
- [Netavark Network Backend](https://github.com/containers/netavark)
- [WSL2 Networking](https://docs.microsoft.com/en-us/windows/wsl/networking)

---

## Version Information

This configuration was tested with:

- **OS**: Linux 6.6.87.2-microsoft-standard-WSL2
- **Podman**: 5.4.2
- **Docker Compose**: v2.39.1-desktop.1
- **Netavark**: 1.14.0
- **Date**: October 2025

---

## Notes

- These configurations are specific to WSL2 + Podman setups
- Standard Linux installations may not require these changes
- Docker (non-Podman) users typically don't encounter these issues
- Changes are persistent across WSL2 restarts
- Consider documenting any additional custom configurations for your team
