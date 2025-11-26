from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional

from app.database import Base
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from app.models.user import User


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True, nullable=False)
    description: Mapped[Optional[str]]
    is_completed: Mapped[bool] = mapped_column(default=False, server_default=text("false"), nullable=False)
    priority: Mapped[Literal["low", "medium", "high"]] = mapped_column(
        default="medium", server_default=text("'medium'")
    )
    category: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped[User] = relationship("User", back_populates="tasks")

    __table_args__ = (CheckConstraint("priority IN ('low', 'medium','high')", name="task_priority_check"),)
