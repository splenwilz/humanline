# 🐳 Humanline Backend - Docker Deployment Guide

This guide covers deploying the Humanline Backend using Docker for production-grade deployment.

## 🏗️ Architecture

The Docker setup includes:

- **FastAPI Backend** - Main application server
- **PostgreSQL 16** - Primary database with Alpine Linux
- **Redis 7** - Caching and session storage
- **Nginx** - Reverse proxy and load balancer (optional)

## 🚀 Quick Start

### 1. Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- At least 5GB disk space

### 2. Environment Setup

```bash
# Copy environment template
cp env.docker .env

# Edit configuration (IMPORTANT!)
nano .env
```

**Required Configuration:**
- Set secure passwords for `POSTGRES_PASSWORD` and `REDIS_PASSWORD`
- Generate a secure `SECRET_KEY` (at least 32 characters)
- Update `ALLOWED_ORIGINS` with your frontend URLs

### 3. Build and Deploy

```bash
# Build the application
./docker-build.sh

# Deploy all services
./docker-deploy.sh
```

### 4. Verify Deployment

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend

# Test API
curl http://localhost:8000/health
```

## 📋 Available Services

| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | Main FastAPI application |
| PostgreSQL | 5432 | Database server |
| Redis | 6379 | Cache and sessions |
| Nginx | 80/443 | Reverse proxy (optional) |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `humanline` |
| `POSTGRES_USER` | Database user | `humanline_user` |
| `POSTGRES_PASSWORD` | Database password | **Required** |
| `REDIS_PASSWORD` | Redis password | **Required** |
| `SECRET_KEY` | JWT signing key | **Required** |
| `ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` |
| `ENVIRONMENT` | App environment | `production` |

### Production Recommendations

1. **Security:**
   ```bash
   # Generate secure passwords
   openssl rand -base64 32  # For SECRET_KEY
   openssl rand -base64 24  # For database passwords
   ```

2. **SSL/TLS:**
   - Place SSL certificates in `nginx/ssl/`
   - Uncomment SSL configuration in `nginx/nginx.conf`
   - Update `ALLOWED_ORIGINS` to use HTTPS URLs

3. **Resource Limits:**
   ```yaml
   # Add to docker-compose.yml services
   deploy:
     resources:
       limits:
         memory: 512M
         cpus: '0.5'
   ```

## 🛠️ Management Commands

### Building

```bash
# Build application image
./docker-build.sh

# Build specific service
docker-compose build backend

# Build without cache
docker-compose build --no-cache backend
```

### Deployment

```bash
# Full deployment with health checks
./docker-deploy.sh

# Start services
docker-compose up -d

# Start with production profile (includes Nginx)
docker-compose --profile production up -d

# Scale backend instances
docker-compose up -d --scale backend=3
```

### Database Management

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Database backup
docker-compose exec postgres pg_dump -U humanline_user humanline > backup.sql

# Database restore
docker-compose exec -T postgres psql -U humanline_user humanline < backup.sql
```

### Monitoring

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis

# Monitor resources
docker stats

# Health checks
curl http://localhost:8000/health
docker-compose exec backend python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use:**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Change port in .env
   BACKEND_PORT=8001
   ```

2. **Database Connection Failed:**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Verify database is healthy
   docker-compose exec postgres pg_isready -U humanline_user
   ```

3. **Permission Denied:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER logs/ uploads/
   chmod +x docker-*.sh
   ```

4. **Out of Memory:**
   ```bash
   # Check memory usage
   docker stats
   
   # Reduce worker count in Dockerfile
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
   ```

### Health Checks

```bash
# Backend health
curl -f http://localhost:8000/health || echo "Backend unhealthy"

# Database health
docker-compose exec postgres pg_isready -U humanline_user || echo "Database unhealthy"

# Redis health
docker-compose exec redis redis-cli ping || echo "Redis unhealthy"
```

## 📊 Performance Tuning

### Backend Optimization

1. **Worker Processes:**
   ```dockerfile
   # In Dockerfile, adjust based on CPU cores
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
   ```

2. **Memory Limits:**
   ```yaml
   # In docker-compose.yml
   backend:
     deploy:
       resources:
         limits:
           memory: 1G
         reservations:
           memory: 512M
   ```

### Database Optimization

1. **PostgreSQL Configuration:**
   ```yaml
   postgres:
     command: >
       postgres
       -c shared_preload_libraries=pg_stat_statements
       -c max_connections=100
       -c shared_buffers=256MB
       -c effective_cache_size=1GB
   ```

2. **Connection Pooling:**
   ```python
   # In core/database.py
   engine = create_async_engine(
       settings.database_url,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True,
   )
   ```

## 🔐 Security Best Practices

1. **Network Security:**
   ```yaml
   # Isolate services
   networks:
     backend:
       internal: true
     frontend:
       driver: bridge
   ```

2. **Secrets Management:**
   ```bash
   # Use Docker secrets in production
   echo "my_secret_password" | docker secret create postgres_password -
   ```

3. **Regular Updates:**
   ```bash
   # Update base images
   docker-compose pull
   ./docker-build.sh
   ./docker-deploy.sh
   ```

## 📈 Monitoring and Logging

### Log Management

```bash
# Configure log rotation
docker-compose exec backend logrotate /etc/logrotate.conf

# View structured logs
docker-compose logs --since 1h backend | jq '.'
```

### Metrics Collection

Consider adding:
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for log analysis

## 🚀 Production Deployment

### Cloud Deployment

1. **AWS ECS/Fargate:**
   ```bash
   # Build for ARM64 if using Graviton
   docker buildx build --platform linux/arm64 -t humanline/backend .
   ```

2. **Google Cloud Run:**
   ```bash
   # Build and push to GCR
   docker tag humanline/backend gcr.io/PROJECT_ID/humanline-backend
   docker push gcr.io/PROJECT_ID/humanline-backend
   ```

3. **Azure Container Instances:**
   ```bash
   # Create resource group and deploy
   az container create --resource-group myResourceGroup --name humanline-backend --image humanline/backend
   ```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and Deploy
        run: |
          ./docker-build.sh
          ./docker-deploy.sh
```

## 📞 Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review health checks: `curl http://localhost:8000/health`
- Verify configuration: `docker-compose config`

---

**🎉 Happy Deploying!** Your Humanline Backend is now production-ready with Docker!
