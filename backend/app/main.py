import os

from app.api import auth, tasks
from app.core.config import settings
from app.database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Task Management API", description="A simple task management system", version="1.0.0")


@app.on_event("startup")
def create_tables():
    """Create database tables on application startup."""
    # Skip database creation during testing
    if os.getenv("TESTING") != "true":
        Base.metadata.create_all(bind=engine)


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
    return {"status": "healthy"}
