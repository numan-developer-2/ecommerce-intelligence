# 🚀 E-COMMERCE INTELLIGENCE - DEPLOYMENT GUIDE

**Last Updated:** January 6, 2026  
**Version:** 2.0.0  
**Status:** Production Ready ✅

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 PREREQUISITES

### Required Software

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Docker & Docker Compose** - [Download](https://www.docker.com/products/docker-desktop)
- **Git** - [Download](https://git-scm.com/downloads)

### Required API Keys

- **OpenRouter API Key** - [Get Key](https://openrouter.ai/)

---

## 💻 LOCAL DEVELOPMENT

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ecommerce-intelligence.git
cd ecommerce-intelligence
```

### Step 2: Create Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create a `.env` file in the project root:

```env
# API Configuration
OPENROUTER_API_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000

# Optional: Database (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce

# Optional: Redis (for caching)
REDIS_URL=redis://localhost:6379/0
```

### Step 5: Run System Check

```bash
python check_system.py
```

Expected output:

```
======================================================================
  SCORE: 6/6 checks passed
======================================================================
SUCCESS! All systems ready for development.
```

### Step 6: Collect Data

**Option A: Run Complete Pipeline**

```bash
python main.py
```

**Option B: Generate Sample Data (for testing)**

```bash
python generate_sample_data.py
```

### Step 7: Start API Server

```bash
python src/api_server.py
```

Server will start at: `http://localhost:8000`

- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Step 8: Open Frontend

Open `frontend/index.html` in your browser or use a local server:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 3000
```

Then visit: `http://localhost:3000`

---

## 🐳 DOCKER DEPLOYMENT

### Quick Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services Included

1. **API Server** - Port 8000
2. **Redis Cache** - Port 6379
3. **Nginx Reverse Proxy** - Port 80/443

### Custom Build

```bash
# Build only
docker-compose build

# Build with no cache
docker-compose build --no-cache

# Start specific service
docker-compose up api
```

### Docker Commands

```bash
# View running containers
docker ps

# Access container shell
docker exec -it ecommerce-api bash

# View container logs
docker logs ecommerce-api

# Restart service
docker-compose restart api

# Remove all containers and volumes
docker-compose down -v
```

---

## 🌐 PRODUCTION DEPLOYMENT

### Option 1: Deploy to Heroku

#### Backend (API)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create ecommerce-intelligence-api

# Set environment variables
heroku config:set OPENROUTER_API_KEY=your_key_here

# Deploy
git push heroku main

# Open app
heroku open
```

#### Frontend (Netlify)

1. Push code to GitHub
2. Go to [Netlify](https://www.netlify.com/)
3. Click "New site from Git"
4. Select your repository
5. Set build settings:
   - **Build command:** (leave empty)
   - **Publish directory:** `frontend`
6. Deploy!

### Option 2: Deploy to AWS

#### Backend (EC2 + Docker)

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone https://github.com/yourusername/ecommerce-intelligence.git
cd ecommerce-intelligence

# Create .env file
nano .env
# Add your environment variables

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

#### Frontend (S3 + CloudFront)

```bash
# Install AWS CLI
pip install awscli

# Configure AWS
aws configure

# Sync frontend to S3
aws s3 sync frontend/ s3://your-bucket-name/ --acl public-read

# Create CloudFront distribution (via AWS Console)
# Point to S3 bucket
```

### Option 3: Deploy to Railway

1. Go to [Railway](https://railway.app/)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Dockerfile
6. Add environment variables
7. Deploy!

### Option 4: Deploy to Render

1. Go to [Render](https://render.com/)
2. Click "New +"
3. Select "Web Service"
4. Connect GitHub repository
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python src/api_server.py`
6. Add environment variables
7. Deploy!

---

## ⚙️ ENVIRONMENT CONFIGURATION

### Required Variables

| Variable             | Description        | Example        |
| -------------------- | ------------------ | -------------- |
| `OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-v1-...` |
| `API_HOST`           | API server host    | `0.0.0.0`      |
| `API_PORT`           | API server port    | `8000`         |

### Optional Variables

| Variable       | Description                  | Default |
| -------------- | ---------------------------- | ------- |
| `DATABASE_URL` | PostgreSQL connection string | SQLite  |
| `REDIS_URL`    | Redis connection string      | None    |
| `LOG_LEVEL`    | Logging level                | `INFO`  |
| `CORS_ORIGINS` | Allowed CORS origins         | `*`     |

### Production Environment

```env
# Production .env file
OPENROUTER_API_KEY=sk-or-v1-your-production-key
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql://user:pass@db-host:5432/ecommerce
REDIS_URL=redis://redis-host:6379/0
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 🔍 HEALTH CHECKS

### API Health Check

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
  "status": "online",
  "message": "E-Commerce Intelligence API",
  "version": "1.0.0"
}
```

### Docker Health Check

```bash
docker-compose ps
```

All services should show `healthy` status.

---

## 🐛 TROUBLESHOOTING

### Issue: API Server Won't Start

**Solution:**

```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # macOS/Linux
```

### Issue: Frontend Can't Connect to API

**Solution:**

1. Check if API server is running: `curl http://localhost:8000/`
2. Check CORS settings in `src/config.py`
3. Update `frontend/app.js` API_URL if needed
4. Clear browser cache and reload

### Issue: Docker Build Fails

**Solution:**

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker logs
docker-compose logs api
```

### Issue: Missing Data

**Solution:**

```bash
# Run scraper
python main.py --step scrape

# Or generate sample data
python generate_sample_data.py

# Verify data exists
ls data/raw/
ls data/cleaned/
```

### Issue: OpenRouter API Errors

**Solution:**

1. Verify API key is correct
2. Check API key has credits
3. Test API key:

```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 📊 MONITORING

### Production Monitoring Tools

1. **Application Performance:**

   - [New Relic](https://newrelic.com/)
   - [Datadog](https://www.datadoghq.com/)
   - [Sentry](https://sentry.io/)

2. **Uptime Monitoring:**

   - [UptimeRobot](https://uptimerobot.com/)
   - [Pingdom](https://www.pingdom.com/)

3. **Log Management:**
   - [Loggly](https://www.loggly.com/)
   - [Papertrail](https://www.papertrail.com/)

### Basic Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Simple health check script

while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)

    if [ $response -eq 200 ]; then
        echo "$(date): API is healthy"
    else
        echo "$(date): API is down! Response code: $response"
        # Send alert (email, Slack, etc.)
    fi

    sleep 60  # Check every minute
done
```

---

## 🔐 SECURITY CHECKLIST

- [ ] Remove hardcoded API keys
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS in production
- [ ] Implement rate limiting
- [ ] Add authentication (JWT)
- [ ] Restrict CORS origins
- [ ] Keep dependencies updated
- [ ] Use Docker secrets for sensitive data
- [ ] Enable firewall rules
- [ ] Regular security audits

---

## 📈 SCALING

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
```

### Load Balancing

Use Nginx or AWS ELB to distribute traffic across multiple API instances.

### Database Optimization

1. Add indexes for frequently queried fields
2. Use connection pooling
3. Implement caching with Redis
4. Consider read replicas

---

## 🎯 NEXT STEPS

1. ✅ Deploy to staging environment
2. ✅ Run integration tests
3. ✅ Set up monitoring
4. ✅ Configure backups
5. ✅ Deploy to production
6. ✅ Monitor performance
7. ✅ Collect user feedback
8. ✅ Iterate and improve

---

## 📞 SUPPORT

- **Documentation:** [GitHub Wiki](https://github.com/yourusername/ecommerce-intelligence/wiki)
- **Issues:** [GitHub Issues](https://github.com/yourusername/ecommerce-intelligence/issues)
- **Email:** support@yourdomain.com

---

**Happy Deploying! 🚀**
