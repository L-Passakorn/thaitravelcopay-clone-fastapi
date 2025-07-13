# FLASX Development Container Setup

This document provides a comprehensive guide for setting up and using the FLASX FastAPI project with VS Code Dev Containers.

## 🚀 Quick Start

### Prerequisites

1. **VS Code** with the following extensions:
   - [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)

2. **Docker Desktop** installed and running

### Opening in Dev Container

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd mdev-68
   ```

2. **Open in VS Code**:
   ```bash
   code .
   ```

3. **Open in Dev Container**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Dev Containers: Reopen in Container"
   - Select it and wait for the container to build

   **Alternative method:**
   - Click the "Reopen in Container" button when VS Code detects the `.devcontainer` folder

## 🏗️ Dev Container Architecture

The development environment consists of:

### Main Application Container
- **Base**: Debian Trixie Slim
- **Python**: 3.x with Poetry package management
- **User**: Non-root `app` user
- **Workspace**: `/home/app/code`
- **Virtual Environment**: `/home/app/venv`

### Additional Services (via Docker Compose)
- **PostgreSQL 15**: Database service on port 5432
- **Redis 7**: Cache and session store on port 6379

### VS Code Extensions (Auto-installed)
- Python development tools (Python, Pylint, Black, isort, MyPy)
- Debugging support (debugpy)
- Jupyter notebook support
- Docker and YAML editing
- GitHub Copilot (if available)
- Code formatting and linting (Ruff)

## 🔧 Development Features

### Python Environment
- **Virtual Environment**: Pre-configured at `/home/app/venv`
- **Package Manager**: Poetry for dependency management
- **Python Path**: Automatically configured for the project

### Code Quality Tools
- **Formatter**: Black (runs on save)
- **Linter**: Ruff and Pylint
- **Type Checker**: MyPy
- **Import Sorting**: isort (runs on save)

### Testing
- **Framework**: pytest with async support
- **Discovery**: Automatic test discovery in `tests/` folder
- **Running**: Via VS Code Test Explorer or tasks

### Debugging
- **FastAPI Server**: Debug configuration for development server
- **Current File**: Debug any Python file
- **Tests**: Debug individual tests

## 📋 Available VS Code Tasks

Press `Ctrl+Shift+P` and type "Tasks: Run Task" to access:

- **Start FastAPI Dev Server**: Launch the development server with hot reload
- **Run Tests**: Execute the test suite
- **Run Tests with Coverage**: Run tests with coverage reports
- **Install Dependencies**: Install/update Python packages
- **Format Code**: Format code with Black
- **Lint Code**: Check code with Ruff
- **Type Check**: Run MyPy type checking

## 🐛 Debug Configurations

Available in VS Code's Run and Debug panel:

1. **FastAPI Development Server**: Debug the FastAPI app with hot reload
2. **FastAPI Production Server**: Debug the production configuration
3. **Python: Current File**: Debug the currently open Python file
4. **Python: Pytest**: Debug tests with pytest

## 🗃️ Database Access

### PostgreSQL
- **Host**: `postgres` (within container network)
- **Port**: `5432` (also forwarded to host)
- **Database**: `flasx_dev`
- **Username**: `flasx_user`
- **Password**: `flasx_password`

### Redis
- **Host**: `redis` (within container network)
- **Port**: `6379` (also forwarded to host)

### Connection Strings
The container automatically configures these environment variables:
```bash
DATABASE_URL=postgresql+asyncpg://flasx_user:flasx_password@postgres:5432/flasx_dev
REDIS_URL=redis://redis:6379/0
```

## 🚀 Running the Application

### Using VS Code Tasks (Recommended)
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Start FastAPI Dev Server"

### Using Debug Configuration
1. Open the Run and Debug panel (`Ctrl+Shift+D`)
2. Select "FastAPI Development Server"
3. Press F5 or click the play button

### Using Terminal
```bash
# In the VS Code integrated terminal
python -m fastapi dev flasx/main.py --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🧪 Running Tests

### Using VS Code Test Explorer
1. Open the Test Explorer panel
2. Click "Run All Tests" or run individual tests

### Using Tasks
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Run Tests" or "Run Tests with Coverage"

### Using Terminal
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=flasx --cov-report=html
```

## 📁 Project Structure

```
/home/app/code/          # Workspace root (mounted from host)
├── .devcontainer/       # Dev Container configuration
│   ├── devcontainer.json
│   └── docker-compose.yml
├── .vscode/            # VS Code settings
│   ├── launch.json     # Debug configurations
│   └── tasks.json      # Task definitions
├── flasx/              # FastAPI application
├── tests/              # Test files
├── data/               # Database and data files
├── logs/               # Application logs
└── pyproject.toml      # Poetry configuration
```

## 🔄 Development Workflow

### 1. Code Changes
- All code changes are automatically synced between host and container
- Hot reload is enabled for the FastAPI server
- Format on save is enabled for Python files

### 2. Dependencies
- Add dependencies using Poetry in the terminal:
  ```bash
  poetry add package-name
  # or for dev dependencies
  poetry add --group dev package-name
  ```

### 3. Testing
- Write tests in the `tests/` directory
- Tests are automatically discovered by VS Code
- Run tests frequently using the Test Explorer

### 4. Debugging
- Set breakpoints in VS Code
- Use the debug configurations to debug your application
- Debug tests by running them through the debugger

## 🐳 Docker Services Management

The Dev Container uses Docker Compose to manage additional services:

### Viewing Service Status
```bash
# In the VS Code terminal
docker-compose ps
```

### Accessing Service Logs
```bash
# PostgreSQL logs
docker-compose logs postgres

# Redis logs
docker-compose logs redis
```

### Restarting Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart postgres
```

## 🛠️ Troubleshooting

### Container Won't Start
1. Check Docker Desktop is running
2. Verify you have sufficient disk space
3. Try rebuilding the container:
   - Press `Ctrl+Shift+P`
   - Type "Dev Containers: Rebuild Container"

### Database Connection Issues
1. Ensure PostgreSQL service is running:
   ```bash
   docker-compose ps postgres
   ```
2. Check the database logs:
   ```bash
   docker-compose logs postgres
   ```

### Python Import Errors
1. Verify the virtual environment is activated (should be automatic)
2. Check that dependencies are installed:
   ```bash
   poetry install
   ```

### Port Conflicts
If you get port conflicts, you can modify the ports in `.devcontainer/docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port to 8001
```

## 🔒 Security Notes

- The Dev Container runs with a non-root user (`app`)
- Database passwords are for development only
- Don't commit real secrets to version control
- Use environment variables for sensitive configuration

## 🚀 Additional Features

### Volume Persistence
- **Source Code**: Mounted from host (real-time sync)
- **Virtual Environment**: Persistent Docker volume
- **Cache**: Persistent Docker volume for faster rebuilds

### Port Forwarding
VS Code automatically forwards these ports:
- **8000**: FastAPI application
- **5432**: PostgreSQL database
- **6379**: Redis cache

### Git Integration
- Git is pre-installed in the container
- GitHub CLI is available for enhanced Git operations
- Your host Git configuration is automatically shared

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/remote/containers)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [pytest Documentation](https://docs.pytest.org/)

## 🤝 Contributing

When contributing to this project:

1. **Use the Dev Container** for consistent development environment
2. **Run tests** before committing changes
3. **Format code** using the provided tools
4. **Write tests** for new features
5. **Update documentation** as needed

---

For additional help or questions about the development environment, please refer to the project documentation or open an issue.
