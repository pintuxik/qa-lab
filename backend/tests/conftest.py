"""
Pytest configuration and fixtures for backend tests.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set testing environment variable before importing app
os.environ["TESTING"] = "true"

from app.core.security import get_password_hash
from app.database import Base, get_db
from app.main import app
from app.models import Task, User

from tests.test_data import Endpoints, TestUsers

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database."""
    user = User(
        username=TestUsers.VALID_USER["username"],
        email=TestUsers.VALID_USER["email"],
        hashed_password=get_password_hash(TestUsers.VALID_USER["password"]),
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin user in the database."""
    user = User(
        username=TestUsers.ADMIN_USER["username"],
        email=TestUsers.ADMIN_USER["email"],
        hashed_password=get_password_hash(TestUsers.ADMIN_USER["password"]),
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = client.post(
        Endpoints.AUTH_LOGIN,
        data={"username": TestUsers.VALID_USER["username"], "password": TestUsers.VALID_USER["password"]},
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers with token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_task(db_session, test_user):
    """Create a test task in the database."""
    task = Task(
        title="Test Task",
        description="This is a test task",
        priority="high",
        category="testing",
        is_completed=False,
        owner_id=test_user.id,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task
