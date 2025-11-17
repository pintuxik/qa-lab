# Base image
FROM python:3.14-slim-trixie

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies
RUN apt-get update && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy pyproject.toml
COPY pyproject.toml pyproject.toml

# Install dependencies
RUN uv sync

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["bash", "start.sh"]
