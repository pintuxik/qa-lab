from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class IdMixin:
    """Mixin providing auto-incrementing id primary key field."""

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
