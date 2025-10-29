# QA Lab - Task Management System

A full-stack application built with FastAPI (backend) and Flask (frontend) for managing tasks with user authentication and database persistence. This project is designed for comprehensive testing of real-world applications and serves as the QA Lab testing environment.

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
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration & security
│   │   └── database.py     # Database connection
│   ├── pyproject.toml      # uv dependencies
│   ├── Dockerfile
│   ├── start.sh           # Startup script
│   └── init_db.py         # Database initialization
├── frontend/               # Flask frontend
│   ├── app/
│   │   ├── __init__.py
│   │   └── templates/      # HTML templates
│   ├── pyproject.toml      # uv dependencies
│   └── Dockerfile
├── tests/                  # Test files
│   └── test_api.py        # Example test script
├── docker-compose.yml      # Multi-container setup
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
   docker-compose up --build
   ```

3. **Wait for services to start** (first run may take a few minutes)

4. **Access the application:**
   - **Frontend**: http://localhost:5000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Database**: localhost:5432 (postgres/password)

5. **Default admin user:**
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

## 🧪 Testing Opportunities

This application is perfect for comprehensive testing:

### Unit Tests
- Test individual functions and models
- Test authentication logic
- Test task CRUD operations
- Test password hashing and JWT generation

### Integration Tests
- Test API endpoints with real database
- Test authentication flows
- Test frontend-backend communication
- Test database operations

### End-to-End Tests
- Test complete user registration flow
- Test task creation and management
- Test login/logout functionality
- Test responsive UI on different devices

### Performance Tests
- Load testing with multiple users
- Database performance under load
- API response time testing
- Frontend performance optimization

### Security Tests
- Test authentication bypass attempts
- Test SQL injection prevention
- Test JWT token security
- Test password strength requirements

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

# Start all services
docker-compose up

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

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

## 📈 Next Steps for Testing

1. **Set up test frameworks** (pytest, selenium, etc.)
2. **Create test data fixtures**
3. **Implement CI/CD pipeline**
4. **Add monitoring and logging**
5. **Implement caching**
6. **Add more complex features** (file uploads, notifications, etc.)

This application provides a solid foundation for learning and testing various aspects of full-stack development!
