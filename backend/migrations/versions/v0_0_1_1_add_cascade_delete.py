"""Add ON DELETE CASCADE to tasks foreign key

Revision ID: v0.0.1.1
Revises: v0.0.1
Create Date: 2025-12-08

Hotfix: Enables database-level cascade deletion when user is deleted.
This is required because User model uses passive_deletes=True with lazy="noload",
delegating cascade deletion responsibility to the database.

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "v0.0.1.1"
down_revision: Union[str, None] = "v0.0.1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key constraint
    op.drop_constraint("tasks_owner_id_fkey", "tasks", type_="foreignkey")

    # Recreate with ON DELETE CASCADE for database-level cascade deletion
    op.create_foreign_key("tasks_owner_id_fkey", "tasks", "users", ["owner_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    # Drop the CASCADE foreign key
    op.drop_constraint("tasks_owner_id_fkey", "tasks", type_="foreignkey")

    # Restore original foreign key without CASCADE
    op.create_foreign_key("tasks_owner_id_fkey", "tasks", "users", ["owner_id"], ["id"])
