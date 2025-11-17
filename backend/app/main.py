from contextlib import asynccontextmanager

from app.api import auth, tasks
from app.core.config import settings
from app.database import SessionLocal
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup: Database tables are created via Alembic migrations
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Task Management API",
    description="A simple task management system",
    version="1.0.0",
    lifespan=lifespan,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])


@app.get("/")
async def root():
    return {"message": "Task Management API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness probe."""
    return {"status": "healthy", "service": "backend"}


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe.
    Checks database connectivity.
    """
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready", "database": "connected", "service": "backend"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "database": "disconnected", "error": str(e), "service": "backend"},
        )
