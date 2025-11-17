#!/usr/bin/env python3
"""
Run Alembic database migrations
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic import command
from alembic.config import Config


def run_migrations():
    """Run Alembic migrations to latest version"""
    try:
        # Get the path to alembic.ini
        alembic_cfg = Config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini"))

        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")

    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migrations()
