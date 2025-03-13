# Docker Troubleshooting Guide for Cori Electron App

This guide provides solutions for common Docker issues when setting up the Cori Electron App.

## Authentication Issues with Docker Hub

If you're experiencing authentication issues with Docker Hub, try these solutions:

### Solution 1: Use Alpine-based Images

Alpine-based images are smaller and often have fewer authentication issues:

```bash
# Use the alpine version of docker-compose
docker-compose -f docker-compose.alpine.yml up -d
```

### Solution 2: Use Local Development Mode

This approach uses pre-built images without building custom images:

```bash
# Use the local development version of docker-compose
docker-compose -f docker-compose.local.yml up -d
```

### Solution 3: Manual Docker Login

Try logging in to Docker Hub manually before running docker-compose:

```bash
# Log in to Docker Hub
docker login

# Then run docker-compose
docker-compose up -d
```

### Solution 4: Check Docker Desktop Settings

1. Open Docker Desktop
2. Go to Settings > Docker Engine
3. Check the `registry-mirrors` configuration
4. Make sure there are no proxy settings blocking access

### Solution 5: Pull Images Separately

Pull the base images separately before building:

```bash
docker pull python:3.10-slim
docker pull node:20-slim
docker-compose up -d
```

## Network Connectivity Issues

If you're experiencing network connectivity issues:

### Solution 1: Check Firewall Settings

Ensure your firewall allows Docker to access the internet:

```bash
# Test connectivity to Docker Hub
curl -v https://registry-1.docker.io/v2/
```

### Solution 2: Configure DNS

Add Google's DNS servers to your Docker daemon configuration:

```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

### Solution 3: Use HTTP Proxy

If you're behind a corporate firewall, configure Docker to use an HTTP proxy:

```bash
# Set environment variables
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"

# Then run docker-compose
docker-compose up -d
```

## Docker Compose Version Issues

If you're experiencing issues with docker-compose:

### Solution 1: Check Docker Compose Version

```bash
docker-compose version
```

Ensure you're using Docker Compose V2 or later.

### Solution 2: Use Docker Compose V1 Syntax

If you're using an older version of Docker Compose:

```bash
# Edit docker-compose.yml to use version '3.3' instead of '3.8'
```

## Windows-Specific Issues

If you're on Windows:

### Solution 1: Use WSL 2 Backend

Ensure Docker Desktop is configured to use the WSL 2 backend.

### Solution 2: Check Path Format

Make sure paths in volume mounts use the correct format for Windows.

## Getting Help

If you continue to experience issues:

1. Check Docker logs: `docker-compose logs`
2. Check Docker events: `docker events`
3. Verify Docker daemon is running: `docker info`
