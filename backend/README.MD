# QA Lab Backend

## Database Migration Guide

### Creating a New Migration

1. **Make changes to your models** in `app/models/`

2. **Generate migration with autogenerate** (detects model changes automatically):
   ```bash
   uv run alembic revision --autogenerate -m "Add account table"
   ```

   ⚠️ **Important:** Always use `--autogenerate` flag to detect schema changes!

3. **Review the generated migration** in `migrations/versions/`
   - Check that the upgrade() and downgrade() operations are correct
   - Verify data types and constraints
   - Add any custom data migrations if needed

4. **Rename the migration file** following the project convention:
   - Pattern: `NNN_description.py` (e.g., `003_add_account_table.py`)
   - NNN is a 3-digit incremental number (001, 002, 003, etc.)

5. **Update the revision ID** in the migration file:
   - Change `revision = "<hash>"` to `revision = "003"` (matching the filename)
   - Example:
     ```python
     revision = "003"
     down_revision = "002"
     ```

6. **Apply the migration** (choose one method):

   **Automatically (recommended for Docker):**
   ```bash
   docker-compose up --build -d
   ```
   Migrations run automatically on container startup.

   **Manually (for local development):**
   ```bash
   # Start database
   docker-compose up db -d

   # Run migration
   uv run alembic upgrade head
   ```

### Checking Migration Status

```bash
# View current migration version
uv run alembic current

# View migration history
uv run alembic history

# View pending migrations
uv run alembic history --verbose
```

### Rolling Back Migrations

1. **Downgrade to specific revision:**
   ```bash
   docker-compose up db -d
   uv run alembic downgrade 002
   ```

2. **Downgrade one version:**
   ```bash
   uv run alembic downgrade -1
   ```

3. **Revert model changes** in `app/models/`

4. **Delete the migration file** from `migrations/versions/`

### Troubleshooting

#### Empty Migration Generated

If `alembic revision --autogenerate` creates an empty migration:

1. **Check database is up to date:**
   ```bash
   uv run alembic current
   ```

2. **Ensure database schema matches previous migrations:**
   ```bash
   docker-compose up db -d
   uv run alembic upgrade head
   ```

3. **Verify model imports** in `migrations/env.py`:
   ```python
   from app.models import Base  # Ensure this imports all models
   ```

4. **Check model changes are saved** and imports are correct

5. **Try regenerating:**
   ```bash
   uv run alembic revision --autogenerate -m "Your description"
   ```

#### Common Issues

- **Missing `--autogenerate` flag:** Without it, Alembic creates an empty template
- **Database not running:** Start with `docker-compose up db -d`
- **Models not imported:** Check `migrations/env.py` imports all model files
- **Database out of sync:** Run `uv run alembic upgrade head` first
