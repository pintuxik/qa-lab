"""
Pytest configuration and fixtures for backend tests.

Environment variables are loaded from .env.test by pytest-dotenv plugin.
See pyproject.toml [tool.pytest.ini_options] env_files setting.
"""

import pytest
import pytest_asyncio
from app.core.security import get_password_hash
from app.database import get_db
from app.main import app
from app.models import Base, Task, User
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from tests.test_data import Endpoints, TestUsers

# Use in-memory Async SQLite for testing with aiosqlite driver and in-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite connections."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as db:
        yield db

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Create a test client with database session override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user in the database."""
    user = User(
        username=TestUsers.VALID_USER["username"],
        email=TestUsers.VALID_USER["email"],
        hashed_password=await get_password_hash(TestUsers.VALID_USER["password"]),
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session):
    """Create an admin user in the database."""
    user = User(
        username=TestUsers.ADMIN_USER["username"],
        email=TestUsers.ADMIN_USER["email"],
        hashed_password=await get_password_hash(TestUsers.ADMIN_USER["password"]),
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = await client.post(
        Endpoints.AUTH_LOGIN,
        data={"username": TestUsers.VALID_USER["username"], "password": TestUsers.VALID_USER["password"]},
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers with token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def test_task(db_session, test_user):
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
    await db_session.commit()
    await db_session.refresh(task)
    return task
