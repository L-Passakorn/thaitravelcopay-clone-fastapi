# FastAPI Development Environment Guide

This guide provides instructions for setting up and using the development environment for the FastAPI application.

## 🚀 Quick Start

1. **Start development environment**:
   ```bash
   ./dev.sh start
   ```

2. **Access the application**:
   - FastAPI App: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

3. **Stop the environment**:
   ```bash
   ./dev.sh stop
   ```

## 📋 Prerequisites

- Docker 20.10 or higher
- Docker Compose 2.0 or higher
- At least 4GB RAM for full development stack

## 🏗️ Development Stack

### Core Services

- **FastAPI Application** (`flasx-dev`): Main application with hot reload
- **PostgreSQL** (`db`): Development database
- **Redis** (`redis`): Caching and session storage

### Development Tools (Optional)

- **pgAdmin**: Database management interface
- **Redis Commander**: Redis management interface  
- **Mailhog**: Email testing server

### Monitoring Stack (Optional)

- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

## 🛠️ Development Commands

The `dev.sh` script provides convenient commands for managing your development environment:

### Basic Commands

```bash
# Start core services (FastAPI, PostgreSQL, Redis)
./dev.sh start

# Start all services including tools and monitoring
./dev.sh start-all

# Stop all services
./dev.sh stop

# Restart services
./dev.sh restart

# Show service status and health checks
./dev.sh status

# Show service information and URLs
./dev.sh info
```

### Debugging and Logs

```bash
# Show logs for FastAPI application
./dev.sh logs

# Show logs for specific service
./dev.sh logs db
./dev.sh logs redis

# Open shell in FastAPI container
./dev.sh shell

# Open shell in database container
./dev.sh shell db
```

### Testing

```bash
# Run tests
./dev.sh test
```

### Environment Management

```bash
# Reset entire development environment (removes all data)
./dev.sh reset

# Show help
./dev.sh help
```

## 🔧 Manual Docker Compose Commands

If you prefer using Docker Compose directly:

```bash
# Start core services
docker-compose up -d flasx-dev db redis

# Start all services including tools
docker-compose --profile tools --profile monitoring up -d

# View logs
docker-compose logs -f flasx-dev

# Stop services
docker-compose down

# Rebuild services
docker-compose build --no-cache
```

## 🌐 Service URLs and Access

| Service | URL | Credentials |
|---------|-----|-------------|
| FastAPI App | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| ReDoc | http://localhost:8000/redoc | - |
| pgAdmin | http://localhost:5050 | admin@flasx.local / admin123 |
| Redis Commander | http://localhost:8081 | admin / admin123 |
| Mailhog | http://localhost:8025 | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / admin123 |

### Database Connections

- **PostgreSQL**: `localhost:5432`
  - Database: `flasx_dev`
  - Username: `flasx_user`
  - Password: `flasx_password`

- **Redis**: `localhost:6379` (no password)

## 📂 Development File Structure

```
mdev-68/
├── docker-compose.yml              # Development Docker Compose
├── .env.dev                        # Development environment variables
├── dev.sh                          # Development management script
├── config/
│   └── redis.conf                  # Redis configuration
├── scripts/
│   └── init-db.sql                 # Database initialization
├── monitoring/
│   ├── prometheus-dev.yml          # Prometheus configuration
│   └── grafana/                    # Grafana configurations
├── data/                           # Application data (auto-created)
└── logs/                           # Application logs (auto-created)
```

## ⚙️ Configuration

### Environment Variables

The development environment uses `.env.dev` for configuration. Key settings:

```bash
# Application
ENVIRONMENT=development
DEBUG=true
RELOAD=true

# Database
DATABASE_URL=postgresql+asyncpg://flasx_user:flasx_password@db:5432/flasx_dev

# Redis
REDIS_URL=redis://redis:6379/0

# Email (Mailhog)
SMTP_HOST=mailhog
SMTP_PORT=1025
```

### Hot Reloading

The development setup includes hot reloading:
- Source code is mounted as a volume
- FastAPI runs with `--reload` flag
- Changes to Python files automatically restart the server

### Database Persistence

- PostgreSQL data is persisted in a Docker volume
- Database is automatically initialized with `scripts/init-db.sql`
- Use `./dev.sh reset` to clear all data and start fresh

## 🧪 Testing

### Running Tests

```bash
# Run all tests
./dev.sh test

# Run tests manually
docker-compose --profile test run --rm test-runner
```

### Test Configuration

- Tests use a separate SQLite database (`test_database.db`)
- Test reports are generated in the `test_reports` volume
- Coverage reports are available in HTML format

## 🔍 Monitoring and Debugging

### Application Logs

```bash
# Real-time logs
./dev.sh logs

# Specific service logs
docker-compose logs -f db
docker-compose logs -f redis
```

### Health Checks

```bash
# Check all service health
./dev.sh status

# Manual health check
curl http://localhost:8000/health
```

### Metrics

When monitoring is enabled:
- Prometheus metrics: http://localhost:9090
- Grafana dashboards: http://localhost:3000

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: 
   ```bash
   # Check what's using the ports
   lsof -i :8000
   lsof -i :5432
   ```

2. **Permission issues**:
   ```bash
   # Fix ownership
   sudo chown -R $(whoami):$(whoami) data/ logs/
   ```

3. **Database connection issues**:
   ```bash
   # Reset database
   docker-compose down -v
   ./dev.sh start
   ```

4. **Out of space**:
   ```bash
   # Clean up Docker
   docker system prune -f
   docker volume prune
   ```

### Reset Environment

If you encounter persistent issues:

```bash
# Complete reset (removes all data)
./dev.sh reset
```

## 🔄 Development Workflow

### Typical Development Session

1. **Start environment**:
   ```bash
   ./dev.sh start
   ```

2. **Make code changes**: Edit files in your IDE - changes are automatically reloaded

3. **Test changes**: Access http://localhost:8000/docs to test API

4. **Check logs**: 
   ```bash
   ./dev.sh logs
   ```

5. **Run tests**:
   ```bash
   ./dev.sh test
   ```

6. **Stop when done**:
   ```bash
   ./dev.sh stop
   ```

### Database Development

1. **Access database via pgAdmin**: http://localhost:5050
2. **Connect using**:
   - Host: `db`
   - Port: `5432`
   - Database: `flasx_dev`
   - Username: `flasx_user`
   - Password: `flasx_password`

3. **Run SQL directly**:
   ```bash
   ./dev.sh shell db
   psql -U flasx_user -d flasx_dev
   ```

### Email Testing

1. **Configure app to use Mailhog**:
   - SMTP Host: `mailhog`
   - SMTP Port: `1025`

2. **View emails**: http://localhost:8025

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

---

**Happy Coding!** 🎉
