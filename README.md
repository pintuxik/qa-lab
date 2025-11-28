# QA Lab 

[![Tests](https://img.shields.io/badge/tests-273%20passing-brightgreen)](https://github.com/pintuxik/qa-lab)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green)](https://github.com/pintuxik/qa-lab)
[![Python](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**⭐ If you find this project helpful, please consider giving it a star!**

## 🙏 Acknowledgments
This application is my playground for learning full-stack development, testing practices, containerization, DB Migration and many more. Some features like UI, units, parts of automation and tests were originally built by AI agents. Backend is mostly rewritten by me with occasional assistance of Claude Code. Lots of things still lack polishing and even have rough edges. This is my way to learn: start building and grow knowledge. 

WHAT'S NEXT: Kubernetes cluster including minikube in local, CI/CD pipelines in Github Actions, Quality gates, Test and Prod environments, deployments into private cloud. 

## Description
A production-ready full-stack task management application built with FastAPI (backend) and Flask (frontend), featuring comprehensive automated testing, Docker deployment, and modern development practices.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#testing)
- [Docker Commands](#-docker-commands)
- [Future Enhancements](#-future-enhancements)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (optional for local development) 

### Running the Application

1. **Clone the repo and navigate to QA Lab directory:**
   ```bash
   git clone https://github.com/pintuxik/qa-lab.git
   cd qa-lab
   ```

2. **Start all services:**
   ```bash
   # Production-like mode (recommended for testing)
   docker-compose up --build
   
   # OR Development mode with hot reload
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **Wait for services to start** (first run may take a few minutes)

4. **Run tests:**
    ```bash
   # Run all tests (unit + API + UI)
   chmod +x run_all_tests.sh
   ./run_all_tests.sh
   ```

5. **Access the application:**
   - **Frontend**: http://localhost:5001
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Database**: localhost:5432 (postgres/password)

### First Time Setup

1. Register a new account or use the admin account (admin/admin123)
2. Login to access the dashboard
3. Create your first task using the "Add Task" button
4. Explore the API documentation at http://localhost:8000/docs


## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy ORM, Pydantic
- **Frontend**: Flask with Jinja2 templates and Bootstrap
- **Database**: PostgreSQL with automatic migrations with alembic
- **Authentication**: JWT tokens with secure password hashing
- **Containerization**: Docker & Docker Compose
- **Package Manager**: uv (ultra-fast package manager written in Rust)

## 📁 Project Structure

```
qa-lab/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── api/                 # API routes (auth, tasks)
│   │   ├── core/                # Configuration & security
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # Database connection
│   │   └── init_db.py           # Database initialization
│   │── tests/                   # Backend unit tests (45 tests)
├── frontend/                     # Flask frontend
│   ├── app/
│   │   ├── templates/           # Jinja2 HTML templates
│   │   ├── routes.py            # Flask routes
│   │   └── __init__.py
│   │── tests/                   # Frontend unit tests
├── tests/                        # Integration tests
│   ├── api/                     # API integration tests 
│   └── ui/                      # UI integration tests
├── docker-compose.yml            # Production-like setup (no volumes)
└── docker-compose.dev.yml        # Development setup (with volumes)
```

## 🔧 Configuration

### Environment Variables

The project uses `.env` files for configuration. Example templates are provided:

- [tests/.env.example](tests/.env.example) - Integration configuration
- [backend/.env.example](backend/.env.example) - Backend configuration
- [frontend/.env.example](frontend/.env.example) - Frontend configuration

**Quick Setup:**
```bash
# Copy example files
cp tests/.env.example tests/.env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

**Key Variables:**

**Backend (.env)**
```
DATABASE_URL=postgresql+psycopg://postgres:password@db:5432/taskmanager
SECRET_KEY=<your-generated-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:5001
```

**Frontend (.env)**
```
API_BASE_URL=http://backend:8000
SECRET_KEY=<your-generated-secret-key>
```

**Tests (.env)**
```
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5001
HEADLESS=true
```

## 🛠️ Development

### install git hooks

```bash
uv sync
pre-commit install
```

### Start Backend
```bash
cd qa-lab/backend
uv sync --group test
uv run granian --interface asgi app.main:app --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd qa-lab/frontend
uv sync --group test
uv run granian --interface wsgi app.main:app --host 0.0.0.0 --port 5001
```

## 🔬Testing

### Running Tests
```bash
# Run all tests (unit + integration)
cd tests
./run_all_tests.sh

# Run specific test suites
cd tests
./run_api_tests.sh              # API integration tests 
./run_ui_tests.sh               # UI tests with Playwright 
cd backend && uv run pytest     # Backend unit tests
cd frontend && uv run pytest    # Frontend unit tests
```

### Test Coverage

| Test Type | Count   | Coverage | Framework           | Execution                     |
|-----------|---------|----------|---------------------|-------------------------------|
| Backend Unit Tests | 199     | 79%      | pytest              | **Parallel -n auto (~10s)**   |
| Frontend Unit Tests | 21      | 86%      | pytest              | **Parallel -n auto (~3s)**    |
| API Integration Tests | 34      | -        | pytest + requests   | **Parallel -n auto (~4s)**    |
| UI Integration Tests | 19      | -        | pytest + Playwright | **Parallel -n auto/2 (~11s)** |
| **Total** | **273** | **88%**  | -                   | **~32s total**                |
 Execution time measured on Macbook Pro 16 2019 A2141

### Test Features
-  Automated test execution scripts
-  Allure reporting integration
-  Screenshot capture on UI test failures
-  Code coverage reports (HTML format)
-  CI/CD ready configuration
-  Comprehensive test documentation
-  Parallel execution for all tests including UI
-  100% test isolation with UUID-based identifiers

See [tests/README.md](tests/README.md) for detailed testing documentation.

## 🐳 Docker Commands

```bash
# Navigate to the project directory
cd qa-lab

# Start all services (production-like, no hot reload)
docker-compose up

# Start in development mode (with hot reload)
docker-compose -f docker-compose.dev.yml up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Access database
docker-compose exec db psql -U postgres -d taskmanager

# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### Docker Compose Files

- **`docker-compose.yml`** - Production-like setup without volume mounts. Use this for running tests.
- **`docker-compose.dev.yml`** - Development setup with volume mounts for hot code reloading. Use this when actively developing.

## 🚀 Future Enhancements

This is version 0.0.1 - planned improvements include:

### Testing & Quality
- [ ] Visual regression testing
- [ ] Performance/load testing with Locust
- [ ] Security testing (OWASP)
- [ ] Contract testing for API
- [ ] Mutation testing

### Features
- [ ] File attachments for tasks
- [ ] Task comments and collaboration
- [ ] Task templates and recurring tasks
- [ ] Advanced filtering and search

### Architecture
- [ ] Microservices architecture exploration
- [ ] Caching layer (Redis)
- [ ] Message queue (RabbitMQ/Celery)
- [ ] Modern frontend (React/Vue)

### DevOps
- [ ] GitHub Actions CI/CD pipeline
- [ ] Kubernetes deployment
- [ ] Monitoring and logging (Prometheus/Grafana)
- [ ] API rate limiting
- [x] Database migrations with Alembic

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**: Stop other services using ports 5001, 8000, or 5432
2. **Database connection failed**: Wait for PostgreSQL to fully start
3. **Frontend can't reach backend**: Check Docker network connectivity
4. **Permission denied**: Ensure Docker has proper permissions

## 🤝 Contributing

This is a learning project, but suggestions and feedback are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests
- Share your testing approaches
- Suggest new technologies to explore

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
