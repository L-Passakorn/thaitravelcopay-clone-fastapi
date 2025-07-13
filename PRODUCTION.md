# FLASX Production Deployment Guide

This guide covers deploying FLASX in a production environment using Docker.

## 📁 Production Files Overview

- `Dockerfile.prod` - Optimized production Docker image
- `docker-compose.prod.yml` - Production Docker Compose configuration
- `.dockerignore.prod` - Production build exclusions
- `.env.prod.template` - Production environment template
- `deploy-prod.sh` - Automated deployment script
- `nginx/nginx.conf` - Reverse proxy configuration

## 🚀 Quick Deployment

### 1. Prerequisites

- Docker and Docker Compose installed
- At least 1GB RAM available
- Port 8000 (and optionally 80/443) available

### 2. Setup Environment

```bash
# Copy and edit production environment
cp .env.prod.template .env.prod
nano .env.prod  # Edit with your production settings
```

**Important**: Change the secret keys and other sensitive values in `.env.prod`!

### 3. Deploy

```bash
# Make deployment script executable
chmod +x deploy-prod.sh

# Deploy the application
./deploy-prod.sh deploy
```

## 🔧 Manual Deployment

If you prefer manual deployment:

```bash
# 1. Create necessary directories
mkdir -p data logs backups

# 2. Build the production image
docker build -f Dockerfile.prod -t flasx:latest .

# 3. Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 4. Check health
curl http://localhost:8000/health
```

## 📊 Monitoring and Management

### Health Checks

```bash
# Check application health
./deploy-prod.sh health

# Or manually
curl http://localhost:8000/health
```

### Logs

```bash
# View real-time logs
./deploy-prod.sh logs

# Or manually
docker logs -f flasx-production
```

### Control Commands

```bash
# Stop the application
./deploy-prod.sh stop

# Restart the application
./deploy-prod.sh restart

# View container status
docker-compose -f docker-compose.prod.yml ps
```

## 🌐 Reverse Proxy (Optional)

To use the included nginx reverse proxy:

```bash
# Deploy with nginx
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

### SSL Configuration

1. Place your SSL certificates in `nginx/ssl/`:
   - `nginx/ssl/cert.pem`
   - `nginx/ssl/privkey.pem`

2. Update `nginx/nginx.conf` to enable HTTPS

## 🗄️ Database Management

### Backup

```bash
# Manual backup
cp data/database.db backups/database_$(date +%Y%m%d_%H%M%S).db

# Automated backups are created during deployment
```

### Restore

```bash
# Stop the application
./deploy-prod.sh stop

# Restore from backup
cp backups/database_TIMESTAMP.db data/database.db

# Start the application
./deploy-prod.sh deploy
```

## 🔒 Security Considerations

### Environment Variables

- Change all default secret keys
- Use strong, unique passwords
- Set appropriate CORS origins

### Container Security

- Application runs as non-root user
- Read-only filesystem where possible
- No new privileges allowed
- Network isolation

### Network Security

- Consider using HTTPS in production
- Configure firewall rules
- Use nginx rate limiting
- Monitor access logs

## 📈 Performance Tuning

### Resource Limits

Edit `docker-compose.prod.yml` to set resource limits:

```yaml
services:
  flasx-prod:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### Database Optimization

For production workloads, consider:
- Using PostgreSQL instead of SQLite
- Setting up database connection pooling
- Implementing database backups

## 🔍 Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   # Check logs
   docker logs flasx-production
   
   # Check environment variables
   docker exec flasx-production env
   ```

2. **Health check fails**
   ```bash
   # Check if container is running
   docker ps
   
   # Test health endpoint manually
   docker exec flasx-production curl localhost:8000/health
   ```

3. **Permission errors**
   ```bash
   # Fix data directory permissions
   sudo chown -R 999:999 data/
   ```

### Log Analysis

```bash
# Application logs
docker logs flasx-production

# Nginx logs (if using reverse proxy)
docker logs flasx-nginx

# System resource usage
docker stats flasx-production
```

## 🔄 Updates and Rollbacks

### Update Application

```bash
# Pull latest code
git pull

# Deploy new version (automatically backs up data)
./deploy-prod.sh deploy
```

### Rollback

```bash
# Stop current version
./deploy-prod.sh stop

# Restore previous database backup if needed
cp backups/database_PREVIOUS.db data/database.db

# Use previous image
docker tag flasx:PREVIOUS_TAG flasx:latest
./deploy-prod.sh deploy
```

## 📞 Support

- Check application logs for errors
- Verify environment configuration
- Ensure all required ports are accessible
- Monitor system resources (CPU, memory, disk)

For additional help, check the application documentation or create an issue in the project repository.
