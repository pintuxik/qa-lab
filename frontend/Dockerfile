# Base image
FROM python:3.14-slim-trixie

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy pyproject.toml
COPY pyproject.toml pyproject.toml

# Install dependencies
RUN uv sync

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Run the application
CMD ["bash", "start.sh"]
