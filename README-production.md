# FastAPI Production Deployment Guide

This guide provides comprehensive instructions for deploying the FastAPI application in a production environment using Docker and Docker Compose.

## 📋 Prerequisites

- Docker 20.10 or higher
- Docker Compose 2.0 or higher
- At least 2GB RAM and 10GB disk space
- SSL certificates (for HTTPS)

## 🚀 Quick Start

1. **Clone and navigate to the project**:
   ```bash
   git clone <repository-url>
   cd mdev-68
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.prod.template .env.prod
   # Edit .env.prod with your production values
   nano .env.prod
   ```

3. **Deploy the application**:
   ```bash
   ./deploy_prod.sh deploy
   ```

4. **Check the deployment**:
   ```bash
   ./deploy_prod.sh status
   ```

The application will be available at:
- HTTP: http://localhost:8000
- HTTPS: https://localhost (if nginx is enabled)
- Health check: http://localhost:8000/health

## 📁 Production Files Structure

```
mdev-68/
├── Dockerfile.prod                 # Optimized production Dockerfile
├── docker-compose.prod.yml         # Production Docker Compose configuration
├── .dockerignore.prod             # Production Docker ignore file
├── .env.prod.template             # Environment variables template
├── .env.prod                      # Your production environment (create this)
├── deploy_prod.sh                 # Production deployment script
├── nginx/
│   └── nginx.conf                 # Nginx reverse proxy configuration
├── data/                          # Application data (auto-created)
├── logs/                          # Application logs (auto-created)
└── backups/                       # Database backups (auto-created)
```

## ⚙️ Configuration

### Environment Variables (.env.prod)

**Critical Security Settings** (Change these!):
```bash
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too
```

**Database Configuration**:
```bash
DATABASE_URL=sqlite+aiosqlite:///./data/database.db
# For PostgreSQL: postgresql+asyncpg://user:password@host:port/database
```

**Server Configuration**:
```bash
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
DEBUG=false
```

**CORS and Security**:
```bash
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### SSL/TLS Certificates

For production, replace the self-signed certificates with proper SSL certificates:

1. **Using Let's Encrypt**:
   ```bash
   # Install certbot
   sudo apt-get install certbot
   
   # Generate certificates
   sudo certbot certonly --standalone -d yourdomain.com
   
   # Copy certificates
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
   sudo chown $(whoami):$(whoami) nginx/ssl/*.pem
   ```

2. **Using existing certificates**:
   ```bash
   cp /path/to/your/cert.pem nginx/ssl/cert.pem
   cp /path/to/your/private.key nginx/ssl/key.pem
   chmod 644 nginx/ssl/cert.pem
   chmod 600 nginx/ssl/key.pem
   ```

## 🔧 Deployment Commands

The `deploy_prod.sh` script provides several commands for managing your deployment:

### Basic Commands

```bash
# Deploy the application
./deploy_prod.sh deploy

# Show service status
./deploy_prod.sh status

# View live logs
./deploy_prod.sh logs

# Restart services
./deploy_prod.sh restart

# Stop services
./deploy_prod.sh stop

# Backup database
./deploy_prod.sh backup

# Clean up (stop and remove containers)
./deploy_prod.sh cleanup
```

### Manual Docker Compose Commands

If you prefer using Docker Compose directly:

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down

# Rebuild images
docker-compose -f docker-compose.prod.yml build --no-cache
```

## 🏗️ Architecture

### Multi-Stage Docker Build

The production Dockerfile uses a multi-stage build for optimization:

1. **Builder stage**: Installs dependencies and builds the application
2. **Production stage**: Creates a minimal runtime image with only necessary components

### Services

1. **flasx-prod**: Main FastAPI application
   - Runs as non-root user for security
   - Health checks enabled
   - Read-only filesystem (except data and logs)

2. **nginx** (optional): Reverse proxy and load balancer
   - SSL termination
   - Rate limiting
   - Security headers
   - Static file serving

3. **redis** (optional): Caching and session storage
   - Password protected
   - Persistent data storage

## 🔒 Security Features

### Application Security
- Non-root user execution
- Read-only filesystem
- No new privileges
- Resource limits
- Environment variable validation

### Network Security
- Internal Docker network
- Nginx reverse proxy
- Rate limiting
- SSL/TLS encryption
- Security headers

### Data Security
- Encrypted connections
- Secure password hashing
- JWT token authentication
- CORS protection

## 📊 Monitoring and Logging

### Health Checks
- Application health endpoint: `/health`
- Docker health checks enabled
- Nginx health monitoring

### Logging
- Structured JSON logging
- Log rotation
- Centralized log collection
- Error tracking

### Optional Monitoring Stack
Enable monitoring with the `monitoring` profile:

```bash
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

This includes:
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## 🔄 Updates and Maintenance

### Updating the Application

1. **Pull latest code**:
   ```bash
   git pull origin main
   ```

2. **Backup current state**:
   ```bash
   ./deploy_prod.sh backup
   ```

3. **Rebuild and deploy**:
   ```bash
   docker-compose -f docker-compose.prod.yml build --no-cache
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Database Migrations

If your application uses database migrations:

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec flasx-prod python -m alembic upgrade head
```

### Log Rotation

Set up log rotation to prevent disk space issues:

```bash
# Add to crontab
0 0 * * 0 find /path/to/logs -name "*.log" -mtime +30 -delete
```

## 🐛 Troubleshooting

### Common Issues

1. **Container fails to start**:
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod.yml logs flasx-prod
   
   # Check configuration
   docker-compose -f docker-compose.prod.yml config
   ```

2. **Database connection issues**:
   ```bash
   # Check database file permissions
   ls -la data/
   
   # Recreate database
   rm data/database.db
   docker-compose -f docker-compose.prod.yml restart flasx-prod
   ```

3. **SSL certificate issues**:
   ```bash
   # Check certificate validity
   openssl x509 -in nginx/ssl/cert.pem -text -noout
   
   # Regenerate self-signed certificates
   rm nginx/ssl/*.pem
   ./deploy_prod.sh deploy
   ```

4. **Permission issues**:
   ```bash
   # Fix ownership
   sudo chown -R $(whoami):$(whoami) data/ logs/
   chmod 755 data/ logs/
   ```

### Performance Tuning

1. **Increase worker processes**:
   ```bash
   # In .env.prod
   WORKERS=4
   ```

2. **Optimize database**:
   ```bash
   # Use PostgreSQL for better performance
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   ```

3. **Enable caching**:
   ```bash
   # Enable Redis service
   docker-compose -f docker-compose.prod.yml up -d redis
   ```

## 📞 Support

### Logs and Debugging

```bash
# View all logs
./deploy_prod.sh logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs flasx-prod
docker-compose -f docker-compose.prod.yml logs nginx

# Debug container
docker-compose -f docker-compose.prod.yml exec flasx-prod bash
```

### Health Checks

```bash
# Application health
curl -f http://localhost:8000/health

# Service status
./deploy_prod.sh status

# Container inspection
docker inspect flasx-production
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**Note**: This is a production deployment guide. Always test deployments in a staging environment before deploying to production. Remember to regularly update your dependencies and monitor your application for security vulnerabilities.
