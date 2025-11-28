from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.task import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text("false"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tasks: Mapped[List[Task]] = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
