from typing import TYPE_CHECKING, Literal

from sqlalchemy import CheckConstraint, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixin import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Task(IdMixin, TimestampMixin, Base):
    """Task model representing user tasks with priority and completion status."""

    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str | None]
    is_completed: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    priority: Mapped[Literal["low", "medium", "high"]] = mapped_column(
        default="medium", server_default=text("'medium'")
    )
    category: Mapped[str | None]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="tasks")

    __table_args__ = (CheckConstraint("priority IN ('low', 'medium', 'high')", name="task_priority_check"),)
