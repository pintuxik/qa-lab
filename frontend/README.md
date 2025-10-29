# Frontend Application

Flask-based frontend for the Task Management System.

## Structure

```
frontend/
├── app/
│   ├── __init__.py      # Application factory & entry point
│   ├── routes.py        # Route handlers
│   └── templates/       # Jinja2 templates
├── pyproject.toml       # Dependencies
└── Dockerfile           # Container definition
```

## Running Locally

```bash
# Install dependencies
uv sync

# Run the application
python app/__init__.py
```

## Running with Docker

```bash
# Build and run frontend only
docker-compose up --build frontend

# Or run the entire stack
docker-compose up --build
```

The frontend will be available at **http://localhost:5000**

## Architecture

- **Application Factory Pattern**: `create_app()` in `app/__init__.py` creates and configures the Flask app
- **Modular Routes**: All route handlers are in `app/routes.py` and registered via `register_routes()`
- **Flexible Imports**: Hybrid import system supports both direct script execution and module imports
- **Environment Config**: Uses `.env` file for configuration

## Environment Variables

- `API_BASE_URL`: Backend API endpoint (default: `http://backend:8000`)
- `SECRET_KEY`: Flask session secret key
