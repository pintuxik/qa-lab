from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixin import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.task import Task


class User(IdMixin, TimestampMixin, Base):
    """User model representing application users."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text("false"))

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
