# Deployment Guide

## Overview
This guide covers dockerizing and deploying the Navelle AI Module to AWS EC2.

## Prerequisites
- Docker installed locally (Windows: Docker Desktop)
- Docker Hub account (for storing images)
- AWS account with EC2 access
- Git configured with SSH key

---

## Local Docker Testing

### 1. Build Docker Image
```bash
docker build -t navelle-ai:latest .
```

### 2. Run Single Container (Development)
```bash
docker run -p 8000:8000 \
  --env-file .env \
  -e OPENAI_API_KEY=your_key \
  navelle-ai:latest
```

Test: `curl http://localhost:8000/health`

### 3. Run with Docker Compose (Production-like)
```bash
# Copy and fill .env.example to .env
cp .env.example .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

---

## AWS EC2 Deployment

### 1. Launch EC2 Instance
- **AMI:** Ubuntu 22.04 LTS
- **Instance Type:** t3.medium (or t2.medium)
- **Storage:** 20-30 GB
- **Security Group:** Allow ports 80, 443, 8000, 27017

### 2. SSH into Instance
```bash
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP
```

### 3. Install Docker & Docker Compose
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### 4. Clone Repository
```bash
cd /home/ubuntu
git clone https://github.com/rahi96/ai_part.git
cd ai_part
```

### 5. Set Up Environment Variables
```bash
# Copy example and edit
cp .env.example .env
nano .env

# Add your keys:
# OPENAI_API_KEY
# CUSTOMER_TOKEN
# ADMIN_TOKEN
```

### 6. Deploy with Docker Compose
```bash
# Pull latest image from Docker Hub
docker pull rahi96/navelle-ai:latest

# Or build locally
docker build -t navelle-ai:latest .

# Start services
docker-compose up -d

# Check status
docker ps
docker-compose logs -f app
```

### 7. Verify Deployment
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test from outside (using public IP)
curl http://EC2_PUBLIC_IP:8000/health
```

---

## CI/CD with GitHub Actions

### 1. Configure Docker Hub Credentials
Go to GitHub repo → Settings → Secrets and variables → Actions

Add secrets:
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token (not password)

### 2. Workflow Triggers
- Automatically builds and pushes on `push` to `main`
- Creates tags: `latest` and `COMMIT_SHA`

### 3. Deployment Script (Optional)
Create `deploy.sh` on EC2:

```bash
#!/bin/bash
set -e

cd /home/ubuntu/ai_part

# Pull latest image
docker pull rahi96/navelle-ai:latest

# Stop and remove old container
docker-compose down || true

# Start new services
docker-compose up -d

# Check health
sleep 5
curl http://localhost:8000/health || exit 1

echo "Deployment successful!"
```

Make executable: `chmod +x deploy.sh`

Then from GitHub Actions, call: `ssh ubuntu@EC2_IP './deploy.sh'`

---

## Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

### Health Endpoint
```bash
curl http://localhost:8000/health
```

### Metrics
- Response times logged in requests
- Check `X-Process-Time` header in responses

---

## Troubleshooting

### Container won't start
```bash
docker-compose logs app
```

### MongoDB connection error
- Ensure MongoDB is healthy: `docker-compose logs mongo`
- Check connection string in `.env`
- Verify credentials match compose file

### Port already in use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Or change port in docker-compose.yml
# ports:
#   - "8001:8000"
```

### Out of disk space
```bash
# Clean up unused images/containers
docker system prune -a

# Check disk usage
docker system df
```

---

## Scaling

For production, consider:
1. **AWS ALB** (Application Load Balancer) for port 80/443
2. **RDS MongoDB** instead of self-hosted
3. **CloudWatch** for centralized logging
4. **ECS/Fargate** instead of manual EC2 management
5. **Auto Scaling Groups** for multiple instances

---

## Security Notes

- ✅ Non-root user in Docker container
- ✅ Environment variables via `.env` (not hardcoded)
- ✅ CORS middleware in place
- ✅ Health check configured
- ⚠️ TODO: Add HTTPS/SSL certificate (AWS ACM + ALB)
- ⚠️ TODO: Remove `DEBUG=False` check in code
- ⚠️ TODO: Add authentication to API endpoints

---

## Support
For issues, check logs: `docker-compose logs app`
