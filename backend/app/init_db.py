#!/usr/bin/env python3
"""
Database initialization script to create default admin user
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User


async def create_admin_user():
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = async_sessionmaker(expire_on_commit=False, autocommit=False, autoflush=False, bind=engine)

    async with SessionLocal() as db:
        try:
            # Check if admin already exists
            stmt = select(User).where(User.username == "admin")
            result = await db.execute(stmt)
            admin_user = result.scalar_one_or_none()

            if admin_user:
                print("Admin user already exists")
                return

            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=await get_password_hash("admin123"),
                is_admin=True,
                is_active=True,
            )

            db.add(admin_user)
            await db.commit()
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("Email: admin@example.com")

        except Exception as e:
            print(f"Error creating admin user: {e}")
            await db.rollback()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
