from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# PERFORMANCE: Connection pooling configuration
# pool_size: Number of connections to keep open (default: 5)
# max_overflow: Additional connections allowed beyond pool_size (default: 10)
# pool_recycle: Recycle connections after N seconds to prevent stale connections (3600 = 1 hour)
# pool_pre_ping: Test connections before using them (slight overhead, but prevents errors)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Increased from 5 for 200 concurrent users
    max_overflow=30,  # Increased from 10 (50 total connections max)
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=False,  # Disabled for performance (asyncpg handles reconnection)
)
SessionLocal = async_sessionmaker(expire_on_commit=False, autocommit=False, autoflush=False, bind=engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db
