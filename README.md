# QA Lab - Task Management System

[![Tests](https://img.shields.io/badge/tests-119%20passing-brightgreen)](https://github.com/pintuxik/qa-lab)
[![Coverage](https://img.shields.io/badge/coverage-88%25-green)](https://github.com/pintuxik/qa-lab)
[![Python](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.120-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A production-ready full-stack task management application built with FastAPI (backend) and Flask (frontend), featuring comprehensive automated testing, Docker deployment, and modern development practices. This project demonstrates AI-assisted development and serves as a complete QA testing environment.

**🎯 Key Highlights:**
- 119 automated tests with 88% code coverage
- Complete CI/CD automation scripts
- Docker-ready production deployment
- RESTful API with OpenAPI documentation
- Modern responsive UI with Bootstrap 5

## 📋 Table of Contents

- [Architecture](#️-architecture)
- [Project Structure](#-project-structure)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Development](#️-development)
- [Comprehensive Testing](#-comprehensive-testing-suite)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)
- [Docker Commands](#-docker-commands)
- [Database Schema](#️-database-schema)
- [Security Features](#-security-features)
- [Troubleshooting](#-troubleshooting)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: Flask with Jinja2 templates and Bootstrap
- **Database**: PostgreSQL with automatic migrations
- **Authentication**: JWT tokens with secure password hashing
- **Containerization**: Docker & Docker Compose
- **UI**: Responsive Bootstrap 5 interface
- **Package Manager**: uv (ultra-fast Python package manager)

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
│   ├── tests/                   # Backend unit tests (45 tests)
│   │   ├── test_auth.py
│   │   ├── test_tasks.py
│   │   └── test_security.py
│   ├── pyproject.toml           # Dependencies & config
│   ├── Dockerfile
│   └── start.sh
├── frontend/                     # Flask frontend
│   ├── app/
│   │   ├── templates/           # Jinja2 HTML templates
│   │   ├── routes.py            # Flask routes
│   │   └── __init__.py
│   ├── tests/                   # Frontend unit tests (21 tests)
│   │   └── test_routes.py
│   ├── pyproject.toml
│   └── Dockerfile
├── tests/                        # Integration tests
│   ├── api/                     # API integration tests (34 tests)
│   │   ├── test_auth_api.py
│   │   ├── test_tasks_api.py
│   │   ├── conftest.py
│   │   └── README.md
│   └── ui/                      # UI integration tests (19 tests)
│       ├── test_auth_ui.py
│       ├── test_tasks_ui.py
│       ├── conftest.py
│       └── README.md
├── utils/                        # Shared utilities
│   └── utils.py
├── docker-compose.yml            # Production-like setup (no volumes)
├── docker-compose.dev.yml        # Development setup (with volumes)

├── run_all_tests.sh             # Run all 119 tests
├── run_api_tests.sh             # Run API integration tests
├── run_ui_tests.sh              # Run UI integration tests
├── setup_backend_for_tests.sh   # Automated backend setup
├── stop_backend.sh              # Stop backend services
├── TESTING.md                   # Comprehensive testing guide
└── README.md
```

## ✨ Features

- **User Management**: Registration, login, and authentication
- **Task CRUD**: Create, read, update, and delete tasks
- **Task Properties**: Title, description, priority, category, completion status
- **Dashboard**: Statistics and task overview
- **Responsive UI**: Modern Bootstrap interface
- **RESTful API**: Complete API with automatic documentation
- **Database**: PostgreSQL with proper relationships
- **Security**: JWT authentication and password hashing

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- uv package manager (optional for local development)
- Git (optional, for cloning)

### Running the Application

1. **Navigate to the QA Lab directory:**
   ```bash
   cd qa-lab
   ```

2. **Start all services:**
   ```bash
   # Production-like mode (recommended for testing)
   docker-compose up --build
   
   # OR Development mode with hot reload
   docker-compose -f docker-compose.dev.yml up --build
   ```
   
   **Note**: Use the default `docker-compose.yml` for running tests to avoid container reload issues. Use `docker-compose.dev.yml` when actively developing and you want code changes to reflect immediately.

3. **Wait for services to start** (first run may take a few minutes)

4. **Run tests:** (UI tests are executed in headed mode with slow motion enabled for demonstration purposes.)
    ```bash
   # Run all tests (unit + API + UI)
   chmod +x run_all_tests.sh
   ./run_all_tests.sh
   ```

5. **Access the application:**
   - **Frontend**: http://localhost:5000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Database**: localhost:5432 (postgres/password)

6. **Default admin user:**
   - **Username**: admin
   - **Password**: admin123
   - **Email**: admin@example.com

### First Time Setup

1. Register a new account or use the admin account
2. Login to access the dashboard
3. Create your first task using the "Add Task" button
4. Explore the API documentation at http://localhost:8000/docs

## 🛠️ Development

### Backend Development (FastAPI)
```bash
cd qa-lab/backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development (Flask)
```bash
cd qa-lab/frontend
uv sync
uv run python app/__init__.py
```

### Database Management
The database is automatically initialized with:
- Required tables (users, tasks)
- Default admin user
- Proper relationships and constraints

## 🧪 Comprehensive Testing Suite

This project includes **119 automated tests** with **88% code coverage**, demonstrating professional testing practices.

### Test Coverage

| Test Type | Count | Coverage | Framework |
|-----------|-------|----------|-----------|
| Backend Unit Tests | 45 | 85% | pytest |
| Frontend Unit Tests | 21 | 91% | pytest |
| API Integration Tests | 34 | - | pytest + requests |
| UI Integration Tests | 19 | - | Playwright |
| **Total** | **119** | **88%** | - |

### Running Tests

```bash
# Run all tests (unit + integration)
./run_all_tests.sh

# Run specific test suites
./run_api_tests.sh              # API integration tests
./run_ui_tests.sh               # UI tests with Playwright
cd backend && uv run pytest     # Backend unit tests
cd frontend && uv run pytest    # Frontend unit tests
```

### Test Features
- ✅ Automated test execution scripts
- ✅ Allure reporting integration
- ✅ Screenshot capture on UI test failures
- ✅ Code coverage reports (HTML format)
- ✅ CI/CD ready configuration
- ✅ Comprehensive test documentation

See [TESTING.md](TESTING.md) for detailed testing documentation.

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Tasks
- `GET /api/tasks` - Get user's tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### System
- `GET /` - API status
- `GET /health` - Health check

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
DATABASE_URL=postgresql://postgres:password@db:5432/taskmanager
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:5000
```

**Frontend (.env)**
```
API_BASE_URL=http://backend:8000
SECRET_KEY=your-super-secret-key-change-in-production
```

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
```

### Docker Compose Files

- **`docker-compose.yml`** - Production-like setup without volume mounts. Use this for running tests to avoid container reload issues.
- **`docker-compose.dev.yml`** - Development setup with volume mounts for hot code reloading. Use this when actively developing.
- **`docker-compose.prod.yml`** - Same as default, provided for clarity.

## 🗄️ Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique)
- `username` (Unique)
- `hashed_password`
- `is_active`
- `is_admin`
- `created_at`

### Tasks Table
- `id` (Primary Key)
- `title`
- `description`
- `is_completed`
- `priority` (low/medium/high)
- `category`
- `created_at`
- `updated_at`
- `owner_id` (Foreign Key to Users)

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- CORS protection
- SQL injection prevention
- Input validation with Pydantic
- Secure session management

## 📱 UI Features

- Responsive Bootstrap 5 design
- Task cards with priority indicators
- Modal forms for task creation
- Dropdown menus for task actions
- Statistics dashboard
- Flash messages for user feedback
- Font Awesome icons

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**: Stop other services using ports 5000, 8000, or 5432
2. **Database connection failed**: Wait for PostgreSQL to fully start
3. **Frontend can't reach backend**: Check Docker network connectivity
4. **Permission denied**: Ensure Docker has proper permissions
5. **Frontend container reloading during tests**: This was caused by volume mounts in docker-compose.yml. The default configuration now uses production-like setup without volume mounts. For development with hot reload, use `docker-compose -f docker-compose.dev.yml up`

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

## 🚀 Future Enhancements

This is version 1.0 - planned improvements include:

### Testing & Quality
- [ ] Visual regression testing
- [ ] Performance/load testing with Locust
- [ ] Security testing (OWASP)
- [ ] Contract testing for API
- [ ] Mutation testing

### Features
- [ ] Real-time notifications (WebSockets)
- [ ] File attachments for tasks
- [ ] Task comments and collaboration
- [ ] Task templates and recurring tasks
- [ ] Advanced filtering and search

### Architecture
- [ ] GraphQL API option
- [ ] Microservices architecture exploration
- [ ] Caching layer (Redis)
- [ ] Message queue (RabbitMQ/Celery)
- [ ] Modern frontend (React/Vue)

### DevOps
- [ ] GitHub Actions CI/CD pipeline
- [ ] Kubernetes deployment
- [ ] Monitoring and logging (Prometheus/Grafana)
- [ ] API rate limiting
- [ ] Database migrations with Alembic

## 🤝 Contributing

This is a learning project, but suggestions and feedback are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests
- Share your testing approaches
- Suggest new technologies to explore

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Windsurf AI](https://codeium.com/windsurf) coding assistant
- Demonstrates AI-assisted development practices
- Inspired by modern full-stack development patterns

---

**⭐ If you find this project helpful, please consider giving it a star!**

This application provides a solid foundation for learning full-stack development, testing practices, and AI-assisted coding!
